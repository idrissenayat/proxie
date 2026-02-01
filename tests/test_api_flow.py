import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import status
from src.platform.main import fastapi_app as app
from src.platform.auth import get_current_user, require_role, get_optional_user

def test_full_transaction_flow(client: TestClient):
    # Use unique data to avoid matching other test data
    unique_suffix = uuid4().hex[:8]
    test_city = f"Brooklyn_{unique_suffix}"
    
    # Setup dependency overrides for provider
    provider_id_val = str(uuid4())
    provider_user = {
        "sub": provider_id_val,
        "email": f"provider_{unique_suffix}@example.com",
        "public_metadata": {"role": "provider"}
    }
    
    app.dependency_overrides[get_current_user] = lambda: provider_user
    app.dependency_overrides[get_optional_user] = lambda: provider_user
    
    try:
        # 1. Create Provider
        print("Step 1: Create Provider")
        provider_email = provider_user["email"]
        prov_resp = client.post("/providers/", json={
            "name": "Flow Provider",
            "email": provider_email,
            "location": {
                "city": test_city,
                "service_radius_km": 50
            },
            "specializations": ["hair"],
            "availability": {
                 "timezone": "UTC"
            }
        })
        assert prov_resp.status_code == 201, f"Failed at Step 1: {prov_resp.json()}"
        provider_id = prov_resp.json()["id"]

        # 2. Add Service
        print("Step 2: Add Service")
        svc_resp = client.post(f"/providers/{provider_id}/services", json={
            "name": "Curly Haircut",
            "description": "Expert curly cut",
            "price_min": 50,
            "price_max": 100,
            "duration_minutes": 60
        })
        assert svc_resp.status_code == 201, f"Failed at Step 2: {svc_resp.json()}"
        service_id = svc_resp.json()["id"]

        # 3. Consumer Creates Request
        print("Step 3: Consumer Creates Request")
        consumer_id_val = str(uuid4())
        consumer_user = {
            "sub": consumer_id_val,
            "email": f"consumer_{unique_suffix}@example.com",
            "public_metadata": {"role": "consumer"}
        }
        
        # Switch to Consumer
        app.dependency_overrides[get_current_user] = lambda: consumer_user
        app.dependency_overrides[get_optional_user] = lambda: consumer_user

        req_resp = client.post("/requests/", json={
            "consumer_id": consumer_id_val,
            "raw_input": "I need a curly haircut in " + test_city,
            "service_category": "hair",
            "service_type": "haircut",
            "requirements": {
                "specializations": ["hair"] # Match provider specialization
            },
            "location": {
                "city": test_city
            },
            "timing": {
                "urgency": "flexible"
            },
            "budget": {
                "min": 40,
                "max": 200
            }
        })
        assert req_resp.status_code == 201, f"Failed at Step 3: {req_resp.json()}"
        request_data = req_resp.json()
        request_id = request_data["id"]
        
        # 4. Verify Match
        print(f"Step 4: Verify Match. Provider ID: {provider_id}, Matched: {request_data.get('matched_providers')}")
        assert provider_id in request_data["matched_providers"]

        # 5. Provider Creates Offer
        print("Step 5: Provider Creates Offer")
        # Switch back to Provider
        app.dependency_overrides[get_current_user] = lambda: provider_user
        app.dependency_overrides[get_optional_user] = lambda: provider_user

        offer_resp = client.post("/offers/", json={
            "request_id": request_id,
            "provider_id": provider_id,
            "service_id": service_id,
            "service_name": "Curly Haircut",
            "available_slots": [
                {"date": "2026-05-20", "start_time": "10:00", "end_time": "11:00"}
            ],
            "price": 75.0,
            "message": "I can do this!"
        })
        assert offer_resp.status_code == 201, f"Failed at Step 5: {offer_resp.json()}"
        offer_id = offer_resp.json()["id"]

        # 6. Consumer Accepts Offer
        print("Step 6: Consumer Accepts Offer")
        # Switch back to Consumer
        app.dependency_overrides[get_current_user] = lambda: consumer_user
        app.dependency_overrides[get_optional_user] = lambda: consumer_user

        accept_resp = client.put(f"/offers/{offer_id}/accept")
        assert accept_resp.status_code == 200, f"Failed at Step 6: {accept_resp.json()}"
        booking_data = accept_resp.json()
        booking_id = booking_data["id"]
        assert booking_data["status"] == "confirmed"

        # 7. Complete Booking
        print("Step 7: Complete Booking")
        # Let's use provider
        app.dependency_overrides[get_current_user] = lambda: provider_user
        app.dependency_overrides[get_optional_user] = lambda: provider_user

        complete_resp = client.put(f"/bookings/{booking_id}/complete")
        assert complete_resp.status_code == 200, f"Failed at Step 7: {complete_resp.json()}"
        assert complete_resp.json()["status"] == "completed"

        # 8. Review
        print("Step 8: Review")
        # Consumer reviews
        app.dependency_overrides[get_current_user] = lambda: consumer_user
        app.dependency_overrides[get_optional_user] = lambda: consumer_user

        review_resp = client.post("/reviews/", json={
            "booking_id": booking_id,
            "provider_id": provider_id,
            "consumer_id": consumer_id_val,
            "rating": 5,
            "comment": "Great cut!"
        })
        assert review_resp.status_code == 201, f"Failed at Step 8: {review_resp.json()}"
    finally:
        app.dependency_overrides = {}
