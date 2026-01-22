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
