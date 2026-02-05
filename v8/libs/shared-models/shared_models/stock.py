"""Stock-related models and schemas."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, String, Text

from shared_models.base import Base


class Stock(Base):
    """SQLAlchemy Stock model."""

    __tablename__ = "stocks"

    symbol = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class StockPrice(Base):
    """SQLAlchemy Stock Price model."""

    __tablename__ = "stock_prices"

    id = Column(String, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class StockBase(BaseModel):
    """Base Pydantic schema for Stock."""

    symbol: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    exchange: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[float] = None
    description: Optional[str] = None


class StockCreate(StockBase):
    """Schema for creating a stock."""

    pass


class StockResponse(StockBase):
    """Schema for stock response."""

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StockPriceBase(BaseModel):
    """Base Pydantic schema for Stock Price."""

    symbol: str = Field(..., min_length=1, max_length=10)
    date: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)


class StockPriceCreate(StockPriceBase):
    """Schema for creating a stock price."""

    pass


class StockPriceResponse(StockPriceBase):
    """Schema for stock price response."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
