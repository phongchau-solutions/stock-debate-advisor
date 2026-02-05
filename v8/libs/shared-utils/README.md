# Shared Utils Library

Shared utility functions for logging, caching, and validation.

## Features

- **Logging utilities** - Consistent logging setup across services
- **Caching utilities** - Redis-based async caching
- **Validation utilities** - Common validation functions

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

### Logging

```python
from shared_utils.logging import setup_logger, get_logger

# Set up a logger
logger = setup_logger("my-service", level=logging.INFO)

# Get an existing logger
logger = get_logger("my-service")

logger.info("Service started")
logger.error("An error occurred")
```

### Caching

```python
from shared_utils.cache import CacheClient

# Initialize cache client
cache = CacheClient("redis://localhost:6379/0")
await cache.connect()

# Set a value
await cache.set("key", {"data": "value"}, ttl=3600)

# Get a value
value = await cache.get("key")

# Delete a value
await cache.delete("key")

# Check if key exists
exists = await cache.exists("key")

# Cleanup
await cache.disconnect()
```

### Validation

```python
from shared_utils.validation import (
    validate_stock_symbol,
    validate_email,
    sanitize_string,
    normalize_stock_symbol,
)

# Validate stock symbol
is_valid = validate_stock_symbol("AAPL")  # True
is_valid = validate_stock_symbol("invalid")  # False

# Validate email
is_valid = validate_email("user@example.com")  # True

# Sanitize string
clean = sanitize_string("  hello  ", max_length=10)  # "hello"

# Normalize stock symbol
symbol = normalize_stock_symbol("aapl")  # "AAPL"
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy shared_utils

# Linting
poetry run flake8 shared_utils
```
