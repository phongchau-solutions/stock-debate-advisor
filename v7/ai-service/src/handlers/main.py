from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.config import settings
from src.utils.models import DebateRequest, DebateResponse, HealthResponse
from src.core.engine import DebateEngine

logging.basicConfig(level=logging.INFO if settings.VERBOSE else logging.WARNING)
logger = logging.getLogger(__name__)

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("Starting AI Service...")
    settings.validate()
    engine = DebateEngine()
    logger.info("Engine initialized")
    yield
    logger.info("Shutting down AI Service...")

app = FastAPI(
    title="Stock Debate Advisor API",
    description="Multi-agent stock analysis debate system",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", version="2.0")

@app.post("/debate", response_model=DebateResponse)
async def start_debate(request: DebateRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        result = engine.debate(
            request.ticker,
            request.timeframe,
            request.min_rounds,
            request.max_rounds
        )
        
        return DebateResponse(
            ticker=request.ticker,
            timeframe=request.timeframe,
            actual_rounds=result["actual_rounds"],
            rounds=result["rounds"],
            final_recommendation=result["final_recommendation"],
            confidence=result["confidence"],
            rationale=result["rationale"],
            risks=result["risks"],
            monitor=result["monitor"]
        )
    except Exception as e:
        logger.error(f"Debate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
