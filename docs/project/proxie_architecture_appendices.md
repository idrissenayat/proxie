# Proxie Technical Appendices

**Companion to:** Proxie Platform Technical Architecture Specification  
**Version:** 2.0  
**Date:** January 27, 2026

---

## Appendix A: Complete Database Schema

```sql
-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('consumer', 'provider', 'admin'))
);

CREATE TABLE consumers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    default_location GEOGRAPHY(POINT, 4326),
    preferences JSONB DEFAULT '{}'::jsonb
);

-- ============================================
-- PROVIDERS
-- ============================================

CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    business_name VARCHAR(255),
    bio TEXT,
    profile_photo_url VARCHAR(500),
    years_experience INTEGER,
    
    -- Location
    location GEOGRAPHY(POINT, 4326),
    service_radius_km INTEGER DEFAULT 10,
    address VARCHAR(500),
    city VARCHAR(100),
    
    -- Stats (denormalized)
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    jobs_completed INTEGER DEFAULT 0,
    response_rate DECIMAL(3,2) DEFAULT 0.00,
    average_response_time_hours DECIMAL(5,2),
    
    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    
    -- Embeddings
    embedding VECTOR(1536),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE provider_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    service_type VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2),
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE provider_portfolio_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    photo_url VARCHAR(500) NOT NULL,
    caption TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE provider_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'pending_verification', 'verified', 'rejected')),
    data JSONB DEFAULT '{}'::jsonb,
    verified_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SERVICE REQUESTS
-- ============================================

CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID NOT NULL REFERENCES consumers(id),
    
    service_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    raw_input TEXT,
    
    -- Location
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    city VARCHAR(100),
    
    -- Budget
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    
    -- Timing
    timing_flexibility VARCHAR(20) 
        CHECK (timing_flexibility IN ('asap', 'this_week', 'this_month', 'specific_date')),
    preferred_date DATE,
    preferred_time_start TIME,
    preferred_time_end TIME,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'matching' 
        CHECK (status IN ('matching', 'pending', 'booked', 'completed', 'cancelled')),
    status_history JSONB DEFAULT '[]'::jsonb,
    
    -- Analysis
    specialist_analysis JSONB DEFAULT '{}'::jsonb,
    
    -- Counts
    offer_count INTEGER DEFAULT 0,
    
    -- Embeddings
    embedding VECTOR(1536),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE request_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    media_type VARCHAR(20) NOT NULL CHECK (media_type IN ('image', 'video')),
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    analysis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- OFFERS & BOOKINGS
-- ============================================

CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES service_requests(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    
    price DECIMAL(10,2) NOT NULL,
    message TEXT,
    
    available_date DATE NOT NULL,
    available_time_start TIME NOT NULL,
    available_time_end TIME NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'declined', 'withdrawn', 'expired')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    UNIQUE(request_id, provider_id)
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id UUID UNIQUE NOT NULL REFERENCES offers(id),
    request_id UUID NOT NULL REFERENCES service_requests(id),
    consumer_id UUID NOT NULL REFERENCES consumers(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    
    scheduled_date DATE NOT NULL,
    scheduled_time_start TIME NOT NULL,
    scheduled_time_end TIME NOT NULL,
    
    location GEOGRAPHY(POINT, 4326),
    address VARCHAR(500),
    
    agreed_price DECIMAL(10,2) NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    checked_in_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancel_reason TEXT
);

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID UNIQUE NOT NULL REFERENCES bookings(id),
    consumer_id UUID NOT NULL REFERENCES consumers(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    
    response TEXT,
    responded_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TRACKING & NOTIFICATIONS
-- ============================================

CREATE TABLE provider_lead_views (
    provider_id UUID NOT NULL REFERENCES providers(id),
    request_id UUID NOT NULL REFERENCES service_requests(id),
    viewed_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (provider_id, request_id)
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    data JSONB DEFAULT '{}'::jsonb,
    channels VARCHAR(20)[] DEFAULT '{}',
    priority VARCHAR(10) DEFAULT 'normal',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ
);

CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    messages JSONB NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_providers_user_id ON providers(user_id);
CREATE INDEX idx_providers_location ON providers USING GIST(location);
CREATE INDEX idx_providers_is_active ON providers(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_providers_embedding ON providers USING ivfflat(embedding vector_cosine_ops);

CREATE INDEX idx_provider_services_provider ON provider_services(provider_id);
CREATE INDEX idx_provider_services_type ON provider_services(service_type);

CREATE INDEX idx_requests_consumer ON service_requests(consumer_id);
CREATE INDEX idx_requests_status ON service_requests(status);
CREATE INDEX idx_requests_location ON service_requests USING GIST(location);
CREATE INDEX idx_requests_created ON service_requests(created_at DESC);

CREATE INDEX idx_offers_request ON offers(request_id);
CREATE INDEX idx_offers_provider ON offers(provider_id);
CREATE INDEX idx_offers_status ON offers(status);

CREATE INDEX idx_bookings_consumer ON bookings(consumer_id);
CREATE INDEX idx_bookings_provider ON bookings(provider_id);
CREATE INDEX idx_bookings_scheduled ON bookings(scheduled_date, scheduled_time_start);

CREATE INDEX idx_reviews_provider ON reviews(provider_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
```

---

## Appendix B: API Endpoint Specifications

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | None |
| POST | `/auth/login` | Login user | None |
| POST | `/auth/logout` | Logout user | Required |
| POST | `/auth/refresh` | Refresh access token | Refresh |
| GET | `/auth/me` | Get current user | Required |

### Chat

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/chat` | Send message to agent | Required |
| GET | `/chat/sessions` | List user's sessions | Required |
| GET | `/chat/sessions/{id}` | Get session history | Required |
| DELETE | `/chat/sessions/{id}` | Delete session | Required |
| WS | `/chat/ws` | WebSocket connection | Required |

### Requests

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/requests` | Create service request | Consumer |
| GET | `/requests` | List user's requests | Consumer |
| GET | `/requests/{id}` | Get request details | Owner |
| PATCH | `/requests/{id}` | Update request | Owner |
| POST | `/requests/{id}/cancel` | Cancel request | Owner |
| GET | `/requests/{id}/offers` | Get offers | Owner |

### Offers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/offers` | Submit offer | Provider |
| GET | `/offers` | List provider's offers | Provider |
| GET | `/offers/{id}` | Get offer details | Participant |
| POST | `/offers/{id}/accept` | Accept offer | Consumer |
| POST | `/offers/{id}/decline` | Decline offer | Consumer |
| POST | `/offers/{id}/withdraw` | Withdraw offer | Provider |

### Bookings

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/bookings` | List bookings | Required |
| GET | `/bookings/{id}` | Get booking details | Participant |
| POST | `/bookings/{id}/checkin` | Provider check-in | Provider |
| POST | `/bookings/{id}/complete` | Mark complete | Provider |
| POST | `/bookings/{id}/cancel` | Cancel booking | Participant |

### Providers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/providers/{id}` | Get public profile | None |
| GET | `/providers/{id}/profile` | Get full profile | Owner |
| PATCH | `/providers/{id}/profile` | Update profile | Owner |
| GET | `/providers/{id}/portfolio` | Get portfolio | None |
| POST | `/providers/{id}/portfolio` | Add photo | Owner |
| DELETE | `/providers/{id}/portfolio/{photo_id}` | Remove photo | Owner |
| GET | `/providers/{id}/services` | List services | None |
| POST | `/providers/{id}/services` | Add service | Owner |
| GET | `/providers/{id}/reviews` | Get reviews | None |
| GET | `/providers/leads` | Get matching leads | Provider |

### Reviews

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/reviews` | Submit review | Consumer |
| GET | `/reviews/{id}` | Get review | None |
| POST | `/reviews/{id}/respond` | Provider response | Provider |

### MCP (Agent Interface)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/mcp/sse` | SSE connection | Bearer |
| POST | `/mcp/messages` | JSON-RPC messages | Bearer |

---

## Appendix C: System Prompts

### Consumer Agent

```
You are Proxie, an AI concierge that helps people find and book skilled service providers.

## Your Role
- Help consumers describe what service they need
- Collect necessary details (location, budget, timing)
- Show available providers and their offers
- Facilitate booking confirmation
- Handle post-service reviews

## Personality
- Warm, helpful, and professional
- Conversational but efficient
- Never pushy or salesy

## Tools Available
- create_service_request: Create a new service request
- get_offers: Get provider offers for a request
- accept_offer: Book a provider
- get_request_status: Check request status
- cancel_request: Cancel a request
- submit_review: Leave a review

## Guidelines
1. Always confirm details before creating a request
2. Present offers clearly with key details
3. Never make up provider information
4. Respect budget constraints
5. Show draft preview before posting
```

### Provider Agent

```
You are Proxie, an AI assistant helping service providers manage their business.

## Your Role
- Show relevant leads matching provider's skills
- Help providers craft competitive offers
- Provide pricing guidance
- Manage availability and bookings
- Track offer status

## Tools Available
- get_matching_requests: Get new leads
- get_lead_details: View full request details
- suggest_offer: Get AI pricing suggestions
- submit_offer: Send an offer to a consumer
- update_availability: Modify schedule

## Guidelines
1. Prioritize leads that match provider's strengths
2. Analyze consumer media before suggesting prices
3. Consider market rates and experience
4. Help craft personalized messages
5. Be honest about competition
```

### Enrollment Agent

```
You are Proxie, guiding new service providers through enrollment.

## Your Role
- Collect provider information conversationally
- Help select appropriate service categories
- Guide portfolio photo uploads
- Assist with pricing strategy
- Draft professional bio
- Explain verification process

## Enrollment Flow
1. Welcome and explain process (~5 minutes)
2. Collect: Name, business name, contact info
3. Service selection from catalog
4. Pricing and duration for each service
5. Service area (location + radius)
6. Portfolio photos (minimum 3)
7. Professional bio (you help draft)
8. Review and submit

## Tools Available
- get_service_catalog: Show available services
- update_enrollment: Save collected data
- request_portfolio: Trigger photo upload
- submit_enrollment: Finalize enrollment
```

---

## Appendix D: Environment Variables

```bash
# ============================================
# APPLICATION
# ============================================
APP_ENV=production
APP_DEBUG=false
APP_URL=https://api.proxie.app

# ============================================
# DATABASE
# ============================================
DATABASE_URL=postgresql://user:pass@host:5432/proxie
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://:password@host:6379/0
REDIS_SESSION_DB=0
REDIS_CACHE_DB=1
REDIS_QUEUE_DB=2

# ============================================
# LLM PROVIDERS
# ============================================
GOOGLE_API_KEY=your-gemini-api-key
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key

LLM_PRIMARY_PROVIDER=gemini
LLM_PRIMARY_MODEL=gemini-2.5-flash-preview
LLM_FALLBACK_PROVIDER=anthropic
LLM_FALLBACK_MODEL=claude-3-5-sonnet

LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600

# ============================================
# AUTHENTICATION (Clerk)
# ============================================
CLERK_SECRET_KEY=sk_live_xxx
CLERK_PUBLISHABLE_KEY=pk_live_xxx
CLERK_WEBHOOK_SECRET=whsec_xxx

# ============================================
# STORAGE (Cloudflare R2)
# ============================================
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=proxie-media
R2_PUBLIC_URL=https://media.proxie.app

# ============================================
# NOTIFICATIONS
# ============================================
FCM_PROJECT_ID=proxie-prod
FCM_PRIVATE_KEY=your-private-key
FCM_CLIENT_EMAIL=firebase@proxie.iam.gserviceaccount.com

SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=hello@proxie.app

TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# ============================================
# SECURITY
# ============================================
SECRET_KEY=your-256-bit-secret-key
JWT_SECRET=your-jwt-secret
JWT_EXPIRY_HOURS=24
REFRESH_TOKEN_EXPIRY_DAYS=30

CORS_ORIGINS=https://proxie.app,https://www.proxie.app
RATE_LIMIT_PER_MINUTE=60

# ============================================
# OBSERVABILITY
# ============================================
SENTRY_DSN=https://key@sentry.io/project
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=proxie-api

# ============================================
# FEATURE FLAGS
# ============================================
FEATURE_WEBSOCKET_ENABLED=true
FEATURE_PUSH_NOTIFICATIONS_ENABLED=true
FEATURE_LLM_CACHING_ENABLED=true
FEATURE_SPECIALIST_AGENTS_ENABLED=true

# ============================================
# CELERY
# ============================================
CELERY_BROKER_URL=redis://:password@host:6379/2
CELERY_RESULT_BACKEND=redis://:password@host:6379/2
CELERY_TASK_ALWAYS_EAGER=false

# ============================================
# TEMPORAL
# ============================================
TEMPORAL_HOST=temporal:7233
TEMPORAL_NAMESPACE=proxie-prod
TEMPORAL_TASK_QUEUE=proxie-workflows
```

---

## Appendix E: Kubernetes Configurations

### API Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: proxie-api
  namespace: proxie-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: proxie-api
  template:
    metadata:
      labels:
        app: proxie-api
    spec:
      containers:
      - name: api
        image: gcr.io/proxie/api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        envFrom:
        - secretRef:
            name: proxie-secrets
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: proxie-api-hpa
  namespace: proxie-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: proxie-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: proxie-api
  namespace: proxie-prod
spec:
  selector:
    app: proxie-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: proxie-api-ingress
  namespace: proxie-prod
  annotations:
    kubernetes.io/ingress.class: kong
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.proxie.app
    secretName: proxie-api-tls
  rules:
  - host: api.proxie.app
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: proxie-api
            port:
              number: 80
```

---

## Appendix F: CI/CD Pipeline

```yaml
# .github/workflows/deploy.yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      
      - name: Run linting
        run: |
          ruff check .
          mypy src/
      
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GCR
        uses: docker/login-action@v3
        with:
          registry: gcr.io
          username: _json_key
          password: ${{ secrets.GCP_SA_KEY }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: gcr.io/proxie/api:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          gcloud container clusters get-credentials proxie-staging
          kubectl set image deployment/proxie-api api=gcr.io/proxie/api:${{ github.sha }}
          kubectl rollout status deployment/proxie-api

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          gcloud container clusters get-credentials proxie-prod
          kubectl set image deployment/proxie-api api=gcr.io/proxie/api:${{ github.sha }}
          kubectl rollout status deployment/proxie-api
```

---

## Appendix G: Notification Templates

### Email Templates

**Booking Confirmed (Consumer)**
```
Subject: Your booking with {{provider_name}} is confirmed! ✅

Hi {{consumer_name}},

Great news! Your {{service_type}} appointment is confirmed.

📅 {{scheduled_date}} at {{scheduled_time}}
📍 {{address}}
💰 {{agreed_price}}

Your provider: {{provider_name}} ({{provider_rating}}⭐)

Need to make changes? Reply to this email or open the Proxie app.

— The Proxie Team
```

**New Lead (Provider)**
```
Subject: New {{service_type}} lead in {{city}} 🎯

Hi {{provider_name}},

A new lead matches your services!

Service: {{service_type}}
Location: {{city}}
Budget: {{budget_min}} - {{budget_max}}
Timing: {{timing_flexibility}}

Open the Proxie app to view details and submit your offer.

— The Proxie Team
```

### Push Notification Templates

| Type | Title | Body |
|------|-------|------|
| `offer.new` | New offer received! | {{provider_name}} sent you an offer for {{price}} |
| `offer.accepted` | Offer accepted! 🎉 | {{consumer_name}} accepted your offer |
| `booking.reminder` | Reminder: {{service_type}} | Tomorrow at {{time}} with {{provider_name}} |
| `review.requested` | How was your experience? | Rate your {{service_type}} with {{provider_name}} |

---

## Appendix H: Service Catalog (MVP)

```json
{
  "categories": [
    {
      "id": "hair-beauty",
      "name": "Hair & Beauty",
      "icon": "✂️",
      "services": [
        {
          "id": "haircut",
          "name": "Haircut",
          "price_range": {"min": 30, "max": 150},
          "duration_range": {"min": 30, "max": 90},
          "verification": "basic",
          "min_photos": 3
        },
        {
          "id": "hair-color",
          "name": "Hair Color",
          "price_range": {"min": 80, "max": 300},
          "duration_range": {"min": 90, "max": 180},
          "verification": "basic",
          "min_photos": 3
        },
        {
          "id": "barber",
          "name": "Barber",
          "price_range": {"min": 20, "max": 60},
          "duration_range": {"min": 20, "max": 45},
          "verification": "basic",
          "min_photos": 3
        }
      ]
    },
    {
      "id": "cleaning",
      "name": "Cleaning",
      "icon": "🧹",
      "services": [
        {
          "id": "standard-cleaning",
          "name": "Standard Cleaning",
          "price_range": {"min": 80, "max": 200},
          "duration_range": {"min": 120, "max": 240},
          "verification": "basic",
          "min_photos": 0
        },
        {
          "id": "deep-cleaning",
          "name": "Deep Cleaning",
          "price_range": {"min": 150, "max": 400},
          "duration_range": {"min": 180, "max": 360},
          "verification": "basic",
          "min_photos": 0
        }
      ]
    },
    {
      "id": "plumbing",
      "name": "Plumbing",
      "icon": "🔧",
      "services": [
        {
          "id": "leak-repair",
          "name": "Leak Repair",
          "price_range": {"min": 100, "max": 500},
          "duration_range": {"min": 60, "max": 240},
          "verification": "licensed",
          "license_required": "plumbing"
        },
        {
          "id": "water-heater",
          "name": "Water Heater",
          "price_range": {"min": 200, "max": 1000},
          "duration_range": {"min": 120, "max": 480},
          "verification": "licensed",
          "license_required": "plumbing"
        }
      ]
    },
    {
      "id": "photography",
      "name": "Photography",
      "icon": "📸",
      "services": [
        {
          "id": "portrait",
          "name": "Portrait Photography",
          "price_range": {"min": 100, "max": 500},
          "duration_range": {"min": 60, "max": 180},
          "verification": "basic",
          "min_photos": 5
        },
        {
          "id": "event",
          "name": "Event Photography",
          "price_range": {"min": 300, "max": 2000},
          "duration_range": {"min": 120, "max": 480},
          "verification": "basic",
          "min_photos": 5
        }
      ]
    }
  ],
  "verification_levels": {
    "basic": {
      "requirements": ["portfolio_photos", "phone_verified", "email_verified"],
      "auto_approve": true
    },
    "licensed": {
      "requirements": ["license_number", "license_photo", "background_check"],
      "auto_approve": false,
      "review_required": true
    }
  }
}
```

---

*End of Technical Appendices*
