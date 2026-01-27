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
# Edit .env with your configuration

# Run database migrations
python scripts/migrate.py

# Start the server
python -m src.platform.main
```

### Running Tests

```bash
# Backend tests
pytest tests/
```

### Proxie Web (PWA)

The primary user interface is an **AI Chatbot** powered by Gemini (Google), with a Progressive Web App built with Vite, React, and Tailwind CSS.

**Features:**
- 🌙 Dark mode Service Marketplace dashboard
- 💬 Conversational Input Bar (Ask anything)
- 🎤 Voice input via Web Speech API
- 🔊 Voice output (text-to-speech)
- 📸 Multi-modal input (photos, videos)
- 🎨 Premium UI with glassmorphism and animations
- ⚡ **Real-time Updates** - Low-latency events via Socket.io
- 💾 **Redis Sessions** - Scalable, persistent session management
- 👤 **Provider Enrollment** - Conversational onboarding with AI
- 📊 **Provider Dashboard** - Leads view and offer management
- 📋 **Consumer Dashboard** - Request tracking and booking history
- ✅ **Auto-Verification** - Instant activation for basic services
- 📝 **Request Details** - Full lifecycle tracking with status timeline
- 🌟 **Provider Profiles** - Rich portfolios with photos and reviews
- ✏️ **Edit/Cancel Requests** - Consumer control with safeguards
- 🔒 **Enterprise-ready Security** - Clerk auth + Kong API Gateway

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
```

### Mobile App (Archive)

The legacy mobile interface in `/mobile` is built with Expo. It is currently archived as the project focuses on the PWA.

## Documentation

- [Project Overview](docs/project/overview.md)
- [Vision & Mission](docs/project/vision.md)
- [Roadmap](docs/project/roadmap.md)
- [API Documentation](docs/api/README.md)
- [Testing Guide](docs/testing/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Sprint 10 Summary](docs/project/sprint_10_summary.md) - Request Details & Provider Profiles
- [Sprint 9C Summary](docs/project/sprint_9c_summary.md) - Provider Enrollment
- [Security Audit](docs/security/audit_report.md)

## Project Structure

```
proxie/
├── docs/           # Documentation and specifications
├── src/            # Source code
├── web/            # Primary PWA (Vite + React)
├── mobile/         # Legacy Mobile App (Expo)
├── tests/          # Test suite
└── scripts/        # Utility scripts
```

## Technology Stack (Architecture 2.0)

- **UI**: Next.js 14, React, Tailwind CSS
- **AI**: LiteLLM (Gemini 2.5 + Claude 3.5 Fallback)
- **Backend**: Python, FastAPI, Celery, Temporal
- **Database**: PostgreSQL 16 (pgvector), Redis 7
- **Operating**: Kubernetes (GKE), Kong API Gateway

## Contributing

See [Contributing Guide](docs/guides/contributing.md) for details.

## License

[MIT License](LICENSE)

---

**Proxie** — *Your craft, represented.*
