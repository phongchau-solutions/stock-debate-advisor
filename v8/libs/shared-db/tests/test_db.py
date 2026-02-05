"""Test shared database utilities."""

from shared_db.base import Base
from shared_db.session import create_db_engine, create_session_maker


def test_base_class():
    """Test Base class exists."""
    assert Base is not None


def test_create_db_engine():
    """Test database engine creation."""
    engine = create_db_engine("sqlite+aiosqlite:///:memory:")
    assert engine is not None


def test_create_session_maker():
    """Test session maker creation."""
    engine = create_db_engine("sqlite+aiosqlite:///:memory:")
    session_maker = create_session_maker(engine)
    assert session_maker is not None
