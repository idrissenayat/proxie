# Cursor Rules for Proxie

## Project Context

Proxie is an agent-native platform connecting service providers with consumers.
Read `/docs/project/overview.md` for full context.

## When Writing Code

1. Check `/docs/schemas/` for data structure definitions
2. Follow patterns in existing code
3. Add type hints to all functions
4. Write tests for new functionality

## Key Files

- Entry point: `src/platform/main.py`
- Config: `src/platform/config.py`
- Models: `src/platform/models/`

## Style

- Black formatting (100 char lines)
- isort for imports
- Ruff for linting
