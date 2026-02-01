import pytest
from langchain_core.messages import HumanMessage, AIMessage
from src.platform.services.orchestrator import proxie_orchestrator, router_node

@pytest.mark.asyncio
async def test_router_specialist_routing():
    """Test that the router correctly identifies specialist keywords."""
    # Test haircut routing
    state = {"messages": [HumanMessage(content="I need a haircut")]}
    result = await router_node(state)
    assert result["next_step"] == "specialist"
    assert result["current_specialist"] == "haircut"

    # Test cleaning routing
    state = {"messages": [HumanMessage(content="My house needs cleaning")]}
    result = await router_node(state)
    assert result["next_step"] == "specialist"
    assert result["current_specialist"] == "cleaning"

@pytest.mark.asyncio
async def test_router_concierge_routing():
    """Test that the router defaults to concierge for general queries."""
    state = {"messages": [HumanMessage(content="Hello, how are you?")]}
    result = await router_node(state)
    assert result["next_step"] == "concierge"

@pytest.mark.asyncio
async def test_orchestrator_consumer_flow():
    """Test the full orchestrator flow for a consumer request in mock mode."""
    # This will trigger the mock draft message in llm_gateway.py
    messages = [HumanMessage(content="I need a cleaning in Brooklyn")]
    context = {"consumer_profile": {"name": "Test User"}}
    
    response_text, final_messages, final_context = await proxie_orchestrator.run(
        messages=messages,
        context=context,
        role="consumer"
    )
    
    assert "drafted a cleaning request" in response_text.lower()
    assert "ready to post" in response_text.lower()
    # Check if context was updated by the HACK in concierge_node
    assert "gathered_info" in final_context
    assert final_context["gathered_info"]["service_type"] == "cleaning"
