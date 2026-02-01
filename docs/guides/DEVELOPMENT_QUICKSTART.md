# Proxie Development Quick Start Guide

Get your local development environment running in under 10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

## 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd proxie

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web-next && npm install && cd ..
```

## 2. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Required variables to set:
# - DATABASE_URL: PostgreSQL connection string
# - REDIS_URL: Redis connection string
# - CLERK_SECRET_KEY: Your Clerk secret key
# - GOOGLE_API_KEY: Gemini API key (or leave blank for mock mode)
```

**Minimum .env for local development:**

```env
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/proxie
REDIS_URL=redis://localhost:6379/0
CLERK_SECRET_KEY=sk_test_your_key
GOOGLE_API_KEY=  # Leave empty for mock LLM mode
```

## 3. Start Infrastructure

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d

# Verify services are running
docker-compose ps
```

## 4. Database Setup

```bash
# Run database migrations
alembic upgrade head

# (Optional) Seed with test data
python scripts/seed_data.py
```

## 5. Run the Application

**Terminal 1 - Backend API:**

```bash
source venv/bin/activate
uvicorn src.platform.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker (for async tasks):**

```bash
source venv/bin/activate
celery -A src.platform.worker worker --loglevel=info
```

**Terminal 3 - Frontend:**

```bash
cd web-next
npm run dev
```

## 6. Verify Everything Works

- **API Docs:** http://localhost:8000/api/docs
- **Frontend:** http://localhost:3000
- **Health Check:** `curl http://localhost:8000/health`

## Quick Commands Reference

| Task | Command |
|------|---------|
| Run tests | `pytest tests/ -v` |
| Run with coverage | `pytest tests/ --cov=src --cov-report=html` |
| Lint code | `ruff check src/ tests/` |
| Format code | `black src/ tests/` |
| Type check | `mypy src/` |
| Create migration | `alembic revision --autogenerate -m "description"` |
| Apply migrations | `alembic upgrade head` |
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| View logs | `docker-compose logs -f` |

## Project Structure

```
proxie/
├── src/
│   ├── platform/          # Backend application
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── utils/         # Utilities
│   ├── agents/            # Agent implementations
│   └── mcp/               # MCP protocol handlers
├── web-next/              # Next.js frontend
├── tests/                 # Test suite
├── alembic/               # Database migrations
└── docs/                  # Documentation
```

## Common Development Tasks

### Adding a New API Endpoint

1. Create/update router in `src/platform/routers/`
2. Add business logic in `src/platform/services/`
3. Define schemas in `src/platform/schemas/`
4. Add tests in `tests/`

### Adding a New Database Model

1. Create model in `src/platform/models/`
2. Create migration: `alembic revision --autogenerate -m "add model"`
3. Apply: `alembic upgrade head`

### Running in Mock LLM Mode

Leave `GOOGLE_API_KEY` empty in `.env` to use mock LLM responses. This is useful for:
- Development without API costs
- Running tests
- Offline development

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

- Read the [Architecture Guide](../project/proxie-agent-architecture-v2.md)
- Review [API Documentation](../api/)
- Explore [Testing Guide](../testing/)
