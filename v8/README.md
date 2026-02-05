# Stock Debate Advisor v8

AI-powered stock analysis platform with multi-agent debates.

## Architecture

- **Monorepo**: All code in one repository
- **Frontend**: React 18.3 (LTS) + TypeScript + Vite
- **Backend**: Python 3.12 + FastAPI microservices
- **AI**: Google ADK (Gemini models)
- **Database**: PostgreSQL + Redis
- **Infrastructure**: Firebase + Google Cloud

## Quick Start

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.12+
- Poetry 1.8+
- Docker & Docker Compose
- Just (command runner)

### Installation

```bash
# Install Just (if not installed)
# macOS: brew install just
# Linux: cargo install just
# Windows: choco install just

# Install all dependencies
just install

# Setup environment
just setup

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Development

```bash
# Start entire dev environment (all services + frontend)
just dev

# Or start individually:
just dev-frontend        # Frontend only
just dev-services        # All backend services
just dev-service debate-service  # Specific service
```

### Testing

```bash
# Run all tests
just test

# Run frontend tests only
pnpm test

# Run specific service tests
cd services/debate-service && poetry run pytest
```

### Building

```bash
# Build frontend
pnpm build

# Build Docker images for all services
just docker-build
```

## Project Structure

- `apps/` - Deployable applications (frontend, docs)
- `services/` - Backend microservices (Python)
- `packages/` - Shared TypeScript packages
- `libs/` - Shared Python libraries
- `infrastructure/` - IaC and Docker configs
- `scripts/` - Utility scripts
- `docs/` - Documentation

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React web application |
| Debate Service | 8001 | Debate lifecycle management |
| Data Service | 8002 | Stock data fetching & caching |
| AI Service | 8003 | Google ADK integration |
| Analytics Service | 8004 | Analytics & predictions |
| User Service | 8005 | User management |
| Notification Service | 8006 | Notifications |

## Documentation

- [Architecture](./ARCHITECTURE.md)
- [Firebase Architecture](./FIREBASE_ARCHITECTURE.md)
- [Zero Cost Strategy](./ZERO_COST_ARCHITECTURE.md)
- [Monorepo Structure](./MONOREPO_ARCHITECTURE.md)
- [Frontend Specification](./FRONTEND_SPECIFICATION.md)
- [Backend Specification](./BACKEND_SPECIFICATION.md)
- [Data Pipeline Specification](./DATA_PIPELINE_SPEC.md)
- [Development Plan](./DEVELOPMENT_PLAN.md)

## Development Workflow

1. **Create a feature branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Edit code in the appropriate workspace
3. **Test locally**: `just test`
4. **Build**: `just build`
5. **Commit**: `git commit -m "feat: your feature description"`
6. **Push**: `git push origin feature/your-feature`
7. **Create PR**: Open a pull request on GitHub

## Monorepo Commands

### Install Dependencies

```bash
# Install all dependencies (frontend + backend)
just install

# Install frontend only
pnpm install

# Install specific service
cd services/debate-service && poetry install
```

### Development

```bash
# Run frontend dev server
just dev-frontend

# Run all backend services
just dev-services

# Run specific service
just dev-service debate-service
```

### Testing

```bash
# Run all tests
just test

# Run frontend tests
pnpm test

# Run backend tests for specific service
cd services/ai-service && poetry run pytest
```

### Linting & Formatting

```bash
# Lint all code
just lint

# Format all code
just format
```

### Building

```bash
# Build all apps
just build

# Build Docker images
just docker-build
```

### Database Migrations

```bash
# Run all migrations
just migrate

# Create new migration for specific service
cd services/debate-service && poetry run alembic revision --autogenerate -m "migration message"
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- **Firebase**: API keys, project ID, auth domain
- **Google AI**: Gemini API key
- **Database**: PostgreSQL connection string
- **Redis**: Redis connection string
- **External APIs**: Alpha Vantage, Finnhub keys

## Technology Stack

### Frontend

- React 18.3 (LTS)
- TypeScript 5.3+
- Vite 5.0+
- Material Design 3 (@mui/material-nextgen)
- Font Awesome 7.0
- Tailwind CSS 3.4+
- TanStack Query (React Query)
- Zustand (state management)

### Backend

- Python 3.12
- FastAPI 0.110+
- FastCRUD 0.12+
- SQLAlchemy 2.0+
- Alembic (migrations)
- Pydantic 2.6+
- Uvicorn (ASGI server)

### AI/ML

- Google ADK (AI Development Kit)
- Gemini 1.5 Flash
- Gemini 1.5 Pro
- Gemini 2.0 Flash

### Infrastructure

- Firebase (Auth, Hosting, Functions, Firestore)
- Cloud Run (microservices)
- Cloud Composer (Airflow - data pipelines)
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- BigQuery (analytics)

### Development Tools

- Turborepo (build orchestration)
- pnpm (package management)
- Poetry (Python dependency management)
- Just (task runner)
- Docker & Docker Compose
- GitHub Actions (CI/CD)

## CI/CD

The project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline**: Runs on every PR (lint, test, build)
- **Deploy Frontend**: Deploys frontend to Vercel on merge to main
- **Deploy Services**: Deploys services to Railway/Cloud Run on merge to main

## Cost Optimization

The v8 architecture is designed to start at **$0/month** using free tiers:

- Vercel Free Tier (frontend)
- Firebase Free Tier (auth, database)
- Railway Free Tier (backend services)
- Neon PostgreSQL Free Tier
- Upstash Redis Free Tier
- Google AI Studio Free Tier
- GitHub Actions Free Tier

See [ZERO_COST_ARCHITECTURE.md](./ZERO_COST_ARCHITECTURE.md) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## License

MIT

## Support

For issues or questions:
- Check documentation in `docs/`
- Open an issue on GitHub
- Contact the team

---

**Version**: 8.0.0  
**Status**: In Development  
**Last Updated**: February 2026
