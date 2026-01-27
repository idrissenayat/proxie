import asyncio
import os
from src.platform.services.llm_gateway import llm_gateway
from src.platform.config import settings

async def test_gateway():
    print("Testing LLMGateway...")
    messages = [{"role": "user", "content": "Hello, who are you?"}]
    
    try:
        response = await llm_gateway.chat_completion(messages=messages)
        print("\nResponse from LLM:")
        print(response.choices[0].message.content)
        print(f"\nModel used: {response.model}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure GOOGLE_API_KEY is set in environment for LiteLLM
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    
    asyncio.run(test_gateway())
