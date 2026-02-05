"""Database session utilities."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def create_db_engine(database_url: str, echo: bool = False):
    """
    Create async database engine.

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements

    Returns:
        Async engine instance
    """
    return create_async_engine(
        database_url,
        echo=echo,
        future=True,
    )


def create_session_maker(engine):
    """
    Create async session maker.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Session maker instance
    """
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session(session_maker) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    Args:
        session_maker: Session maker instance

    Yields:
        Database session
    """
    async with session_maker() as session:
        yield session
