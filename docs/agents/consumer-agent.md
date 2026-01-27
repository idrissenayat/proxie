# Consumer Agent Specification

## Overview

The Consumer Agent helps users find and book service providers by:
1. Understanding their natural language requests
2. **Analyzing visual media (photos/videos) shared by the user**
3. **Drafting structured service requests (with Specialist validation)**
4. Presenting matched offers
5. Facilitating booking

## Capabilities

### 1. Parse Natural Language & Vision

The agent processes both text and visual media to extract structured data:
- **Input:** "I need a haircut for curly hair in Brooklyn" + [Photo]
- **Output:** Structured request with specialist-enriched metadata.

### 2. Multi-Modal Analysis

Processes image and video attachments to:
- Identify hair type, length, and texture (Hair Specialist).
- Verify service complexity (e.g., plumbing damage level).
- Extract style preferences from reference photos from conversation history.

### 3. Specialist Consultation

When a domain is identified, the agent consults a Specialist:
- **Input:** User's raw text + AI vision descriptions.
- **Action:** Specialist validates data, fills in missing technical details, and provides "specialist notes" for the request.
- **Output:** Enriched service request metadata.

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
