# Proxie Platform: Technical Architecture Specification

**Document Version:** 2.0  
**Date:** January 27, 2026  
**Status:** Ready for Implementation Planning  
**Prepared For:** AntiGravity Engineering Team  
**Classification:** Internal / Confidential

---

## Executive Summary

### What is Proxie?

Proxie is an **agent-native marketplace** that connects skilled service providers (hairstylists, cleaners, plumbers, photographers) with consumers through AI agents. Unlike traditional gig platforms, Proxie eliminates the need for providers to market themselves—their AI agent represents them 24/7, handling discovery, negotiation, and booking.

**Core Value Proposition:**
- **For Providers:** No marketing required. Your skill is your only qualification.
- **For Consumers:** Describe what you need in natural language. Get matched in minutes.
- **For the Market:** Agent-to-agent transactions as the future of service discovery.

### Current State (Sprint 11 Complete)

| Metric | Status |
|--------|--------|
| Backend API | ✅ Functional (FastAPI + PostgreSQL) |
| AI Chat Interface | ✅ Live (Gemini 2.0 Flash) |
| Consumer Dashboard | ✅ Complete (Request lifecycle) |
| Provider Dashboard | ✅ Complete (Leads + Offers) |
| Provider Enrollment | ✅ Complete (Conversational onboarding) |
| MCP Protocol | ✅ Implemented (External agent support) |
| Multi-Modal Vision | ✅ Working (Photo/video analysis) |
| Authentication | ✅ Live (Clerk + Agent-Native Sync) |
| Production Readiness | ⚠️ Gaps identified (see below) |

### Critical Gaps Requiring Immediate Attention

| Gap | Risk | Priority |
|-----|------|----------|
| In-memory session storage | Resolved (Redis Migration) | 🟢 Complete |
| No real-time communication | Resolved (Socket.io) | 🟢 Complete |
| No observability | Resolved (Sentry/Structlog) | 🟢 Complete |
| Single-process architecture | Cannot scale beyond one instance | 🟠 High |
| No message queue | Tight coupling, blocking LLM calls | 🟠 High |
| Basic caching | Repeated LLM calls, slow responses | 🟡 Medium |

### Why This Document Exists

This document specifies the target architecture across five layers, providing AntiGravity with everything needed to:

1. **Restructure the codebase** for production readiness
2. **Update all project documentation** to reflect new architecture
3. **Create a phased implementation plan** with clear milestones
4. **Establish technical standards** for ongoing development

---

## Architecture Overview

### Target Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              TARGET STATE                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           UI LAYER                                       │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │  Next.js Web App    │  React Native Mobile  │  MCP/REST Agent Interface │ │
│  │  • SSR + PWA        │  • iOS + Android      │  • Claude Desktop         │ │
│  │  • Real-time Chat   │  • Push Notifications │  • Custom Agents          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        API GATEWAY (Kong)                                │ │
│  │         Rate Limiting │ Auth │ Routing │ SSL Termination                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                    ┌─────────────────┼─────────────────┐                     │
│                    ▼                 ▼                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           AI LAYER                                       │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │  Agent Orchestrator    │  LLM Gateway (LiteLLM)  │  Specialist Agents   │ │
│  │  • Session Management  │  • Gemini (Primary)     │  • Haircut           │ │
│  │  • Context Windowing   │  • Claude (Fallback)    │  • Cleaning          │ │
│  │  • Tool Execution      │  • Response Caching     │  • Plumbing          │ │
│  │  • Multi-Agent Routing │  • Cost Tracking        │  • Photography       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                          LOGIC LAYER                                     │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │  FastAPI Services      │  Celery Workers         │  Temporal Workflows  │ │
│  │  • Request Management  │  • Async LLM Calls      │  • Booking Flow      │ │
│  │  • Offer Processing    │  • Matching Engine      │  • Notifications     │ │
│  │  • Booking Workflow    │  • Media Processing     │  • Review Requests   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                    ┌─────────────────┼─────────────────┐                     │
│                    ▼                 ▼                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                          DATA LAYER                                      │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │  PostgreSQL + pgvector │  Redis Cluster          │  S3 / Cloudflare R2  │ │
│  │  • Transactions        │  • Sessions             │  • Media Storage     │ │
│  │  • Relationships       │  • Cache                │  • Portfolio Photos  │ │
│  │  • Vector Embeddings   │  • Pub/Sub              │  • Documents         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                       OPERATING LAYER                                    │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │  Kubernetes (GKE)      │  Observability          │  Security            │ │
│  │  • Auto-scaling        │  • OpenTelemetry        │  • Clerk Auth        │ │
│  │  • Load Balancing      │  • Grafana + Loki       │  • Vault Secrets     │ │
│  │  • Service Mesh        │  • Sentry Errors        │  • WAF + DDoS        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary Cloud | Google Cloud Platform (GCP) | Best Gemini integration, competitive pricing |
| Container Orchestration | Kubernetes (GKE Autopilot) | Managed control plane, auto-scaling |
| Primary LLM | Gemini 2.5 Flash | Speed, cost, vision capabilities, native GCP |
| Fallback LLM | Claude 3.5 Sonnet | Superior reasoning for complex cases |
| Database | PostgreSQL 16 + pgvector | ACID compliance, vector search, mature ecosystem |
| Cache/Queue | Redis 7 (Cluster Mode) | Sessions, caching, pub/sub, task queue |
| Frontend Framework | Next.js 14 (App Router) | SSR, API routes, React Server Components |
| Mobile Framework | React Native + Expo | Code sharing, OTA updates, native performance |
| Auth Provider | Clerk | Social login, session management, RBAC |
| Observability | OpenTelemetry + Grafana Stack | Vendor-neutral, comprehensive |

---

## Layer 1: UI Layer

### Technology Stack

| Component | Current | Target | Migration Priority |
|-----------|---------|--------|-------------------|
| Web Framework | Vite + React (CSR) | Next.js 14 (SSR + CSR) | Phase 2 |
| Styling | Tailwind CSS v4 | Tailwind CSS v4 | No change |
| State Management | useState/useEffect | Zustand + TanStack Query | Phase 2 |
| Real-time | 5s Polling | Socket.io | Phase 1 (Critical) |
| Component Library | Custom | shadcn/ui + Radix | Phase 2 |
| Mobile | PWA only | React Native + Expo | Phase 3 |

### WebSocket Events Specification

**Client → Server:**
| Event | Payload | Description |
|-------|---------|-------------|
| `chat:message` | `{session_id, content, media[]}` | Send chat message |
| `chat:typing` | `{session_id, is_typing}` | Typing indicator |
| `presence:online` | `{user_id}` | User came online |

**Server → Client:**
| Event | Payload | Description |
|-------|---------|-------------|
| `chat:response` | `{session_id, content, data}` | Agent response |
| `chat:stream` | `{session_id, token}` | Streaming token |
| `offer:new` | `{request_id, offer}` | New offer received |
| `booking:confirmed` | `{booking}` | Booking confirmed |

---

## Layer 2: AI Layer

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM Gateway | LiteLLM | Provider abstraction, fallback, caching |
| Primary LLM | Gemini 2.5 Flash | Fast responses, vision, cost-effective |
| Fallback LLM | Claude 3.5 Sonnet | Complex reasoning, function calling |
| Embedding Model | text-embedding-3-large | Semantic search, similarity |
| Agent Framework | LangGraph | Multi-agent orchestration |
| Vector Store | pgvector | Embeddings storage |

### LLM Provider Configuration

```yaml
providers:
  gemini:
    models: [gemini-2.5-flash-preview, gemini-2.5-pro-preview]
    default: gemini-2.5-flash-preview
    cost_per_1k_input: $0.000125
    cost_per_1k_output: $0.000375
    supports_vision: true

  anthropic:
    models: [claude-3-5-sonnet, claude-3-5-haiku]
    default: claude-3-5-sonnet
    cost_per_1k_input: $0.003
    cost_per_1k_output: $0.015
    supports_vision: true

routing:
  default: gemini
  fallback_chain: [gemini, anthropic, openai]
  complexity_routing:
    simple: gemini
    complex: anthropic

caching:
  enabled: true
  backend: redis
  ttl_seconds: 3600
```

### Tool Definitions

**Consumer Tools:**
| Tool | Description |
|------|-------------|
| `create_service_request` | Create and submit a service request |
| `get_offers` | Retrieve offers for a request |
| `accept_offer` | Accept an offer and create booking |
| `cancel_request` | Cancel an active request |
| `submit_review` | Rate and review completed service |

**Provider Tools:**
| Tool | Description |
|------|-------------|
| `get_matching_requests` | Get new leads matching skills |
| `get_lead_details` | View full request details |
| `suggest_offer` | Get AI-powered pricing suggestions |
| `submit_offer` | Send offer to consumer |
| `update_availability` | Modify schedule |

---

## Layer 3: Logic Layer

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | FastAPI 0.109+ | Async HTTP endpoints |
| Background Jobs | Celery 5.3+ | Async task processing |
| Workflow Engine | Temporal.io | Complex workflow orchestration |
| ORM | SQLAlchemy 2.0 | Database operations |
| Validation | Pydantic v2 | Request/response validation |

### Service Architecture

```
src/platform/
├── main.py                 # FastAPI application entry
├── config.py               # Configuration management
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── routers/                # API endpoints
├── services/               # Business logic
├── workers/                # Celery tasks
└── workflows/              # Temporal workflows
```

### Matching Engine Algorithm

```python
WEIGHTS = {
    "skill_match": 0.30,      # Service type compatibility
    "location_score": 0.25,   # Geographic proximity
    "availability": 0.20,     # Schedule compatibility
    "price_fit": 0.10,        # Budget alignment
    "rating_weight": 0.10,    # Provider reputation
    "response_rate": 0.05,    # Historical responsiveness
}
```

### Booking Workflow States

```
Request → Pending → Confirmed → In Progress → Completed → Reviewed
              ↓                      ↓
          Cancelled              No Show
```

---

## Layer 4: Data Layer

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary Database | PostgreSQL 16 | Transactions, relationships |
| Vector Store | pgvector 0.6+ | Embeddings for semantic search |
| Cache | Redis 7 (Cluster) | Sessions, cache, pub/sub, queue |
| Search | Elasticsearch 8 | Full-text search (future) |
| File Storage | Cloudflare R2 | Media, documents |
| CDN | Cloudflare | Static assets, media delivery |

### Redis Data Structures

```
# Session storage
session:{session_id} → Hash (user_id, role, context, messages)
TTL: 24 hours

# Rate limiting
rate_limit:{user_id}:{endpoint} → Sorted Set (timestamps)

# Pub/Sub channels
notifications:{user_id}
chat:{session_id}

# Task queue
celery (default), celery:high, celery:low
```

### Backup Strategy

| Data Type | Frequency | Retention |
|-----------|-----------|-----------|
| PostgreSQL (WAL) | Continuous | 7 days |
| PostgreSQL (Full) | Daily | 30 days |
| Redis (RDB) | Hourly | 3 days |
| R2 Media | Real-time replication | Indefinite |

---

## Layer 5: Operating Layer

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Cloud Platform | Google Cloud Platform | Primary infrastructure |
| Container Orchestration | GKE Autopilot | Managed Kubernetes |
| API Gateway | Kong | Rate limiting, auth, routing |
| CI/CD | GitHub Actions | Build, test, deploy |
| Secrets Management | Google Secret Manager | Secure secrets |

### Observability Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | System and business metrics |
| Logging | Loki + Grafana | Centralized logs |
| Tracing | Tempo + Grafana | Distributed tracing |
| Errors | Sentry | Exception tracking |
| Alerting | PagerDuty | Incident management |

### Key Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| API Latency Critical | p99 > 5s for 2m | Critical |
| Error Rate High | > 1% for 5m | Warning |
| LLM Failures | > 10% for 5m | Critical |
| Queue Backlog | > 1000 tasks | Warning |

---

## Security & Compliance

### Authentication (Clerk)

- Social login (Google, Apple)
- Magic link authentication
- Session management with JWT
- Role-based access control (RBAC)

### Security Layers

| Layer | Implementation |
|-------|----------------|
| Edge | Cloudflare WAF, DDoS protection |
| Gateway | Kong rate limiting, JWT verification |
| Transport | TLS 1.3, HSTS |
| Application | Input validation, CORS |
| Data | Encryption at rest, field-level for PII |

### Compliance

| Regulation | Key Requirements |
|------------|------------------|
| GDPR | Right to access, erasure, portability |
| CCPA | Right to know, delete, opt-out |
| PCI DSS (Future) | Stripe tokenization, no card storage |

---

## Disaster Recovery

### Recovery Objectives

| Metric | Target |
|--------|--------|
| Recovery Time Objective (RTO) | 1 hour |
| Recovery Point Objective (RPO) | 5 minutes |
| Availability Target | 99.9% |

### Failover Strategy

- **Primary Region:** us-central1
- **Secondary Region:** us-east1
- **Failover Trigger:** Primary unavailable > 5 minutes
- **Estimated Failover Time:** 15-30 minutes

---

## Cost Projections

### Pilot Phase (50 Users): $330/month

| Component | Cost |
|-----------|------|
| Compute (GKE) | $150 |
| Database (Cloud SQL) | $50 |
| Cache (Redis) | $25 |
| LLM API (Gemini) | $100 |
| Storage | $5 |

### Scale Phase (10,000 Users): $6,000/month

| Component | Cost |
|-----------|------|
| Compute (GKE) | $1,500 |
| Database (HA + Replicas) | $500 |
| Cache (Redis Cluster) | $300 |
| LLM API (Gemini) | $2,500 |
| Search (Elasticsearch) | $500 |
| Other | $700 |

### Cost Optimization Strategies

| Strategy | Savings |
|----------|---------|
| LLM response caching | -40% LLM costs |
| Spot instances | -70% compute |
| Model routing | -50% LLM costs |

---

## Implementation Phases

### Phase 1: Foundation Hardening (Weeks 1-2)

| Task | Priority | Effort |
|------|----------|--------|
| Move sessions to Redis | Critical | 2 days |
| Implement structured logging | Critical | 1 day |
| Add health check endpoints | Critical | 0.5 days |
| Set up Sentry | Critical | 0.5 days |
| Add OpenTelemetry tracing | High | 2 days |
| Implement WebSocket for chat | High | 3 days |

### Phase 2: Async & Scale Prep (Weeks 3-4)

| Task | Priority | Effort |
|------|----------|--------|
| Set up Celery + Redis queue | High | 2 days |
| Migrate LLM calls to async | High | 2 days |
| Implement LLM Gateway | High | 2 days |
| Add response caching | High | 1 day |
| Push notification service | Medium | 2 days |

### Phase 3: Frontend Modernization (Weeks 5-6)

| Task | Priority | Effort |
|------|----------|--------|
| Migrate to Next.js 14 | High | 5 days |
| Implement Zustand + TanStack Query | High | 2 days |
| Integrate Socket.io client | High | 1 day |
| Set up Clerk authentication | High | 2 days |

### Phase 4: Infrastructure (Weeks 7-8)

| Task | Priority | Effort |
|------|----------|--------|
| Set up GKE Autopilot | High | 2 days |
| Configure Kong API Gateway | High | 2 days |
| Deploy Grafana stack | High | 2 days |
| Set up CI/CD pipeline | High | 2 days |
| Load testing | High | 2 days |
| Security audit | High | 2 days |

### Phase 5: Mobile (Weeks 9-10)

| Task | Priority | Effort |
|------|----------|--------|
| Initialize React Native | High | 1 day |
| Implement core screens | High | 5 days |
| Push notification integration | High | 1 day |
| App Store preparation | Medium | 2 days |

---

## Success Criteria

### Technical Metrics

| Metric | Target |
|--------|--------|
| API Latency (p99) | < 500ms |
| Error Rate | < 0.1% |
| Uptime | 99.9% |
| LLM Response Time | < 3 seconds |
| Cache Hit Rate | > 50% |

### Business Metrics

| Metric | Target |
|--------|--------|
| Provider Enrollment Completion | > 80% |
| Request to Offer Conversion | > 60% |
| Offer to Booking Conversion | > 30% |
| User Retention (7-day) | > 40% |
| Average Rating | > 4.5 |

---

## Appendices

See companion document: **Proxie Technical Appendices** for:
- A: Complete Database Schema (SQL)
- B: API Endpoint Specifications
- C: System Prompts
- D: Environment Variables
- E: Kubernetes Configurations
- F: CI/CD Pipeline Definitions

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | Architecture Team | Initial draft |
| 2.0 | 2026-01-27 | Architecture Team | AntiGravity-ready version |

**Next Review:** After Phase 1 completion  
**Distribution:** AntiGravity Engineering, Proxie Leadership
