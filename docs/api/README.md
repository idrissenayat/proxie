# Proxie API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Proxie Architecture 2.0 uses **Clerk** for identity management and session handling.
- **Method:** JWT (JSON Web Token) via Bearer Authorization header.
- **Roles:** `consumer`, `provider`, `admin`.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | None |
| POST | `/auth/login` | Login user | None |
| POST | `/auth/logout` | Logout user | Required |
| POST | `/auth/refresh` | Refresh access token | Refresh |
| GET | `/auth/me` | Get current user | Required |

---

## Enrollment Endpoints

### Start Enrollment
Create a new provider enrollment session.

**Endpoint:** `POST /enrollment/start`

**Response:**
```json
{
  "enrollment_id": "uuid",
  "status": "draft"
}
```

---

### Get Enrollment
Retrieve current enrollment data.

**Endpoint:** `GET /enrollment/{id}`

**Response:**
```json
{
  "id": "uuid",
  "status": "draft|pending|verified|rejected",
  "data": {
    "full_name": "string",
    "business_name": "string",
    "email": "string",
    "phone": "string",
    "services": [...],
    "location": {...},
    "availability": {...},
    "bio": "string",
    "portfolio": [...]
  },
  "provider_id": "uuid|null",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

### Update Enrollment
Merge new data into enrollment.

**Endpoint:** `PATCH /enrollment/{id}`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "services": [{"id": "haircut", "name": "Haircut", "price": 35, "duration": 30}],
  "location": {"city": "Brooklyn", "address": "123 Main St"}
}
```

**Response:** Updated enrollment object

---

### Submit Enrollment
Submit enrollment for verification.

**Endpoint:** `POST /enrollment/{id}/submit`

**Response:**
```json
{
  "status": "verified|pending_verification",
  "message": "string",
  "provider_id": "uuid",
  "can_auto_verify": true
}
```

**Auto-Verification Rules:**
- ✅ Auto-verify: Services with `requires_license: false`
- ⏳ Manual review: Services with `requires_license: true`

---

## Service Catalog Endpoints

### Get Full Catalog
Get all categories with nested services.

**Endpoint:** `GET /services/catalog/full`

**Response:**
```json
[
  {
    "id": "hair_beauty",
    "name": "Hair & Beauty",
    "icon": "Scissors",
    "verification_level": "basic",
    "services": [
      {
        "id": "haircut",
        "name": "Haircut",
        "description": "Hair cutting and styling",
        "requires_license": false,
        "min_photos": 3,
        "typical_price_range": {"min": 30, "max": 100},
        "specializations": ["Men's cuts", "Women's cuts", ...]
      }
    ]
  }
]
```

---

### Get Category Details
Get a specific category with its services.

**Endpoint:** `GET /services/catalog/{category_id}`

**Response:** Single category object with services

---

### Get Service Details
Get metadata for a specific service.

**Endpoint:** `GET /services/services/{service_id}`

**Response:**
```json
{
  "id": "haircut",
  "name": "Haircut",
  "category_id": "hair_beauty",
  "category_name": "Hair & Beauty",
  "description": "Hair cutting and styling",
  "requires_license": false,
  "min_photos": 3,
  "typical_price_range": {"min": 30, "max": 100}
}
```

---

## Chat Endpoints

### Send Message
Interact with AI agents (consumer, provider, or enrollment).

**Endpoint:** `POST /chat/`
**Auth:** Required

**Request Body:**
```json
{
  "message": "I want to be a barber",
  "role": "consumer|provider|enrollment",
  "session_id": "uuid|null",
  "media": [...],
  "action": "approve_request|submit_enrollment|submit_offer|null"
}
```

---

### Chat Sessions
Manage conversation history and context.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/chat/sessions` | List user's sessions | Required |
| GET | `/chat/sessions/{id}` | Get session history | Required |
| DELETE | `/chat/sessions/{id}` | Delete session | Required |
| WS | `/chat/ws` | WebSocket connection | Required |

---

## MCP Endpoints (Agent Interface)
Real-time interface for external agents to interact with Proxie.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/mcp/sse` | SSE connection | Bearer |
| POST | `/mcp/messages` | JSON-RPC messages | Bearer |

---

## Provider Endpoints

### Get Public Profile
**Endpoint:** `GET /providers/{id}`
**Auth:** None

**Response:**
```json
{
  "id": "uuid",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-1234",
  "bio": "10 years experience...",
  "profile_photo_url": "url|null",
  "location": {
    "city": "Brooklyn",
    "address": "123 Main St",
    "coordinates": {...}
  },
  "specializations": ["Fades", "Curly hair"],
  "availability": {...},
  "status": "active|inactive",
  "verified": true,
  "rating": 4.8,
  "review_count": 42,
  "completed_bookings": 156
}
```

---

### List Providers
**Endpoint:** `GET /providers`

**Query Params:**
- `service_type`: Filter by service
- `location`: Filter by city
- `verified`: Filter by verification status

---

### Update Provider
**Endpoint:** `PUT /providers/{id}`

**Request Body:** Partial provider object

---

### Get Provider Profile (Public)
**Endpoint:** `GET /providers/{id}/profile`

**Response:**
```json
{
  "id": "uuid",
  "name": "John Smith",
  "email": "john@example.com",
  "business_name": "Smith's Cuts",
  "bio": "10 years experience specializing in curly hair...",
  "profile_photo_url": "https://...",
  "years_experience": 10,
  "location": {
    "city": "Brooklyn",
    "service_radius_km": 5.0
  },
  "specializations": ["Fades", "Curly hair"],
  "verified": true,
  "rating": 4.8,
  "review_count": 42,
  "jobs_completed": 156,
  "response_rate": 0.95,
  "average_response_time_hours": 2.3
}
```

---

### Update Provider Profile (Self)
**Endpoint:** `PATCH /providers/{id}/profile`

**Request Body:**
```json
{
  "name": "John Smith",
  "business_name": "Smith's Premium Cuts",
  "bio": "Updated bio...",
  "profile_photo_url": "https://...",
  "years_experience": 11
}
```

**Response:** Updated provider profile

**Notes:**
- Only the provider themselves can use this endpoint
- Fields are optional (partial update)

---

### Get Provider Portfolio
**Endpoint:** `GET /providers/{id}/portfolio`

**Response:**
```json
[
  {
    "id": "uuid",
    "provider_id": "uuid",
    "photo_url": "https://...",
    "caption": "Fade cut for client",
    "display_order": 0,
    "created_at": "timestamp"
  }
]
```

**Notes:** Sorted by `display_order` ascending

---

### Add Portfolio Photo
**Endpoint:** `POST /providers/{id}/portfolio`

**Request Body:**
```json
{
  "photo_url": "https://...",
  "caption": "Before and after transformation",
  "display_order": 5
}
```

**Response:** Created portfolio photo object (201 Created)

---

### Update Portfolio Photo
**Endpoint:** `PATCH /providers/{id}/portfolio/{photo_id}`

**Request Body:**
```json
{
  "caption": "Updated caption",
  "display_order": 2
}
```

**Response:** Updated portfolio photo object

---

### Delete Portfolio Photo
**Endpoint:** `DELETE /providers/{id}/portfolio/{photo_id}`

**Response:** 204 No Content

---

### Add Provider Service
**Endpoint:** `POST /providers/{id}/services`

**Request Body:**
```json
{
  "service_type": "Haircut",
  "price": 45,
  "duration_minutes": 30,
  "description": "Men's haircut with styling"
}
```

**Response:** Created service object (201 Created)

---

### Update Provider Service
**Endpoint:** `PATCH /providers/{id}/services/{service_id}`

**Request Body:**
```json
{
  "price": 50,
  "duration_minutes": 45
}
```

**Response:** Updated service object

---

### Delete Provider Service
**Endpoint:** `DELETE /providers/{id}/services/{service_id}`

**Response:** 204 No Content

---

## Request Endpoints

### Create Request
**Endpoint:** `POST /requests`

**Request Body:**
```json
{
  "consumer_id": "uuid",
  "service_category": "hair",
  "service_type": "Haircut",
  "raw_input": "I need a haircut for curly hair",
  "requirements": {...},
  "location": {"city": "Brooklyn"},
  "timing": {"urgency": "flexible"},
  "budget": {"min": 50, "max": 100},
  "media": [...]
}
```

---

### Get Request
**Endpoint:** `GET /requests/{id}`

**Response:**
```json
{
  "id": "uuid",
  "consumer_id": "uuid",
  "service_type": "Haircut",
  "service_category": "hair",
  "raw_input": "I need a haircut for curly hair",
  "requirements": {...},
  "location": {"city": "Brooklyn"},
  "budget": {"min": 50, "max": 100},
  "timing": {"preference": "Weekend"},
  "status": "matching|pending|confirmed|completed|cancelled",
  "status_history": [
    {
      "status": "matching",
      "timestamp": "2026-01-27T10:00:00Z",
      "note": "Request created"
    },
    {
      "status": "pending",
      "timestamp": "2026-01-27T11:30:00Z",
      "note": "3 offers received"
    }
  ],
  "media": [...],
  "offer_count": 3,
  "created_at": "timestamp"
}
```

**Notes:**
- `status_history` tracks all status transitions
- Use this for request detail pages and timeline displays

---

### Edit Request
**Endpoint:** `PATCH /requests/{id}`

**Request Body:**
```json
{
  "raw_input": "Updated request details...",
  "budget": {"min": 60, "max": 120},
  "timing": {"preference": "Anytime"}
}
```

**Response:** Updated request object

**Business Rules:**
- ✅ Allowed: `status == "matching"` AND `offer_count == 0`
- ❌ Blocked: After offers are received

**Notes:**
- Prevents bait-and-switch after providers have responded
- Use this for "Edit Request" functionality

---

### Cancel Request
**Endpoint:** `POST /requests/{id}/cancel`

**Response:**
```json
{
  "id": "uuid",
  "status": "cancelled",
  "status_history": [
    {...},
    {
      "status": "cancelled",
      "timestamp": "2026-01-27T12:00:00Z",
      "note": "Request cancelled (was pending)"
    }
  ]
}
```

**Business Rules:**
- ✅ Allowed: `status in ["matching", "pending"]`
- ❌ Blocked: After booking is confirmed or service completed

**Notes:**
- Automatically appends cancellation to status_history
- Status cannot be changed after cancellation

---

### List Requests
**Endpoint:** `GET /requests`

**Query Params:**
- `status`: `matching|pending|confirmed|completed`
- `consumer_id`: Filter by consumer
- `service_type`: Filter by service

---

### Get Consumer Requests
**Endpoint:** `GET /consumers/{consumer_id}/requests`

**Response:**
```json
{
  "counts": {
    "open": 2,
    "pending": 1,
    "upcoming": 3,
    "completed": 15
  },
  "requests": {
    "open": [...],
    "pending": [...],
    "upcoming": [...],
    "completed": [...]
  }
}
```

---

## Offer Endpoints

### Submit Offer
**Endpoint:** `POST /offers`

**Request Body:**
```json
{
  "request_id": "uuid",
  "provider_id": "uuid",
  "price": 75,
  "message": "I specialize in curly hair...",
  "proposed_slots": [
    {"date": "2026-01-28", "start_time": "14:00", "end_time": "15:00"}
  ]
}
```

---

### Get Offers for Request
**Endpoint:** `GET /requests/{request_id}/offers`

---

### Accept Offer
**Endpoint:** `PUT /offers/{offer_id}/accept`

**Request Body:**
```json
{
  "selected_slot": {
    "date": "2026-01-28",
    "start_time": "14:00"
  }
}
```

**Response:**
```json
{
  "booking_id": "uuid",
  "status": "confirmed"
}
```

---

## Booking Endpoints

### Get Booking
**Endpoint:** `GET /bookings/{id}`

**Response:**
```json
{
  "id": "uuid",
  "request_id": "uuid",
  "offer_id": "uuid",
  "provider_id": "uuid",
  "consumer_id": "uuid",
  "status": "confirmed|completed|cancelled",
  "scheduled_time": "2026-01-28T14:00:00Z",
  "price": 75,
  "location": {...},
  "created_at": "timestamp"
}
```

---

## Media Endpoints

### Upload Media
**Endpoint:** `POST /media/upload`

**Request Body:** `multipart/form-data`
- `file`: Image or video file
- `type`: `image|video`

**Response:**
```json
{
  "id": "uuid",
  "url": "https://...",
  "type": "image",
  "mime_type": "image/jpeg"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## Rate Limits
Currently no rate limits in MVP.

## Webhooks
Not implemented in MVP.

## Changelog

### v0.11.0 (2026-01-27)
- ✅ Request Details & Lifecycle Management
- ✅ Provider Profile System (Public & Self-Edit)
- ✅ Portfolio Management (CRUD)
- ✅ Service Management (CRUD)
- ✅ Status History Tracking
- ✅ Request Edit & Cancel with Business Rules

### v0.1.0 (2026-01-26)
- ✅ Provider Enrollment & Verification
- ✅ Service Catalog
- ✅ Chat with enrollment agent
- ✅ Auto-verification for basic services
- ✅ Consumer request management
- ✅ Offer submission and acceptance
