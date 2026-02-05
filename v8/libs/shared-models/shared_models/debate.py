"""Debate-related models and schemas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text

from shared_models.base import Base


class DebateStatus(str, Enum):
    """Debate status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Debate(Base):
    """SQLAlchemy Debate model."""

    __tablename__ = "debates"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    stock_symbol = Column(String(10), nullable=False)
    status = Column(SQLEnum(DebateStatus), nullable=False, default=DebateStatus.PENDING)
    bull_agent_id = Column(String, nullable=True)
    bear_agent_id = Column(String, nullable=True)
    judge_verdict = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DebateBase(BaseModel):
    """Base Pydantic schema for Debate."""

    stock_symbol: str = Field(..., min_length=1, max_length=10)


class DebateCreate(DebateBase):
    """Schema for creating a debate."""

    pass


class DebateResponse(DebateBase):
    """Schema for debate response."""

    id: str
    user_id: str
    status: DebateStatus
    bull_agent_id: Optional[str] = None
    bear_agent_id: Optional[str] = None
    judge_verdict: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
