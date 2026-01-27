import requests
import json

BASE_URL = "http://localhost:8000"
REQUEST_ID = "afbdc692-60ab-4c77-9883-28d03b1e942b"
PROVIDER_ID = "f7ac8389-8c66-4954-a78f-a4c227ece7f6"

def test_request_details():
    print(f"\n--- Testing Request Details ({REQUEST_ID}) ---")
    resp = requests.get(f"{BASE_URL}/requests/{REQUEST_ID}")
    print(f"GET /requests/{REQUEST_ID}: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Status: {data.get('status')}")
        print(f"Status History Count: {len(data.get('status_history', []))}")
        print(f"Status History Sample: {data.get('status_history')[0] if data.get('status_history') else 'None'}")

def test_provider_profile():
    print(f"\n--- Testing Provider Profile ({PROVIDER_ID}) ---")
    resp = requests.get(f"{BASE_URL}/providers/{PROVIDER_ID}/profile")
    print(f"GET /providers/{PROVIDER_ID}/profile: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Business Name: {data.get('business_name')}")
        print(f"Jobs Completed: {data.get('jobs_completed')}")
        print(f"Response Rate: {data.get('response_rate')}")

def test_provider_portfolio():
    print(f"\n--- Testing Provider Portfolio ({PROVIDER_ID}) ---")
    # First get portfolio
    resp = requests.get(f"{BASE_URL}/providers/{PROVIDER_ID}/portfolio")
    print(f"GET /providers/{PROVIDER_ID}/portfolio: {resp.status_code}")
    
    # Add a photo
    print("Adding a photo...")
    photo_data = {
        "photo_url": "https://example.com/test-photo.jpg",
        "caption": "Test Photo",
        "display_order": 1
    }
    add_resp = requests.post(f"{BASE_URL}/providers/{PROVIDER_ID}/portfolio", json=photo_data)
    print(f"POST /providers/{PROVIDER_ID}/portfolio: {add_resp.status_code}")
    if add_resp.status_code == 200:
        photo_id = add_resp.json().get('id')
        print(f"Created Photo ID: {photo_id}")
        
        # Cleanup: delete the photo
        del_resp = requests.delete(f"{BASE_URL}/providers/{PROVIDER_ID}/portfolio/{photo_id}")
        print(f"DELETE /providers/{PROVIDER_ID}/portfolio/{photo_id}: {del_resp.status_code}")

def test_request_cancel():
    print(f"\n--- Testing Request Cancellation ---")
    # We should probably create a new request to test cancellation so we don't mess up existing data
    req_data = {
        "service_type": "Consultation",
        "raw_input": "I need a test consultation",
        "consumer_id": "00000000-0000-0000-0000-000000000000",
        "location": {"city": "New York"},
        "budget": {"min": 100, "max": 200},
        "timing": {"preference": "Anytime"},
        "service_category": "Professional Services",
        "requirements": {"details": "Test requirements"}
    }
    create_resp = requests.post(f"{BASE_URL}/requests/", json=req_data)
    if create_resp.status_code == 201: # It should be 201 for POST
        new_id = create_resp.json().get('id')
        print(f"Created new request: {new_id}")
        
        cancel_resp = requests.post(f"{BASE_URL}/requests/{new_id}/cancel")
        print(f"POST /requests/{new_id}/cancel: {cancel_resp.status_code}")
        
        # Verify status
        check_resp = requests.get(f"{BASE_URL}/requests/{new_id}")
        data = check_resp.json()
        print(f"New Status: {data.get('status')}")
        print(f"Status History Length: {len(data.get('status_history', []))}")
        print(f"Status History: {json.dumps(data.get('status_history'), indent=2)}")
    else:
        print(f"Failed to create request: {create_resp.status_code}")
        print(f"Response: {create_resp.text}")

if __name__ == "__main__":
    test_request_details()
    test_provider_profile()
    test_provider_portfolio()
    test_request_cancel()
