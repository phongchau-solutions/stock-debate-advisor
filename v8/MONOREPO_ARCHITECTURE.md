# Stock Debate Advisor v8 - Monorepo Architecture

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026  
**Architecture:** Microservices Monorepo

---

## Monorepo Overview

### Technology Choices

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Monorepo Tool** | Turborepo | 2.0+ | Build orchestration |
| **Package Manager** | pnpm | 9.0+ | Fast, disk-efficient |
| **Frontend** | React (LTS) | 18.3+ | UI framework |
| **Backend** | Python | 3.14 | Services runtime |
| **Python Package Manager** | Poetry | 1.8+ | Dependency management |
| **Task Runner** | Just | 1.25+ | Command runner |

### Why Monorepo?

✅ **Single source of truth** - All code in one repository  
✅ **Atomic changes** - Update multiple services together  
✅ **Code sharing** - Shared libraries and types  
✅ **Consistent tooling** - Same linting, testing, building  
✅ **Easier refactoring** - Change interfaces across services  
✅ **Simplified CI/CD** - Single pipeline configuration  

---

## Repository Structure

```
stock-debate-advisor/
├── .github/                          # GitHub workflows
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy-frontend.yml
│   │   ├── deploy-services.yml
│   │   └── test.yml
│   └── dependabot.yml
│
├── apps/                             # Applications (deployable)
│   ├── frontend/                     # React frontend
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   └── docs/                         # Documentation site (optional)
│       ├── src/
│       ├── package.json
│       └── README.md
│
├── services/                         # Backend microservices (Python)
│   ├── debate-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── alembic/
│   │   ├── pyproject.toml
│   │   ├── poetry.lock
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── data-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── ai-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── analytics-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── user-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   └── notification-service/
│       ├── app/
│       ├── tests/
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── README.md
│
├── packages/                         # Shared packages (TypeScript)
│   ├── ui/                           # Shared UI components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── types/                        # Shared TypeScript types
│   │   ├── src/
│   │   │   ├── api.ts
│   │   │   ├── models.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── utils/                        # Shared utilities
│   │   ├── src/
│   │   │   ├── format.ts
│   │   │   ├── validation.ts
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── config/                       # Shared configurations
│       ├── eslint-config/
│       │   ├── index.js
│       │   └── package.json
│       ├── tsconfig/
│       │   ├── base.json
│       │   ├── react.json
│       │   └── package.json
│       └── tailwind-config/
│           ├── index.js
│           └── package.json
│
├── libs/                             # Shared Python libraries
│   ├── shared-models/                # Shared data models
│   │   ├── shared_models/
│   │   │   ├── __init__.py
│   │   │   ├── debate.py
│   │   │   ├── stock.py
│   │   │   └── user.py
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── shared-utils/                 # Shared utilities
│   │   ├── shared_utils/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   ├── cache.py
│   │   │   └── validation.py
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── shared-db/                    # Shared database utilities
│       ├── shared_db/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── session.py
│       ├── tests/
│       ├── pyproject.toml
│       └── README.md
│
├── infrastructure/                   # Infrastructure as code
│   ├── terraform/
│   │   ├── modules/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   └── README.md
│   │
│   └── docker/
│       ├── docker-compose.yml
│       ├── docker-compose.dev.yml
│       └── README.md
│
├── scripts/                          # Utility scripts
│   ├── setup.sh
│   ├── dev.sh
│   ├── build.sh
│   ├── deploy.sh
│   └── migrate.py
│
├── docs/                             # Documentation
│   ├── architecture/
│   ├── api/
│   ├── guides/
│   └── README.md
│
├── .vscode/                          # VS Code workspace settings
│   ├── settings.json
│   ├── extensions.json
│   └── launch.json
│
├── .gitignore
├── .editorconfig
├── .prettierrc
├── .prettierignore
├── package.json                      # Root package.json
├── pnpm-workspace.yaml               # PNPM workspace config
├── turbo.json                        # Turborepo config
├── pyproject.toml                    # Root Python config
├── justfile                          # Task runner
└── README.md
```

---

## Configuration Files

### Root package.json

```json
{
  "name": "stock-debate-advisor",
  "version": "8.0.0",
  "private": true,
  "packageManager": "pnpm@9.0.0",
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,md}\"",
    "frontend:dev": "turbo run dev --filter=frontend",
    "services:dev": "just dev-services"
  },
  "devDependencies": {
    "@types/node": "^20.11.16",
    "prettier": "^3.2.5",
    "turbo": "^2.0.0",
    "typescript": "^5.3.3"
  },
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=9.0.0"
  }
}
```

### pnpm-workspace.yaml

```yaml
packages:
  # Applications
  - "apps/*"
  
  # Shared packages
  - "packages/*"
  - "packages/config/*"
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env"],
  "globalEnv": [
    "NODE_ENV",
    "VITE_FIREBASE_API_KEY",
    "VITE_FIREBASE_PROJECT_ID"
  ],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**", ".next/**"],
      "env": ["NODE_ENV"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts", "test/**/*.tsx"]
    },
    "lint": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "clean": {
      "cache": false
    }
  }
}
```

### Root pyproject.toml

```toml
[tool.poetry]
name = "stock-debate-advisor"
version = "8.0.0"
description = "Stock Debate Advisor - AI-powered stock analysis platform"
authors = ["Your Team <team@example.com>"]
readme = "README.md"
packages = []

[tool.poetry.dependencies]
python = "^3.14"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.4"
black = "^24.1.1"
flake8 = "^7.0.0"
mypy = "^1.8.0"
isort = "^5.13.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py314']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### justfile (Task Runner)

```makefile
# justfile - Command runner for monorepo

# Default recipe to display help information
default:
    @just --list

# Install all dependencies (frontend + backend)
install:
    @echo "Installing frontend dependencies..."
    pnpm install
    @echo "Installing Python dependencies..."
    cd services/debate-service && poetry install
    cd services/data-service && poetry install
    cd services/ai-service && poetry install
    cd services/analytics-service && poetry install
    cd services/user-service && poetry install
    cd services/notification-service && poetry install
    @echo "✓ All dependencies installed"

# Run frontend in development mode
dev-frontend:
    pnpm --filter frontend dev

# Run all backend services in development mode
dev-services:
    @echo "Starting all backend services..."
    docker-compose -f infrastructure/docker/docker-compose.dev.yml up

# Run specific service
dev-service SERVICE:
    cd services/{{SERVICE}} && poetry run uvicorn app.main:app --reload --port 8000

# Run database migrations for all services
migrate:
    @echo "Running migrations for all services..."
    cd services/debate-service && poetry run alembic upgrade head
    cd services/data-service && poetry run alembic upgrade head
    cd services/user-service && poetry run alembic upgrade head
    @echo "✓ All migrations complete"

# Run tests for all services
test:
    @echo "Running frontend tests..."
    pnpm test
    @echo "Running backend tests..."
    cd services/debate-service && poetry run pytest
    cd services/data-service && poetry run pytest
    cd services/ai-service && poetry run pytest
    cd services/analytics-service && poetry run pytest
    cd services/user-service && poetry run pytest
    cd services/notification-service && poetry run pytest

# Run linting for all code
lint:
    @echo "Linting frontend..."
    pnpm lint
    @echo "Linting backend..."
    cd services/debate-service && poetry run black . && poetry run flake8
    cd services/data-service && poetry run black . && poetry run flake8
    cd services/ai-service && poetry run black . && poetry run flake8

# Format all code
format:
    @echo "Formatting frontend..."
    pnpm format
    @echo "Formatting backend..."
    find services -name "*.py" -not -path "*/venv/*" -not -path "*/.venv/*" | xargs poetry run black

# Build all applications
build:
    pnpm build

# Build Docker images for all services
docker-build:
    @echo "Building Docker images..."
    docker build -t debate-service:latest -f services/debate-service/Dockerfile services/debate-service
    docker build -t data-service:latest -f services/data-service/Dockerfile services/data-service
    docker build -t ai-service:latest -f services/ai-service/Dockerfile services/ai-service
    docker build -t analytics-service:latest -f services/analytics-service/Dockerfile services/analytics-service
    docker build -t user-service:latest -f services/user-service/Dockerfile services/user-service
    docker build -t notification-service:latest -f services/notification-service/Dockerfile services/notification-service

# Clean all build artifacts and dependencies
clean:
    @echo "Cleaning..."
    pnpm clean
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "dist" -exec rm -rf {} +
    find . -type d -name "build" -exec rm -rf {} +
    @echo "✓ Cleaned"

# Setup development environment
setup:
    @echo "Setting up development environment..."
    @just install
    cp .env.example .env
    @echo "✓ Setup complete. Please update .env with your configuration."

# Start entire development environment
dev:
    @echo "Starting development environment..."
    docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d
    pnpm --filter frontend dev
```

---

## Workspace Examples

### Frontend App (apps/frontend/package.json)

```json
{
  "name": "frontend",
  "version": "8.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@mui/material": "^5.15.9",
    "@mui/material-nextgen": "^6.0.0",
    "@fortawesome/react-fontawesome": "^0.2.0",
    "@fortawesome/free-solid-svg-icons": "^6.5.1",
    "firebase": "^10.8.0",
    "@tanstack/react-query": "^5.20.5",
    "zustand": "^4.5.0",
    "react-router-dom": "^6.22.0",
    "@stock-debate/types": "workspace:*",
    "@stock-debate/ui": "workspace:*",
    "@stock-debate/utils": "workspace:*"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.1.0",
    "vitest": "^1.2.2",
    "@stock-debate/eslint-config": "workspace:*",
    "@stock-debate/tsconfig": "workspace:*"
  }
}
```

### Shared UI Package (packages/ui/package.json)

```json
{
  "name": "@stock-debate/ui",
  "version": "8.0.0",
  "private": true,
  "type": "module",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./components": "./src/components/index.ts",
    "./hooks": "./src/hooks/index.ts"
  },
  "scripts": {
    "lint": "eslint . --ext ts,tsx",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.3.1",
    "@mui/material": "^5.15.9",
    "@fortawesome/react-fontawesome": "^0.2.0",
    "@stock-debate/types": "workspace:*"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "typescript": "^5.3.3",
    "@stock-debate/eslint-config": "workspace:*",
    "@stock-debate/tsconfig": "workspace:*"
  },
  "peerDependencies": {
    "react": "^18.3.1"
  }
}
```

### Backend Service (services/debate-service/pyproject.toml)

```toml
[tool.poetry]
name = "debate-service"
version = "8.0.0"
description = "Debate Service - Manages debate lifecycle"
authors = ["Your Team <team@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.14"
fastapi = "^0.110.0"
fastcrud = "^0.12.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.27"}
alembic = "^1.13.1"
pydantic = "^2.6.1"
pydantic-settings = "^2.1.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
asyncpg = "^0.29.0"
httpx = "^0.26.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
# Local dependencies
shared-models = {path = "../../libs/shared-models", develop = true}
shared-utils = {path = "../../libs/shared-utils", develop = true}
shared-db = {path = "../../libs/shared-db", develop = true}

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.4"
pytest-cov = "^4.1.0"
black = "^24.1.1"
flake8 = "^7.0.0"
mypy = "^1.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Shared Python Library (libs/shared-models/pyproject.toml)

```toml
[tool.poetry]
name = "shared-models"
version = "8.0.0"
description = "Shared data models for all services"
authors = ["Your Team <team@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.14"
pydantic = "^2.6.1"
sqlalchemy = "^2.0.27"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## Docker Compose for Development

```yaml
# infrastructure/docker/docker-compose.dev.yml

version: '3.9'

services:
  # PostgreSQL database
  postgres:
    image: postgres:16
    container_name: stock-debate-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: stock_debate
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    container_name: stock-debate-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Debate Service
  debate-service:
    build:
      context: ../../services/debate-service
      dockerfile: Dockerfile
    container_name: debate-service
    ports:
      - "8001:8080"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/stock_debate
      - REDIS_URL=redis://redis:6379/0
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../../services/debate-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  # Data Service
  data-service:
    build:
      context: ../../services/data-service
      dockerfile: Dockerfile
    container_name: data-service
    ports:
      - "8002:8080"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/stock_debate
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../../services/data-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  # AI Service
  ai-service:
    build:
      context: ../../services/ai-service
      dockerfile: Dockerfile
    container_name: ai-service
    ports:
      - "8003:8080"
    environment:
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
      - REDIS_URL=redis://redis:6379/2
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ../../services/ai-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  # Analytics Service
  analytics-service:
    build:
      context: ../../services/analytics-service
      dockerfile: Dockerfile
    container_name: analytics-service
    ports:
      - "8004:8080"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/stock_debate
      - REDIS_URL=redis://redis:6379/3
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../../services/analytics-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  # User Service
  user-service:
    build:
      context: ../../services/user-service
      dockerfile: Dockerfile
    container_name: user-service
    ports:
      - "8005:8080"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/stock_debate
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ../../services/user-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

  # Notification Service
  notification-service:
    build:
      context: ../../services/notification-service
      dockerfile: Dockerfile
    container_name: notification-service
    ports:
      - "8006:8080"
    environment:
      - REDIS_URL=redis://redis:6379/4
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ../../services/notification-service:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

volumes:
  postgres_data:
  redis_data:
```

---

## VS Code Workspace Settings

```json
// .vscode/settings.json

{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  
  // Python settings
  "python.defaultInterpreterPath": "${workspaceFolder}/services/debate-service/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true,
  
  // Multi-root workspace folders
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/node_modules": true,
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.egg-info": true
  },
  
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/.venv": true,
    "**/venv": true
  }
}
```

```json
// .vscode/extensions.json

{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker",
    "tamasfe.even-better-toml"
  ]
}
```

---

## CI/CD Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Frontend
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Type check
        run: pnpm type-check
      
      - name: Lint
        run: pnpm lint
      
      - name: Test
        run: pnpm test
      
      - name: Build
        run: pnpm build

  # Backend Services
  backend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [debate-service, data-service, ai-service, analytics-service, user-service, notification-service]
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python 3.14
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        working-directory: services/${{ matrix.service }}
        run: poetry install
      
      - name: Lint
        working-directory: services/${{ matrix.service }}
        run: |
          poetry run black --check .
          poetry run flake8
          poetry run mypy .
      
      - name: Test
        working-directory: services/${{ matrix.service }}
        run: poetry run pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: services/${{ matrix.service }}/coverage.xml
          flags: ${{ matrix.service }}
```

---

## Root README.md

```markdown
# Stock Debate Advisor v8

AI-powered stock analysis platform with multi-agent debates.

## Architecture

- **Monorepo**: All code in one repository
- **Frontend**: React 18.3 (LTS) + TypeScript + Vite
- **Backend**: Python 3.14 + FastAPI microservices
- **AI**: Google ADK (Gemini models)
- **Database**: PostgreSQL + Redis
- **Infrastructure**: Firebase + Google Cloud

## Quick Start

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.14+
- Poetry 1.8+
- Docker & Docker Compose
- Just (command runner)

### Installation

```bash
# Install Just (if not installed)
# macOS: brew install just
# Linux: cargo install just

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

- [Architecture](./docs/architecture/README.md)
- [API Documentation](./docs/api/README.md)
- [Development Guide](./docs/guides/development.md)
- [Deployment Guide](./docs/guides/deployment.md)

## License

MIT
```

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Architecture:** Microservices Monorepo  
**Status:** Ready for Implementation
