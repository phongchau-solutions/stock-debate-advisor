"""User-related models and schemas."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, String, Text

from shared_models.base import Base


class User(Base):
    """SQLAlchemy User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    firebase_uid = Column(String(128), unique=True, nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class UserBase(BaseModel):
    """Base Pydantic schema for User."""

    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=255)
    photo_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    firebase_uid: Optional[str] = Field(None, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    display_name: Optional[str] = Field(None, max_length=255)
    photo_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    firebase_uid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
