"""User endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.user import user_crud
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["users"])


@router.get("", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get current authenticated user information.
    """
    # In production: fetch user from database
    # user = await user_crud.get(db, id=current_user["id"])
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    # Mock response for development
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        firebase_uid=current_user.get("firebase_uid"),
        display_name=current_user.get("display_name"),
        photo_url=current_user.get("photo_url"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@router.put("", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update current authenticated user information.
    """
    # In production: update user in database
    # user = await user_crud.update(db, id=current_user["id"], obj_in=user_update)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    # Mock response for development
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        firebase_uid=current_user.get("firebase_uid"),
        display_name=user_update.display_name or current_user.get("display_name"),
        photo_url=user_update.photo_url or current_user.get("photo_url"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get user by ID.
    """
    # In production: fetch user from database
    # user = await user_crud.get(db, id=user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    # Mock response for development
    return UserResponse(
        id=user_id,
        email="user@example.com",
        firebase_uid="firebase_123",
        display_name="Test User",
        photo_url="https://example.com/photo.jpg",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
