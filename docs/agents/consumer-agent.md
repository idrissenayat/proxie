# Consumer Agent Specification

## Overview

The Consumer Agent helps users find and book service providers by:
1. Understanding their natural language requests
2. Creating structured service requests
3. Presenting matched offers
4. Facilitating booking

## Capabilities

### 1. Parse Natural Language

**Input:** "I need a haircut for curly hair in Brooklyn this weekend"

**Output:**
```json
{
  "service_category": "hairstylist",
  "service_type": "haircut",
  "requirements": {"specializations": ["curly hair"]},
  "location": {"city": "Brooklyn"},
  "timing": {"preferred_dates": ["2026-01-24", "2026-01-25"]}
}
```

### 2. Ask Clarifying Questions

When information is missing or ambiguous:
- "What area of Brooklyn are you in?"
- "Do you have a budget in mind?"
- "Any time preferences - morning or afternoon?"

### 3. Present Offers

Format offers for easy comparison:
- Provider name and rating
- Availability that matches request
- Price
- Relevant portfolio samples
- Key differentiators

### 4. Handle Booking

- Confirm selection with user
- Submit acceptance to platform
- Share booking confirmation details

## Decision Logic

```
1. Receive user input
2. Parse intent and entities
3. If missing critical info → ask clarifying question
4. If complete → create service request
5. Wait for offers
6. Present offers to user
7. If user selects → accept offer
8. Confirm booking
```

## Prompts

See `src/agents/consumer/prompts.py` for LLM prompts.
