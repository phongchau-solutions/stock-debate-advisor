"""
Database models for the Data Service.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class FinancialData(Base):
    """Financial data from VietCap API."""
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # balance_sheet, income_statement, cash_flow, metrics
    period = Column(String(20))  # Q1-2024, FY-2023
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PriceData(Base):
    """Historical price data."""
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsArticle(Base):
    """News articles from web crawlers."""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True)
    content = Column(Text)
    source = Column(String(100))  # vietstock, cafef, vneconomy
    published_at = Column(DateTime)
    sentiment_score = Column(Float)  # -1 to 1
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyInfo(Base):
    """Company basic information."""
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200))
    industry = Column(String(100))
    sector = Column(String(100))
    market_cap = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DataPipelineLog(Base):
    """Log for data pipeline executions."""
    __tablename__ = "data_pipeline_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False)
    symbol = Column(String(20), index=True)
    status = Column(String(20))  # success, failed, running
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
