"""Stock schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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


class StockListResponse(BaseModel):
    """Schema for stock list response."""

    stocks: list[StockResponse]
    total: int


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


class StockPriceListResponse(BaseModel):
    """Schema for stock price list response."""

    prices: list[StockPriceResponse]
    total: int
