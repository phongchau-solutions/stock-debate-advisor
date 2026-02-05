# Stock Debate Advisor v8 - Backend Specification

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026  
**Stack:** Python + FastAPI + FastCRUD + SQLAlchemy + Alembic

---

## Backend Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Programming language |
| **FastAPI** | 0.110+ | Web framework |
| **FastCRUD** | 0.12+ | CRUD operations with Pydantic v2 |
| **SQLAlchemy** | 2.0+ | ORM |
| **Alembic** | 1.13+ | Database migrations |
| **Pydantic** | 2.6+ | Data validation |
| **uvicorn** | 0.27+ | ASGI server |
| **asyncpg** | 0.29+ | Async PostgreSQL driver |
| **redis** | 5.0+ | Caching (optional) |

### Additional Libraries

| Library | Purpose |
|---------|---------|
| **httpx** | Async HTTP client |
| **python-jose** | JWT tokens |
| **passlib** | Password hashing |
| **python-multipart** | Form data parsing |
| **google-cloud-aiplatform** | Google ADK integration |
| **google-generativeai** | Gemini API |
| **pandas** | Data processing |
| **numpy** | Numerical operations |
| **pytest** | Testing |
| **pytest-asyncio** | Async testing |

---

## Project Setup

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi[all]==0.110.0
pip install fastcrud==0.12.0
pip install sqlalchemy[asyncio]==2.0.27
pip install alembic==1.13.1
pip install pydantic==2.6.1
pip install pydantic-settings==2.1.0
pip install uvicorn[standard]==0.27.0
pip install asyncpg==0.29.0
pip install redis==5.0.1
pip install httpx==0.26.0
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install python-multipart==0.0.9
pip install google-cloud-aiplatform==1.42.1
pip install google-generativeai==0.3.2
pip install pandas==2.2.0
pip install numpy==1.26.3

# Development dependencies
pip install pytest==8.0.0
pip install pytest-asyncio==0.23.4
pip install pytest-cov==4.1.0
pip install black==24.1.1
pip install flake8==7.0.0
pip install mypy==1.8.0

# Save dependencies
pip freeze > requirements.txt
```

### Project Structure

```
backend/
├── alembic/                      # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration settings
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── debates.py
│   │       ├── stocks.py
│   │       ├── users.py
│   │       ├── analytics.py
│   │       └── auth.py
│   │
│   ├── crud/                     # FastCRUD operations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── debate.py
│   │   ├── stock.py
│   │   ├── user.py
│   │   └── financial_report.py
│   │
│   ├── db/                       # Database
│   │   ├── __init__.py
│   │   ├── base.py              # Base model
│   │   ├── session.py           # DB session
│   │   └── init_db.py           # DB initialization
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── debate.py
│   │   ├── stock.py
│   │   ├── user.py
│   │   ├── financial_report.py
│   │   └── price.py
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── debate.py
│   │   ├── stock.py
│   │   ├── user.py
│   │   ├── financial_report.py
│   │   └── common.py
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── gemini_client.py
│   │   │   ├── agent_orchestrator.py
│   │   │   └── debate_engine.py
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── stock_fetcher.py
│   │   │   └── news_fetcher.py
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── firebase_auth.py
│   │       └── jwt_handler.py
│   │
│   ├── core/                     # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── cache.py
│   │   └── exceptions.py
│   │
│   └── utils/                    # Helper functions
│       ├── __init__.py
│       ├── logging.py
│       └── formatting.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_crud/
│   └── test_services/
│
├── .env.example
├── .env.development
├── .env.production
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## Core Implementation

### Configuration (config.py)

```python
# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Stock Debate Advisor"
    APP_VERSION: str = "8.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Redis (optional, for caching)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5 minutes
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_DATABASE_URL: str
    
    # Google AI
    GOOGLE_AI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
```

### Database Session (db/session.py)

```python
# app/db/session.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Base Model (db/base.py)

```python
# app/db/base.py

from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Models Example (models/debate.py)

```python
# app/models/debate.py

from sqlalchemy import Column, String, Integer, Enum, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel

class DebateStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Recommendation(str, enum.Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class Debate(BaseModel):
    __tablename__ = "debates"
    
    symbol = Column(String(10), nullable=False, index=True)
    status = Column(Enum(DebateStatus), default=DebateStatus.INITIATED, nullable=False)
    rounds = Column(Integer, default=3, nullable=False)
    
    # User relationship
    user_id = Column(String, nullable=False, index=True)  # Firebase UID
    
    # Results
    recommendation = Column(Enum(Recommendation), nullable=True)
    confidence = Column(Float, nullable=True)
    debate_summary = Column(JSON, nullable=True)
    verdict = Column(JSON, nullable=True)
    
    # Metadata
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Relationships
    # debate_rounds = relationship("DebateRound", back_populates="debate", cascade="all, delete-orphan")
```

### Pydantic Schemas (schemas/debate.py)

```python
# app/schemas/debate.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class DebateStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Recommendation(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class DebateBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    rounds: int = Field(default=3, ge=1, le=10)

class DebateCreate(DebateBase):
    pass

class DebateUpdate(BaseModel):
    status: Optional[DebateStatus] = None
    recommendation: Optional[Recommendation] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    debate_summary: Optional[dict] = None
    verdict: Optional[dict] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None

class DebateInDB(DebateBase):
    id: UUID
    status: DebateStatus
    user_id: str
    recommendation: Optional[Recommendation] = None
    confidence: Optional[float] = None
    debate_summary: Optional[dict] = None
    verdict: Optional[dict] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DebateResponse(DebateInDB):
    pass

class DebateListResponse(BaseModel):
    items: List[DebateResponse]
    total: int
    page: int
    size: int
```

### CRUD Operations with FastCRUD (crud/debate.py)

```python
# app/crud/debate.py

from fastcrud import FastCRUD
from app.models.debate import Debate
from app.schemas.debate import DebateCreate, DebateUpdate

class DebateCRUD(FastCRUD[Debate, DebateCreate, DebateUpdate]):
    """CRUD operations for Debate model"""
    
    async def get_by_symbol(self, db, symbol: str, user_id: str, skip: int = 0, limit: int = 10):
        """Get debates by symbol for a user"""
        return await self.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            symbol=symbol,
            user_id=user_id
        )
    
    async def get_user_debates(self, db, user_id: str, skip: int = 0, limit: int = 10):
        """Get all debates for a user"""
        return await self.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            user_id=user_id
        )

# Create instance
debate_crud = DebateCRUD(Debate)
```

### FastAPI Routes (api/v1/debates.py)

```python
# app/api/v1/debates.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.crud.debate import debate_crud
from app.schemas.debate import (
    DebateCreate,
    DebateResponse,
    DebateListResponse,
)
from app.schemas.user import User
from app.services.ai.debate_engine import start_debate_background

router = APIRouter()

@router.post("/", response_model=DebateResponse, status_code=201)
async def create_debate(
    debate_in: DebateCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new debate.
    
    The debate will be processed asynchronously in the background.
    """
    # Create debate record
    debate_data = debate_in.model_dump()
    debate_data["user_id"] = current_user.uid
    
    debate = await debate_crud.create(db=db, object=debate_data)
    
    # Start debate processing in background
    background_tasks.add_task(start_debate_background, str(debate.id), debate_in.symbol, debate_in.rounds)
    
    return debate

@router.get("/", response_model=DebateListResponse)
async def list_debates(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List debates for current user"""
    debates = await debate_crud.get_user_debates(
        db=db,
        user_id=current_user.uid,
        skip=skip,
        limit=limit
    )
    
    total = await debate_crud.count(db=db, user_id=current_user.uid)
    
    return {
        "items": debates,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
    }

@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(
    debate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific debate"""
    debate = await debate_crud.get(db=db, id=debate_id)
    
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    
    if debate.user_id != current_user.uid:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return debate

@router.delete("/{debate_id}", status_code=204)
async def delete_debate(
    debate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (cancel) a debate"""
    debate = await debate_crud.get(db=db, id=debate_id)
    
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    
    if debate.user_id != current_user.uid:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await debate_crud.delete(db=db, id=debate_id)
    return None
```

### AI Service with Google ADK (services/ai/debate_engine.py)

```python
# app/services/ai/debate_engine.py

import asyncio
from datetime import datetime
import google.generativeai as genai
from app.config import settings
from app.crud.debate import debate_crud
from app.db.session import AsyncSessionLocal
from app.models.debate import DebateStatus, Recommendation

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_AI_API_KEY)

class DebateEngine:
    """AI-powered debate engine using Google Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def run_debate(self, symbol: str, company_data: dict, rounds: int = 3):
        """Run multi-agent debate"""
        
        debate_history = []
        
        for round_num in range(rounds):
            # Fundamental analysis
            fundamental_prompt = f"""
            As a fundamental analyst, analyze {symbol} stock based on:
            {company_data}
            
            Provide: BUY/HOLD/SELL recommendation with confidence (0-100%).
            """
            fundamental_response = await self._get_response(fundamental_prompt)
            
            # Technical analysis
            technical_prompt = f"""
            As a technical analyst, analyze {symbol} stock price trends and indicators.
            Previous round: {debate_history[-1] if debate_history else 'First round'}
            
            Provide: BUY/HOLD/SELL recommendation with confidence.
            """
            technical_response = await self._get_response(technical_prompt)
            
            # Sentiment analysis
            sentiment_prompt = f"""
            As a sentiment analyst, analyze market sentiment for {symbol}.
            Consider news, social media, and investor behavior.
            
            Provide: BUY/HOLD/SELL recommendation with confidence.
            """
            sentiment_response = await self._get_response(sentiment_prompt)
            
            debate_history.append({
                "round": round_num + 1,
                "fundamental": fundamental_response,
                "technical": technical_response,
                "sentiment": sentiment_response,
            })
        
        # Final verdict
        verdict_prompt = f"""
        As an impartial judge, synthesize the following debate:
        {debate_history}
        
        Provide final verdict:
        - Recommendation: BUY/HOLD/SELL
        - Confidence: 0-100%
        - Summary: Brief explanation
        
        Format: JSON with keys: recommendation, confidence, summary
        """
        
        verdict_response = await self._get_response(verdict_prompt)
        
        return {
            "debate_history": debate_history,
            "verdict": self._parse_verdict(verdict_response),
        }
    
    async def _get_response(self, prompt: str) -> str:
        """Get response from Gemini model"""
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        return response.text
    
    def _parse_verdict(self, verdict_text: str) -> dict:
        """Parse verdict from AI response"""
        # Simple parsing - should be more robust in production
        try:
            import json
            return json.loads(verdict_text)
        except:
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "summary": verdict_text[:500],
            }

debate_engine = DebateEngine()

async def start_debate_background(debate_id: str, symbol: str, rounds: int):
    """Background task to process debate"""
    async with AsyncSessionLocal() as db:
        try:
            # Update status
            await debate_crud.update(
                db=db,
                object={"status": DebateStatus.IN_PROGRESS},
                id=debate_id
            )
            
            # Fetch company data (mock for now)
            company_data = {"symbol": symbol, "data": "..."}
            
            # Run debate
            start_time = datetime.utcnow()
            result = await debate_engine.run_debate(symbol, company_data, rounds)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Update with results
            await debate_crud.update(
                db=db,
                object={
                    "status": DebateStatus.COMPLETED,
                    "recommendation": Recommendation[result["verdict"]["recommendation"]],
                    "confidence": result["verdict"]["confidence"] / 100.0,
                    "debate_summary": result["debate_history"],
                    "verdict": result["verdict"],
                    "duration_seconds": duration,
                },
                id=debate_id
            )
            
        except Exception as e:
            # Update with error
            await debate_crud.update(
                db=db,
                object={
                    "status": DebateStatus.FAILED,
                    "error_message": str(e),
                },
                id=debate_id
            )
```

### Main Application (main.py)

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import debates, stocks, users, analytics, auth

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(debates.router, prefix="/api/v1/debates", tags=["debates"])
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["stocks"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API v{settings.APP_VERSION}"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
```

### Database Migrations with Alembic

```python
# alembic/versions/001_initial_schema.py

"""Initial schema

Revision ID: 001
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create debates table
    op.create_table(
        'debates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('status', sa.Enum('INITIATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='debatestatus'), nullable=False),
        sa.Column('rounds', sa.Integer, default=3, nullable=False),
        sa.Column('user_id', sa.String, nullable=False, index=True),
        sa.Column('recommendation', sa.Enum('BUY', 'HOLD', 'SELL', name='recommendation'), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('debate_summary', sa.JSON, nullable=True),
        sa.Column('verdict', sa.JSON, nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('error_message', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

def downgrade():
    op.drop_table('debates')
```

---

## Testing

### Pytest Configuration

```python
# tests/conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.base import BaseModel

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """Create test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    
    await engine.dispose()
```

### Example Test

```python
# tests/test_crud/test_debate.py

import pytest
from app.crud.debate import debate_crud
from app.schemas.debate import DebateCreate

@pytest.mark.asyncio
async def test_create_debate(db_session):
    """Test debate creation"""
    debate_in = DebateCreate(symbol="AAPL", rounds=3)
    debate_data = debate_in.model_dump()
    debate_data["user_id"] = "test_user_123"
    
    debate = await debate_crud.create(db=db_session, object=debate_data)
    
    assert debate.symbol == "AAPL"
    assert debate.rounds == 3
    assert debate.user_id == "test_user_123"
    assert debate.status.value == "INITIATED"
```

---

## Docker Deployment

```dockerfile
# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Expose port
EXPOSE 8080

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8080
```

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Stack:** Python + FastAPI + FastCRUD + SQLAlchemy + Alembic  
**Status:** Ready for Implementation
