# Shared Python Libraries

Shared Python libraries for backend microservices.

## Libraries

### shared-models
Common data models and Pydantic schemas.

### shared-utils
Utility functions (logging, caching, validation).

### shared-db
Database utilities and base models.

## Development

```bash
# Install library locally
cd libs/shared-models
poetry install

# Run tests
poetry run pytest

# Build package
poetry build
```

## Usage

In a service's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
shared-models = {path = "../../libs/shared-models", develop = true}
shared-utils = {path = "../../libs/shared-utils", develop = true}
shared-db = {path = "../../libs/shared-db", develop = true}
```

## Status

🚧 **In Development** - Structure created, implementation pending
