import json
from src.platform.services.session_manager import SessionManager
from src.platform.services.context_tracker import ConversationContext, KnownFact, ContextSource

def test_serialization():
    sm = SessionManager(".test_sessions.json")
    
    # Create a complex session
    context = ConversationContext(service_type="haircut")
    context.facts_log.append(KnownFact(key="service_type", value="haircut", source=ContextSource.CURRENT_MESSAGE))
    
    session = {
        "messages": [
            {"role": "system", "content": "Hi"},
            {"role": "user", "content": "I need a haircut"}
        ],
        "context": context.dict(),
        "tools": [{"name": "test_tool", "parameters": {}}]
    }
    
    print("Attempting to save session...")
    try:
        sm.save_session("test_id", session)
        print("Success! File created.")
    except Exception as e:
        print(f"Failed to save session: {e}")

if __name__ == "__main__":
    test_serialization()
