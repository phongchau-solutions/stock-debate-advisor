from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get current user from JWT token.
    For now, returns a mock user ID.
    TODO: Implement proper JWT validation with Firebase.
    """
    # Mock implementation
    return "user_123"


async def get_db_session(
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """Database session dependency."""
    return db
