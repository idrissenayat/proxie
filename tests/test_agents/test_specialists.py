import pytest
from langchain_core.messages import HumanMessage
from src.platform.services.orchestrator import proxie_orchestrator

@pytest.mark.asyncio
async def test_specialist_node_execution():
    """Test that routing to a specialist works and returns specialist info."""
    messages = [HumanMessage(content="I need a haircut fade")]
    context = {}
    
    # This should:
    # 1. Route to specialist (haircut)
    # 2. Execute specialist_node
    # 3. Return to concierge
    # 4. Return final response from concierge
    
    response_text, final_messages, final_context = await proxie_orchestrator.run(
        messages=messages,
        context=context,
        role="consumer"
    )
    
    # The specialist node currently returns: 
    # f"I am the {specialist_key.title()} Specialist. Based on your request, I've noted some technical requirements."
    # Then it goes to concierge, which might override if it's mock mode.
    # However, concierge_node adds a message to the state and then returns.
    
    # Let's check if the specialist message is in history or if response_text contains it
    # Actually, concierge_node will be the last one to run.
    # In mock mode, concierge_node will return "I've drafted a cleaning request..." OR "I understand..."
    
    # If it routed to specialist, the specialist message SHOULD be in final_messages.
    specialist_msgs = [m for m in final_messages if "Specialist" in m.content]
    assert len(specialist_msgs) > 0
    assert "Haircut Specialist" in specialist_msgs[0].content
