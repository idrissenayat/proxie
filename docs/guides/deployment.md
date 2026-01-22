# Deployment Guide

## Prerequisites

- Docker
- A PostgreSQL database (or use managed service)
- Anthropic API key

## Environment Variables

Set these in your deployment environment:

```
ENVIRONMENT=production
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<generate-secure-key>
```

## Docker Deployment

```bash
# Build image
docker build -t proxie .

# Run
docker run -p 8000:8000 --env-file .env proxie
```

## Platform-Specific

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy

### Render

1. Create new Web Service
2. Connect repository
3. Set environment variables
4. Deploy

## Database Migrations

Run migrations before starting:

```bash
python scripts/migrate.py
```
