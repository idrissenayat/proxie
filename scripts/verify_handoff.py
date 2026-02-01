"""
Verify Phase 4: Orchestrator Handoff.
"""

import asyncio
import sys
import uuid
from uuid import uuid4

# Ensure src is in path
sys.path.insert(0, ".")

from src.platform.services.chat import ChatService
from src.platform.services.session_manager import session_manager

async def verify_handoff():
    print("🧪 Verifying Handoff Logic...")
    
    chat_service = ChatService()
    session_id = str(uuid4())
    
    # 1. Start as Guest
    print("\n👤 Step 1: Guest Interaction")
    # Manually create a session stored in memory (via session_manager)
    # The actual chat service logic would do this, but we want to prepopulate it to simulate history
    
    # Simulate a guest session
    initial_context = {
        "role": "guest",
        "consumer_profile": {"name": "Guest"},
        "gathered_info": {"service": "haircut"} 
    }
    
    initial_session = {
        "messages": [{"role": "assistant", "content": "Hello guest!"}],
        "tools": [],
        "context": initial_context,
        "specialist_feedback": None
    }
    session_manager.save_session(session_id, initial_session)
    
    # 2. Upgrade to Consumer (Simulate Login)
    print("\n👤 Step 2: User 'Logs In' (Role Change to Consumer)")
    
    # We call handle_chat with range "consumer" on the SAME session_id
    # We mock the orchestration response to avoid calling actual LLM
    
    # Override orchestrator run to check for system message
    original_run = chat_service._execute_tool
    
    # We'll just check the session state after the "check_handoff" logic runs inside handle_chat
    # Since handle_chat is async and calls orchestrator, we can use a simpler approach:
    # We will simulate the same logic we added to handle_chat manually to verify HandoffManager
    
    from src.platform.services.handoff_manager import HandoffManager
    
    # Load session again
    session = session_manager.get_session(session_id)
    
    # Check Handoff
    is_handoff, msg = HandoffManager.check_handoff(session, "consumer", "Alice")
    
    print(f"Handoff Detected: {is_handoff}")
    print(f"Message: {msg}")
    
    assert is_handoff is True
    assert "Welcome back, Alice" in msg
    assert "personal history" in msg
    
    # 3. Simulate Provider Enrollment Handoff
    print("\n👤 Step 3: Enrollment -> Provider Handoff")
    
    sess_id_2 = str(uuid4())
    enroll_session = {
         "context": {"role": "enrollment"},
         "messages": []
    }
    HandoffManager.check_handoff(enroll_session, "provider", "Bob") # Should be detected
    
    is_handoff_prov, msg_prov = HandoffManager.check_handoff(
        {"context": {"role": "enrollment"}}, 
        "provider", 
        "Bob"
    )
    
    print(f"Provider Handoff Detected: {is_handoff_prov}")
    print(f"Message: {msg_prov}")
    
    assert is_handoff_prov is True
    assert "Bob" in msg_prov
    assert "Business Manager" in msg_prov

    print("\n✅ Handoff Logic Verified!")

if __name__ == "__main__":
    asyncio.run(verify_handoff())
