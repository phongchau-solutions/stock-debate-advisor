# User Service

FastAPI-based microservice for user authentication and management with Firebase integration.

## Features

- RESTful API for user management
- Firebase authentication integration
- JWT token-based authentication
- User profile management
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
- Firebase project with Admin SDK credentials

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Update .env with your Firebase credentials
# Set FIREBASE_CREDENTIALS_PATH and FIREBASE_PROJECT_ID

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn app.main:app --reload --port 8005
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
- OpenAPI docs: http://localhost:8005/api/v1/docs
- ReDoc: http://localhost:8005/api/v1/redoc

## Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with Firebase token
- `POST /api/v1/auth/register` - Register new user with Firebase token

### Users
- `GET /api/v1/user` - Get current authenticated user
- `PUT /api/v1/user` - Update current user profile
- `GET /api/v1/user/{id}` - Get user by ID

### Health
- `GET /health` - Health check

## Authentication Flow

1. Client authenticates with Firebase (client-side)
2. Client receives Firebase ID token
3. Client sends Firebase token to `/auth/login` or `/auth/register`
4. Service verifies Firebase token with Firebase Admin SDK
5. Service issues JWT token for subsequent requests
6. Client includes JWT token in Authorization header for protected endpoints

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
docker build -t user-service:latest .

# Run container
docker run -p 8005:8080 --env-file .env user-service:latest
```

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase Admin SDK credentials JSON
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `SECRET_KEY` - JWT secret key
- `DEBUG` - Enable debug mode
- `CORS_ORIGINS` - Allowed CORS origins

## Architecture

```
user-service/
├── app/
│   ├── api/
│   │   ├── deps.py         # API dependencies (auth, db)
│   │   └── v1/
│   │       ├── auth.py     # Auth endpoints
│   │       └── users.py    # User endpoints
│   ├── crud/
│   │   └── user.py         # CRUD operations
│   ├── models/
│   │   └── user.py         # SQLAlchemy models
│   ├── schemas/
│   │   └── user.py         # Pydantic schemas
│   ├── services/
│   │   └── firebase.py     # Firebase integration
│   ├── db/
│   │   ├── base.py         # Database base
│   │   └── session.py      # DB session
│   ├── config.py           # Settings
│   └── main.py             # FastAPI app
├── tests/
│   ├── conftest.py         # Test fixtures
│   └── test_users.py       # User tests
├── alembic/                # Database migrations
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication in Firebase Console
3. Generate Admin SDK credentials:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file securely
4. Update `.env` with:
   - `FIREBASE_CREDENTIALS_PATH`: Path to the credentials JSON
   - `FIREBASE_PROJECT_ID`: Your Firebase project ID

## Stub Implementation

**Note**: The current implementation includes stub/mock responses for development purposes:

- Firebase token verification returns mock user data
- Authentication endpoints return mock JWT tokens
- User endpoints return mock user information

For production deployment:
1. Implement actual Firebase Admin SDK integration in `app/services/firebase.py`
2. Implement JWT token generation and validation
3. Connect CRUD operations to the database
4. Add proper error handling and validation
5. Configure Firebase credentials

## Security Considerations

- Never commit Firebase credentials to version control
- Use strong, randomly generated `SECRET_KEY` in production
- Enable HTTPS in production
- Implement rate limiting for authentication endpoints
- Add input validation and sanitization
- Implement proper logging and monitoring
- Use environment-specific configuration
