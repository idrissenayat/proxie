import asyncio
import os
import json
from src.platform.services.chat import ChatService
from src.platform.config import settings
import structlog

# Set up logging for the test
structlog.configure(
    processors=[structlog.processors.JSONRenderer()]
)

async def test_chat_flow():
    print("--- Testing Chat Service Multi-turn Integration ---")
    chat_service = ChatService()
    session_id = None
    
    # Turn 1: Initial request
    message1 = "I need a haircut in New York. My budget is around 60 dollars."
    print(f"\nUser: {message1}")
    
    session_id, response1, data1, draft1, awaiting1 = await chat_service.handle_chat(
        message=message1,
        session_id=session_id,
        role="consumer"
    )
    print(f"\nAI: {response1}")

    # Turn 2: Providing remaining info and asking to post
    message2 = "I need it tomorrow at 2pm. I have short wavy hair. Go ahead and create the request."
    print(f"\nUser: {message2}")
    
    session_id, response2, data2, draft2, awaiting2 = await chat_service.handle_chat(
        message=message2,
        session_id=session_id,
        role="consumer"
    )
    
    print(f"\nAI: {response2}")
    
    if draft2:
        print("\n[SUCCESS] Draft Request Detected!")
        print(f"Draft Details: {json.dumps(draft2.dict(), indent=2)}")
    else:
        print("\n[INFO] No draft yet. AI might still be clarifying.")

async def test_error_handling():
    print("\n--- Testing Error Handling (Invalid Model) ---")
    chat_service = ChatService()
    
    # We should see the fallback or error handling logic
    # (Since we can't easily break litellm without changing config, we'll just check if it survives a weird input)
    try:
        session_id, response, data, draft, awaiting = await chat_service.handle_chat(
            message="Hi",
            role="consumer"
        )
        print(f"Chat survived basic interaction: {True if response else False}")
    except Exception as e:
        print(f"Error handling failed: {e}")

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Just to ensure fallback doesn't crash on init if key is missing (though it shouldn't unless called)
        os.environ["ANTHROPIC_API_KEY"] = "mock-key"
        
    asyncio.run(test_chat_flow())
    asyncio.run(test_error_handling())
