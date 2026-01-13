"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for development (faster, no setup needed)
# Change to PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./stock_debate_data.db"  # SQLite for development
    # "postgresql://postgres:postgres@localhost:5432/stock_debate_data"  # PostgreSQL for production
)

# MongoDB connection
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/"
)
MONGODB_DB = os.getenv("MONGODB_DB", "stock_debate")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session for dependency injection."""
    return SessionLocal()


# MongoDB client (optional, for document storage)
def get_mongo_client():
    """Get MongoDB client."""
    from pymongo import MongoClient
    return MongoClient(MONGODB_URL)


def get_mongo_db():
    """Get MongoDB database."""
    client = get_mongo_client()
    return client[MONGODB_DB]
