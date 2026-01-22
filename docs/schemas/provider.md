# Provider Schema

## Overview

A Provider represents a skilled individual offering services through Proxie.

## Schema Definition

```yaml
Provider:
  id: uuid                      # Unique identifier
  created_at: datetime          # When registered
  updated_at: datetime          # Last modified
  
  # Identity
  name: string                  # Display name
  email: string                 # Contact email (private)
  phone: string                 # Contact phone (private)
  verified: boolean             # Identity verified
  
  # Profile
  bio: text                     # About the provider
  profile_photo_url: string     # Profile image
  
  # Location
  location:
    address: string             # Full address (private)
    city: string                # City
    neighborhood: string        # Neighborhood/area
    coordinates:                # For distance calculations
      lat: float
      lng: float
    service_radius_km: float    # How far they'll travel
  
  # Services (for hairstylist MVP)
  services:
    - id: uuid
      name: string              # e.g., "Curly Hair Cut"
      description: text
      duration_minutes: int
      price_min: decimal
      price_max: decimal
      currency: string          # Default: USD
  
  # Specializations
  specializations: string[]     # e.g., ["curly hair", "coloring", "braids"]
  
  # Portfolio
  portfolio:
    - id: uuid
      image_url: string
      caption: string
      service_id: uuid          # Which service this showcases
      created_at: datetime
  
  # Availability
  availability:
    timezone: string            # e.g., "America/New_York"
    schedule:                   # Weekly recurring schedule
      monday: [{start: "10:00", end: "18:00"}]
      tuesday: [{start: "10:00", end: "18:00"}]
      # ...
    exceptions: []              # Date-specific overrides
  
  # Settings
  settings:
    auto_accept: boolean        # Auto-accept matching requests
    min_notice_hours: int       # Minimum booking notice
    max_bookings_per_day: int
    instant_booking: boolean    # Allow instant booking
  
  # Reputation
  reputation:
    rating: float               # Average rating (1-5)
    review_count: int
    completed_bookings: int
    response_rate: float        # % of inquiries responded to
    response_time_hours: float  # Average response time
  
  # Status
  status: enum                  # active, paused, inactive
```

## Example

```json
{
  "id": "prov_abc123",
  "name": "Maya Johnson",
  "bio": "Curly hair specialist with 8 years of experience. I believe every curl is unique and deserves personalized care.",
  "location": {
    "city": "Brooklyn",
    "neighborhood": "Bed-Stuy",
    "service_radius_km": 5
  },
  "services": [
    {
      "name": "Curly Hair Cut",
      "description": "Dry cut technique for natural curls",
      "duration_minutes": 60,
      "price_min": 60,
      "price_max": 80
    }
  ],
  "specializations": ["curly hair", "natural hair", "dry cutting"],
  "reputation": {
    "rating": 4.9,
    "review_count": 47
  },
  "status": "active"
}
```

## Notes

- Phone and full address are kept private; only shared after booking confirmation
- Portfolio images stored in S3, URLs are pre-signed
- Availability is stored in provider's local timezone
- Reputation metrics are calculated, not directly editable
