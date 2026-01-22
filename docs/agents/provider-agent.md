# Provider Agent Specification

## Overview

The Provider Agent represents a service provider by:
1. Receiving relevant service requests
2. Evaluating if they match provider's profile
3. Generating offers based on provider's rules
4. Confirming bookings

## Capabilities

### 1. Evaluate Requests

Check if request matches:
- Service category
- Specializations
- Location/service area
- Available dates/times
- Price range

### 2. Generate Offers

Based on provider's configuration:
- Check calendar for availability
- Calculate price based on service and rules
- Select relevant portfolio samples
- Compose personalized message

### 3. Follow Provider Rules

Respect provider settings:
- Auto-accept threshold
- Minimum notice time
- Maximum bookings per day
- Price ranges

### 4. Manage Bookings

- Confirm accepted offers
- Update provider's calendar
- Notify provider of new bookings

## Rules Engine

```python
def should_make_offer(request, provider):
    # Check service match
    if request.service_category not in provider.categories:
        return False
    
    # Check location
    if not is_in_service_area(request.location, provider.location):
        return False
    
    # Check availability
    if not has_available_slot(request.timing, provider.availability):
        return False
    
    # Check price fit
    if request.budget.max < provider.price_min:
        return False
    
    return True
```

## Prompts

See `src/agents/provider/prompts.py` for LLM prompts.
