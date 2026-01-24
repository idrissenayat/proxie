import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

def test_full_transaction_flow(client: TestClient):
    # 1. Create Provider
    provider_email = f"provider_{uuid4()}@example.com"
    prov_resp = client.post("/providers/", json={
        "name": "Flow Provider",
        "email": provider_email,
        "location": {
            "city": "Brooklyn",
            "service_radius_km": 5
        },
        "specializations": ["hair"],
        "availability": {
             "timezone": "UTC"
        }
    })
    assert prov_resp.status_code == 201
    provider_id = prov_resp.json()["id"]

    # 2. Add Service
    svc_resp = client.post(f"/providers/{provider_id}/services", json={
        "name": "Curly Haircut",
        "description": "Expert curly cut",
        "price_min": 50,
        "price_max": 100,
        "duration_minutes": 60
    })
    assert svc_resp.status_code == 201
    service_id = svc_resp.json()["id"]

    # 3. Consumer Creates Request
    # Use a matching city and service keyword
    consumer_id = str(uuid4())
    req_resp = client.post("/requests/", json={
        "consumer_id": consumer_id,
        "raw_input": "I need a curly haircut in Brooklyn",
        "service_category": "hair",
        "service_type": "haircut", # 'Curly Haircut' contains 'haircut' -> match? 
                                   # Matching logic ilike %service_type% -> %haircut% matches 'Curly Haircut'
                                   # Wait, simple ilike check: "Curly Haircut" LIKE "%haircut%"? Yes.
        "requirements": {
            "specializations": ["curly"]
        },
        "location": {
            "city": "Brooklyn"
        },
        "timing": {},
        "budget": {}
    })
    assert req_resp.status_code == 201
    request_data = req_resp.json()
    request_id = request_data["id"]
    
    # 4. Verify Match
    # Ideally matched_providers contains provider_id
    # Note: DB commit timing might be issue in some test envs, but here single thread.
    print(f"Matched Providers: {request_data['matched_providers']}")
    assert provider_id in request_data["matched_providers"]

    # 5. Provider Creates Offer
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
    assert offer_resp.status_code == 201
    offer_id = offer_resp.json()["id"]

    # 6. Consumer Accepts Offer
    accept_resp = client.put(f"/offers/{offer_id}/accept")
    assert accept_resp.status_code == 200
    booking_data = accept_resp.json()
    booking_id = booking_data["id"]
    assert booking_data["status"] == "confirmed"

    # 7. Complete Booking
    complete_resp = client.put(f"/bookings/{booking_id}/complete")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"

    # 8. Review
    review_resp = client.post("/reviews/", json={
        "booking_id": booking_id,
        "provider_id": provider_id,
        "consumer_id": consumer_id,
        "rating": 5,
        "comment": "Great cut!"
    })
    assert review_resp.status_code == 201
