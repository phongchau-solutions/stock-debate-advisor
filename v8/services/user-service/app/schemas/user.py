"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base Pydantic schema for User."""

    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=255)
    photo_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema for creating a user."""

    firebase_uid: Optional[str] = Field(None, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    display_name: Optional[str] = Field(None, max_length=255)
    photo_url: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    firebase_uid: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for login request."""

    firebase_token: str = Field(..., description="Firebase ID token")


class LoginResponse(BaseModel):
    """Schema for login response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    """Schema for registration request."""

    email: EmailStr
    firebase_token: str = Field(..., description="Firebase ID token")
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


class RegisterResponse(BaseModel):
    """Schema for registration response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
