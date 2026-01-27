# Proxie Product Backlog

**Last Updated:** January 27, 2026  
**Product:** Proxie - Agent-Native Service Marketplace  
**Version:** Architecture 2.0

---

## Backlog Overview

| Priority | Category | Total Items | Completed | Remaining |
|----------|----------|-------------|-----------|-----------|
| 🔴 Critical | Core Infrastructure | 14 | 15 | 0 |
| 🟠 High | Production Polish | 12 | 0 | 12 |
| 🟡 Medium | Feature Enhancements | 15 | 0 | 15 |
| 🟢 Low | Future/Nice-to-Have | 12 | 0 | 12 |

---

## ✅ Completed (Archive)

### Sprint 10+ Completions

| ID | Item | Category | Completed |
|----|------|----------|-----------|
| DONE-001 | Next.js 14 Migration | Frontend | 2026-01-26 |
| DONE-002 | LiteLLM Gateway | AI Layer | 2026-01-27 |
| DONE-003 | Redis Session Management | Backend | 2026-01-27 |
| DONE-004 | Celery Background Workers | Backend | 2026-01-27 |
| DONE-005 | LLM Response Caching | AI Layer | 2026-01-27 |
| DONE-006 | Kubernetes Manifests | DevOps | 2026-01-27 |
| DONE-007 | Kong API Gateway Config | DevOps | 2026-01-27 |
| DONE-008 | Socket.io Real-time Chat | Backend | 2026-01-25 |
| DONE-009 | Sentry + OpenTelemetry | Observability | 2026-01-25 |
| DONE-010 | Health/Readiness Probes | Backend | 2026-01-25 |
| DONE-011 | Consumer Dashboard | Frontend | 2026-01-24 |
| DONE-012 | Provider Dashboard | Frontend | 2026-01-24 |
| DONE-013 | Provider Enrollment Flow | Frontend | 2026-01-23 |
| DONE-014 | Specialist Agents (Haircut) | AI Layer | 2026-01-22 |
| DONE-015 | Clerk Authentication (Frontend) | Frontend | 2026-01-27 |
| DONE-016 | Agent-Native Profile Sync | AI Layer | 2026-01-27 |

---

## 🔴 Critical Priority (P0)

*Must complete before pilot launch*

### Authentication & Security

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P0-001 | Clerk Authentication | Replace mock auth with Clerk SDK | 3d | ✅ |
| P0-002 | JWT Middleware | Backend JWT verification for all protected routes | 1d | 🔲 |
| P0-003 | Role-Based Access | Consumer vs Provider vs Admin permissions | 2d | 🔲 |
| P0-004 | API Key Secrets | Move all API keys to secure secret management | 0.5d | 🔲 |

### Deployment & CI/CD

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P0-005 | GitHub Actions CI | Run tests on every PR | 1d | ✅ |
| P0-006 | GitHub Actions CD | Auto-deploy to GKE on merge to main | 1d | ✅ |
| P0-007 | GKE Cluster Setup | Create production GKE Autopilot cluster | 0.5d | 🔲 |
| P0-008 | Domain & SSL | Configure proxie.app domain with SSL | 0.5d | 🔲 |

---

## 🟠 High Priority (P1)

*Should complete for production quality*

### Observability

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P1-001 | Grafana Dashboards | API latency, error rates, request counts | 2d | 🔲 |
| P1-002 | LLM Cost Dashboard | Track token usage and costs by model | 1d | 🔲 |
| P1-003 | Business Metrics | Requests created, offers made, bookings | 1d | 🔲 |
| P1-004 | Log Aggregation | Loki setup for centralized logs | 1d | 🔲 |

### Alerting

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P1-005 | Slack Alerts | Critical errors, LLM failures, high latency | 1d | 🔲 |
| P1-006 | PagerDuty Integration | On-call rotation for production issues | 0.5d | 🔲 |

### Data Quality

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P1-007 | Database Migrations | Alembic setup for schema versioning | 1d | 🔲 |
| P1-008 | Data Backup Automation | Automated PostgreSQL backups to GCS | 1d | 🔲 |

### Testing

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P1-009 | E2E Test Suite | Playwright tests for critical flows | 3d | 🔲 |
| P1-010 | Load Testing | k6 scripts for 100+ concurrent users | 1d | 🔲 |
| P1-011 | Security Audit | OWASP Top 10 vulnerability scan | 2d | 🔲 |
| P1-012 | API Documentation | OpenAPI/Swagger with examples | 1d | 🔲 |

---

## 🟡 Medium Priority (P2)

*Important for scale and user experience*

### AI Enhancements

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P2-001 | Embedding Model | text-embedding-3-large integration | 2d | 🔲 |
| P2-002 | Semantic Search | pgvector-based provider matching | 3d | 🔲 |
| P2-003 | LangGraph Orchestration | Multi-agent conversation routing | 5d | 🔲 |
| P2-004 | LLM Cost Tracking | Per-session and per-user cost limits | 2d | 🔲 |
| P2-005 | Additional Specialists | Cleaning, Plumbing, Photography agents | 3d each | 🔲 |

### User Experience

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P2-006 | Push Notifications | FCM/APNs for offers and bookings | 3d | 🔲 |
| P2-007 | Email Notifications | Transactional emails via SendGrid | 2d | 🔲 |
| P2-008 | SMS Notifications | Twilio for critical updates | 1d | 🔲 |
| P2-009 | In-App Notifications | Real-time notification center | 2d | 🔲 |

### Provider Features

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P2-010 | Availability Calendar | Visual calendar for schedule management | 3d | 🔲 |
| P2-011 | Earnings Dashboard | Revenue tracking and analytics | 2d | 🔲 |
| P2-012 | Portfolio Management | Photo/video upload and organization | 2d | 🔲 |

### Consumer Features

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P2-013 | Booking History | Past bookings with re-book option | 1d | 🔲 |
| P2-014 | Favorites List | Save preferred providers | 1d | 🔲 |
| P2-015 | Review System | Rate and review completed services | 2d | 🔲 |

---

## 🟢 Low Priority (P3)

*Future enhancements and nice-to-haves*

### Mobile Application

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P3-001 | React Native Setup | Expo project initialization | 1d | 🔲 |
| P3-002 | Core Mobile Screens | Home, Chat, Dashboard, Profile | 5d | 🔲 |
| P3-003 | Mobile Push Notifications | Firebase Cloud Messaging | 2d | 🔲 |
| P3-004 | iOS App Store Submission | Apple review process | 3d | 🔲 |
| P3-005 | Android Play Store Submission | Google review process | 2d | 🔲 |

### Advanced Infrastructure

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P3-006 | Elasticsearch | Full-text search for providers | 3d | 🔲 |
| P3-007 | Cloudflare R2 | Media storage migration | 2d | 🔲 |
| P3-008 | CDN Integration | Static asset optimization | 1d | 🔲 |
| P3-009 | Multi-Region Deployment | us-east1 failover | 3d | 🔲 |

### Complex Workflows

| ID | Item | Description | Effort | Status |
|----|------|-------------|--------|--------|
| P3-010 | Temporal.io | Workflow orchestration engine | 5d | 🔲 |
| P3-011 | Payment Processing | Stripe integration for bookings | 5d | 🔲 |
| P3-012 | Provider Payouts | Automated earnings distribution | 3d | 🔲 |

---

## Icebox (Future Consideration)

*Ideas for future evaluation*

| ID | Item | Notes |
|----|------|-------|
| ICE-001 | Voice Interface | Alexa/Google Assistant integration |
| ICE-002 | Video Consultations | Real-time video for remote services |
| ICE-003 | AI-Generated Quotes | Automatic pricing based on request complexity |
| ICE-004 | Provider Certification | Verified skills and credentials |
| ICE-005 | Referral Program | User growth incentives |
| ICE-006 | B2B API | White-label marketplace for partners |
| ICE-007 | Provider Equipment Lending | Tool/equipment rental marketplace |
| ICE-008 | Group Services | Multiple consumers, single provider |

---

## Sprint Planning Reference

### Suggested Sprint Priorities

**Sprint 11 (Current)** - Production Readiness
- P0-001 through P0-008 (Authentication + Deployment)

**Sprint 12** - Observability
- P1-001 through P1-006 (Dashboards + Alerting)

**Sprint 13** - Quality & Testing
- P1-007 through P1-012 (Testing + Documentation)

**Sprint 14** - AI Enhancements
- P2-001 through P2-005 (Embeddings + Specialists)

**Sprint 15** - Notifications
- P2-006 through P2-009 (Push + Email + SMS)

---

## Definition of Done

- [ ] Code reviewed and approved
- [ ] Unit tests passing (>80% coverage for new code)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] No critical/high security vulnerabilities
- [ ] Deployed to staging and verified
- [ ] Product owner sign-off

---

## Backlog Grooming Notes

**Last Groomed:** January 27, 2026

**Key Decisions:**
1. Clerk chosen for auth (simpler than custom JWT)
2. Grafana stack preferred over Datadog (cost)
3. Mobile app deprioritized until web stable
4. Payment processing deferred to post-pilot

**Next Grooming:** After Sprint 11 completion
