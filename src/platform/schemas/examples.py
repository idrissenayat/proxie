"""
Example request/response data for API documentation.
"""

# Request Examples
REQUEST_CREATE_EXAMPLE = {
    "consumer_id": "550e8400-e29b-41d4-a716-446655440000",
    "raw_input": "I need a haircut for curly hair in Brooklyn this weekend",
    "service_category": "hairstylist",
    "service_type": "haircut",
    "requirements": {
        "description": "Need someone experienced with curly hair",
        "specializations": ["curly hair"]
    },
    "location": {
        "city": "Brooklyn",
        "neighborhood": "Bed-Stuy",
        "max_distance_km": 5
    },
    "timing": {
        "urgency": "specific_date",
        "preferred_dates": ["2026-02-15"],
        "preferred_times": ["afternoon"]
    },
    "budget": {
        "min": 60,
        "max": 80,
        "currency": "USD"
    }
}

PROVIDER_CREATE_EXAMPLE = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "location": {
        "city": "Brooklyn",
        "neighborhood": "Bed-Stuy",
        "service_radius_km": 10
    },
    "specializations": ["curly hair", "color", "styling"],
    "availability": {
        "timezone": "America/New_York",
        "monday": ["9:00-17:00"],
        "tuesday": ["9:00-17:00"],
        "wednesday": ["9:00-17:00"],
        "thursday": ["9:00-17:00"],
        "friday": ["9:00-17:00"]
    },
    "bio": "15 years of experience specializing in curly hair cuts and color."
}

OFFER_CREATE_EXAMPLE = {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "provider_id": "550e8400-e29b-41d4-a716-446655440002",
    "service_id": "550e8400-e29b-41d4-a716-446655440003",
    "service_name": "Haircut",
    "available_slots": [
        {
            "date": "2026-02-15",
            "start_time": "14:00",
            "end_time": "15:00"
        },
        {
            "date": "2026-02-16",
            "start_time": "10:00",
            "end_time": "11:00"
        }
    ],
    "price": 75.0,
    "currency": "USD",
    "price_notes": "Includes styling",
    "message": "I specialize in curly hair cuts and would love to help you!"
}

REVIEW_CREATE_EXAMPLE = {
    "booking_id": "550e8400-e29b-41d4-a716-446655440004",
    "provider_id": "550e8400-e29b-41d4-a716-446655440002",
    "consumer_id": "550e8400-e29b-41d4-a716-446655440000",
    "rating": 5,
    "comment": "Excellent service! Jane really knows how to work with curly hair."
}

CHAT_REQUEST_EXAMPLE = {
    "message": "I need a haircut for curly hair in Brooklyn",
    "session_id": "session_123",
    "role": "consumer",
    "consumer_id": "550e8400-e29b-41d4-a716-446655440000"
}

# Response Examples
REQUEST_RESPONSE_EXAMPLE = {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "consumer_id": "550e8400-e29b-41d4-a716-446655440000",
    "raw_input": "I need a haircut for curly hair in Brooklyn this weekend",
    "service_category": "hairstylist",
    "service_type": "haircut",
    "status": "matching",
    "matched_providers": [
        "550e8400-e29b-41d4-a716-446655440002"
    ],
    "created_at": "2026-01-28T10:00:00Z"
}

PROVIDER_RESPONSE_EXAMPLE = {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "location": {
        "city": "Brooklyn",
        "neighborhood": "Bed-Stuy"
    },
    "specializations": ["curly hair", "color", "styling"],
    "rating": 4.8,
    "review_count": 42,
    "status": "active",
    "verified": True
}

OFFER_RESPONSE_EXAMPLE = {
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "provider_id": "550e8400-e29b-41d4-a716-446655440002",
    "service_name": "Haircut",
    "available_slots": [
        {
            "date": "2026-02-15",
            "start_time": "14:00",
            "end_time": "15:00"
        }
    ],
    "price": 75.0,
    "currency": "USD",
    "status": "pending",
    "created_at": "2026-01-28T10:05:00Z"
}

BOOKING_RESPONSE_EXAMPLE = {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "offer_id": "550e8400-e29b-41d4-a716-446655440005",
    "provider_id": "550e8400-e29b-41d4-a716-446655440002",
    "consumer_id": "550e8400-e29b-41d4-a716-446655440000",
    "service_name": "Haircut",
    "scheduled_date": "2026-02-15",
    "scheduled_start": "14:00",
    "scheduled_end": "15:00",
    "price": 75.0,
    "currency": "USD",
    "status": "confirmed",
    "created_at": "2026-01-28T10:10:00Z"
}

# Error Examples
ERROR_404_EXAMPLE = {
    "detail": "Provider not found (id: 550e8400-e29b-41d4-a716-446655440000)"
}

ERROR_403_EXAMPLE = {
    "detail": "Not authorized to edit this profile"
}

ERROR_400_EXAMPLE = {
    "detail": "Invalid input data",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
}

ERROR_429_EXAMPLE = {
    "detail": "Rate limit exceeded. Maximum 60 requests per minute.",
    "rate_limit": {
        "limit": 60,
        "remaining": 0,
        "reset": 1706457600
    }
}
