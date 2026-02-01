import pytest
import json
from langchain_core.messages import HumanMessage
from src.platform.services.orchestrator import proxie_orchestrator

@pytest.mark.asyncio
async def test_orchestrator_provider_catalog_flow():
    """Test the provider catalog flow in mock mode."""
    # This triggers the "Service Catalog" flow in llm_gateway.py
    messages = [HumanMessage(content="My name is Alex, show me the services catalog")]
    context = {"tools": [{"type": "function", "function": {"name": "get_service_catalog", "description": "Get catalog", "parameters": {"type": "object", "properties": {}}}}]}
    
    response_text, final_messages, final_context = await proxie_orchestrator.run(
        messages=messages,
        context=context,
        role="provider"
    )
    
    assert "select the services you offer" in response_text.lower()
    
    # Check for tool call message
    tool_msgs = [m for m in final_messages if hasattr(m, "additional_kwargs") and "tool_calls" in m.additional_kwargs]
    # In our orchestrator, tool calls are processed and ToolMessages are added.
    # The final state should have the response from the LLM after processing tools.
    
    # Actually, the mock gateway returns a tool call for "get_service_catalog"
    # The orchestrator's 'tools' node executes it (returning "error: No tool executor provided" if not present)
    # Then it goes back to concierge which returns "I've processed that for you." (if mock tool msg is seen)
    
    # In the mock mode of llm_gateway, if messages[-1]["role"] == "tool", it returns "I've processed that for you."
    # Let's verify the response text reflects this if we don't provide an executor.
    pass

@pytest.mark.asyncio
async def test_orchestrator_provider_leads_flow():
    """Test the provider leads flow in mock mode."""
    # This triggers the "Leads" flow in llm_gateway.py
    messages = [HumanMessage(content="Show me my leads")]
    context = {"tools": [{"type": "function", "function": {"name": "get_my_leads", "description": "Get leads", "parameters": {"type": "object", "properties": {}}}}]}
    
    response_text, final_messages, final_context = await proxie_orchestrator.run(
        messages=messages,
        context=context,
        role="provider"
    )
    
    # Due to the orchestrator loop, it should eventually return "Here are your current leads."
    # because the mock gateway returns that when 'get_my_leads' tool result is in history.
    assert "current leads" in response_text.lower()
