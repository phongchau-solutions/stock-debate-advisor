"""API dependencies."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.firebase import verify_token

# Placeholder for authentication
# In production, this would validate JWT tokens


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async for session in get_db():
        yield session


async def get_current_user(
    # In production: token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Get current user from JWT token.
    This is a stub implementation for development.
    """
    # TODO: Implement JWT token validation
    # For now, return a placeholder user
    return {
        "id": "user_123",
        "email": "user@example.com",
        "firebase_uid": "firebase_123",
        "display_name": "Test User",
        "photo_url": None,
    }


async def get_optional_user() -> Optional[dict]:
    """
    Get current user if authenticated, otherwise None.
    Useful for endpoints that work with or without authentication.
    """
    try:
        return await get_current_user()
    except HTTPException:
        return None
