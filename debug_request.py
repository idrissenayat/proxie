#!/usr/bin/env python3
"""Debug script to test create_service_request directly."""

import asyncio
import sys
sys.path.insert(0, '.')

# Minimal test - just try to import and call the function
async def test():
    from uuid import uuid4

    print("Step 1: Importing handlers...")
    try:
        from src.mcp import handlers
        print("  OK")
    except Exception as e:
        print(f"  FAILED: {e}")
        return

    print("Step 2: Importing schemas...")
    try:
        from src.platform.schemas.request import (
            ServiceRequestCreate, RequestLocation,
            RequestRequirements, RequestTiming, RequestBudget
        )
        print("  OK")
    except Exception as e:
        print(f"  FAILED: {e}")
        return

    print("Step 3: Testing schema creation...")
    try:
        # Simulate what handlers.py does
        timing = {"urgency": "flexible"}
        budget = {"min": 40, "max": 40}
        location = {"city": "Alexandria"}
        requirements = {}

        schema = ServiceRequestCreate(
            consumer_id=uuid4(),
            raw_input="I need a haircut",
            service_category="haircut",
            service_type="haircut",
            requirements=RequestRequirements(**requirements),
            location=RequestLocation(**location),
            timing=RequestTiming(**timing),
            budget=RequestBudget(**budget),
            media=[]
        )
        print(f"  OK - Schema: {schema}")
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Step 4: Testing database connection...")
    try:
        from src.platform.database import SessionLocal, check_db_connection
        if check_db_connection():
            print("  OK - Database connected")
        else:
            print("  FAILED - Database not reachable")
            return
    except Exception as e:
        print(f"  FAILED: {e}")
        return

    print("Step 5: Testing full create_service_request...")
    try:
        result = await handlers.create_service_request(
            consumer_id=uuid4(),
            service_category="haircut",
            service_type="haircut",
            raw_input="I need a haircut in Alexandria, budget $40",
            requirements={},
            location={"city": "Alexandria"},
            timing={"urgency": "flexible"},
            budget={"min": 40, "max": 40},
            media=[]
        )
        print(f"  OK - Result: {result}")
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
