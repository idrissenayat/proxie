"""
Verify Memory Layer Foundation implementation.
"""

import asyncio
import sys
import uuid
from typing import Dict, Any

# Ensure src is in path
sys.path.insert(0, ".")

from src.platform.database import SessionLocal
from src.platform.services.memory_service import MemoryService
from src.platform.models.consumer import Consumer
from src.platform.models.provider import Provider

async def verify_memory_layer():
    print("🧪 Starting Memory Layer Verification...")
    
    db = SessionLocal()
    memory_service = MemoryService(db)
    
    # 1. Create a test consumer
    consumer_id = uuid.uuid4()
    print(f"👤 Creating test consumer: {consumer_id}")
    try:
        consumer = Consumer(
            id=consumer_id,
            name="Test User",
            email=f"test.user.{consumer_id}@example.com",
            phone="555-0100"
        )
        db.add(consumer)
        db.commit()
    except Exception as e:
        print(f"❌ Failed to create consumer: {e}")
        return

    # 2. Get initial context (should create empty memory)
    print("📥 Retrieving initial context...")
    try:
        context = await memory_service.get_consumer_context(consumer_id)
        assert context["memory"].consumer_id == consumer_id
        assert context["memory"].total_bookings == 0
        print("✅ Initial context retrieved successfully")
    except Exception as e:
        print(f"❌ Failed to retrieve context: {e}")
        return

    # 3. Simulate an interaction
    print("🔄 Simulating interaction...")
    interaction_data = {
        "session_id": uuid.uuid4(),
        "type": "request_creation",
        "input": "I need a haircut for $50 in Brooklyn",
        "output": "I can help with that.",
        "outcome": "in_progress",
        "tools": [
            {
                "name": "update_request_details",
                "args": {
                    "budget_min": 40,
                    "budget_max": 60,
                    "location": "Brooklyn, NY",
                    "budget": "40-60"
                }
            }
        ]
    }
    
    try:
        await memory_service.update_consumer_memory(consumer_id, interaction_data)
        print("✅ Memory updated successfully")
    except Exception as e:
        print(f"❌ Failed to update memory: {e}")
        return

    # 4. Verify updates
    print("🔍 Verifying updates...")
    try:
        updated_context = await memory_service.get_consumer_context(consumer_id)
        memory = updated_context["memory"]
        
        # Check explicit preferences
        assert memory.preferred_budget_min == 40
        assert memory.preferred_budget_max == 60
        
        # Check learned preferences
        assert memory.learned_preferences.get("last_location") == "Brooklyn, NY"
        
        # Check embedding (might be mocked or real depending on env)
        # assert memory.preference_embedding is not None 
        # (Embedding might be None if OPENAI key is missing/invalid, skipping assert)
        
        print("✅ Updates verified!")
        print(f"   Budget: {memory.preferred_budget_min}-{memory.preferred_budget_max}")
        print(f"   Location: {memory.learned_preferences.get('last_location')}")
        
    except Exception as e:
        print(f"❌ Failed to verify updates: {e}")
        return
        
    # Cleanup
    try:
        db.delete(consumer)
        db.commit()
        print("🧹 Cleanup complete")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

    print("\n🎉 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_memory_layer())
