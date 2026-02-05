# Backend Microservices

Python 3.12 + FastAPI microservices for Stock Debate Advisor.

## Services

### 1. Debate Service (Port 8001)
Manages debate lifecycle, orchestration, and results.

### 2. Data Service (Port 8002)
Fetches and caches stock market data.

### 3. AI Service (Port 8003)
Google ADK integration for multi-agent debates.

### 4. Analytics Service (Port 8004)
Advanced analytics and predictions.

### 5. User Service (Port 8005)
User management and profiles.

### 6. Notification Service (Port 8006)
Multi-channel notifications.

## Development

```bash
# Install dependencies for a service
cd services/debate-service
poetry install

# Run service
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run flake8
```

## Technology Stack

- Python 3.12
- FastAPI 0.110+
- FastCRUD 0.12+
- SQLAlchemy 2.0+
- Alembic (migrations)
- Pydantic 2.6+
- Google ADK (Gemini)

## Structure

Each service follows this structure:

```
service-name/
├── app/
│   ├── api/        # API routes
│   ├── crud/       # CRUD operations
│   ├── models/     # SQLAlchemy models
│   ├── schemas/    # Pydantic schemas
│   ├── services/   # Business logic
│   └── main.py     # FastAPI app
├── tests/          # Tests
├── alembic/        # Migrations
├── Dockerfile      # Docker image
└── pyproject.toml  # Dependencies
```

## Status

🚧 **In Development** - Structure created, implementation pending
