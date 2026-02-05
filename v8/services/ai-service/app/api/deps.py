"""API dependencies."""

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async for session in get_db():
        yield session


async def get_current_user() -> str:
    """
    Get current user from JWT token.
    This is a stub implementation for development.
    """
    # TODO: Implement JWT token validation
    return "user_placeholder"


async def get_optional_user() -> Optional[str]:
    """Get current user if authenticated, otherwise None."""
    try:
        return await get_current_user()
    except HTTPException:
        return None
