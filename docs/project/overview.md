# Proxie Project Overview

## What is Proxie?

Proxie is an agent-native platform that connects skilled individual service providers with consumers through AI agents. No websites, no social media, no marketing hustle. Just skills, fairly represented.

## The Problem

Millions of people are genuinely good at something: cutting hair, fixing leaks, capturing moments, caring for children, walking dogs, cleaning spaces. Yet the modern economy makes it unreasonably hard for them to connect with people who need exactly what they offer.

To sell your skills today, you need to become something you are not: a marketer, a web designer, a social media manager, an SEO strategist.

**This is broken.**

## The Solution

Proxie eliminates the digital tax on skilled work:

1. **Providers** register once, describing their skills, availability, and pricing
2. Their **AI agent** represents them 24/7
3. **Consumers** describe what they need in natural language
4. **Agent-to-agent** matching and negotiation happens automatically
5. Booking is confirmed in minutes, not hours

## How It Works

### Provider Enrollment
```
Provider: "I want to become a provider"
    ↓
Enrollment Agent: Guides through conversational onboarding
    ↓
Provider: Selects services, sets pricing, adds portfolio
    ↓
Verification Service: Auto-verifies basic services, queues licensed services
    ↓
Provider activated and ready to receive leads
```

### Consumer Request & Booking
```
Consumer: "I need a haircut for curly hair, Brooklyn, this weekend"
    ↓
Consumer Agent: Creates structured service request
    ↓
Platform: Matches to relevant provider agents
    ↓
Provider Agents: Generate offers with availability and pricing
    ↓
Consumer Agent: Presents options
    ↓
Consumer: "Book Maya for Saturday 2pm"
    ↓
Done. Under 5 minutes.
```

## Target Market (MVP)

- **Vertical**: Hairstylists
- **Location**: Single city/neighborhood
- **Why**: Clean service, personal skill matters, current discovery is painful

## Technology Stack (Architecture 2.0)

- **UI Layer**: Next.js 14 (App Router) + Socket.io Client
- **AI Layer**: LiteLLM Gateway (Gemini 2.5 + Claude 3.5 Fallback) + LangGraph
- **Logic Layer**: FastAPI + Celery (Async Jobs) + Temporal (Workflows)
- **Data Layer**: PostgreSQL 16 (pgvector) + Redis 7 (Sessions/Cache) + Cloudflare R2
- **Operating Layer**: Kubernetes (GKE) + Kong API Gateway + OpenTelemetry

## Success Metrics

| Metric | Target |
|--------|--------|
| Providers onboarded | 10-20 |
| Consumers activated | 20-30 |
| Transactions completed | 20+ |
| Time to book | Under 5 minutes |
| Satisfaction | 80%+ |

## Project Phases

1. **Foundation** (Weeks 1-4): Define schemas, design agents, validate (COMPLETED)
2. **Core Build** (Weeks 5-10): Build platform, agents, MCP server (COMPLETED)
3. **Architecture 2.0** (Weeks 11-14): Foundation hardening, Redis sessions, Socket.io, Next.js migration (IN PROGRESS)
4. **Learn & Iterate** (Weeks 15-18): Learn and improve
5. **Expand** (Week 19+): Scale what works

---

See [vision.md](vision.md) for mission and principles.
See [roadmap.md](roadmap.md) for detailed timeline.
