import enum

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.sql import func

from app.db.base import Base


class DebateStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Debate(Base):
    """Debate model."""

    __tablename__ = "debates"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=False)  # "1_month", "3_months", etc.
    status = Column(SQLEnum(DebateStatus), default=DebateStatus.PENDING)

    # Debate results
    verdict = Column(String, nullable=True)  # "BUY", "HOLD", "SELL"
    confidence = Column(String, nullable=True)  # "LOW", "MEDIUM", "HIGH"
    reasoning = Column(JSON, nullable=True)
    transcript = Column(JSON, nullable=True)  # Full debate transcript

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
