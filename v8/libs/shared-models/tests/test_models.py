"""Test shared models."""

import pytest

from shared_models.debate import DebateCreate, DebateStatus
from shared_models.stock import StockCreate
from shared_models.user import UserCreate


def test_debate_create_schema():
    """Test DebateCreate schema validation."""
    debate = DebateCreate(stock_symbol="AAPL")
    assert debate.stock_symbol == "AAPL"


def test_debate_status_enum():
    """Test DebateStatus enum values."""
    assert DebateStatus.PENDING == "pending"
    assert DebateStatus.RUNNING == "running"
    assert DebateStatus.COMPLETED == "completed"
    assert DebateStatus.FAILED == "failed"


def test_stock_create_schema():
    """Test StockCreate schema validation."""
    stock = StockCreate(
        symbol="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        sector="Technology",
    )
    assert stock.symbol == "AAPL"
    assert stock.name == "Apple Inc."


def test_user_create_schema():
    """Test UserCreate schema validation."""
    user = UserCreate(
        email="test@example.com",
        display_name="Test User",
    )
    assert user.email == "test@example.com"
    assert user.display_name == "Test User"
