# Debate Service

FastAPI-based microservice for managing debate lifecycle and orchestration.

## Features

- RESTful API with FastAPI
- Async database operations with SQLAlchemy 2.0
- Database migrations with Alembic
- FastCRUD for rapid CRUD operations
- JWT authentication ready
- Comprehensive testing with pytest

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry 1.8+
- PostgreSQL 16+
- Redis 7+

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --port 8001
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
- OpenAPI docs: http://localhost:8001/api/v1/docs
- ReDoc: http://localhost:8001/api/v1/redoc

## Endpoints

- `POST /api/v1/debates` - Create new debate
- `GET /api/v1/debates/{id}` - Get debate details
- `GET /api/v1/debates` - List user debates
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
docker build -t debate-service:latest .

# Run container
docker run -p 8001:8080 --env-file .env debate-service:latest
```
