"""Authentication endpoints."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.crud.user import user_crud
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.services.firebase import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Login with Firebase token.
    This is a stub implementation that returns a mock response.
    """
    # In production: verify Firebase token
    # firebase_user = await verify_token(request.firebase_token)

    # Mock response for development
    mock_user = UserResponse(
        id="user_123",
        email="user@example.com",
        firebase_uid="firebase_123",
        display_name="Test User",
        photo_url="https://example.com/photo.jpg",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    return LoginResponse(
        access_token="mock_jwt_token_12345",
        token_type="bearer",
        user=mock_user,
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Register a new user with Firebase token.
    This is a stub implementation that returns a mock response.
    """
    # In production: verify Firebase token
    # firebase_user = await verify_token(request.firebase_token)

    # In production: create user in database
    # user = await user_crud.create(db, obj_in=UserCreate(**request.dict()))

    # Mock response for development
    mock_user = UserResponse(
        id="user_456",
        email=request.email,
        firebase_uid="firebase_456",
        display_name=request.display_name or "New User",
        photo_url=request.photo_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    return RegisterResponse(
        access_token="mock_jwt_token_67890",
        token_type="bearer",
        user=mock_user,
    )
