"""
FastAPI server for Stock Debate Advisor agentic system
Provides REST API endpoints for frontend integration
Uses knowledge management for persistent data loading across debate sessions
"""

import uuid
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config
from orchestrator_v2 import get_orchestrator
from knowledge_manager import get_knowledge_manager
from data_loader import DataLoader
from models import (
    DebateRequest,
    DebateSessionResponse,
    DebateResultResponse,
    VerdictResponse,
    SymbolListResponse,
    DebateStatusResponse,
    ErrorResponse,
    InvestmentAction,
    ConfidenceLevel,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Debate Advisor API",
    description="Multi-agent debate system for stock analysis using CrewAI",
    version="2.0.0",
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
orchestrator = get_orchestrator()
knowledge_manager = get_knowledge_manager()
data_loader = DataLoader()


def run_debate_background(session_id: str, symbol: str, rounds: int):
    """Run debate in background thread"""
    try:
        logger.info(f"🎯 Starting debate for {symbol} (Session: {session_id})")
        
        # Run the debate rounds
        for round_num in range(1, rounds + 1):
            logger.info(f"   Round {round_num}/{rounds}")
            result = orchestrator.run_debate_round(session_id, round_num)
            
            if result.get("status") == "error":
                logger.error(f"   Error in round {round_num}: {result.get('error')}")
                break
        
        logger.info(f"✅ Debate completed for {symbol} (Session: {session_id})")
        
    except Exception as e:
        logger.error(f"❌ Error during debate: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    config.validate()
    logger.info("✅ Services initialized successfully")


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Stock Debate Advisor API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["knowledge_management", "persistent_data", "multi_round_debates"]
    }


@app.get("/api/symbols", response_model=SymbolListResponse, tags=["Data"])
async def get_available_symbols():
    """Get list of available stock symbols from data pipeline"""
    try:
        symbols = orchestrator.get_available_symbols()
        return SymbolListResponse(symbols=symbols, count=len(symbols))
    
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/api/debate/start", response_model=DebateSessionResponse, tags=["Debate"])
async def start_debate(request: DebateRequest, background_tasks: BackgroundTasks):
    """
    Start a new debate session with persistent knowledge loading.
    
    This endpoint:
    1. Creates a new debate session
    2. Loads financial reports for fundamental analysis
    3. Loads technical data for technical analysis
    4. Loads news articles for sentiment analysis
    5. Keeps data persistent throughout debate
    
    Use /api/debate/status/{session_id} to check progress.
    """
    try:
        # Validate symbol
        available_symbols = orchestrator.get_available_symbols()
        if request.symbol not in available_symbols:
            raise HTTPException(
                status_code=400,
                detail=f"Symbol {request.symbol} not found. Available: {available_symbols}"
            )
        
        # Validate rounds
        if not (config.MIN_ROUNDS <= request.rounds <= config.MAX_ROUNDS):
            raise HTTPException(
                status_code=400,
                detail=f"Rounds must be between {config.MIN_ROUNDS} and {config.MAX_ROUNDS}"
            )
        
        # Start debate session with knowledge loading
        session_info = orchestrator.start_debate_session(request.symbol, request.rounds)
        
        if session_info.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=session_info.get("error")
            )
        
        session_id = session_info["session_id"]
        
        # Run debate in background
        background_tasks.add_task(run_debate_background, session_id, request.symbol, request.rounds)
        
        return DebateSessionResponse(
            session_id=session_id,
            symbol=request.symbol,
            rounds=request.rounds,
            status="started",
            created_at=datetime.utcnow().isoformat(),
            data_loaded=session_info.get("data_loaded")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting debate: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/debate/status/{session_id}",
    response_model=DebateStatusResponse,
    tags=["Debate"]
)
async def get_debate_status(session_id: str):
    """Get current status of a debate session"""
    try:
        session_info = orchestrator.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return DebateStatusResponse(
            session_id=session_id,
            symbol=session_info["symbol"],
            status="in_progress",
            current_round=session_info["current_round"],
            total_rounds=1,
            progress=int((session_info["current_round"] / 1) * 100) if session_info["current_round"] > 0 else 0
        )
    
    except Exception as e:
        logger.error(f"Error getting debate status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/debate/status/{session_id}",
    response_model=DebateStatusResponse,
    tags=["Debate"]
)
async def get_debate_status(session_id: str):
    """Get current status of a debate session"""
    try:
        if session_id not in debate_sessions:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        session = debate_sessions[session_id]
        status = session["status"]
        current_round = session.get("current_round", 0)
        total_rounds = session["rounds"]
        
        # Calculate progress
        if status == "completed":
            progress = 100
        elif status == "failed":
            progress = 0
        else:
            progress = int((current_round / total_rounds) * 100) if total_rounds > 0 else 0
        
        # Calculate estimated completion
        estimated_completion = None
        if status == "in_progress":
            elapsed = (datetime.utcnow() - datetime.fromisoformat(session["started_at"])).total_seconds()
            if current_round > 0:
                time_per_round = elapsed / current_round
                remaining_rounds = total_rounds - current_round
                estimated_seconds = time_per_round * remaining_rounds
                estimated_completion = (
                    datetime.utcnow() + timedelta(seconds=estimated_seconds)
                ).isoformat()
        
        return DebateStatusResponse(
            session_id=session_id,
            symbol=session["symbol"],
            status=status,
            progress=progress,
            current_round=current_round,
            total_rounds=total_rounds,
            estimated_completion=estimated_completion,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching debate status: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get(
    "/api/debate/result/{session_id}",
    response_model=DebateResultResponse,
    tags=["Debate"]
)
async def get_debate_result(session_id: str):
    """Get complete debate result"""
    try:
        if session_id not in debate_sessions:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        session = debate_sessions[session_id]
        
        if session["status"] not in ["completed", "failed"]:
            raise HTTPException(
                status_code=202,
                detail="Debate still in progress. Check status endpoint."
            )
        
        # Load financial and technical data
        symbol = session["symbol"]
        financial_data = None
        technical_data = None
        
        try:
            financial_data = data_loader.load_financial_data(symbol)
            technical_data = data_loader.load_technical_data(symbol)
        except Exception as e:
            logger.warning(f"Could not load data for {symbol}: {e}")
        
        verdict = None
        if session.get("verdict"):
            verdict_raw = session["verdict"]
            verdict = VerdictResponse(
                recommendation=InvestmentAction(verdict_raw.get("recommendation", "HOLD")),
                confidence=ConfidenceLevel(verdict_raw.get("confidence", "MEDIUM")),
                rationale=verdict_raw.get("rationale", ""),
                score=float(verdict_raw.get("score", 5.0)),
            )
        
        return DebateResultResponse(
            session_id=session_id,
            symbol=symbol,
            status=session["status"],
            rounds=session["rounds"],
            verdict=verdict,
            debate_summary=session.get("debate_summary"),
            financial_data=financial_data,
            technical_data=technical_data,
            error=session.get("error"),
            completed_at=session.get("completed_at"),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching debate result: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/sessions", tags=["Session"])
async def list_sessions():
    """List all debate sessions"""
    sessions = []
    for session_id, session in debate_sessions.items():
        sessions.append({
            "session_id": session_id,
            "symbol": session["symbol"],
            "status": session["status"],
            "created_at": session["created_at"],
            "completed_at": session.get("completed_at"),
        })
    
    return {
        "total": len(sessions),
        "sessions": sessions,
    }


@app.get("/api/sessions/{session_id}", tags=["Session"])
async def get_session_details(session_id: str):
    """Get session details"""
    if session_id not in debate_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return debate_sessions[session_id]


@app.delete("/api/sessions/{session_id}", tags=["Session"])
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in debate_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    del debate_sessions[session_id]
    return {"message": f"Session {session_id} deleted"}


@app.get("/api/config", tags=["Config"])
async def get_config():
    """Get current configuration (non-sensitive)"""
    return {
        "crewai_model": Config.CREWAI_MODEL,
        "temperature": Config.TEMPERATURE,
        "max_tokens": Config.MAX_TOKENS,
        "debate_rounds": Config.DEBATE_ROUNDS,
        "min_rounds": Config.MIN_ROUNDS,
        "max_rounds": Config.MAX_ROUNDS,
        "crew_verbose": Config.CREW_VERBOSE,
        "crew_memory": Config.CREW_MEMORY,
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Include knowledge management endpoints
from api_endpoints_v2 import router as v2_router
app.include_router(v2_router)


# Additional useful endpoints
@app.get("/api/session/{session_id}/knowledge", tags=["Knowledge"])
async def get_session_knowledge(session_id: str):
    """Get all loaded knowledge for a session"""
    try:
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "symbol": session_info["symbol"],
            "knowledge_loaded": session_info["data"],
            "created_at": session_info["created_at"]
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", tags=["Admin"])
async def get_stats():
    """Get system statistics"""
    return {
        "active_sessions": len(orchestrator.sessions),
        "available_symbols": len(orchestrator.get_available_symbols()),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
