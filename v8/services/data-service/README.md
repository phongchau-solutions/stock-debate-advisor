# Data Service

FastAPI-based microservice for stock data APIs and caching.

## Features

- RESTful API for stock data management
- Stock information (symbol, name, sector, industry, etc.)
- Stock price history (OHLCV data)
- Company information endpoints
- Async database operations with SQLAlchemy 2.0
- Database migrations with Alembic
- FastCRUD for rapid CRUD operations
- Redis-ready caching layer
- Comprehensive testing with pytest

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry 1.8+
- PostgreSQL 16+
- Redis 7+ (optional, for caching)

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --port 8002
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
- OpenAPI docs: http://localhost:8002/api/v1/docs
- ReDoc: http://localhost:8002/api/v1/redoc

## Endpoints

### Stocks
- `POST /api/v1/stocks` - Create new stock
- `GET /api/v1/stocks/{symbol}` - Get stock by symbol
- `GET /api/v1/stocks` - List all stocks
- `DELETE /api/v1/stocks/{symbol}` - Delete stock

### Prices
- `POST /api/v1/price` - Create stock price entry
- `GET /api/v1/price/{symbol}` - Get price history for symbol
- `GET /api/v1/price/{symbol}/latest` - Get latest price for symbol

### Companies
- `GET /api/v1/company/{symbol}` - Get company information
- `GET /api/v1/company` - Search companies (filter by sector, industry)

### Health
- `GET /health` - Health check

## Development

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```

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
docker build -t data-service:latest .

# Run container
docker run -p 8002:8080 --env-file .env data-service:latest
```

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `DEBUG` - Enable debug mode
- `CACHE_TTL` - Cache time-to-live in seconds
- `CORS_ORIGINS` - Allowed CORS origins

## Architecture

```
data-service/
├── app/
│   ├── api/
│   │   ├── deps.py         # API dependencies (auth, db)
│   │   └── v1/
│   │       ├── stocks.py   # Stock endpoints
│   │       ├── prices.py   # Price endpoints
│   │       └── companies.py # Company endpoints
│   ├── crud/
│   │   └── stock.py        # CRUD operations
│   ├── models/
│   │   └── stock.py        # SQLAlchemy models
│   ├── schemas/
│   │   └── stock.py        # Pydantic schemas
│   ├── db/
│   │   ├── base.py         # Database base
│   │   └── session.py      # DB session
│   ├── config.py           # Settings
│   └── main.py             # FastAPI app
├── tests/
│   ├── conftest.py         # Test fixtures
│   └── test_stocks.py      # Stock tests
├── alembic/                # Database migrations
├── Dockerfile
├── pyproject.toml
└── README.md
```
