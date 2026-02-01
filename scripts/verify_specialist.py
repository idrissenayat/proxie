"""
Verify Phase 5: Specialist Agents.
"""

import asyncio
import sys
from unittest.mock import MagicMock

# Ensure src is in path
sys.path.insert(0, ".")

from src.platform.services.specialist_service import specialist_service
from src.platform.services.orchestrator import graph, AgentState

async def verify_specialist():
    print("🧪 Verifying Specialist Logic...")
    
    # 1. Test Service Directly
    print("\n🔍 Step 1: Testing SpecialistService.consult")
    result = specialist_service.consult("haircut", "I need a color correction for my 4C hair")
    
    print(f"Analysis: {result}")
    
    assert result["specialist"] == "haircut"
    assert "color_correction" in str(result["pricing_factors"])
    assert result["complexity_multiplier"] >= 3.0
    assert "4C" in result["terms_identified"]
    
    print("✅ Service logic verified")
    
    # 2. Test Orchestrator Routing
    print("\n🔍 Step 2: Testing Orchestrator Routing")
    
    # We simulate the graph execution
    from langchain_core.messages import HumanMessage
    
    initial_state = {
        "messages": [HumanMessage(content="I want a complex fade haircut")],
        "context": {},
        "user_id": "test",
        "session_id": "test",
        "role": "consumer",
        "next_step": "continue",
        "current_specialist": None,
        "response_text": ""
    }
    
    # Run the graph (this calls router -> specialist -> concierge)
    final_state = await graph.ainvoke(initial_state)
    
    # Check if specialist was engaged (search in message history)
    specialist_msg_found = False
    for m in final_state["messages"]:
        if "Haircut Specialist Analysis" in str(m.content):
            specialist_msg_found = True
            break
            
    print(f"Specialist Message Found: {specialist_msg_found}")
    assert specialist_msg_found is True
    
    response = final_state["response_text"]
    assert "fade" in response.lower()
    
    print("✅ Orchestrator routing verified")

if __name__ == "__main__":
    asyncio.run(verify_specialist())
