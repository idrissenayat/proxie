
import asyncio
import sys
from uuid import uuid4
sys.path.insert(0, ".")

from src.platform.database import SessionLocal
from src.platform.models.request import ServiceRequest
from src.platform.routers.consumers import get_consumer_requests

async def test_retrieval():
    print("🧪 Testing request retrieval logic...")
    db = SessionLocal()
    
    # Create a test consumer
    c_id = uuid4()
    
    # Create requests with different statuses
    reqs = [
        ServiceRequest(id=uuid4(), consumer_id=c_id, status="matching", service_type="matching_test"),
        ServiceRequest(id=uuid4(), consumer_id=c_id, status="open", service_type="open_test"),
        ServiceRequest(id=uuid4(), consumer_id=c_id, status="pending", service_type="pending_test"),
        ServiceRequest(id=uuid4(), consumer_id=c_id, status="cancelled", service_type="cancelled_test"),
    ]
    
    for r in reqs:
        db.add(r)
    db.commit()
    
    try:
        # Test retrieval
        result = get_consumer_requests(c_id, db, user=None)
        open_list = result["requests"]["open"]
        types = [r["service_type"] for r in open_list]
        
        print(f"Retrieved types: {types}")
        
        assert "matching_test" in types
        assert "open_test" in types
        assert "pending_test" in types
        assert "cancelled_test" not in types
        
        print("✅ Retrieval logic verified!")
    finally:
        for r in reqs:
            db.delete(r)
        db.commit()
        db.close()

if __name__ == "__main__":
    asyncio.run(test_retrieval())
