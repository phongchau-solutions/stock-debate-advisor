"""User database models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String

from app.db.base import Base


class User(Base):
    """SQLAlchemy User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    firebase_uid = Column(String(128), nullable=True, unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
