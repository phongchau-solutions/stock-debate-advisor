"""Validation utilities."""

import re
from typing import Optional


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format.

    Args:
        symbol: Stock symbol to validate

    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False

    # Stock symbols are typically 1-5 uppercase letters
    pattern = r"^[A-Z]{1,10}$"
    return bool(re.match(pattern, symbol.upper()))


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    # Basic email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input.

    Args:
        value: String to sanitize
        max_length: Maximum length (optional)

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    # Remove leading/trailing whitespace
    sanitized = value.strip()

    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def normalize_stock_symbol(symbol: str) -> str:
    """
    Normalize stock symbol to uppercase.

    Args:
        symbol: Stock symbol

    Returns:
        Normalized stock symbol
    """
    return sanitize_string(symbol).upper()
