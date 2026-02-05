# AI Service

FastAPI-based microservice for Google Gemini/OpenAI orchestration and multi-agent stock debates.

## Features

- Multi-agent debate orchestration
- Support for multiple AI providers:
  - Google Gemini
  - OpenAI GPT
  - Anthropic Claude
- Stock analysis with bull and bear agents
- Impartial judge for verdict decisions
- Async operations for scalability
- Extensible provider architecture

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry 1.8+
- PostgreSQL 16+ (optional, for storing debate history)
- Redis 7+ (optional, for caching)
- API keys for AI providers (Google, OpenAI, or Anthropic)

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# GOOGLE_API_KEY=your-google-api-key
# OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key

# Run database migrations (optional)
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --port 8003
```

### Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html
```

## API Documentation

Once running, visit:
- OpenAPI docs: http://localhost:8003/api/v1/docs
- ReDoc: http://localhost:8003/api/v1/redoc

## Endpoints

### Analysis
- `POST /api/v1/analyze` - Run stock debate analysis with bull and bear agents

### Judge
- `POST /api/v1/judge` - Get judge's verdict on a debate

### Agents
- `GET /api/v1/agents` - List available AI agents and configurations

### Health
- `GET /health` - Health check

## Usage Examples

### Analyze a Stock

```bash
curl -X POST http://localhost:8003/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "AAPL",
    "provider": "gemini"
  }'
```

### Judge a Debate

```bash
curl -X POST http://localhost:8003/api/v1/judge \
  -H "Content-Type: application/json" \
  -d '{
    "debate_id": "debate_123",
    "bull_argument": "AAPL has strong fundamentals...",
    "bear_argument": "AAPL is overvalued...",
    "provider": "openai"
  }'
```

### List Available Agents

```bash
curl http://localhost:8003/api/v1/agents
```

## AI Providers

### Google Gemini
- Model: `gemini-pro`
- Requires: `GOOGLE_API_KEY`
- Best for: Fast, cost-effective analysis

### OpenAI
- Model: `gpt-4-turbo-preview`
- Requires: `OPENAI_API_KEY`
- Best for: Detailed, nuanced analysis

### Anthropic Claude
- Model: `claude-3-opus-20240229`
- Requires: `ANTHROPIC_API_KEY`
- Best for: Balanced, thoughtful reasoning

## Architecture

```
ai-service/
├── app/
│   ├── api/
│   │   ├── deps.py              # API dependencies
│   │   └── v1/
│   │       ├── analyze.py       # Analysis endpoints
│   │       ├── judge.py         # Judge endpoints
│   │       └── agents.py        # Agent list endpoints
│   ├── services/
│   │   ├── providers/
│   │   │   ├── base.py          # Base provider interface
│   │   │   ├── gemini.py        # Google Gemini provider
│   │   │   ├── openai.py        # OpenAI provider
│   │   │   ├── claude.py        # Claude provider
│   │   │   └── factory.py       # Provider factory
│   │   └── orchestration/
│   │       └── debate.py        # Debate orchestrator
│   ├── schemas/
│   │   └── ai.py                # Pydantic schemas
│   ├── db/                      # Database (optional)
│   ├── config.py                # Settings
│   └── main.py                  # FastAPI app
├── tests/
│   ├── conftest.py              # Test fixtures
│   └── test_ai.py               # AI tests
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Development

### Adding a New Provider

1. Create a new provider class in `app/services/providers/`
2. Inherit from `AIProviderBase`
3. Implement required methods: `generate()`, `analyze_stock()`, `judge_debate()`
4. Add to provider factory in `factory.py`

### Code Quality

```bash
# Format code
poetry run black .
poetry run isort .

# Lint
poetry run flake8
poetry run mypy .
```

## Docker

```bash
# Build image
docker build -t ai-service:latest .

# Run container
docker run -p 8003:8080 --env-file .env ai-service:latest
```

## Environment Variables

See `.env.example` for all available configuration options:

- `GOOGLE_API_KEY` - Google Gemini API key
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `DEFAULT_AI_PROVIDER` - Default provider (gemini, openai, claude)
- `GEMINI_MODEL` - Gemini model name
- `OPENAI_MODEL` - OpenAI model name
- `CLAUDE_MODEL` - Claude model name

## Future Enhancements

- [ ] Persistent debate history in database
- [ ] Webhook notifications for debate completion
- [ ] Real-time streaming of agent responses
- [ ] Custom agent configurations per user
- [ ] Multi-turn debate conversations
- [ ] Integration with market data APIs
