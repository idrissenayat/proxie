# Local Development Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Docker)
- An Anthropic API key

## Quick Start with Docker

```bash
# Start PostgreSQL
docker-compose up -d db

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Anthropic API key

# Run migrations
python scripts/migrate.py

# Seed sample data (optional)
python scripts/seed_data.py

# Start the server
python -m src.platform.main
```

## Without Docker

1. Install PostgreSQL locally
2. Create database: `createdb proxie_db`
3. Update DATABASE_URL in .env
4. Follow remaining steps above

## Running Tests

```bash
pytest tests/
```

## Code Quality

```bash
# Format
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```
