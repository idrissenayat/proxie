# Proxie Troubleshooting Guide

Common issues and their solutions for development and production.

## Table of Contents

- [Development Issues](#development-issues)
- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [LLM/AI Issues](#llmai-issues)
- [Redis/Caching Issues](#rediscaching-issues)
- [Frontend Issues](#frontend-issues)
- [WebSocket Issues](#websocket-issues)
- [Deployment Issues](#deployment-issues)

---

## Development Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Set PYTHONPATH to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root directory
cd /path/to/proxie
python -m src.platform.main
```

### Tests Failing After Auth Changes

**Problem:** Tests return 401 Unauthorized after modifying authentication.

**Solution:**
Ensure test fixtures include auth bypass headers:

```python
@pytest.fixture
def authed_client():
    client = TestClient(app)
    client.headers.update({
        "X-Load-Test-Secret": settings.LOAD_TEST_SECRET,
        "X-Test-User-Id": "test-user-id",
        "X-Test-User-Role": "consumer"
    })
    return client
```

### Virtual Environment Issues

**Problem:** Wrong Python version or packages not found.

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Database Issues

### Connection Refused

**Problem:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Start PostgreSQL
docker-compose up -d postgres

# Verify connection
psql -h localhost -U postgres -d proxie -c "SELECT 1"
```

### Migration Errors

**Problem:** `alembic.util.exc.CommandError: Target database is not up to date`

**Solution:**
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Force to specific revision (use with caution)
alembic stamp head

# Then upgrade
alembic upgrade head
```

### Duplicate Key Error

**Problem:** `IntegrityError: duplicate key value violates unique constraint`

**Solution:**
```bash
# Reset sequences (development only)
python -c "
from src.platform.database import SessionLocal, engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('SELECT setval(pg_get_serial_sequence(\"providers\", \"id\"), COALESCE(MAX(id), 1)) FROM providers'))
    conn.commit()
"
```

---

## Authentication Issues

### Invalid Token Error

**Problem:** `401 Unauthorized: Invalid or expired token`

**Possible Causes:**
1. Token expired
2. Wrong Clerk secret key
3. Token from different Clerk instance

**Solution:**
```bash
# Verify Clerk configuration
echo $CLERK_SECRET_KEY

# Check token manually
python -c "
from src.platform.auth import verify_token
try:
    result = verify_token('your-token-here')
    print(result)
except Exception as e:
    print(f'Error: {e}')
"
```

### Role Mismatch

**Problem:** `403 Forbidden: Resource requires 'provider' role`

**Solution:**
1. Check user's role in Clerk dashboard
2. Verify role is set in `public_metadata.role`
3. Or check database has Provider/Consumer record for the user

---

## LLM/AI Issues

### LLM Timeout

**Problem:** Chat requests taking too long or timing out.

**Solution:**
```python
# Increase timeout in config
LLM_TIMEOUT = 60  # seconds

# Or use async processing
FEATURE_ASYNC_CHAT_ENABLED = True
```

### Budget Exceeded

**Problem:** `Exception: LLM usage limit exceeded for this session/day`

**Solution:**
```bash
# Check current usage
python -c "
from src.platform.database import SessionLocal
from src.platform.services.usage import LLMUsageService
with SessionLocal() as db:
    service = LLMUsageService(db)
    print(service.get_user_daily_usage('user-id'))
"

# Reset limits (development only)
# Increase limits in config:
LLM_DAILY_LIMIT_PER_USER = 5.00  # $5 per day
LLM_SESSION_LIMIT = 1.00  # $1 per session
```

### Mock Mode Not Working

**Problem:** LLM requests failing instead of using mock responses.

**Solution:**
```bash
# Ensure environment is set correctly
export ENVIRONMENT=testing
export GOOGLE_API_KEY=  # Empty to enable mock mode

# Verify mock mode is active
python -c "
from src.platform.config import settings
print(f'Environment: {settings.ENVIRONMENT}')
print(f'API Key set: {bool(settings.GOOGLE_API_KEY)}')
"
```

---

## Redis/Caching Issues

### Connection Refused

**Problem:** `redis.exceptions.ConnectionError: Error connecting to localhost:6379`

**Solution:**
```bash
# Start Redis
docker-compose up -d redis

# Verify connection
redis-cli ping  # Should return PONG

# Check Redis URL
echo $REDIS_URL
```

### Cache Not Working

**Problem:** LLM responses not being cached.

**Solution:**
```python
# Verify cache is enabled
from src.platform.config import settings
print(f"Cache enabled: {settings.LLM_CACHE_ENABLED}")
print(f"Cache TTL: {settings.LLM_CACHE_TTL}")

# Check Redis connectivity
from src.platform.services.llm_gateway import llm_gateway
print(f"Redis client: {llm_gateway.redis_client}")
print(f"Cache enabled: {llm_gateway.cache_enabled}")
```

### Stale Cache Data

**Problem:** Old data being returned from cache.

**Solution:**
```bash
# Clear all LLM cache
redis-cli KEYS "llm_cache:*" | xargs redis-cli DEL

# Or in Python
from src.platform.services.llm_gateway import llm_gateway
llm_gateway.invalidate_cache()
```

---

## Frontend Issues

### Hydration Errors

**Problem:** `Error: Hydration failed because the initial UI does not match`

**Solution:**
1. Check for browser-only code in server components
2. Wrap browser-specific code with `useEffect`
3. Use `suppressHydrationWarning` for known mismatches (dates, etc.)

### Build Failures

**Problem:** `npm run build` fails with type errors.

**Solution:**
```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Run build with verbose output
npm run build -- --debug
```

### Environment Variables Not Loading

**Problem:** `NEXT_PUBLIC_*` variables are undefined.

**Solution:**
1. Ensure variables are prefixed with `NEXT_PUBLIC_`
2. Restart the development server after changing `.env.local`
3. Check variables are in `.env.local` not just `.env`

---

## WebSocket Issues

### Connection Failing

**Problem:** WebSocket connections not establishing.

**Solution:**
```bash
# Check Socket.IO is configured
grep -r "socket" src/platform/main.py

# Verify CORS settings
echo $CORS_ORIGINS

# Test WebSocket endpoint
wscat -c ws://localhost:8000/socket.io/?EIO=4&transport=websocket
```

### Messages Not Received

**Problem:** WebSocket connected but messages not arriving.

**Solution:**
1. Check room/session joining
2. Verify event names match between client and server
3. Check browser console for errors

---

## Deployment Issues

### Container Not Starting

**Problem:** Docker container exits immediately.

**Solution:**
```bash
# Check container logs
docker logs <container-id>

# Run container interactively for debugging
docker run -it <image> /bin/bash

# Check Dockerfile CMD/ENTRYPOINT
```

### Health Check Failing

**Problem:** Kubernetes pod stuck in CrashLoopBackOff.

**Solution:**
```bash
# Check pod logs
kubectl logs <pod-name>

# Check health endpoint
kubectl exec <pod-name> -- curl localhost:8000/health

# Check environment variables
kubectl exec <pod-name> -- env | grep -E "DATABASE|REDIS"
```

### Memory Issues

**Problem:** OOMKilled or high memory usage.

**Solution:**
1. Increase container memory limits
2. Check for memory leaks in long-running tasks
3. Optimize database queries
4. Enable connection pooling

---

## Getting More Help

1. **Check Logs:** Use `structlog` output for detailed context
2. **Enable Debug Mode:** Set `DEBUG=true` in environment
3. **Sentry:** Check error tracking dashboard
4. **Metrics:** Review Prometheus/Grafana dashboards

### Log Locations

- **API Logs:** stdout/stderr (Docker) or console (local)
- **Celery Logs:** Worker stdout or configured log file
- **Frontend Logs:** Browser console + Next.js server logs

### Useful Debug Commands

```bash
# API debug mode
DEBUG=true uvicorn src.platform.main:app --reload

# Celery with verbose logging
celery -A src.platform.worker worker --loglevel=debug

# Frontend with debug
DEBUG=* npm run dev
```
