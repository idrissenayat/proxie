import asyncio
import json
import uuid
from src.platform.services.chat import ChatService
from src.platform.database import SessionLocal
from src.platform.models.consumer import Consumer

async def test_consumer_profile_flow():
    chat_service = ChatService()
    consumer_id = str(uuid.uuid4())
    
    print(f"--- 1. Setting up Consumer Profile for {consumer_id} ---")
    with SessionLocal() as db:
        consumer = Consumer(
            id=uuid.UUID(consumer_id),
            name="Test User",
            default_location={"city": "San Francisco", "state": "CA"}
        )
        db.add(consumer)
        db.commit()
    
    print("Profile created with location: San Francisco")

    print("\n--- 2. Sending Chat Message: 'I need a haircut' ---")
    # We expect the agent to NOT ask for the city because it's in the profile
    session_id, message, data, draft, awaiting_approval = await chat_service.handle_chat(
        message="I need a haircut",
        role="consumer",
        consumer_id=consumer_id
    )
    
    print(f"Agent Response: {message}")
    
    # Check if a draft was created or if the agent didn't ask for city
    if "San Francisco" in message or (draft and draft.get('location', {}).get('city') == "San Francisco"):
        print("\nSUCCESS: Agent acknowledged San Francisco or used it in the draft!")
    elif "city" not in message.lower() and "where" not in message.lower():
        print("\nSUCCESS: Agent did not ask for the city (likely used the profile).")
    else:
        print("\nFAILURE: Agent asked for the city or didn't use the profile info.")

if __name__ == "__main__":
    asyncio.run(test_consumer_profile_flow())
