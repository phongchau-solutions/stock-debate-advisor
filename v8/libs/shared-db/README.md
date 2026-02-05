# Shared DB Library

Shared database utilities and base models for SQLAlchemy.

## Features

- Base model class for SQLAlchemy models
- Database engine and session management
- Async database session utilities

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

### Database Base Class

```python
from shared_db.base import Base
from sqlalchemy import Column, String

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
```

### Database Session

```python
from shared_db.session import create_db_engine, create_session_maker, get_db_session

# Create engine
engine = create_db_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/dbname",
    echo=True
)

# Create session maker
session_maker = create_session_maker(engine)

# Use in FastAPI dependency
from fastapi import Depends

async def get_db():
    async for session in get_db_session(session_maker):
        yield session

# Use in route
@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    # Use db session
    pass
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy shared_db

# Linting
poetry run flake8 shared_db
```
