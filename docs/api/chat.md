# Proxie Chat API

The Chat API provides a conversational AI interface powered by Gemini (Google) for natural language interaction with the Proxie platform.

## Endpoint

```
POST /chat/
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | The user's message text |
| `session_id` | string (UUID) | No | Session ID for conversation continuity. If not provided, creates new session. |
| `role` | string | No | User role: `"consumer"` (default) or `"provider"` |
| `provider_id` | string (UUID) | No | Required if role is `"provider"` |

### Example Request

```json
{
  "message": "I need a haircut in Brooklyn, budget around $60-80",
  "session_id": null,
  "role": "consumer"
}
```

## Response

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string (UUID) | Session ID to use for subsequent messages |
| `message` | string | The agent's text response |
| `data` | object | Optional structured data (providers, bookings, requests) |

### Example Response

```json
{
  "session_id": "232403d8-8f99-4ade-af9e-78c99c753d25",
  "message": "Great! I found some amazing providers in Brooklyn. Here are your options:",
  "data": {
    "offers": [
      {
        "id": "uuid",
        "service_name": "Curly Haircut",
        "price": 75,
        "available_slots": [
          {"date": "2026-01-25", "start_time": "14:00", "end_time": "15:00"}
        ],
        "provider_snapshot": {
          "name": "Maya Johnson",
          "rating": 4.9,
          "review_count": 47
        },
        "message": "I specialize in curly and textured hair."
      }
    ]
  }
}
```

## Data Types

### When `data.offers` is present
The agent is presenting provider options. Each offer contains:
- `id`: Offer UUID
- `service_name`: Name of the service
- `price`: Price in USD
- `available_slots`: Array of time slots
- `provider_snapshot`: Provider details (name, rating, review_count)
- `message`: Provider's pitch

### When `data.booking` is present
The agent has confirmed a booking:
- `booking_id`: Booking UUID
- `status`: "confirmed"
- `provider_name`: Provider's name
- `service_name`: Service name
- `date`: Booking date
- `time`: Booking time
- `price`: Final price

### When `data.requests` is present (Provider role)
The agent is showing matching leads:
- `request_id`: Request UUID
- `service_type`: Type of service needed
- `location`: Location object with `city`
- `budget`: Budget object with `min` and `max`
- `raw_input`: Consumer's original description

## Agent Tools

The Gemini agent has access to the following tools:

| Tool | Description |
|------|-------------|
| `create_service_request` | Create a service request and trigger provider matching |
| `get_offers` | Retrieve offers for a specific request |
| `accept_offer` | Accept an offer to create a booking |
| `get_matching_requests` | Get leads matching a provider's profile |
| `submit_offer` | Submit a price and availability offer |

## Conversation Flow

### Consumer Example
```
User: "I need a haircut"
Agent: "I can help with that! Where are you located?"
[No data]

User: "Brooklyn, around $60-80"
Agent: "Found great options in Brooklyn!"
[data.offers contains provider list]

User: "Book Maya"
Agent: "Done! Your appointment is confirmed."
[data.booking contains confirmation]
```

### Provider Example
```
User: "Show me new leads"
Agent: "Here are matching requests in your area:"
[data.requests contains lead list]

User: "I want to make an offer on the first one"
Agent: "What price and availability would you like to offer?"
[No data, awaiting input]

User: "$70, Saturday at 2pm"
Agent: "Offer submitted successfully!"
[No data]
```

## Error Handling

If the agent encounters an issue, it will respond with a friendly error message:

```json
{
  "session_id": "...",
  "message": "I'm sorry, I'm having trouble processing that right now. Could you try again?",
  "data": null
}
```

## Mock Mode

When `GOOGLE_API_KEY` is not configured, the API uses mock responses for development and testing. Mock responses simulate the full conversation flow without making actual AI calls.

