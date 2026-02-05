"""Stock database models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, Text

from app.db.base import Base


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
