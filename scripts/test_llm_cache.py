import asyncio
import os
import time
from src.platform.services.llm_gateway import llm_gateway
from src.platform.config import settings

async def test_gateway():
    print("--- Testing LLMGateway Caching ---")
    messages = [{"role": "user", "content": "How's the weather today?"}]
    
    # turn on verbose for gateway (if we want to see logs)
    # litellm.set_verbose = True
    
    print("\n[Turn 1] Initial request (expecting real call)...")
    start = time.time()
    response1 = await llm_gateway.chat_completion(messages=messages)
    print(f"Response: {response1.choices[0].message.content[:50]}...")
    print(f"Duration: {time.time() - start:.2f}s")
    
    print("\n[Turn 2] Same request (expecting CACHE HIT)...")
    start = time.time()
    response2 = await llm_gateway.chat_completion(messages=messages)
    print(f"Response: {response2.choices[0].message.content[:50]}...")
    print(f"Duration: {time.time() - start:.2f}s")
    
    if (time.time() - start) < 0.1:
        print("\n[SUCCESS] Cache hit confirmed by latency!")
    else:
        print("\n[WARNING] Request was too slow for a cache hit.")

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    
    asyncio.run(test_gateway())
