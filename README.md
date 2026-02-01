# Proxie

**Your agent. Your proxy. Your craft, represented.**

Proxie is an agent-native platform that connects skilled individual service providers with consumers through AI agents. No websites, no social media, no marketing hustle. Just skills, fairly represented.

## Vision

A world where consumer agents and provider agents negotiate and transact on behalf of humans — accessible only through AI interfaces. Humans describe needs. Humans do the work. Everything in between is agent-to-agent.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Node.js 20+ (for Next.js 14)
- Google Cloud account (Gemini API)

### Installation

**1. Backend**
```bash
# Clone the repository
git clone https://github.com/yourusername/proxie.git
cd proxie

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration (DB, Redis, Gemini, Clerk)

# Run database migrations
python scripts/migrate.py

# Start the server
python -m src.platform.main
```

**2. Frontend (Next.js 14)**
```bash
cd web-next

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
pytest tests/
```

## Features (Architecture 2.0)

Proxie features a premium, agent-native experience built with **Next.js 14** and **Socket.io**.

- 🌙 **Next.js 14 Dashboard** - High-performance SSR/CSR hybrid dashboard
- 💬 **Real-time Chat** - Low-latency events via Socket.io
- 👤 **Clerk Authentication** - Enterprise-grade identity management
- 👤 **Agent-Native Profile Sync** - AI captures user data during chat
- 📷 **Multi-modal Vision** - Gemini 2.0 photo/video analysis
- 💾 **Redis Session Store** - Scalable session management
- 🛠 **Provider Enrollment** - Conversational onboarding system
- 🔒 **Infrastructure Hardening** - Kong API Gateway + GKE support
- 🛡️ **Security & Testing** - JWT auth, RBAC, ownership validation, 143+ tests
- ⚡ **Performance** - Async LLM processing, caching, query optimization, rate limiting
- 📊 **Error Tracking** - Sentry integration for frontend error monitoring

### Mobile App (Archive)

The legacy mobile interface in `/mobile` is built with Expo. It is currently archived as the project focuses on the PWA.

## Documentation

- [Project Overview](docs/project/overview.md)
- [Architecture Main](docs/project/proxie_architecture_main.md)
- [Roadmap](docs/project/roadmap.md)
- [API Documentation](docs/api/README.md)
- [Sprint 11 Summary](docs/project/sprint-11-architecture-2.0.md) - Auth & Profile Sync
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Security, Testing, Performance improvements
- [Quick Reference](QUICK_REFERENCE.md) - Developer quick reference guide
- [Sentry Setup](web-next/SENTRY_SETUP.md) - Frontend error tracking setup

## Project Structure

```
proxie/
├── src/            # Core backend logic (FastAPI + AI Services)
├── web-next/       # Primary Frontend (Next.js 14)
├── docs/           # Architecture and Sprint documentation
├── k8s/            # Kubernetes production manifests
├── tests/          # Integration and unit tests
└── scripts/        # Database and utility scripts
```

## Technology Stack

- **UI**: Next.js 14, Tailwind CSS v4, Lucide
- **AI**: LiteLLM (Gemini 2.5 + Claude 3.5 Fallback)
- **Backend**: FastAPI, Celery (Redis Queue), Socket.io
- **Database**: PostgreSQL 16 (pgvector), Redis 7
- **Operating**: Kubernetes (GKE), Kong Gateway, OpenTelemetry

## Contributing

See [Contributing Guide](docs/guides/contributing.md) for details.

## License

[MIT License](LICENSE)

---

**Proxie** — *Your craft, represented.*
