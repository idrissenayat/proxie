# Proxie Development Patterns

## Overview

This skill defines coding patterns and conventions for the Proxie project.

## Architecture

Proxie follows a layered architecture:

1. **API Layer** (`src/platform/routers/`) - FastAPI route handlers
2. **Service Layer** (`src/platform/services/`) - Business logic
3. **Model Layer** (`src/platform/models/`) - SQLAlchemy models
4. **Schema Layer** (`src/platform/schemas/`) - Pydantic validation

## Conventions

### File Naming
- Models: singular (`provider.py`, `booking.py`)
- Routers: plural (`providers.py`, `bookings.py`)
- Use snake_case for all Python files

### Code Style
- Line length: 100 characters
- Use type hints everywhere
- Document all public functions

### Database
- Use UUID for all primary keys
- Include `created_at` and `updated_at` on all models
- Store complex data as JSON when schema may evolve

### API Design
- RESTful endpoints
- Use Pydantic for request/response validation
- Return consistent error formats

## Agent Development

### Consumer Agent
- Parse natural language to structured requests
- Ask clarifying questions when ambiguous
- Present offers in a clear, comparable format

### Provider Agent
- Follow provider's rules strictly
- Never overcommit availability
- Keep provider informed of all bookings

## Testing

- Write tests for all business logic
- Use fixtures for common test data
- Mock external services (LLM, storage)
