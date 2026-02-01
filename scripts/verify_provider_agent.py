"""
Verify Phase 3: Personal Provider Agent.
"""

import asyncio
import sys
import uuid
import json
from decimal import Decimal

# Ensure src is in path
sys.path.insert(0, ".")

from src.platform.database import SessionLocal
from src.platform.services.chat import ChatService, PERSONAL_PROVIDER_SYSTEM_PROMPT
from src.platform.models.provider import Provider
from src.platform.models.memory import ProviderMemory
from src.platform.services.memory_service import MemoryService

async def verify_provider_agent():
    print("🧪 Verified Personal Provider Agent Integration...")
    
    db = SessionLocal()
    chat_service = ChatService()
    
    # 1. Setup Test Provider with Memory
    provider_id = uuid.uuid4()
    clerk_id = f"prov_{provider_id}"
    print(f"👷 Creating test provider: {provider_id}")
    
    try:
        # Create Provider
        provider = Provider(
            id=provider_id,
            clerk_id=clerk_id,
            name="Bob The Builder",
            email=f"bob.{provider_id}@example.com",
            specializations=["general_contractor"]
        )
        db.add(provider)
        db.commit()
        
        # Add some memory manually
        memory = ProviderMemory(
            provider_id=provider_id,
            total_leads_received=10,
            total_offers_sent=5,
            conversion_rate=Decimal("20.0")
        )
        db.add(memory)
        db.commit()
        
        print("✅ Provider and memory setup complete")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return

    # 2. Test Context Injection
    # We will simulate the handle_chat logic parts related to context building
    
    context = {
        "provider_id": str(provider_id),
        "provider_name": "Bob The Builder",
        "role": "provider",
        "session_id": str(uuid.uuid4())
    }
    
    # Manually invoke memory service to verify retrieval
    memory_service = MemoryService(db)
    provider_ctx = await memory_service.get_provider_context(provider_id)
    
    stats = provider_ctx.get("performance", {})
    print(f"📊 Retrieved Stats: {json.dumps(stats, default=str)}")
    
    assert stats["leads"] == 10
    assert stats["offers"] == 5
    assert stats["conversion"] == 20.0
    print("✅ Stats verification passed")

    # 3. Simulate System Prompt Formatting
    # This logic matches what we put in chat.py
    system_prompt = PERSONAL_PROVIDER_SYSTEM_PROMPT.format(
        provider_name="Bob The Builder",
        leads_count=stats.get("leads", 0),
        offers_count=stats.get("offers", 0),
        conversion_rate=stats.get("conversion", 0.0),
        recent_offers_summary="No recent offers."
    )
    
    if "Total Leads: 10" in system_prompt and "Conversion Rate: 20.0%" in system_prompt:
        print("✅ System Prompt contains correct stats")
    else:
        print("❌ System Prompt malformed")
        print(system_prompt)

    # 4. Verify Tool Execution (Suggest Offer)
    print("🛠️ Testing 'suggest_offer' tool...")
    
    # We need to simulate an offer in history to test the averaging logic?
    # Actually, we didn't insert any offers in step 1, so it should default to 80 or similar.
    # Let's insert a mock offer to test the averaging.
    from src.platform.models.offer import Offer
    from src.platform.models.request import ServiceRequest
    from src.platform.models.consumer import Consumer
    
    try:
        # Need a consumer and request for the offer
        c_id = uuid.uuid4()
        consumer = Consumer(id=c_id, clerk_id=f"c_{c_id}", name="Test Consumer")
        db.add(consumer)
        
        r_id = uuid.uuid4()
        req = ServiceRequest(id=r_id, consumer_id=c_id, service_type="haircut", status="open")
        db.add(req)
        db.commit() # Ensure they exist
        
        offer = Offer(
            id=uuid.uuid4(),
            provider_id=provider_id,
            request_id=r_id,
            price=100.0,
            status="accepted"
        )
        db.add(offer)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to add mock offer: {e}")

    try:
        # Re-fetch context to populate cache if needed, but chat_service fetches it fresh
        result = await chat_service._execute_tool("suggest_offer", {"request_id": "mock_req", "provider_id": str(provider_id)}, context)
        print(f"Tool Result: {json.dumps(result)}")
        
        # Should be near 100 since that's our only offer
        price = result["suggestion"]["price"]
        assert price == 100.0
        print("✅ suggest_offer uses history correctly")
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")

    # Cleanup
    try:
        db.delete(provider) 
        db.commit()
        print("🧹 Cleanup complete")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_provider_agent())
