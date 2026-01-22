# Proxie Project Rules

## Code Standards

- Python 3.11+ required
- Use type hints for all function signatures
- Format with Black (line length 100)
- Sort imports with isort
- Lint with Ruff

## Documentation

- All schemas are documented in `/docs/schemas/`
- Read the schema docs before implementing models
- Keep docs in sync with code

## Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user input with Pydantic

## Git

- Write clear commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic
