"""Test shared utils."""

from shared_utils.logging import get_logger, setup_logger
from shared_utils.validation import (
    normalize_stock_symbol,
    sanitize_string,
    validate_email,
    validate_stock_symbol,
)


def test_setup_logger():
    """Test logger setup."""
    logger = setup_logger("test-logger")
    assert logger is not None
    assert logger.name == "test-logger"


def test_get_logger():
    """Test getting logger instance."""
    logger = get_logger("test-logger-2")
    assert logger is not None
    assert logger.name == "test-logger-2"


def test_validate_stock_symbol():
    """Test stock symbol validation."""
    assert validate_stock_symbol("AAPL") is True
    assert validate_stock_symbol("MSFT") is True
    assert validate_stock_symbol("invalid") is False
    assert validate_stock_symbol("123") is False
    assert validate_stock_symbol("") is False


def test_validate_email():
    """Test email validation."""
    assert validate_email("user@example.com") is True
    assert validate_email("test.user@domain.co.uk") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@example.com") is False
    assert validate_email("") is False


def test_sanitize_string():
    """Test string sanitization."""
    assert sanitize_string("  hello  ") == "hello"
    assert sanitize_string("test", max_length=2) == "te"
    assert sanitize_string("") == ""


def test_normalize_stock_symbol():
    """Test stock symbol normalization."""
    assert normalize_stock_symbol("aapl") == "AAPL"
    assert normalize_stock_symbol("  msft  ") == "MSFT"
    assert normalize_stock_symbol("GOOGL") == "GOOGL"
