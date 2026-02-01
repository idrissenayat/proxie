# Proxie Platform: Quick Reference Guide

Quick reference for key features, commands, and workflows implemented in this project.

---

## 🔐 Security

### Authentication
- **Method:** JWT via Clerk
- **Header:** `Authorization: Bearer <token>`
- **Public Endpoints:** `/requests/`, `/providers/`, `/health`
- **Protected Endpoints:** Most endpoints require authentication

### Roles
- **consumer** - Service requesters
- **provider** - Service providers  
- **admin** - Platform administrators

### Ownership
- Users can only modify their own resources
- Admin users can modify any resource
- Validated via `require_ownership()` dependency

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific category
pytest tests/test_auth.py -v
pytest tests/test_services/ -v
pytest tests/test_integration/ -v

# With coverage
pytest tests/ --cov=src/platform --cov-report=html
```

### Test Coverage
- **Security:** 48+ tests
- **Unit:** 29 tests
- **Integration:** 12 tests
- **Error:** 30+ tests
- **Total:** 119+ tests

---

## ⚡ Performance

### Async Chat Processing
```bash
# Enable async mode
POST /chat/?async_mode=true

# Poll for result
GET /chat/task/{task_id}
```

### Caching
- **LLM Cache:** Enabled by default (50%+ hit rate)
- **API Cache:** Available via `@cached` decorator
- **TTL:** Configurable per endpoint

### Database Optimization
- **Indexes:** 30+ indexes added
- **Batch Loading:** Use `query_utils` helpers
- **Migration:** `alembic upgrade head`

---

## 📚 Code Quality

### Using Utilities

**Database Helpers:**
```python
from src.platform.utils.db_helpers import get_or_404

provider = get_or_404(db, Provider, provider_id, "Provider")
```

**Exception Helpers:**
```python
from src.platform.utils.exceptions import raise_not_found

raise raise_not_found("Provider", provider_id)
```

**Response Helpers:**
```python
from src.platform.utils.responses import success_response

return success_response(data={...}, message="Created")
```

---

## 🗄️ Database Migrations

### Common Commands
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Check status
alembic current
alembic history
```

### Apply Indexes
```bash
# Via Alembic
alembic upgrade head

# Or direct SQL
psql -d proxie_db -f migrations/add_indexes.sql
```

---

## 🚨 Error Handling

### Frontend Error Boundaries
```jsx
import ErrorBoundary from '@/components/ErrorBoundary';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

### Error Hooks
```jsx
import { useErrorHandler } from '@/hooks/useErrorHandler';

const { error, handleAPIError, clearError } = useErrorHandler();
```

### Error Display
```jsx
import { ErrorDisplay } from '@/components/ErrorDisplay';

{error && <ErrorDisplay error={error} onDismiss={clearError} />}
```

---

## 📖 API Documentation

### Access Points
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Key Endpoints

**Chat:**
- `POST /chat/` - Send message (sync or async)
- `GET /chat/task/{task_id}` - Poll async task status

**Requests:**
- `POST /requests/` - Create request (requires consumer role)
- `GET /requests/` - List requests
- `GET /requests/{id}` - Get request details

**Providers:**
- `GET /providers/` - List providers
- `GET /providers/{id}/profile` - Get provider profile
- `PATCH /providers/{id}/profile` - Update profile (requires ownership)

**Offers:**
- `POST /offers/` - Create offer (requires provider role)
- `PUT /offers/{id}/accept` - Accept offer (requires consumer role)

---

## 🔧 Configuration

### Environment Variables

**Database:**
```bash
DATABASE_URL=postgresql://user:pass@localhost/proxie_db
```

**Redis:**
```bash
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_DB=1
```

**Rate Limiting:**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_CHAT_PER_MINUTE=30
```

**Features:**
```bash
FEATURE_ASYNC_CHAT_ENABLED=false  # Enable async chat
FEATURE_LLM_CACHING_ENABLED=true
```

---

## 🚀 Deployment

### Pre-Deployment Checklist
- [ ] Run test suite: `pytest tests/ -v`
- [ ] Apply migrations: `alembic upgrade head`
- [ ] Check database indexes
- [ ] Verify environment variables
- [ ] Test rate limiting
- [ ] Verify error boundaries

### Deployment Steps
1. **Database:** Apply migrations
2. **Backend:** Deploy FastAPI app
3. **Frontend:** Deploy Next.js app
4. **Workers:** Start Celery workers
5. **Redis:** Ensure Redis is running
6. **Monitoring:** Verify health endpoints

---

## 📊 Monitoring

### Health Checks
- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe (checks DB + Redis)
- `GET /metrics` - Prometheus metrics

### Rate Limit Headers
All responses include:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## 🐛 Troubleshooting

### Common Issues

**Database Connection:**
```bash
# Check connection
python -c "from src.platform.database import check_db_connection; print(check_db_connection())"
```

**Redis Connection:**
```bash
# Check Redis
redis-cli ping
```

**Migrations:**
```bash
# Check current state
alembic current

# View history
alembic history

# Resolve conflicts
alembic stamp head
```

**Rate Limiting:**
- Check Redis connection
- Verify `RATE_LIMIT_ENABLED=true`
- Check rate limit headers in responses

---

## 📚 Documentation Files

- `TASK_*.md` - Individual task completions
- `PHASE_*.md` - Phase summaries
- `REFACTORING_GUIDE.md` - Code refactoring guide
- `ALEMBIC_USAGE.md` - Migration guide
- `PROJECT_COMPLETE.md` - Final summary
- `FINAL_PROJECT_SUMMARY.md` - Executive summary

---

## 🎯 Key Features

### Security
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Resource ownership validation
- ✅ WebSocket authentication
- ✅ Per-user rate limiting

### Performance
- ✅ Async LLM processing
- ✅ Request/response caching
- ✅ Database query optimization
- ✅ Rate limiting

### Quality
- ✅ Comprehensive testing
- ✅ Code refactoring
- ✅ Complete documentation
- ✅ Error handling

---

**For detailed information, see individual task completion documents.**
