# Proxie Deployment Guide

## Current Status: MVP / Development

The system is currently running in development mode. This guide covers both local development and future production deployment.

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ (Next.js 14 requirement)
- PostgreSQL 16+
- Redis 7+
- Google Cloud account (for Gemini API & GKE)
- Clerk account (for Auth)
- Sentry account (for Monitoring)

### Backend Setup

```bash
# 1. Clone repository
cd /Users/idrissenayat/Project\ Proxie

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL
# - GEMINI_API_KEY
# - CORS_ORIGINS

# 5. Initialize database
python scripts/migrate.py

# 6. (Optional) Seed test data
python scripts/seed_data.py

# 7. Run server
python src/platform/main.py
# Server runs on http://localhost:8000
```

### Frontend Setup (Next.js 14)

```bash
# 1. Navigate to web-next directory
cd web-next

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# 4. Run development server
npm run dev
# Frontend runs on http://localhost:3000
```

---

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/proxie

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication (Clerk)
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...

# AI Gateway (LiteLLM)
GOOGLE_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key

# Monitoring
SENTRY_DSN=https://...
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Server
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
```

---

## Database Setup

### PostgreSQL Installation (macOS)
```bash
# Install via Homebrew
brew install postgresql@14

# Start service
brew services start postgresql@14

# Create database
createdb proxie

# Create user (optional)
psql postgres
CREATE USER proxie_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE proxie TO proxie_user;
```

### Run Migrations
```bash
source venv/bin/activate
python scripts/migrate.py
```

### Database Schema
The migration script creates:
- `providers` - Provider profiles
- `provider_enrollments` - Enrollment tracking
- `provider_lead_views` - Lead analytics
- `service_requests` - Consumer requests
- `offers` - Provider offers
- `bookings` - Confirmed bookings
- `reviews` - Post-service reviews

---

### Production Deployment (Target Architecture 2.0)

- **Compute**: Google Kubernetes Engine (GKE) Autopilot
- **Database**: Cloud SQL for PostgreSQL 16
- **Caching/Sessions**: Google Cloud Memorystore (Redis)
- **API Gateway**: Kong Gateway (HELM chart on GKE)
- **Storage**: Cloudflare R2 (S3 compatible)
- **Auth**: Clerk (External Managed)

### Docker Setup (Architecture 2.0)

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "src.platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile (Next.js)
```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

### Docker Compose (Local Testing)
```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=proxie
      - POSTGRES_PASSWORD=password

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/proxie
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Cloud Run Deployment

```bash
# 1. Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/proxie-backend

# 2. Deploy to Cloud Run
gcloud run deploy proxie-backend \
  --image gcr.io/PROJECT_ID/proxie-backend \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL,GEMINI_API_KEY=$GEMINI_API_KEY

# 3. Get service URL
gcloud run services describe proxie-backend --region us-east1 --format 'value(status.url)'
```

---

## Security Checklist

### Before Production
- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Add authentication/authorization
- [ ] Implement API key rotation
- [ ] Set up monitoring and alerts
- [ ] Enable database backups
- [ ] Add input validation
- [ ] Implement CSRF protection
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable audit logging

### Current Security Features
- ✅ CORS configured
- ✅ Security headers (X-Frame-Options, etc.)
- ✅ Input validation via Pydantic
- ⚠️ No authentication (MVP only)
- ⚠️ No rate limiting (MVP only)

---

## Monitoring & Logging

### Development
```bash
# Backend logs
tail -f logs/proxie.log

# Frontend logs
# Check browser DevTools → Console
```

### Production (Future)
- Google Cloud Logging for backend
- Sentry for error tracking
- Google Analytics for frontend
- Custom dashboards for business metrics

---

## Backup & Recovery

### Database Backup
```bash
# Manual backup
pg_dump proxie > backup_$(date +%Y%m%d).sql

# Restore
psql proxie < backup_20260126.sql
```

### Automated Backups (Production)
- Cloud SQL automatic backups (daily)
- Point-in-time recovery enabled
- Backup retention: 30 days

---

## Performance Optimization

### Backend
- [ ] Add Redis for caching
- [ ] Implement connection pooling
- [ ] Add database indexes
- [ ] Enable query optimization
- [ ] Implement CDN for static assets

### Frontend
- [ ] Code splitting
- [ ] Lazy loading
- [ ] Image optimization
- [ ] Service worker for offline support

---

## Scaling Strategy

### Current Capacity
- Single server
- ~100 concurrent users
- ~1000 requests/day

### Scale to 10K Users
1. **Database**: Cloud SQL with read replicas
2. **Backend**: Multiple Cloud Run instances (auto-scaling)
3. **Frontend**: CDN (Cloudflare/Fastly)
4. **Caching**: Redis for sessions and catalog
5. **Queue**: Cloud Tasks for async jobs

---

## Cost Estimates (Production)

### Monthly Costs (1000 active users)
| Service | Cost |
|---------|------|
| Cloud Run (Backend) | $20-50 |
| Cloud SQL (PostgreSQL) | $50-100 |
| Cloud Storage | $5-10 |
| Gemini API | $100-300 |
| Vercel (Frontend) | $0-20 |
| **Total** | **$175-480/mo** |

### At Scale (10K users)
- Cloud Run: $200-400
- Cloud SQL: $200-400
- Gemini API: $1000-2000
- **Total**: ~$1500-3000/mo

---

## Maintenance Tasks

### Daily
- Monitor error logs
- Check API response times
- Review Gemini API usage

### Weekly
- Database backup verification
- Security updates
- Performance review

### Monthly
- Cost analysis
- User feedback review
- Feature prioritization

---

## Rollback Procedure

### Backend
```bash
# Revert to previous Cloud Run revision
gcloud run services update-traffic proxie-backend \
  --to-revisions PREVIOUS_REVISION=100

# Or rollback database
psql proxie < backup_latest.sql
```

### Frontend
```bash
# Vercel: Use dashboard to rollback deployment
# Or redeploy previous commit
git checkout PREVIOUS_COMMIT
npm run build
vercel --prod
```

---

## Support & Troubleshooting

### Common Issues

**Database connection failed**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Restart if needed
brew services restart postgresql@14
```

**Gemini API quota exceeded**
- Check usage in Google Cloud Console
- Upgrade quota or implement caching

**Frontend can't reach backend**
- Verify CORS_ORIGINS in .env
- Check backend is running on correct port
- Verify VITE_API_URL in frontend

---

## Next Steps

1. ✅ Local development working
2. ⏭️ Set up staging environment
3. ⏭️ Implement authentication
4. ⏭️ Add monitoring
5. ⏭️ Production deployment
6. ⏭️ Load testing
7. ⏭️ Launch pilot program
