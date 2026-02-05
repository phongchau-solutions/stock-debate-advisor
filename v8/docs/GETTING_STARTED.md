# Getting Started with Stock Debate Advisor v8

This guide will help you set up your development environment and start contributing to the project.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Node.js 20+**: [Download](https://nodejs.org/)
- **pnpm 9+**: `npm install -g pnpm@9`
- **Python 3.12+**: [Download](https://www.python.org/)
- **Poetry 1.8+**: [Installation Guide](https://python-poetry.org/docs/#installation)
- **Docker**: [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose**: Included with Docker Desktop

### Optional but Recommended

- **Just**: Task runner
  - macOS: `brew install just`
  - Linux: `cargo install just`
  - Windows: `choco install just`
- **VS Code**: [Download](https://code.visualstudio.com/)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/phongchau-solutions/stock-debate-advisor.git
cd stock-debate-advisor/v8
```

### 2. Install Dependencies

```bash
# Using Just (recommended)
just install

# Or manually:
pnpm install
cd services/debate-service && poetry install
cd ../data-service && poetry install
# ... repeat for other services
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required:
# - Firebase credentials
# - Google AI API key
# - Database connection strings
```

### 4. Set Up Firebase

1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com)
2. Enable Authentication (Email/Password, Google)
3. Create a Firestore database
4. Copy your Firebase configuration to `.env`

### 5. Get API Keys

- **Google AI**: [https://ai.google.dev](https://ai.google.dev) (Free tier available)
- **Alpha Vantage**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key) (Free)
- **Finnhub**: [https://finnhub.io](https://finnhub.io) (Free tier available)

## Running the Application

### Development Mode

#### Option 1: Using Just (Recommended)

```bash
# Start all services
just dev-services

# In another terminal, start frontend
just dev-frontend
```

#### Option 2: Using Docker Compose

```bash
# Start all backend services
docker-compose -f infrastructure/docker/docker-compose.dev.yml up

# In another terminal, start frontend
cd apps/frontend
pnpm dev
```

#### Option 3: Manual Start

```bash
# Terminal 1: Database services
docker-compose -f infrastructure/docker/docker-compose.dev.yml up postgres redis

# Terminal 2: Debate Service
cd services/debate-service
poetry run uvicorn app.main:app --reload --port 8001

# Terminal 3: Data Service
cd services/data-service
poetry run uvicorn app.main:app --reload --port 8002

# Terminal 4: Frontend
cd apps/frontend
pnpm dev
```

### Access the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Debate Service**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Data Service**: [http://localhost:8002/docs](http://localhost:8002/docs)

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit files in the appropriate workspace:
- Frontend: `apps/frontend/`
- Backend services: `services/*/`
- Shared packages: `packages/*/` or `libs/*/`

### 3. Test Your Changes

```bash
# Run all tests
just test

# Or test specific workspace
cd apps/frontend && pnpm test
cd services/debate-service && poetry run pytest
```

### 4. Lint and Format

```bash
# Lint all code
just lint

# Format all code
just format
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Common Tasks

### Database Migrations

```bash
# Create new migration
cd services/debate-service
poetry run alembic revision --autogenerate -m "add new table"

# Run migrations
just migrate
```

### Add New Dependency

**Frontend:**
```bash
cd apps/frontend
pnpm add package-name
```

**Backend Service:**
```bash
cd services/debate-service
poetry add package-name
```

### Build for Production

```bash
# Build frontend
cd apps/frontend
pnpm build

# Build Docker images
just docker-build
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart database
docker-compose -f infrastructure/docker/docker-compose.dev.yml restart postgres
```

### Poetry Installation Issues

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

### pnpm Installation Issues

```bash
# Clear pnpm cache
pnpm store prune

# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## Next Steps

- Read the [Architecture Documentation](../ARCHITECTURE.md)
- Explore the [API Documentation](../docs/api/)
- Check the [Development Plan](../DEVELOPMENT_PLAN.md)
- Join the team chat (if applicable)

## Getting Help

- Check existing documentation in `docs/`
- Search for existing GitHub issues
- Create a new GitHub issue
- Ask in team chat

## Resources

- [React Documentation](https://react.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Google AI Documentation](https://ai.google.dev/docs)
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Documentation](https://pnpm.io)
- [Poetry Documentation](https://python-poetry.org/docs)

---

**Need help?** Open an issue or contact the team!
