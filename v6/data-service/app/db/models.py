"""
Database models for the Data Service.
Designed with clear separation of concerns:
- CompanyInfo: Static company metadata
- FinancialReport: Quarterly and annual financial statements (separate tables)
- StockPrice: Daily OHLCV price data
- CompanyNews: News articles and press releases
- DataPipelineLog: Pipeline execution tracking
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


# ============================================================================
# COMPANY INFORMATION - Static data that changes rarely
# ============================================================================

class CompanyInfo(Base):
    """Company basic information (refreshed quarterly or on-demand)."""
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    english_name = Column(String(200))
    industry = Column(String(100))
    sector = Column(String(100))
    market_cap = Column(Float)  # in VND
    market_cap_usd = Column(Float)  # in USD
    employees = Column(Integer)
    website = Column(String(500))
    description = Column(Text)
    company_info_raw = Column(JSON)  # Full data from Yahoo Finance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_symbol', 'symbol'),
    )


# ============================================================================
# FINANCIAL REPORTS - Quarterly and Annual reports (separate tables)
# ============================================================================

class QuarterlyFinancialReport(Base):
    """Quarterly financial statements from Yahoo Finance."""
    __tablename__ = "quarterly_financial_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)  # e.g., 2024
    fiscal_quarter = Column(Integer, nullable=False)  # 1-4, or 0 for FY
    period_end_date = Column(DateTime, nullable=False)
    
    # Income Statement
    revenue = Column(Float)
    operating_income = Column(Float)
    net_income = Column(Float)
    gross_profit = Column(Float)
    
    # Balance Sheet
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    
    # Cash Flow
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    
    # Key Metrics
    eps = Column(Float)  # Earnings per share
    book_value_per_share = Column(Float)
    
    # Full raw data
    raw_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_quarterly_symbol_date', 'symbol', 'period_end_date'),
        UniqueConstraint('symbol', 'fiscal_year', 'fiscal_quarter', name='uq_symbol_period'),
    )


class AnnualFinancialReport(Base):
    """Annual financial statements from Yahoo Finance."""
    __tablename__ = "annual_financial_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    period_end_date = Column(DateTime, nullable=False)
    
    # Income Statement
    revenue = Column(Float)
    operating_income = Column(Float)
    net_income = Column(Float)
    gross_profit = Column(Float)
    
    # Balance Sheet
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    
    # Cash Flow
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    
    # Key Metrics
    eps = Column(Float)
    book_value_per_share = Column(Float)
    
    # Full raw data
    raw_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_symbol_year', 'symbol', 'fiscal_year'),
        UniqueConstraint('symbol', 'fiscal_year', name='uq_symbol_year'),
    )


class FinancialMetrics(Base):
    """Key financial metrics and ratios (calculated or from Yahoo Finance)."""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    metric_date = Column(DateTime, nullable=False)
    
    # Valuation Metrics
    pe_ratio = Column(Float)  # Price-to-Earnings
    pb_ratio = Column(Float)  # Price-to-Book
    ps_ratio = Column(Float)  # Price-to-Sales
    peg_ratio = Column(Float)  # PEG ratio
    
    # Profitability Metrics
    roe = Column(Float)  # Return on Equity
    roa = Column(Float)  # Return on Assets
    roic = Column(Float)  # Return on Invested Capital
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    
    # Liquidity Metrics
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    debt_to_equity = Column(Float)
    
    # Growth Metrics
    revenue_growth = Column(Float)  # YoY
    earnings_growth = Column(Float)  # YoY
    
    # Raw metrics data
    raw_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_metrics_symbol_date', 'symbol', 'metric_date'),
    )


# ============================================================================
# STOCK PRICE DATA - Historical daily prices
# ============================================================================

class StockPrice(Base):
    """Historical daily stock price data (OHLCV)."""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price_date = Column(DateTime, nullable=False, index=True)
    
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    adj_close_price = Column(Float)
    volume = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_price_symbol_date', 'symbol', 'price_date'),
        UniqueConstraint('symbol', 'price_date', name='uq_symbol_date'),
    )


class Dividend(Base):
    """Dividend payment history."""
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    ex_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    dividend_per_share = Column(Float, nullable=False)
    dividend_type = Column(String(50))  # cash, stock, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_dividend_symbol_date', 'symbol', 'ex_date'),
        UniqueConstraint('symbol', 'ex_date', name='uq_symbol_exdate'),
    )


class StockSplit(Base):
    """Stock split history."""
    __tablename__ = "stock_splits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    split_date = Column(DateTime, nullable=False)
    split_ratio = Column(String(50), nullable=False)  # e.g., "2:1", "3:1"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_split_symbol_date', 'symbol', 'split_date'),
        UniqueConstraint('symbol', 'split_date', name='uq_symbol_split_date'),
    )


# ============================================================================
# COMPANY NEWS - Articles and press releases from multiple sources
# ============================================================================

class CompanyNews(Base):
    """News articles and press releases related to companies."""
    __tablename__ = "company_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    
    # Source information
    source = Column(String(100), nullable=False)  # yahoo_finance, cafef, vneconomy, vietstock, etc.
    source_name = Column(String(200))  # Display name
    
    # Publication info
    published_at = Column(DateTime)
    crawled_at = Column(DateTime, nullable=False)
    
    # Content analysis
    language = Column(String(10), default='vi')  # Vietnamese by default
    content_length = Column(Integer)
    image_url = Column(String(1000))
    
    # Sentiment analysis
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # negative, neutral, positive
    
    # Keyword extraction
    keywords = Column(JSON)  # List of keywords
    
    # Deduplication
    content_hash = Column(String(64), index=True)  # SHA256 hash for deduplication
    
    # Tracking
    is_archived = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_symbol_published', 'symbol', 'published_at'),
        Index('idx_source_symbol', 'source', 'symbol'),
        Index('idx_content_hash', 'content_hash'),
        UniqueConstraint('url', name='uq_url'),
    )


# ============================================================================
# PIPELINE MANAGEMENT
# ============================================================================

class DataPipelineLog(Base):
    """Log for data pipeline executions and monitoring."""
    __tablename__ = "data_pipeline_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False)  # e.g., fetch_financials, crawl_news
    pipeline_type = Column(String(50), nullable=False)  # financial, news, price
    
    symbol = Column(String(20), index=True)  # NULL if processing all symbols
    
    status = Column(String(20), nullable=False)  # success, failed, running, partial
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Execution timing
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Details
    details = Column(JSON)  # Additional metadata
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_pipeline_status', 'pipeline_name', 'status'),
        Index('idx_pipeline_time', 'pipeline_name', 'created_at'),
    )
