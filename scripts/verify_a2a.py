"""
Verify Phase 6: Agent-to-Agent Protocol.
"""

import asyncio
import sys
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

# Ensure src is in path
sys.path.insert(0, ".")

from src.platform.services.a2a_protocol import a2a_protocol
from src.platform.services.chat import ChatService

async def verify_a2a():
    print("🧪 Verifying A2A Protocol...")
    
    # 1. Mock the MemoryService and SessionLocal internally used by A2A
    # We use patch.object or patch("module.Class")
    
    # Mock where they are defined, not where imported (since imported locally)
    with patch("src.platform.services.memory_service.MemoryService") as MockMemoryService:
        # Create a mock instance
        mock_instance = AsyncMock()
        MockMemoryService.return_value = mock_instance
        
        # Mock Provider Context
        class MockOffer:
            def __init__(self, price):
                self.price = price

        mock_ctx = {
            "recent_offers": [MockOffer(80.0), MockOffer(120.0)] # Avg 100
        }
        mock_instance.get_provider_context.return_value = mock_ctx
        
        # Also patch SessionLocal to context manage correctly
        with patch("src.platform.database.SessionLocal") as MockSessionLocal:
             mock_db = MagicMock()
             MockSessionLocal.return_value.__enter__.return_value = mock_db
             
             # 2. Test Direct Call
             print("\n🔍 Step 1: Testing A2AProtocol.request_quotes")
    
             provider_ids = [str(uuid4()), str(uuid4())]
             request = {"complexity_multiplier": 1.5, "service": "haircut"}
    
             quotes = await a2a_protocol.request_quotes(request, provider_ids)
    
             print(f"Quotes received: {len(quotes)}")
             if quotes:
                 print(f"Sample Quote: {quotes[0]}")
    
             assert len(quotes) == 2
             # Base 100 * 1.5 complexity = 150
             assert quotes[0]["price"] == 150.0
             assert quotes[0]["status"] == "quoted"

             print("✅ Protocol logic verified")
    
    # 3. Test Tool Integration (Mocking check)
    print("\n🔍 Step 2: Checking ChatService Tool Integration")
    from src.platform.services.chat import TOOL_DECLARATIONS
    # verify tool exists in declarations
    tool_names = [t["name"] for t in TOOL_DECLARATIONS]
    assert "request_quotes_from_agents" in tool_names
    print("✅ Tool 'request_quotes_from_agents' is registered")

    print("\n✅ Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_a2a())
