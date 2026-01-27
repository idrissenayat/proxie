import asyncio
import os
import json
import base64
from src.platform.services.chat import ChatService
from src.platform.services.specialists import specialist_registry
from src.platform.sessions import session_manager
from src.platform.config import settings

async def test_specialist_direct():
    """Test specialist analysis directly without LLM."""
    print("--- Testing Specialist Analysis Directly ---")
    
    specialist = specialist_registry.find_for_service("haircut")
    if not specialist:
        print("[ERROR] Haircut specialist not found!")
        return
    
    print(f"Found specialist: {specialist.name}")
    
    # Test analysis
    analysis = await specialist.analyze(
        service_type="haircut",
        description="I need a trim on my curly hair",
        location={"city": "New York"},
        budget={"min": 50, "max": 100},
        timing="Tomorrow at 2pm",
        media_descriptions=["Photo shows curly 3B hair, shoulder length"],
        additional_context={}
    )
    
    print(f"\n[SUCCESS] Specialist Analysis:")
    print(f"  - Valid: {analysis.is_valid}")
    print(f"  - Hair Type: {analysis.hair_type}")
    print(f"  - Complexity: {analysis.service_complexity}")
    print(f"  - Duration: {analysis.estimated_duration}")
    print(f"  - Notes: {analysis.notes}")

async def test_session_persistence():
    """Test that sessions are properly saved and retrieved from Redis."""
    print("\n--- Testing Redis Session Persistence ---")
    
    test_session_id = "test-session-12345"
    test_data = {
        "messages": [{"role": "system", "content": "You are helpful."}],
        "context": {"role": "consumer", "gathered_info": {"service_type": "haircut"}},
    }
    
    # Save
    session_manager.save_session(test_session_id, test_data)
    print(f"Saved session: {test_session_id}")
    
    # Retrieve
    retrieved = session_manager.get_session(test_session_id)
    if retrieved and retrieved.get("context", {}).get("gathered_info", {}).get("service_type") == "haircut":
        print("[SUCCESS] Session persisted and retrieved correctly!")
    else:
        print("[FAILED] Session data mismatch!")
        print(f"Retrieved: {retrieved}")
    
    # Cleanup
    session_manager.delete_session(test_session_id)

async def test_worker_task():
    """Test Celery worker task directly."""
    print("\n--- Testing Celery Worker Task ---")
    
    # Create a fake session in Redis first
    test_session_id = "worker-test-session"
    session_data = {
        "messages": [{"role": "system", "content": "You are helpful."}],
        "context": {
            "role": "consumer",
            "gathered_info": {"service_type": "haircut", "description": "curly hair trim"},
            "media": [{"id": "fake-media", "type": "image"}],
            "media_descriptions": ["3B curly hair, medium length"],
        },
    }
    session_manager.save_session(test_session_id, session_data)
    print(f"Created test session: {test_session_id}")
    
    # Run the task synchronously (simulating eager mode)
    from src.platform.worker import analyze_session_media
    result = analyze_session_media(test_session_id)
    
    print(f"Task result: {result}")
    
    # Check if specialist analysis was added
    updated_session = session_manager.get_session(test_session_id)
    analysis = updated_session.get("context", {}).get("specialist_analysis")
    
    if analysis:
        print(f"[SUCCESS] Specialist analysis added by worker!")
        print(f"  - Notes: {analysis.get('notes')}")
    else:
        print("[FAILED] No specialist analysis found after worker task.")
    
    # Cleanup
    session_manager.delete_session(test_session_id)

if __name__ == "__main__":
    asyncio.run(test_specialist_direct())
    asyncio.run(test_session_persistence())
    asyncio.run(test_worker_task())
