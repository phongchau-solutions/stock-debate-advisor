"""
Database models for caching stock data and analysis results.
SQLite database for PoC demo - can be switched to PostgreSQL in production.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class StockPrice(Base):
    """OHLCV price data cache."""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    data_source = Column(String(50))  # vietcap, yfinance, synthetic
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'data_source': self.data_source
        }


class StockFinancials(Base):
    """Financial ratios and metrics cache."""
    __tablename__ = 'stock_financials'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True, unique=True)
    pe = Column(Float)
    pb = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    revenue = Column(Float)
    net_income = Column(Float)
    market_cap = Column(Float)
    data_source = Column(String(50))
    is_synthetic = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'pe': self.pe,
            'pb': self.pb,
            'roe': self.roe,
            'roa': self.roa,
            'eps': self.eps,
            'dividend_yield': self.dividend_yield,
            'revenue': self.revenue,
            'net_income': self.net_income,
            'market_cap': self.market_cap,
            'data_source': self.data_source,
            'is_synthetic': self.is_synthetic,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class NewsArticle(Base):
    """News articles cache."""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000))
    source = Column(String(100))
    published_date = Column(DateTime)
    content = Column(Text)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'content': self.content,
            'is_demo': self.is_demo
        }


class DebateSession(Base):
    """Debate session metadata."""
    __tablename__ = 'debate_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    period_days = Column(Integer, default=30)
    rounds = Column(Integer, default=3)
    status = Column(String(20))  # running, completed, failed
    final_decision = Column(String(20))  # buy, hold, sell
    final_confidence = Column(Float)
    data_source = Column(String(50))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'symbol': self.symbol,
            'period_days': self.period_days,
            'rounds': self.rounds,
            'status': self.status,
            'final_decision': self.final_decision,
            'final_confidence': self.final_confidence,
            'data_source': self.data_source,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class AgentAnalysis(Base):
    """Individual agent analysis results."""
    __tablename__ = 'agent_analyses'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    round_number = Column(Integer, nullable=False)
    signal = Column(String(20))  # buy, hold, sell
    confidence = Column(Float)
    rationale = Column(Text)
    indicators = Column(JSON)  # Store technical indicators as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'agent_name': self.agent_name,
            'round_number': self.round_number,
            'signal': self.signal,
            'confidence': self.confidence,
            'rationale': self.rationale,
            'indicators': self.indicators,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DebateTranscript(Base):
    """Complete debate transcript."""
    __tablename__ = 'debate_transcripts'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    transcript_json = Column(Text, nullable=False)  # Store as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'transcript': json.loads(self.transcript_json) if self.transcript_json else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def create_database(db_path: str = "data/debate_cache.db"):
    """
    Create database and all tables.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        SQLAlchemy engine and session maker
    """
    from pathlib import Path
    
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session maker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine, SessionLocal


def get_session(db_path: str = "data/debate_cache.db"):
    """
    Get a database session.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Database session
    """
    _, SessionLocal = create_database(db_path)
    return SessionLocal()
