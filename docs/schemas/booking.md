# Booking Schema

## Overview

A Booking represents a confirmed appointment between a consumer and provider.

## Schema Definition

```yaml
Booking:
  id: uuid
  created_at: datetime
  updated_at: datetime
  
  # References
  request_id: uuid              # Original request
  offer_id: uuid                # Accepted offer
  provider_id: uuid
  consumer_id: uuid
  
  # Service Details
  service_id: uuid
  service_name: string
  
  # Schedule
  scheduled_date: date
  scheduled_start: time
  scheduled_end: time
  timezone: string
  
  # Location
  location:
    type: enum                  # provider_location, consumer_location, other
    address: string             # Full address (revealed after booking)
    instructions: text          # Access notes, parking, etc.
  
  # Pricing
  price: decimal
  currency: string
  
  # Status
  status: enum                  # confirmed, completed, cancelled, no_show
  
  # Cancellation (if applicable)
  cancellation:
    cancelled_at: datetime
    cancelled_by: enum          # consumer, provider
    reason: text
  
  # Completion (if applicable)
  completion:
    completed_at: datetime
    actual_duration_minutes: int
    final_price: decimal        # May differ from quoted
    notes: text
  
  # Review (if submitted)
  review_id: uuid
```

## Example

```json
{
  "id": "book_ghi789",
  "request_id": "req_xyz789",
  "offer_id": "off_def456",
  "provider_id": "prov_abc123",
  "consumer_id": "cons_jkl012",
  "service_name": "Curly Hair Cut",
  "scheduled_date": "2026-01-24",
  "scheduled_start": "14:00",
  "scheduled_end": "15:00",
  "timezone": "America/New_York",
  "location": {
    "type": "provider_location",
    "address": "123 Fulton St, Brooklyn, NY 11217",
    "instructions": "Ring buzzer 3B. Second floor."
  },
  "price": 70.00,
  "currency": "USD",
  "status": "confirmed"
}
```

## Status Transitions

```
confirmed → completed (service delivered)
confirmed → cancelled (by either party)
confirmed → no_show (consumer didn't show)
```

## Notifications

On booking confirmation:
- Consumer receives: provider contact, location, instructions
- Provider receives: consumer contact, appointment details
