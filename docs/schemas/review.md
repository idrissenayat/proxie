# Review Schema

## Overview

A Review captures consumer feedback after a completed booking.

## Schema Definition

```yaml
Review:
  id: uuid
  created_at: datetime
  
  # References
  booking_id: uuid
  provider_id: uuid
  consumer_id: uuid
  
  # Rating
  rating: int                   # 1-5 stars
  
  # Feedback
  comment: text                 # Written review
  
  # Specific Ratings (optional)
  ratings_breakdown:
    quality: int                # 1-5
    punctuality: int            # 1-5
    communication: int          # 1-5
    value: int                  # 1-5
  
  # Visibility
  visible: boolean              # Public or hidden
  
  # Provider Response (optional)
  response:
    text: text
    responded_at: datetime
```

## Example

```json
{
  "id": "rev_mno345",
  "booking_id": "book_ghi789",
  "provider_id": "prov_abc123",
  "consumer_id": "cons_jkl012",
  "rating": 5,
  "comment": "Maya was amazing! She really understood my curls and gave me the best haircut I've had in years. Highly recommend!",
  "ratings_breakdown": {
    "quality": 5,
    "punctuality": 5,
    "communication": 5,
    "value": 5
  },
  "visible": true
}
```

## Collection Flow

After booking completion:

1. Consumer agent prompts: "How was your appointment with [Provider]?"
2. Consumer provides rating and optional comment
3. Review is stored and provider reputation is updated
4. Provider agent notifies provider of new review
5. Provider can optionally respond

## Reputation Calculation

Provider rating = weighted average of all reviews
- Recent reviews weighted more heavily
- Minimum 3 reviews before rating is displayed publicly
