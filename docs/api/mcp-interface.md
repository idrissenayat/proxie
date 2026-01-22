# MCP Interface Specification

## Overview

Proxie exposes an MCP (Model Context Protocol) server that allows external AI agents to interact with the platform.

## Server Info

```json
{
  "name": "proxie",
  "version": "0.1.0",
  "description": "Agent-native platform for skilled service providers"
}
```

## Tools

### Consumer-Side Tools

#### create_service_request

Create a new service request.

**Parameters:**
```json
{
  "raw_input": "string - Original natural language request",
  "service_category": "string - e.g., 'hairstylist'",
  "service_type": "string - e.g., 'haircut'",
  "requirements": {
    "specializations": ["string"],
    "description": "string"
  },
  "location": {
    "city": "string",
    "neighborhood": "string (optional)",
    "max_distance_km": "number (optional)"
  },
  "timing": {
    "urgency": "asap | flexible | specific_date",
    "preferred_dates": ["date"],
    "preferred_times": ["morning | afternoon | evening"]
  },
  "budget": {
    "min": "number",
    "max": "number",
    "currency": "string"
  }
}
```

**Returns:**
```json
{
  "request_id": "uuid",
  "status": "pending | matching",
  "message": "string"
}
```

#### get_offers

Get offers for a service request.

**Parameters:**
```json
{
  "request_id": "uuid"
}
```

**Returns:**
```json
{
  "offers": [
    {
      "offer_id": "uuid",
      "provider_name": "string",
      "service_name": "string",
      "available_slots": [...],
      "price": "number",
      "rating": "number",
      "review_count": "number",
      "portfolio_samples": ["url"]
    }
  ]
}
```

#### accept_offer

Accept an offer and create a booking.

**Parameters:**
```json
{
  "offer_id": "uuid",
  "selected_slot": {
    "date": "date",
    "start_time": "time"
  }
}
```

**Returns:**
```json
{
  "booking_id": "uuid",
  "status": "confirmed",
  "details": {...}
}
```

#### submit_review

Submit a review for a completed booking.

**Parameters:**
```json
{
  "booking_id": "uuid",
  "rating": "number (1-5)",
  "comment": "string (optional)"
}
```

### Provider-Side Tools

#### get_requests

Get service requests matching provider's profile.

#### submit_offer

Submit an offer for a service request.

#### confirm_booking

Confirm a booking.

#### update_availability

Update provider's availability.

---

## Authentication

MCP connections are authenticated via API key passed in the connection headers.

## Rate Limits

- 100 requests per minute per API key
- Bulk operations count as single request
