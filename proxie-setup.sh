#!/bin/bash

# ============================================================================
# Proxie Project Setup Script
# ============================================================================
# This script creates the complete folder structure and initial files
# for the Proxie project.
#
# Usage:
#   1. Create a new directory or clone your empty GitHub repo
#   2. cd into that directory
#   3. Run: bash proxie-setup.sh
#
# ============================================================================

set -e  # Exit on error

echo "🚀 Setting up Proxie project structure..."
echo ""

# ============================================================================
# Create Directory Structure
# ============================================================================

echo "📁 Creating directories..."

# Documentation
mkdir -p docs/project
mkdir -p docs/schemas
mkdir -p docs/agents
mkdir -p docs/api
mkdir -p docs/guides

# Source code
mkdir -p src/platform/models
mkdir -p src/platform/schemas
mkdir -p src/platform/routers
mkdir -p src/platform/services
mkdir -p src/agents/consumer
mkdir -p src/agents/provider
mkdir -p src/mcp

# Tests
mkdir -p tests/test_agents
mkdir -p tests/test_mcp

# Scripts
mkdir -p scripts

# Research
mkdir -p research/interviews/notes

# Pilot
mkdir -p pilot

# IDE configurations
mkdir -p .antigravity/skills
mkdir -p .cursor

echo "✅ Directories created"
echo ""

# ============================================================================
# Root Level Files
# ============================================================================

echo "📄 Creating root files..."

# README.md
cat > README.md << 'EOF'
# Proxie

**Your agent. Your proxy. Your craft, represented.**

Proxie is an agent-native platform that connects skilled individual service providers with consumers through AI agents. No websites, no social media, no marketing hustle. Just skills, fairly represented.

## Vision

A world where consumer agents and provider agents negotiate and transact on behalf of humans — accessible only through AI interfaces. Humans describe needs. Humans do the work. Everything in between is agent-to-agent.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- An Anthropic API key

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
pytest tests/
```

## Documentation

- [Project Overview](docs/project/overview.md)
- [Vision & Mission](docs/project/vision.md)
- [Data Schemas](docs/schemas/)
- [Agent Specifications](docs/agents/)
- [API Documentation](docs/api/)

## Project Structure

```
proxie/
├── docs/           # Documentation and specifications
├── src/            # Source code
│   ├── platform/   # Core backend services
│   ├── agents/     # Consumer and provider agents
│   └── mcp/        # MCP server for external agents
├── tests/          # Test suite
├── scripts/        # Utility scripts
├── research/       # User research and validation
└── pilot/          # Pilot program tracking
```

## Technology Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL with pgvector
- **LLM**: Claude API (Anthropic)
- **Agent Protocol**: MCP (Model Context Protocol)

## Contributing

See [Contributing Guide](docs/guides/contributing.md) for details.

## License

[MIT License](LICENSE)

---

**Proxie** — *Your craft, represented.*
EOF

# LICENSE (MIT)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Proxie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# .gitignore
cat > .gitignore << 'EOF'
# ============================================================================
# Environment
# ============================================================================
.env
.env.local
.env.*.local

# ============================================================================
# Python
# ============================================================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# Pytest
.pytest_cache/
.coverage
htmlcov/

# ============================================================================
# IDEs and Editors
# ============================================================================
.idea/
.vscode/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# ============================================================================
# OS Files
# ============================================================================
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ============================================================================
# Project Specific
# ============================================================================
# Research notes (keep private)
research/interviews/notes/*
!research/interviews/notes/.gitkeep

# Database files
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Media uploads (local development)
uploads/

# ============================================================================
# Secrets and Credentials
# ============================================================================
*.pem
*.key
credentials.json
token.json
EOF

# .env.example
cat > .env.example << 'EOF'
# ============================================================================
# Proxie Environment Configuration
# ============================================================================
# Copy this file to .env and fill in your values
# NEVER commit .env to version control
# ============================================================================

# ----------------------------------------------------------------------------
# Environment
# ----------------------------------------------------------------------------
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------
DATABASE_URL=postgresql://proxie_user:your_password@localhost:5432/proxie_db

# ----------------------------------------------------------------------------
# LLM Configuration
# ----------------------------------------------------------------------------
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ----------------------------------------------------------------------------
# Server Configuration
# ----------------------------------------------------------------------------
HOST=0.0.0.0
PORT=8000

# ----------------------------------------------------------------------------
# Security
# ----------------------------------------------------------------------------
SECRET_KEY=your-secret-key-change-in-production
API_KEY_HEADER=X-API-Key

# ----------------------------------------------------------------------------
# MCP Server
# ----------------------------------------------------------------------------
MCP_SERVER_NAME=proxie
MCP_SERVER_VERSION=0.1.0
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
# ============================================================================
# Proxie Dependencies
# ============================================================================

# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.25
psycopg2-binary>=2.9.9
alembic>=1.13.1
pgvector>=0.2.4

# Validation
pydantic>=2.5.3
pydantic-settings>=2.1.0
email-validator>=2.1.0

# LLM
anthropic>=0.18.0

# MCP
mcp>=0.1.0

# Async
httpx>=0.26.0
aiofiles>=23.2.1

# Utilities
python-dotenv>=1.0.0
python-dateutil>=2.8.2

# Testing
pytest>=7.4.4
pytest-asyncio>=0.23.3
pytest-cov>=4.1.0
httpx>=0.26.0

# Development
black>=24.1.0
isort>=5.13.2
mypy>=1.8.0
ruff>=0.1.14
EOF

# pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "proxie"
version = "0.1.0"
description = "Agent-native platform connecting skilled service providers with consumers"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Proxie Team"}
]
keywords = ["ai", "agents", "services", "mcp", "marketplace"]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | __pycache__
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip = [".venv", "__pycache__"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: pgvector/pgvector:pg16
    container_name: proxie_db
    environment:
      POSTGRES_USER: proxie_user
      POSTGRES_PASSWORD: proxie_password
      POSTGRES_DB: proxie_db
    ports:
      - "5432:5432"
    volumes:
      - proxie_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U proxie_user -d proxie_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Proxie API Server (for production-like local dev)
  api:
    build: .
    container_name: proxie_api
    environment:
      - DATABASE_URL=postgresql://proxie_user:proxie_password@db:5432/proxie_db
      - ENVIRONMENT=development
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
    command: uvicorn src.platform.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  proxie_db_data:
EOF

echo "✅ Root files created"
echo ""

# ============================================================================
# Documentation Files
# ============================================================================

echo "📄 Creating documentation files..."

# docs/project/vision.md
cat > docs/project/vision.md << 'EOF'
# Proxie Vision & Mission

## Mission Statement

Eliminate the digital tax on skilled work. Let anyone with a skill be discovered and hired through AI agents. No website, no social media, no algorithm games. Just their craft, fairly represented.

## Vision Statement

A world where consumer agents and provider agents negotiate and transact on behalf of humans — accessible only through AI interfaces. Humans describe needs. Humans do the work. Everything in between is agent-to-agent.

## Core Principles

### Agent-First
The primary interface is conversational, not a traditional UI. Both providers and consumers interact through agents.

### Interoperable
External agents (Claude, ChatGPT, Gemini, personal assistants) can query the platform. Proxie is infrastructure, not a walled garden.

### Provider-Owned Data
Providers control their information. They can export it, delete it, take it elsewhere.

### Trust as a Layer
Verification, reputation, and safety are built into the core, not bolted on.

### Simplicity
Launch small (one vertical, one city) and scale without rewriting everything.

## The World We Want to Create

**Skill matters more than marketing.** The best provider gets found because they are the best, not because they figured out hashtags.

**Individuals can thrive independently.** You do not need to join a gig platform that takes 30% and treats you as replaceable. You own your reputation, your data, your client relationships.

**Access to quality services is democratized.** Anyone can find a trustworthy, skilled person for what they need, not just people who know how to navigate Yelp or have friends to ask.

**Dignity is restored to service work.** The plumber, the nanny, the photographer: they are not gig workers grinding for ratings. They are skilled professionals, represented properly, valued for their craft.

## Our Role

Proxie is not a gig company. We do not employ anyone. We do not take a cut of labor. We are infrastructure. We are the layer that lets skilled individuals exist in the agentic economy without becoming tech-savvy marketers. We represent them, so they can focus on what they are good at.

## Elevator Pitch

> "Proxie connects skilled workers with people who need them through AI agents, not websites or ads. Describe your need, get matched instantly. Your craft is your only marketing."
EOF

# docs/project/overview.md
cat > docs/project/overview.md << 'EOF'
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

## Technology Stack

- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL with pgvector
- **LLM**: Claude API (Anthropic)
- **Agent Protocol**: MCP (Model Context Protocol)
- **Interface**: AI-native only (no traditional web UI)

## Success Metrics

| Metric | Target |
|--------|--------|
| Providers onboarded | 10-20 |
| Consumers activated | 20-30 |
| Transactions completed | 20+ |
| Time to book | Under 5 minutes |
| Satisfaction | 80%+ |

## Project Phases

1. **Foundation** (Weeks 1-4): Define schemas, design agents, validate
2. **Core Build** (Weeks 5-10): Build platform, agents, MCP server
3. **Pilot** (Weeks 11-14): Real providers, real consumers, real transactions
4. **Iterate** (Weeks 15-18): Learn and improve
5. **Expand** (Week 19+): Scale what works

---

See [vision.md](vision.md) for mission and principles.
See [roadmap.md](roadmap.md) for detailed timeline.
EOF

# docs/project/roadmap.md
cat > docs/project/roadmap.md << 'EOF'
# Proxie Roadmap

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Define the Core
- [ ] Finalize service categories for MVP
- [ ] Define geographic scope
- [ ] Document service request schema
- [ ] Document offer schema
- [ ] Document booking schema

### Week 2: Design the Agents
- [ ] Consumer agent specification
- [ ] Provider agent specification
- [ ] Conversation flows
- [ ] Edge cases identified

### Week 3: Design the Platform
- [ ] Complete data model
- [ ] MCP interface specification
- [ ] Matching algorithm design
- [ ] Trust framework v1

### Week 4: Validate
- [ ] Interview 10+ potential providers
- [ ] Interview 10+ potential consumers
- [ ] Refine based on feedback
- [ ] Go/no-go decision

## Phase 2: Core Build (Weeks 5-10)

### Weeks 5-6: Data Layer
- [ ] Set up PostgreSQL database
- [ ] Implement database models
- [ ] Provider registration flow
- [ ] Portfolio storage (S3)

### Weeks 7-8: Agent Runtime
- [ ] Consumer agent implementation
- [ ] Provider agent implementation
- [ ] Agent-to-platform communication
- [ ] Provider rules engine

### Week 9: Service Request Hub
- [ ] Request ingestion
- [ ] Matching engine
- [ ] Offer aggregation
- [ ] Booking confirmation

### Week 10: MCP Interface
- [ ] MCP server implementation
- [ ] Authentication
- [ ] Documentation
- [ ] Test with Claude

## Phase 3: Pilot (Weeks 11-14)

### Week 11: Recruit Providers
- [ ] Identify 10-20 hairstylists
- [ ] Onboard via agent
- [ ] Verify quality
- [ ] Train on system

### Week 12: Recruit Consumers
- [ ] Identify 20-30 early consumers
- [ ] Onboard to AI interface
- [ ] Set expectations

### Weeks 13-14: Live Transactions
- [ ] Facilitate real bookings
- [ ] Monitor end-to-end flow
- [ ] Support both sides
- [ ] Collect feedback
- [ ] Track metrics

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
| Schemas defined | Week 1 | ⬜ |
| Agents designed | Week 2 | ⬜ |
| User validation complete | Week 4 | ⬜ |
| MVP code complete | Week 10 | ⬜ |
| First real booking | Week 13 | ⬜ |
| Pilot complete | Week 14 | ⬜ |
| Ready to scale | Week 18 | ⬜ |
EOF

# docs/schemas/provider.md
cat > docs/schemas/provider.md << 'EOF'
# Provider Schema

## Overview

A Provider represents a skilled individual offering services through Proxie.

## Schema Definition

```yaml
Provider:
  id: uuid                      # Unique identifier
  created_at: datetime          # When registered
  updated_at: datetime          # Last modified
  
  # Identity
  name: string                  # Display name
  email: string                 # Contact email (private)
  phone: string                 # Contact phone (private)
  verified: boolean             # Identity verified
  
  # Profile
  bio: text                     # About the provider
  profile_photo_url: string     # Profile image
  
  # Location
  location:
    address: string             # Full address (private)
    city: string                # City
    neighborhood: string        # Neighborhood/area
    coordinates:                # For distance calculations
      lat: float
      lng: float
    service_radius_km: float    # How far they'll travel
  
  # Services (for hairstylist MVP)
  services:
    - id: uuid
      name: string              # e.g., "Curly Hair Cut"
      description: text
      duration_minutes: int
      price_min: decimal
      price_max: decimal
      currency: string          # Default: USD
  
  # Specializations
  specializations: string[]     # e.g., ["curly hair", "coloring", "braids"]
  
  # Portfolio
  portfolio:
    - id: uuid
      image_url: string
      caption: string
      service_id: uuid          # Which service this showcases
      created_at: datetime
  
  # Availability
  availability:
    timezone: string            # e.g., "America/New_York"
    schedule:                   # Weekly recurring schedule
      monday: [{start: "10:00", end: "18:00"}]
      tuesday: [{start: "10:00", end: "18:00"}]
      # ...
    exceptions: []              # Date-specific overrides
  
  # Settings
  settings:
    auto_accept: boolean        # Auto-accept matching requests
    min_notice_hours: int       # Minimum booking notice
    max_bookings_per_day: int
    instant_booking: boolean    # Allow instant booking
  
  # Reputation
  reputation:
    rating: float               # Average rating (1-5)
    review_count: int
    completed_bookings: int
    response_rate: float        # % of inquiries responded to
    response_time_hours: float  # Average response time
  
  # Status
  status: enum                  # active, paused, inactive
```

## Example

```json
{
  "id": "prov_abc123",
  "name": "Maya Johnson",
  "bio": "Curly hair specialist with 8 years of experience. I believe every curl is unique and deserves personalized care.",
  "location": {
    "city": "Brooklyn",
    "neighborhood": "Bed-Stuy",
    "service_radius_km": 5
  },
  "services": [
    {
      "name": "Curly Hair Cut",
      "description": "Dry cut technique for natural curls",
      "duration_minutes": 60,
      "price_min": 60,
      "price_max": 80
    }
  ],
  "specializations": ["curly hair", "natural hair", "dry cutting"],
  "reputation": {
    "rating": 4.9,
    "review_count": 47
  },
  "status": "active"
}
```

## Notes

- Phone and full address are kept private; only shared after booking confirmation
- Portfolio images stored in S3, URLs are pre-signed
- Availability is stored in provider's local timezone
- Reputation metrics are calculated, not directly editable
EOF

# docs/schemas/service-request.md
cat > docs/schemas/service-request.md << 'EOF'
# Service Request Schema

## Overview

A Service Request represents a consumer's need, parsed and structured by the consumer agent.

## Schema Definition

```yaml
ServiceRequest:
  id: uuid                      # Unique identifier
  created_at: datetime
  updated_at: datetime
  
  # Consumer
  consumer_id: uuid             # Who is requesting
  consumer_agent_id: string     # Which agent created this
  
  # Original Input
  raw_input: text               # Original natural language request
  
  # Parsed Request
  service_category: string      # e.g., "hairstylist"
  service_type: string          # e.g., "haircut"
  
  # Requirements
  requirements:
    specializations: string[]   # e.g., ["curly hair"]
    description: text           # Additional details
  
  # Location
  location:
    city: string
    neighborhood: string        # Optional
    coordinates:                # Optional, for distance
      lat: float
      lng: float
    max_distance_km: float      # How far consumer will travel
  
  # Timing
  timing:
    urgency: enum               # asap, flexible, specific_date
    preferred_dates: date[]     # Specific dates if provided
    preferred_times: string[]   # e.g., ["morning", "afternoon"]
    flexibility: text           # Any notes about flexibility
  
  # Budget
  budget:
    min: decimal
    max: decimal
    currency: string
    flexibility: enum           # strict, somewhat_flexible, flexible
  
  # Status
  status: enum                  # pending, matching, offers_received, 
                                # booked, expired, cancelled
  
  # Matching Results
  matched_providers: uuid[]     # Providers who received this request
  offers: uuid[]                # Offers received
  selected_offer: uuid          # Accepted offer (if any)
```

## Example

```json
{
  "id": "req_xyz789",
  "raw_input": "I need a haircut. I have curly hair and I'm looking for someone who really knows how to work with curls. I'm in Brooklyn, hoping for this weekend, budget around $60-80.",
  "service_category": "hairstylist",
  "service_type": "haircut",
  "requirements": {
    "specializations": ["curly hair"],
    "description": "Looking for someone experienced with curls"
  },
  "location": {
    "city": "Brooklyn",
    "max_distance_km": 10
  },
  "timing": {
    "urgency": "specific_date",
    "preferred_dates": ["2026-01-24", "2026-01-25"],
    "preferred_times": ["morning", "afternoon"],
    "flexibility": "This weekend preferred"
  },
  "budget": {
    "min": 60,
    "max": 80,
    "currency": "USD",
    "flexibility": "somewhat_flexible"
  },
  "status": "matching"
}
```

## Parsing Guidelines

The consumer agent should extract:

1. **Service type** - What do they need done?
2. **Specializations** - Any specific requirements?
3. **Location** - Where are they?
4. **Timing** - When do they need it?
5. **Budget** - What can they pay?

If any field is unclear, the agent should ask clarifying questions.
EOF

# docs/schemas/offer.md
cat > docs/schemas/offer.md << 'EOF'
# Offer Schema

## Overview

An Offer is a provider agent's response to a service request.

## Schema Definition

```yaml
Offer:
  id: uuid
  created_at: datetime
  expires_at: datetime          # When offer expires
  
  # References
  request_id: uuid              # The service request
  provider_id: uuid             # Who is offering
  
  # Proposed Service
  service_id: uuid              # Which of provider's services
  service_name: string          # Human-readable name
  
  # Availability
  available_slots:
    - date: date
      start_time: time
      end_time: time
  
  # Pricing
  price: decimal
  currency: string
  price_notes: text             # Any conditions or notes
  
  # Provider Info (snapshot)
  provider_snapshot:
    name: string
    rating: float
    review_count: int
    portfolio_samples: string[] # 2-3 relevant images
  
  # Message
  message: text                 # Personal message from provider/agent
  
  # Status
  status: enum                  # pending, accepted, declined, expired, withdrawn
```

## Example

```json
{
  "id": "off_def456",
  "request_id": "req_xyz789",
  "provider_id": "prov_abc123",
  "service_name": "Curly Hair Cut",
  "available_slots": [
    {
      "date": "2026-01-24",
      "start_time": "14:00",
      "end_time": "15:00"
    },
    {
      "date": "2026-01-25",
      "start_time": "11:00",
      "end_time": "12:00"
    }
  ],
  "price": 70.00,
  "currency": "USD",
  "provider_snapshot": {
    "name": "Maya Johnson",
    "rating": 4.9,
    "review_count": 47,
    "portfolio_samples": [
      "https://..../curl1.jpg",
      "https://..../curl2.jpg"
    ]
  },
  "message": "I specialize in curly hair and would love to help! I use dry cutting techniques that work great for natural curls.",
  "status": "pending",
  "expires_at": "2026-01-23T18:00:00Z"
}
```

## Generation Rules

Provider agents generate offers based on:

1. **Match quality** - Does request match provider's specializations?
2. **Availability** - What slots are open?
3. **Pricing rules** - Provider's configured pricing
4. **Auto-accept settings** - Should this be auto-offered?

Offers expire after a configurable period (default: 24 hours).
EOF

# docs/schemas/booking.md
cat > docs/schemas/booking.md << 'EOF'
# Booking Schema

## Overview

A Booking represents a confirmed appointment between a consumer and provider.

## Schema Definition

```yaml
Booking:
  id: uuid
  created_at: datetime
  updated_at: datetime
  
  # References
  request_id: uuid              # Original request
  offer_id: uuid                # Accepted offer
  provider_id: uuid
  consumer_id: uuid
  
  # Service Details
  service_id: uuid
  service_name: string
  
  # Schedule
  scheduled_date: date
  scheduled_start: time
  scheduled_end: time
  timezone: string
  
  # Location
  location:
    type: enum                  # provider_location, consumer_location, other
    address: string             # Full address (revealed after booking)
    instructions: text          # Access notes, parking, etc.
  
  # Pricing
  price: decimal
  currency: string
  
  # Status
  status: enum                  # confirmed, completed, cancelled, no_show
  
  # Cancellation (if applicable)
  cancellation:
    cancelled_at: datetime
    cancelled_by: enum          # consumer, provider
    reason: text
  
  # Completion (if applicable)
  completion:
    completed_at: datetime
    actual_duration_minutes: int
    final_price: decimal        # May differ from quoted
    notes: text
  
  # Review (if submitted)
  review_id: uuid
```

## Example

```json
{
  "id": "book_ghi789",
  "request_id": "req_xyz789",
  "offer_id": "off_def456",
  "provider_id": "prov_abc123",
  "consumer_id": "cons_jkl012",
  "service_name": "Curly Hair Cut",
  "scheduled_date": "2026-01-24",
  "scheduled_start": "14:00",
  "scheduled_end": "15:00",
  "timezone": "America/New_York",
  "location": {
    "type": "provider_location",
    "address": "123 Fulton St, Brooklyn, NY 11217",
    "instructions": "Ring buzzer 3B. Second floor."
  },
  "price": 70.00,
  "currency": "USD",
  "status": "confirmed"
}
```

## Status Transitions

```
confirmed → completed (service delivered)
confirmed → cancelled (by either party)
confirmed → no_show (consumer didn't show)
```

## Notifications

On booking confirmation:
- Consumer receives: provider contact, location, instructions
- Provider receives: consumer contact, appointment details
EOF

# docs/schemas/review.md
cat > docs/schemas/review.md << 'EOF'
# Review Schema

## Overview

A Review captures consumer feedback after a completed booking.

## Schema Definition

```yaml
Review:
  id: uuid
  created_at: datetime
  
  # References
  booking_id: uuid
  provider_id: uuid
  consumer_id: uuid
  
  # Rating
  rating: int                   # 1-5 stars
  
  # Feedback
  comment: text                 # Written review
  
  # Specific Ratings (optional)
  ratings_breakdown:
    quality: int                # 1-5
    punctuality: int            # 1-5
    communication: int          # 1-5
    value: int                  # 1-5
  
  # Visibility
  visible: boolean              # Public or hidden
  
  # Provider Response (optional)
  response:
    text: text
    responded_at: datetime
```

## Example

```json
{
  "id": "rev_mno345",
  "booking_id": "book_ghi789",
  "provider_id": "prov_abc123",
  "consumer_id": "cons_jkl012",
  "rating": 5,
  "comment": "Maya was amazing! She really understood my curls and gave me the best haircut I've had in years. Highly recommend!",
  "ratings_breakdown": {
    "quality": 5,
    "punctuality": 5,
    "communication": 5,
    "value": 5
  },
  "visible": true
}
```

## Collection Flow

After booking completion:

1. Consumer agent prompts: "How was your appointment with [Provider]?"
2. Consumer provides rating and optional comment
3. Review is stored and provider reputation is updated
4. Provider agent notifies provider of new review
5. Provider can optionally respond

## Reputation Calculation

Provider rating = weighted average of all reviews
- Recent reviews weighted more heavily
- Minimum 3 reviews before rating is displayed publicly
EOF

echo "✅ Documentation files created"
echo ""

# ============================================================================
# Source Code Files
# ============================================================================

echo "📄 Creating source code files..."

# src/platform/__init__.py
cat > src/platform/__init__.py << 'EOF'
"""Proxie Platform - Core backend services."""
EOF

# src/platform/main.py
cat > src/platform/main.py << 'EOF'
"""
Proxie API Server

Main entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.platform.config import settings

app = FastAPI(
    title="Proxie API",
    description="Agent-native platform for skilled service providers",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Proxie API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# Import and include routers
# from src.platform.routers import providers, requests, offers, bookings, reviews
# app.include_router(providers.router, prefix="/providers", tags=["providers"])
# app.include_router(requests.router, prefix="/requests", tags=["requests"])
# app.include_router(offers.router, prefix="/offers", tags=["offers"])
# app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
# app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
EOF

# src/platform/config.py
cat > src/platform/config.py << 'EOF'
"""
Configuration management for Proxie.

Loads settings from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://proxie_user:proxie_password@localhost:5432/proxie_db"
    
    # LLM
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    
    # MCP
    MCP_SERVER_NAME: str = "proxie"
    MCP_SERVER_VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
EOF

# src/platform/database.py
cat > src/platform/database.py << 'EOF'
"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.platform.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,
    max_overflow=10,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# src/platform/models/__init__.py
cat > src/platform/models/__init__.py << 'EOF'
"""Database models for Proxie."""

from src.platform.models.provider import Provider
from src.platform.models.service import Service
from src.platform.models.request import ServiceRequest
from src.platform.models.offer import Offer
from src.platform.models.booking import Booking
from src.platform.models.review import Review

__all__ = [
    "Provider",
    "Service", 
    "ServiceRequest",
    "Offer",
    "Booking",
    "Review",
]
EOF

# src/platform/models/provider.py
cat > src/platform/models/provider.py << 'EOF'
"""Provider model."""

from sqlalchemy import Column, String, Boolean, Float, Integer, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Provider(Base):
    """A skilled individual offering services."""
    
    __tablename__ = "providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Identity
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    verified = Column(Boolean, default=False)
    
    # Profile
    bio = Column(Text)
    profile_photo_url = Column(String(500))
    
    # Location (stored as JSON for flexibility)
    location = Column(JSON)
    
    # Specializations
    specializations = Column(JSON, default=list)
    
    # Availability (stored as JSON)
    availability = Column(JSON)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Reputation (calculated fields)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    completed_bookings = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active")
EOF

# src/platform/models/service.py
cat > src/platform/models/service.py << 'EOF'
"""Service model."""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Service(Base):
    """A service offered by a provider."""
    
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Provider reference
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    
    # Service details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer)
    
    # Pricing
    price_min = Column(Float)
    price_max = Column(Float)
    currency = Column(String(10), default="USD")
EOF

# src/platform/models/request.py
cat > src/platform/models/request.py << 'EOF'
"""Service Request model."""

from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class ServiceRequest(Base):
    """A consumer's service request."""
    
    __tablename__ = "service_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Consumer
    consumer_id = Column(UUID(as_uuid=True))
    consumer_agent_id = Column(String(255))
    
    # Original input
    raw_input = Column(Text)
    
    # Parsed request
    service_category = Column(String(100))
    service_type = Column(String(100))
    requirements = Column(JSON)
    location = Column(JSON)
    timing = Column(JSON)
    budget = Column(JSON)
    
    # Status
    status = Column(String(50), default="pending")
    
    # Results
    matched_providers = Column(JSON, default=list)
    selected_offer_id = Column(UUID(as_uuid=True))
EOF

# src/platform/models/offer.py
cat > src/platform/models/offer.py << 'EOF'
"""Offer model."""

from sqlalchemy import Column, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Offer(Base):
    """A provider's offer in response to a request."""
    
    __tablename__ = "offers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # References
    request_id = Column(UUID(as_uuid=True), ForeignKey("service_requests.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    
    # Offer details
    service_name = Column(String(255))
    available_slots = Column(JSON)
    price = Column(Float)
    currency = Column(String(10), default="USD")
    price_notes = Column(Text)
    
    # Provider snapshot
    provider_snapshot = Column(JSON)
    
    # Message
    message = Column(Text)
    
    # Status
    status = Column(String(50), default="pending")
EOF

# src/platform/models/booking.py
cat > src/platform/models/booking.py << 'EOF'
"""Booking model."""

from sqlalchemy import Column, String, Float, Date, Time, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Booking(Base):
    """A confirmed appointment."""
    
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # References
    request_id = Column(UUID(as_uuid=True), ForeignKey("service_requests.id"))
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id"))
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    consumer_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Service
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))
    service_name = Column(String(255))
    
    # Schedule
    scheduled_date = Column(Date, nullable=False)
    scheduled_start = Column(Time, nullable=False)
    scheduled_end = Column(Time)
    timezone = Column(String(50))
    
    # Location
    location = Column(JSON)
    
    # Pricing
    price = Column(Float)
    currency = Column(String(10), default="USD")
    
    # Status
    status = Column(String(50), default="confirmed")
    
    # Cancellation details
    cancellation = Column(JSON)
    
    # Completion details
    completion = Column(JSON)
EOF

# src/platform/models/review.py
cat > src/platform/models/review.py << 'EOF'
"""Review model."""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.platform.database import Base


class Review(Base):
    """A consumer review of a provider."""
    
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # References
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    consumer_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    # Detailed ratings
    ratings_breakdown = Column(JSON)
    
    # Visibility
    visible = Column(Boolean, default=True)
    
    # Provider response
    response = Column(JSON)
EOF

# Create empty __init__.py files for other packages
touch src/platform/schemas/__init__.py
touch src/platform/routers/__init__.py
touch src/platform/services/__init__.py
touch src/agents/__init__.py
touch src/agents/consumer/__init__.py
touch src/agents/provider/__init__.py
touch src/mcp/__init__.py

echo "✅ Source code files created"
echo ""

# ============================================================================
# Test Files
# ============================================================================

echo "📄 Creating test files..."

# tests/__init__.py
touch tests/__init__.py

# tests/conftest.py
cat > tests/conftest.py << 'EOF'
"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from src.platform.main import app


@pytest.fixture
def client():
    """Test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_provider():
    """Sample provider data for testing."""
    return {
        "name": "Test Provider",
        "email": "test@example.com",
        "bio": "Test bio",
        "location": {
            "city": "Brooklyn",
            "neighborhood": "Bed-Stuy"
        },
        "specializations": ["curly hair"],
    }


@pytest.fixture
def sample_request():
    """Sample service request for testing."""
    return {
        "raw_input": "I need a haircut for curly hair in Brooklyn this weekend",
        "service_category": "hairstylist",
        "service_type": "haircut",
        "requirements": {
            "specializations": ["curly hair"]
        },
        "location": {
            "city": "Brooklyn"
        },
        "timing": {
            "urgency": "specific_date"
        },
        "budget": {
            "min": 60,
            "max": 80,
            "currency": "USD"
        }
    }
EOF

# tests/test_models.py
cat > tests/test_models.py << 'EOF'
"""Tests for database models."""

import pytest


def test_provider_model():
    """Test Provider model creation."""
    from src.platform.models import Provider
    
    provider = Provider(
        name="Test Provider",
        email="test@example.com"
    )
    
    assert provider.name == "Test Provider"
    assert provider.email == "test@example.com"
    assert provider.status == "active"


def test_service_request_model():
    """Test ServiceRequest model creation."""
    from src.platform.models import ServiceRequest
    
    request = ServiceRequest(
        raw_input="I need a haircut",
        service_category="hairstylist"
    )
    
    assert request.service_category == "hairstylist"
    assert request.status == "pending"
EOF

# tests/test_api.py
cat > tests/test_api.py << 'EOF'
"""Tests for API endpoints."""

import pytest


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Proxie API"
    assert data["status"] == "running"


def test_health(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
EOF

touch tests/test_agents/__init__.py
touch tests/test_agents/test_consumer_agent.py
touch tests/test_agents/test_provider_agent.py
touch tests/test_mcp/__init__.py
touch tests/test_mcp/test_tools.py

echo "✅ Test files created"
echo ""

# ============================================================================
# Script Files
# ============================================================================

echo "📄 Creating script files..."

# scripts/seed_data.py
cat > scripts/seed_data.py << 'EOF'
"""
Seed the database with sample data for development.
"""

import sys
sys.path.insert(0, '.')

from src.platform.database import SessionLocal, engine, Base
from src.platform.models import Provider, Service


def seed_providers():
    """Create sample providers."""
    
    providers = [
        {
            "name": "Maya Johnson",
            "email": "maya@example.com",
            "bio": "Curly hair specialist with 8 years of experience.",
            "location": {
                "city": "Brooklyn",
                "neighborhood": "Bed-Stuy",
                "service_radius_km": 5
            },
            "specializations": ["curly hair", "natural hair", "dry cutting"],
            "rating": 4.9,
            "review_count": 47,
            "status": "active"
        },
        {
            "name": "Dion Williams",
            "email": "dion@example.com",
            "bio": "Mobile stylist specializing in curly cutting techniques.",
            "location": {
                "city": "Brooklyn",
                "neighborhood": "Crown Heights",
                "service_radius_km": 10
            },
            "specializations": ["curly hair", "mobile service"],
            "rating": 4.7,
            "review_count": 28,
            "status": "active"
        },
    ]
    
    db = SessionLocal()
    try:
        for provider_data in providers:
            provider = Provider(**provider_data)
            db.add(provider)
        db.commit()
        print(f"✅ Created {len(providers)} sample providers")
    finally:
        db.close()


def main():
    """Run all seed functions."""
    print("🌱 Seeding database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Seed data
    seed_providers()
    
    print("✅ Database seeded successfully")


if __name__ == "__main__":
    main()
EOF

# scripts/migrate.py
cat > scripts/migrate.py << 'EOF'
"""
Database migration script.

For MVP, we use simple create_all. 
For production, use Alembic for proper migrations.
"""

import sys
sys.path.insert(0, '.')

from src.platform.database import engine, Base
from src.platform.models import *  # Import all models


def migrate():
    """Create all database tables."""
    print("🔄 Running migrations...")
    
    Base.metadata.create_all(bind=engine)
    
    print("✅ Migrations complete")


if __name__ == "__main__":
    migrate()
EOF

echo "✅ Script files created"
echo ""

# ============================================================================
# IDE Configuration Files
# ============================================================================

echo "📄 Creating IDE configuration files..."

# .antigravity/skills/proxie-patterns.md
cat > .antigravity/skills/proxie-patterns.md << 'EOF'
# Proxie Development Patterns

## Overview

This skill defines coding patterns and conventions for the Proxie project.

## Architecture

Proxie follows a layered architecture:

1. **API Layer** (`src/platform/routers/`) - FastAPI route handlers
2. **Service Layer** (`src/platform/services/`) - Business logic
3. **Model Layer** (`src/platform/models/`) - SQLAlchemy models
4. **Schema Layer** (`src/platform/schemas/`) - Pydantic validation

## Conventions

### File Naming
- Models: singular (`provider.py`, `booking.py`)
- Routers: plural (`providers.py`, `bookings.py`)
- Use snake_case for all Python files

### Code Style
- Line length: 100 characters
- Use type hints everywhere
- Document all public functions

### Database
- Use UUID for all primary keys
- Include `created_at` and `updated_at` on all models
- Store complex data as JSON when schema may evolve

### API Design
- RESTful endpoints
- Use Pydantic for request/response validation
- Return consistent error formats

## Agent Development

### Consumer Agent
- Parse natural language to structured requests
- Ask clarifying questions when ambiguous
- Present offers in a clear, comparable format

### Provider Agent
- Follow provider's rules strictly
- Never overcommit availability
- Keep provider informed of all bookings

## Testing

- Write tests for all business logic
- Use fixtures for common test data
- Mock external services (LLM, storage)
EOF

# .antigravity/rules.md
cat > .antigravity/rules.md << 'EOF'
# Proxie Project Rules

## Code Standards

- Python 3.11+ required
- Use type hints for all function signatures
- Format with Black (line length 100)
- Sort imports with isort
- Lint with Ruff

## Documentation

- All schemas are documented in `/docs/schemas/`
- Read the schema docs before implementing models
- Keep docs in sync with code

## Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user input with Pydantic

## Git

- Write clear commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic
EOF

# .cursor/rules.md
cat > .cursor/rules.md << 'EOF'
# Cursor Rules for Proxie

## Project Context

Proxie is an agent-native platform connecting service providers with consumers.
Read `/docs/project/overview.md` for full context.

## When Writing Code

1. Check `/docs/schemas/` for data structure definitions
2. Follow patterns in existing code
3. Add type hints to all functions
4. Write tests for new functionality

## Key Files

- Entry point: `src/platform/main.py`
- Config: `src/platform/config.py`
- Models: `src/platform/models/`

## Style

- Black formatting (100 char lines)
- isort for imports
- Ruff for linting
EOF

echo "✅ IDE configuration files created"
echo ""

# ============================================================================
# Research Files
# ============================================================================

echo "📄 Creating research files..."

# research/interviews/provider-questions.md
cat > research/interviews/provider-questions.md << 'EOF'
# Provider Interview Questions

## Background

1. What services do you offer?
2. How long have you been doing this work?
3. Do you work independently or for a business?

## Current Discovery

4. How do clients currently find you?
5. How much time do you spend on marketing/social media?
6. What's your biggest frustration with getting new clients?

## Handling Inquiries

7. How do potential clients typically contact you?
8. What questions do they usually ask?
9. How long does it take from first contact to booking?
10. What percentage of inquiries turn into bookings?

## Pricing & Availability

11. How do you currently share your pricing?
12. How do you manage your schedule/availability?
13. What tools do you use for booking?

## The Proxie Concept

14. [Explain Proxie] What's your initial reaction?
15. Would you trust an AI agent to answer questions on your behalf?
16. What information would you want the agent to have?
17. What would it NOT be allowed to do?
18. What would make you sign up for something like this?
19. What concerns do you have?

## Wrap Up

20. Is there anything else that would make your work life easier?
EOF

# research/interviews/consumer-questions.md
cat > research/interviews/consumer-questions.md << 'EOF'
# Consumer Interview Questions

## Background

1. When did you last hire a service provider (hairstylist, cleaner, etc.)?
2. What service was it for?

## Current Discovery

3. How did you find them?
4. How long did it take to find someone?
5. What was frustrating about the process?
6. How confident were you in your choice?

## Booking Process

7. How did you contact them?
8. How many back-and-forth messages did it take to book?
9. What information did you need before booking?

## Trust

10. What made you trust this provider?
11. What would have made you NOT book them?
12. How important are reviews to you?

## The Proxie Concept

13. [Explain Proxie] What's your initial reaction?
14. Would you trust an AI to find you a service provider?
15. Would you let an AI book on your behalf, or want final approval?
16. What information would you need to see before booking?
17. What concerns do you have?

## Wrap Up

18. What would make finding service providers easier for you?
EOF

# Create .gitkeep for notes folder
touch research/interviews/notes/.gitkeep

echo "✅ Research files created"
echo ""

# ============================================================================
# Pilot Files
# ============================================================================

echo "📄 Creating pilot files..."

# pilot/providers.md
cat > pilot/providers.md << 'EOF'
# Pilot Providers

## Target

10-20 hairstylists in [Location TBD]

## Recruitment Status

| Name | Specialty | Status | Onboarded | Notes |
|------|-----------|--------|-----------|-------|
| | | | | |

## Onboarding Checklist

- [ ] Initial conversation
- [ ] Explain Proxie concept
- [ ] Get verbal commitment
- [ ] Create profile via agent
- [ ] Upload portfolio
- [ ] Set availability
- [ ] Test booking flow
- [ ] Ready for pilot
EOF

# pilot/metrics.md
cat > pilot/metrics.md << 'EOF'
# Pilot Metrics

## Success Criteria

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Providers onboarded | 10-20 | | ⬜ |
| Consumers activated | 20-30 | | ⬜ |
| Transactions completed | 20+ | | ⬜ |
| Provider satisfaction | 80%+ | | ⬜ |
| Consumer satisfaction | 80%+ | | ⬜ |
| Time to book (avg) | <5 min | | ⬜ |
| Booking conversion | 50%+ | | ⬜ |

## Weekly Tracking

### Week 1
- Requests: 
- Matches: 
- Bookings: 
- Issues: 

### Week 2
- Requests: 
- Matches: 
- Bookings: 
- Issues: 
EOF

# pilot/feedback.md
cat > pilot/feedback.md << 'EOF'
# Pilot Feedback

## Provider Feedback

### Positive
- 

### Issues / Concerns
- 

### Feature Requests
- 

## Consumer Feedback

### Positive
- 

### Issues / Concerns
- 

### Feature Requests
- 

## Technical Issues

| Date | Issue | Severity | Resolution |
|------|-------|----------|------------|
| | | | |
EOF

echo "✅ Pilot files created"
echo ""

# ============================================================================
# API Documentation
# ============================================================================

echo "📄 Creating API documentation..."

# docs/api/mcp-interface.md
cat > docs/api/mcp-interface.md << 'EOF'
# MCP Interface Specification

## Overview

Proxie exposes an MCP (Model Context Protocol) server that allows external AI agents to interact with the platform.

## Server Info

```json
{
  "name": "proxie",
  "version": "0.1.0",
  "description": "Agent-native platform for skilled service providers"
}
```

## Tools

### Consumer-Side Tools

#### create_service_request

Create a new service request.

**Parameters:**
```json
{
  "raw_input": "string - Original natural language request",
  "service_category": "string - e.g., 'hairstylist'",
  "service_type": "string - e.g., 'haircut'",
  "requirements": {
    "specializations": ["string"],
    "description": "string"
  },
  "location": {
    "city": "string",
    "neighborhood": "string (optional)",
    "max_distance_km": "number (optional)"
  },
  "timing": {
    "urgency": "asap | flexible | specific_date",
    "preferred_dates": ["date"],
    "preferred_times": ["morning | afternoon | evening"]
  },
  "budget": {
    "min": "number",
    "max": "number",
    "currency": "string"
  }
}
```

**Returns:**
```json
{
  "request_id": "uuid",
  "status": "pending | matching",
  "message": "string"
}
```

#### get_offers

Get offers for a service request.

**Parameters:**
```json
{
  "request_id": "uuid"
}
```

**Returns:**
```json
{
  "offers": [
    {
      "offer_id": "uuid",
      "provider_name": "string",
      "service_name": "string",
      "available_slots": [...],
      "price": "number",
      "rating": "number",
      "review_count": "number",
      "portfolio_samples": ["url"]
    }
  ]
}
```

#### accept_offer

Accept an offer and create a booking.

**Parameters:**
```json
{
  "offer_id": "uuid",
  "selected_slot": {
    "date": "date",
    "start_time": "time"
  }
}
```

**Returns:**
```json
{
  "booking_id": "uuid",
  "status": "confirmed",
  "details": {...}
}
```

#### submit_review

Submit a review for a completed booking.

**Parameters:**
```json
{
  "booking_id": "uuid",
  "rating": "number (1-5)",
  "comment": "string (optional)"
}
```

### Provider-Side Tools

#### get_requests

Get service requests matching provider's profile.

#### submit_offer

Submit an offer for a service request.

#### confirm_booking

Confirm a booking.

#### update_availability

Update provider's availability.

---

## Authentication

MCP connections are authenticated via API key passed in the connection headers.

## Rate Limits

- 100 requests per minute per API key
- Bulk operations count as single request
EOF

# docs/api/internal-api.md
cat > docs/api/internal-api.md << 'EOF'
# Internal API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health

#### GET /
Health check.

#### GET /health
Detailed health check.

### Providers

#### GET /providers
List providers.

#### POST /providers
Create provider.

#### GET /providers/{id}
Get provider by ID.

#### PUT /providers/{id}
Update provider.

### Requests

#### POST /requests
Create service request.

#### GET /requests/{id}
Get request by ID.

#### GET /requests/{id}/offers
Get offers for request.

### Offers

#### POST /offers
Create offer.

#### PUT /offers/{id}/accept
Accept offer.

### Bookings

#### GET /bookings/{id}
Get booking by ID.

#### PUT /bookings/{id}/complete
Mark booking complete.

#### PUT /bookings/{id}/cancel
Cancel booking.

### Reviews

#### POST /reviews
Create review.

---

Full OpenAPI spec available at `/docs` when server is running.
EOF

# docs/guides/local-setup.md
cat > docs/guides/local-setup.md << 'EOF'
# Local Development Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or Docker)
- An Anthropic API key

## Quick Start with Docker

```bash
# Start PostgreSQL
docker-compose up -d db

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Anthropic API key

# Run migrations
python scripts/migrate.py

# Seed sample data (optional)
python scripts/seed_data.py

# Start the server
python -m src.platform.main
```

## Without Docker

1. Install PostgreSQL locally
2. Create database: `createdb proxie_db`
3. Update DATABASE_URL in .env
4. Follow remaining steps above

## Running Tests

```bash
pytest tests/
```

## Code Quality

```bash
# Format
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```
EOF

echo "✅ API documentation created"
echo ""

# ============================================================================
# Agent Documentation
# ============================================================================

echo "📄 Creating agent documentation..."

# docs/agents/consumer-agent.md
cat > docs/agents/consumer-agent.md << 'EOF'
# Consumer Agent Specification

## Overview

The Consumer Agent helps users find and book service providers by:
1. Understanding their natural language requests
2. Creating structured service requests
3. Presenting matched offers
4. Facilitating booking

## Capabilities

### 1. Parse Natural Language

**Input:** "I need a haircut for curly hair in Brooklyn this weekend"

**Output:**
```json
{
  "service_category": "hairstylist",
  "service_type": "haircut",
  "requirements": {"specializations": ["curly hair"]},
  "location": {"city": "Brooklyn"},
  "timing": {"preferred_dates": ["2026-01-24", "2026-01-25"]}
}
```

### 2. Ask Clarifying Questions

When information is missing or ambiguous:
- "What area of Brooklyn are you in?"
- "Do you have a budget in mind?"
- "Any time preferences - morning or afternoon?"

### 3. Present Offers

Format offers for easy comparison:
- Provider name and rating
- Availability that matches request
- Price
- Relevant portfolio samples
- Key differentiators

### 4. Handle Booking

- Confirm selection with user
- Submit acceptance to platform
- Share booking confirmation details

## Decision Logic

```
1. Receive user input
2. Parse intent and entities
3. If missing critical info → ask clarifying question
4. If complete → create service request
5. Wait for offers
6. Present offers to user
7. If user selects → accept offer
8. Confirm booking
```

## Prompts

See `src/agents/consumer/prompts.py` for LLM prompts.
EOF

# docs/agents/provider-agent.md
cat > docs/agents/provider-agent.md << 'EOF'
# Provider Agent Specification

## Overview

The Provider Agent represents a service provider by:
1. Receiving relevant service requests
2. Evaluating if they match provider's profile
3. Generating offers based on provider's rules
4. Confirming bookings

## Capabilities

### 1. Evaluate Requests

Check if request matches:
- Service category
- Specializations
- Location/service area
- Available dates/times
- Price range

### 2. Generate Offers

Based on provider's configuration:
- Check calendar for availability
- Calculate price based on service and rules
- Select relevant portfolio samples
- Compose personalized message

### 3. Follow Provider Rules

Respect provider settings:
- Auto-accept threshold
- Minimum notice time
- Maximum bookings per day
- Price ranges

### 4. Manage Bookings

- Confirm accepted offers
- Update provider's calendar
- Notify provider of new bookings

## Rules Engine

```python
def should_make_offer(request, provider):
    # Check service match
    if request.service_category not in provider.categories:
        return False
    
    # Check location
    if not is_in_service_area(request.location, provider.location):
        return False
    
    # Check availability
    if not has_available_slot(request.timing, provider.availability):
        return False
    
    # Check price fit
    if request.budget.max < provider.price_min:
        return False
    
    return True
```

## Prompts

See `src/agents/provider/prompts.py` for LLM prompts.
EOF

# docs/agents/matching-algorithm.md
cat > docs/agents/matching-algorithm.md << 'EOF'
# Matching Algorithm

## Overview

The matching algorithm connects service requests with relevant providers.

## Matching Pipeline

```
1. FILTER - Hard constraints (must match)
2. SCORE - Soft factors (ranking)
3. RANK - Order by score
4. ROUTE - Send to top N provider agents
```

## Filter Stage

Remove providers who don't meet basic requirements:

| Criterion | Logic |
|-----------|-------|
| Service category | Must offer the service |
| Location | Within service radius of request |
| Availability | Has slots matching request timing |
| Status | Must be "active" |

## Score Stage

Score remaining providers on fit:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Specialization match | 30% | % of requested specializations provider has |
| Distance | 20% | Closer is better |
| Availability fit | 20% | More matching slots is better |
| Rating | 15% | Higher is better |
| Price fit | 15% | Within budget scores higher |

## Rank Stage

Sort providers by total score, descending.

## Route Stage

Send request to top N providers (default: 10).

Provider agents then decide whether to make an offer.

## Future Improvements

- Semantic matching using embeddings
- Learning from booking patterns
- Provider preference learning
EOF

echo "✅ Agent documentation created"
echo ""

# ============================================================================
# Guides
# ============================================================================

# docs/guides/contributing.md
cat > docs/guides/contributing.md << 'EOF'
# Contributing to Proxie

## Getting Started

1. Fork the repository
2. Clone your fork
3. Set up local development (see [local-setup.md](local-setup.md))
4. Create a feature branch

## Development Workflow

1. Check existing issues or create a new one
2. Discuss approach in the issue
3. Implement changes
4. Write tests
5. Submit pull request

## Code Standards

- Follow existing patterns
- Add type hints
- Write docstrings
- Format with Black
- Pass all tests

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Request review

## Questions?

Open an issue for discussion.
EOF

# docs/guides/deployment.md
cat > docs/guides/deployment.md << 'EOF'
# Deployment Guide

## Prerequisites

- Docker
- A PostgreSQL database (or use managed service)
- Anthropic API key

## Environment Variables

Set these in your deployment environment:

```
ENVIRONMENT=production
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<generate-secure-key>
```

## Docker Deployment

```bash
# Build image
docker build -t proxie .

# Run
docker run -p 8000:8000 --env-file .env proxie
```

## Platform-Specific

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy

### Render

1. Create new Web Service
2. Connect repository
3. Set environment variables
4. Deploy

## Database Migrations

Run migrations before starting:

```bash
python scripts/migrate.py
```
EOF

echo "✅ Guide documentation created"
echo ""

# ============================================================================
# Final Steps
# ============================================================================

echo "🎉 Proxie project structure created successfully!"
echo ""
echo "Next steps:"
echo "  1. Review the generated files"
echo "  2. Initialize git: git init"
echo "  3. Create your GitHub repository"
echo "  4. Add remote: git remote add origin <your-repo-url>"
echo "  5. Commit and push: git add . && git commit -m 'Initial project structure' && git push -u origin main"
echo ""
echo "To start developing:"
echo "  1. Copy .env.example to .env and add your API keys"
echo "  2. Start PostgreSQL: docker-compose up -d db"
echo "  3. Install dependencies: pip install -r requirements.txt"
echo "  4. Run migrations: python scripts/migrate.py"
echo "  5. Start server: python -m src.platform.main"
echo ""
echo "📚 Read docs/project/overview.md for project context"
echo ""
