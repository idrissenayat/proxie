import json
import structlog
from typing import Annotated, Dict, List, Optional, Sequence, TypedDict, Union, Any, Tuple
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END

from src.platform.services.llm_gateway import llm_gateway
from src.platform.config import settings

logger = structlog.get_logger(__name__)

# --- State Definition ---

class AgentState(TypedDict):
    """The state of the conversation graph."""
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
    context: Dict[str, Any]
    user_id: Optional[str]
    session_id: Optional[str]
    role: str # consumer, provider, enrollment
    next_step: str # continue, tools, end
    current_specialist: Optional[str]
    response_text: str

# --- Node Handlers ---

async def router_node(state: AgentState):
    """Determines the intent and routes to the appropriate agent."""
    messages = state["messages"]
    if not messages:
        return {"next_step": "concierge"}
        
    last_human_message = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            last_human_message = m.content
            break
            
    # Use LLM to classify if we need a specialist
    # For now, keyword-based to keep it fast
    keywords = {
        "haircut": ["hair", "cut", "trim", "color", "fade", "barber", "stylist"],
        "cleaning": ["clean", "maid", "house", "apartment"],
        "plumbing": ["plumb", "leak", "pipe", "drain", "faucet"],
    }
    
    for specialist, terms in keywords.items():
        if any(term in last_human_message.lower() for term in terms):
            return {"current_specialist": specialist, "next_step": "specialist"}
            
    return {"next_step": "concierge"}

async def concierge_node(state: AgentState):
    """Handles core interactions, onboarding, and general help."""
    from src.platform.services.chat import CONSUMER_SYSTEM_PROMPT, PROVIDER_SYSTEM_PROMPT, ENROLLMENT_SYSTEM_PROMPT
    
    messages = state["messages"]
    role = state.get("role", "consumer")
    
    # Select prompt
    if role == "provider":
        system_prompt = PROVIDER_SYSTEM_PROMPT.format(provider_name="Professional")
    elif role == "enrollment":
        system_prompt = ENROLLMENT_SYSTEM_PROMPT
    else:
        profile = state["context"].get("consumer_profile", {})
        system_prompt = CONSUMER_SYSTEM_PROMPT.format(consumer_profile=json.dumps(profile))

    # Convert messages for LiteLLM
    llm_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        if isinstance(m, HumanMessage):
            llm_messages.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            # Convert tool calls if present
            msg_dict = {"role": "assistant", "content": m.content}
            if "tool_calls" in m.additional_kwargs:
                msg_dict["tool_calls"] = m.additional_kwargs["tool_calls"]
            llm_messages.append(msg_dict)
        elif isinstance(m, ToolMessage):
             llm_messages.append({
                "role": "tool",
                "tool_call_id": m.tool_call_id,
                "name": m.name,
                "content": m.content
            })

    # Gateway tools should be passed from state
    tools = state["context"].get("tools")

    response = await llm_gateway.chat_completion(
        messages=llm_messages,
        tools=tools,
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
        feature=f"orchestrator_concierge_{role}"
    )
    
    ai_msg = response.choices[0].message
    
    # Check for tool calls
    if ai_msg.tool_calls:
        # We'll need a way for the ChatService to execute these, 
        # or we execute them here if we have reference to ChatService.
        # For simplicity, we'll return them in additional_kwargs.
        lc_ai_msg = AIMessage(
            content=ai_msg.content or "",
            additional_kwargs={"tool_calls": [t.to_dict() for t in ai_msg.tool_calls]}
        )
        return {
            "messages": [lc_ai_msg],
            "next_step": "tools"
        }

    return {
        "messages": [AIMessage(content=ai_msg.content)],
        "response_text": ai_msg.content,
        "next_step": "end"
    }

async def specialist_node(state: AgentState):
    """Handles domain-specific deep-dives."""
    specialist_key = state.get("current_specialist")
    content = f"I've brought in our {specialist_key} specialist to help with the technical details."
    return {
        "messages": [AIMessage(content=content)],
        "response_text": content,
        "next_step": "concierge"
    }

async def tool_node(state: AgentState):
    """Executes tool calls requested by the LLM."""
    # This node will be called if next_step is 'tools'
    # We need to execute the tools and update the state with results.
    # Since tool execution is tied to ChatService instance, 
    # we might need to pass an executor function in context.
    
    executor = state["context"].get("tool_executor")
    last_msg = state["messages"][-1]
    tool_calls = last_msg.additional_kwargs.get("tool_calls", [])
    
    tool_messages = []
    for tc in tool_calls:
        name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])
        
        if executor:
            result = executor(name, args)
        else:
            result = {"error": "No tool executor provided"}
            
        tool_messages.append(ToolMessage(
            tool_call_id=tc["id"],
            name=name,
            content=json.dumps(result)
        ))
        
    return {
        "messages": tool_messages,
        "next_step": "concierge" # Go back to concierge to process tool results
    }

# --- Graph Construction ---

def create_orchestrator():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("concierge", concierge_node)
    workflow.add_node("specialist", specialist_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next_step"],
        {
            "concierge": "concierge",
            "specialist": "specialist"
        }
    )
    
    workflow.add_conditional_edges(
        "concierge",
        lambda x: x["next_step"],
        {
            "tools": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("specialist", "concierge")
    workflow.add_edge("tools", "concierge")
    
    return workflow.compile()

graph = create_orchestrator()

class ProxieOrchestrator:
    """Interface for the ChatService to interact with LangGraph."""
    
    async def run(
        self, 
        messages: List[BaseMessage], 
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        role: str = "consumer"
    ) -> Tuple[str, List[BaseMessage], Dict[str, Any]]:
        
        initial_state = {
            "messages": messages,
            "context": context,
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "next_step": "continue",
            "current_specialist": None,
            "response_text": ""
        }
        
        final_state = await graph.ainvoke(initial_state)
        
        return (
            final_state["response_text"],
            final_state["messages"],
            final_state["context"]
        )

proxie_orchestrator = ProxieOrchestrator()
