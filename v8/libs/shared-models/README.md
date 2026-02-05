# Shared Models Library

Common data models and Pydantic schemas for the Stock Debate Advisor platform.

## Features

- SQLAlchemy ORM models for database entities
- Pydantic schemas for API request/response validation
- Shared model definitions for:
  - Debates (debate lifecycle and status)
  - Stocks (stock information and prices)
  - Users (user profiles and authentication)

## Installation

```bash
# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .
```

## Usage

Import models in your service:

```python
from shared_models.debate import Debate, DebateCreate, DebateResponse, DebateStatus
from shared_models.stock import Stock, StockPrice, StockCreate, StockResponse
from shared_models.user import User, UserCreate, UserResponse
```

## Models

### Debate Models
- `Debate` - SQLAlchemy model for debates table
- `DebateCreate` - Schema for creating debates
- `DebateResponse` - Schema for debate API responses
- `DebateStatus` - Enum for debate statuses (PENDING, RUNNING, COMPLETED, FAILED)

### Stock Models
- `Stock` - SQLAlchemy model for stocks table
- `StockPrice` - SQLAlchemy model for stock prices table
- `StockCreate` - Schema for creating stock records
- `StockResponse` - Schema for stock API responses
- `StockPriceCreate` - Schema for creating price records
- `StockPriceResponse` - Schema for price API responses

### User Models
- `User` - SQLAlchemy model for users table
- `UserCreate` - Schema for creating users
- `UserUpdate` - Schema for updating users
- `UserResponse` - Schema for user API responses

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy shared_models

# Linting
poetry run flake8 shared_models
```
