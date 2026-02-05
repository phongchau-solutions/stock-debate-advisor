from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.debate import DebateStatus


class DebateBase(BaseModel):
    """Base debate schema."""
    symbol: str = Field(..., min_length=1, max_length=10)
    timeframe: str = Field(..., pattern="^(1_month|3_months|6_months|1_year)$")


class DebateCreate(DebateBase):
    """Schema for creating a debate."""
    pass


class DebateResponse(DebateBase):
    """Schema for debate response."""
    id: str
    user_id: str
    status: DebateStatus
    verdict: Optional[str] = None
    confidence: Optional[str] = None
    reasoning: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DebateListResponse(BaseModel):
    """Schema for list of debates."""
    debates: list[DebateResponse]
    total: int
