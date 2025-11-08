"""
Database models for debate logs and analysis persistence.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class FinancialAnalysis(Base):
    """Persisted fundamental analysis results."""
    __tablename__ = "financial_analysis"
    
    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    pe_ratio = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    debt_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    fair_value = Column(Float, nullable=True)
    analysis_json = Column(JSON, nullable=False)


class TechnicalAnalysis(Base):
    """Persisted technical analysis results."""
    __tablename__ = "technical_analysis"
    
    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ma_50 = Column(Float, nullable=True)
    ma_200 = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    analysis_json = Column(JSON, nullable=False)


class SentimentAnalysis(Base):
    """Persisted sentiment analysis results."""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sentiment_score = Column(Float, nullable=False)  # -1.0 to 1.0
    article_count = Column(Integer, nullable=True)
    analysis_json = Column(JSON, nullable=False)


class DebateLog(Base):
    """Debate transcript and decision log."""
    __tablename__ = "debate_logs"
    
    id = Column(Integer, primary_key=True)
    debate_id = Column(String(50), nullable=False, unique=True, index=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime, nullable=True)
    num_rounds = Column(Integer, nullable=True)
    final_decision = Column(String(20), nullable=True)  # BUY, HOLD, SELL
    confidence_score = Column(Float, nullable=True)
    transcript = Column(Text, nullable=False)  # Full debate transcript
    summary = Column(Text, nullable=True)
    debate_json = Column(JSON, nullable=False)  # Full structured data


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, db_url: str = None):
        """
        Initialize database manager.
        
        Args:
            db_url: Database connection URL. If None, uses DATABASE_URL env var
                   or falls back to SQLite.
        """
        if db_url is None:
            db_url = os.getenv(
                "DATABASE_URL",
                "sqlite:////tmp/debate_poc.db"
            )
        
        # Replace postgres:// with postgresql+psycopg2:// for newer versions
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        
        self.engine = create_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        logger.info(f"Database initialized: {db_url}")
    
    def init_db(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables initialized")
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()
