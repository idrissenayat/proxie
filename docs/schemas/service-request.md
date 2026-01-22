# Service Request Schema

## Overview

A Service Request represents a consumer's need, parsed and structured by the consumer agent.

## Schema Definition

```yaml
ServiceRequest:
  id: uuid                      # Unique identifier
  created_at: datetime
  updated_at: datetime
  
  # Consumer
  consumer_id: uuid             # Who is requesting
  consumer_agent_id: string     # Which agent created this
  
  # Original Input
  raw_input: text               # Original natural language request
  
  # Parsed Request
  service_category: string      # e.g., "hairstylist"
  service_type: string          # e.g., "haircut"
  
  # Requirements
  requirements:
    specializations: string[]   # e.g., ["curly hair"]
    description: text           # Additional details
  
  # Location
  location:
    city: string
    neighborhood: string        # Optional
    coordinates:                # Optional, for distance
      lat: float
      lng: float
    max_distance_km: float      # How far consumer will travel
  
  # Timing
  timing:
    urgency: enum               # asap, flexible, specific_date
    preferred_dates: date[]     # Specific dates if provided
    preferred_times: string[]   # e.g., ["morning", "afternoon"]
    flexibility: text           # Any notes about flexibility
  
  # Budget
  budget:
    min: decimal
    max: decimal
    currency: string
    flexibility: enum           # strict, somewhat_flexible, flexible
  
  # Status
  status: enum                  # pending, matching, offers_received, 
                                # booked, expired, cancelled
  
  # Matching Results
  matched_providers: uuid[]     # Providers who received this request
  offers: uuid[]                # Offers received
  selected_offer: uuid          # Accepted offer (if any)
```

## Example

```json
{
  "id": "req_xyz789",
  "raw_input": "I need a haircut. I have curly hair and I'm looking for someone who really knows how to work with curls. I'm in Brooklyn, hoping for this weekend, budget around $60-80.",
  "service_category": "hairstylist",
  "service_type": "haircut",
  "requirements": {
    "specializations": ["curly hair"],
    "description": "Looking for someone experienced with curls"
  },
  "location": {
    "city": "Brooklyn",
    "max_distance_km": 10
  },
  "timing": {
    "urgency": "specific_date",
    "preferred_dates": ["2026-01-24", "2026-01-25"],
    "preferred_times": ["morning", "afternoon"],
    "flexibility": "This weekend preferred"
  },
  "budget": {
    "min": 60,
    "max": 80,
    "currency": "USD",
    "flexibility": "somewhat_flexible"
  },
  "status": "matching"
}
```

## Parsing Guidelines

The consumer agent should extract:

1. **Service type** - What do they need done?
2. **Specializations** - Any specific requirements?
3. **Location** - Where are they?
4. **Timing** - When do they need it?
5. **Budget** - What can they pay?

If any field is unclear, the agent should ask clarifying questions.
