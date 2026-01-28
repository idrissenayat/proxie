# Proxie Roadmap

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Define the Core
- [x] Finalize service categories for MVP
- [x] Define geographic scope
- [x] Document service request schema
- [x] Document offer schema
- [x] Document booking schema

### Week 2: Design the Agents
- [ ] Consumer agent specification
- [ ] Provider agent specification
- [ ] Conversation flows
- [ ] Edge cases identified

### Week 3: Design the Platform
- [x] Complete data model
- [x] MCP interface specification
- [x] Matching algorithm design
- [ ] Trust framework v1

### Week 4: Validate
- [ ] Interview 10+ potential providers
- [ ] Interview 10+ potential consumers
- [ ] Refine based on feedback
- [ ] Go/no-go decision

## Phase 2: Core Build (Weeks 5-10)

### Weeks 5-6: Data Layer
- [x] Set up PostgreSQL database
- [x] Implement database models
- [x] Provider registration flow
- [ ] Portfolio storage (S3)

### Weeks 7-8: Agent Runtime
- [ ] Consumer agent implementation
- [ ] Provider agent implementation
- [ ] Agent-to-platform communication
- [ ] Provider rules engine

### Week 9: Service Request Hub
- [x] Request ingestion
- [x] Matching engine
- [x] Offer aggregation
- [x] Booking confirmation
- [x] **Mobile & Web App (Consumer/Provider flows)**

### Week 10: MCP Interface & AI Features
- [x] MCP server implementation
- [x] Authentication
- [x] Documentation
- [x] Test with Claude
- [x] **AI Chatbot Interface**
- [x] **Dark Mode Dashboard + Conversational Input Bar**
- [x] **Gemini Migration (Claude → Google)**
- [x] **Security Hardening (CORS, Rate Limiting, Headers)**
- [x] **Sprint 8: Multi-Modal Agent + Specialist Framework**
- [x] **Sprint 9: Provider Dashboard & Leads View**
- [x] **Sprint 9B: Consumer Dashboard - My Requests View**
- [x] **Sprint 9C: Provider Enrollment & Verification System**
- [x] **Sprint 10: Request Details & Provider Profiles**

## Phase 3: Architecture 2.0 - Scale & Reliability (Weeks 11-14)

### Week 11: Foundation Hardening
- [x] Migrate session management to **Redis** cluster
- [x] Implement **Sentry** and OpenTelemetry for observability
- [x] Move from polling to **Socket.io** for real-time chat
- [x] Implement health check and readiness probe system

### Week 12: Async LLM & Caching
- [x] Set up **Celery + Redis** for async agent execution
- [x] Implement **LiteLLM Gateway** for model abstraction
- [x] Add LLM response caching to reduce latency/cost

### Weeks 13-14: Frontend Modernization & Infrastructure
- [x] **Sprint 11: Stability, E2E Testing & Mocking Infrastructure**
- [x] Migrate from Vite to **Next.js 14** (App Router)
- [x] Integrate **Clerk Authentication** (Premium UI)
- [x] Prepare **Kubernetes (GKE)** manifests with autopilot
- [x] Set up **Kong API Gateway** configuration for rate limiting/auth

## Phase 4: Learn & Iterate (Weeks 15-18)

- [ ] Analyze all transactions
- [ ] Interview pilot participants
- [ ] Fix critical issues
- [ ] Refine agents
- [ ] Improve matching
- [ ] Strengthen trust layer

## Phase 5: Expand (Week 19+)

- [ ] Add more providers
- [ ] Expand consumer access
- [ ] Add service categories
- [ ] Expand geography
- [ ] Formalize business model

---

## Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Schemas defined | Week 1 | ✅ |
| Agents designed | Week 2 | ✅ |
| User validation complete | Week 4 | ⬜ |
| MCP Backend complete | Week 10 | ✅ |
| Proxie PWA Foundation | Week 10 | ✅ |
| AI Chatbot Interface | Week 10 | ✅ |
| Dark Mode Dashboard | Week 10 | ✅ |
| Gemini Migration | Week 10 | ✅ LIVE |
| Authentication (Clerk) | Week 11 | ✅ |
| Security Hardening | Week 10 | ✅ |
| Multi-Modal Agent & Specialists | Week 10 | ✅ |
| Provider Dashboard & Leads | Week 10 | ✅ |
| Consumer Request Dashboard | Week 10 | ✅ |
| Provider Enrollment System | Week 11 | ✅ |
| Request Details & Provider Profiles | Week 11 | ✅ |
| Architecture 2.0 Infrastructure | Week 12 | ✅ |
| E2E Testing & System Stability | Week 12 | ✅ |
| Legacy Mobile App (Expo) | Week 10 | 💤 |
| First real booking | Week 13 | ⬜ |
| Pilot complete | Week 14 | ⬜ |
| Ready to scale | Week 18 | ⬜ |

