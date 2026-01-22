# Offer Schema

## Overview

An Offer is a provider agent's response to a service request.

## Schema Definition

```yaml
Offer:
  id: uuid
  created_at: datetime
  expires_at: datetime          # When offer expires
  
  # References
  request_id: uuid              # The service request
  provider_id: uuid             # Who is offering
  
  # Proposed Service
  service_id: uuid              # Which of provider's services
  service_name: string          # Human-readable name
  
  # Availability
  available_slots:
    - date: date
      start_time: time
      end_time: time
  
  # Pricing
  price: decimal
  currency: string
  price_notes: text             # Any conditions or notes
  
  # Provider Info (snapshot)
  provider_snapshot:
    name: string
    rating: float
    review_count: int
    portfolio_samples: string[] # 2-3 relevant images
  
  # Message
  message: text                 # Personal message from provider/agent
  
  # Status
  status: enum                  # pending, accepted, declined, expired, withdrawn
```

## Example

```json
{
  "id": "off_def456",
  "request_id": "req_xyz789",
  "provider_id": "prov_abc123",
  "service_name": "Curly Hair Cut",
  "available_slots": [
    {
      "date": "2026-01-24",
      "start_time": "14:00",
      "end_time": "15:00"
    },
    {
      "date": "2026-01-25",
      "start_time": "11:00",
      "end_time": "12:00"
    }
  ],
  "price": 70.00,
  "currency": "USD",
  "provider_snapshot": {
    "name": "Maya Johnson",
    "rating": 4.9,
    "review_count": 47,
    "portfolio_samples": [
      "https://..../curl1.jpg",
      "https://..../curl2.jpg"
    ]
  },
  "message": "I specialize in curly hair and would love to help! I use dry cutting techniques that work great for natural curls.",
  "status": "pending",
  "expires_at": "2026-01-23T18:00:00Z"
}
```

## Generation Rules

Provider agents generate offers based on:

1. **Match quality** - Does request match provider's specializations?
2. **Availability** - What slots are open?
3. **Pricing rules** - Provider's configured pricing
4. **Auto-accept settings** - Should this be auto-offered?

Offers expire after a configurable period (default: 24 hours).
