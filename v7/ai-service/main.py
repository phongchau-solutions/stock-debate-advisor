"""
FastAPI Main Application for Stock Debate Advisor AI Service
Orchestrates multi-agent debate system for stock analysis
Integrates with data-service and frontend via REST API
Production-ready with AWS API Gateway support
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Stock Debate Advisor API Service Starting...")
    try:
        config.validate()
        logger.info("✅ Configuration validated successfully")
        logger.info(f"   Model: {config.CREWAI_MODEL}")
        logger.info(f"   Min Rounds: {config.MIN_ROUNDS}, Max Rounds: {config.MAX_ROUNDS}")
        logger.info(f"   Verbose: {config.VERBOSE}")
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Stock Debate Advisor API Service Shutting Down...")


# Create main FastAPI app
app = FastAPI(
    title="Stock Debate Advisor API",
    description="Multi-agent AI service for structured stock debate and investment analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.api.aws.com", "*.execute-api.*.amazonaws.com"]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
        "*"  # In production, replace with specific frontend domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper formatting"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status": "error",
            "request_path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": "error",
            "request_path": str(request.url),
        },
    )


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with AWS API Gateway compatibility"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Stock Debate Advisor API",
        version="2.0.0",
        description="Multi-agent AI service for structured stock debate and investment analysis",
        routes=app.routes,
    )
    
    # Add x-amazon-apigateway extensions for AWS integration
    openapi_schema["x-amazon-apigateway-cors"] = {
        "allowedHeaders": ["*"],
        "allowedMethods": ["GET", "POST", "OPTIONS"],
        "allowedOrigins": ["*"],
        "maxAge": 300
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - service information"""
    return {
        "service": "Stock Debate Advisor API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "symbols": "/api/v1/symbols",
            "debate": "/api/v1/debate/start",
        }
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "Stock Debate Advisor API",
        "version": "2.0.0",
        "features": {
            "debate_orchestration": True,
            "knowledge_persistence": True,
            "streaming_responses": True,
            "multi_agent_support": True,
        }
    }


# ============================================================================
# API V1 ROUTES (Production)
# ============================================================================

# Import endpoints from api_server
from api_server import (
    get_available_symbols,
    start_debate,
    get_debate_status,
    get_debate_result,
)


@app.get("/api/v1/symbols", tags=["Data"])
async def api_get_symbols():
    """Get available stock symbols for debate"""
    try:
        return await get_available_symbols()
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/debate/start", tags=["Debate"])
async def api_start_debate(request_data: dict, background_tasks: BackgroundTasks):
    """Start a new debate session"""
    try:
        return await start_debate(request_data, background_tasks)
    except Exception as e:
        logger.error(f"Error starting debate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/debate/status/{session_id}", tags=["Debate"])
async def api_get_debate_status(session_id: str):
    """Get debate session status"""
    try:
        return await get_debate_status(session_id)
    except Exception as e:
        logger.error(f"Error fetching debate status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/debate/result/{session_id}", tags=["Debate"])
async def api_get_debate_result(session_id: str):
    """Get final debate result and verdict"""
    try:
        return await get_debate_result(session_id)
    except Exception as e:
        logger.error(f"Error fetching debate result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AWS LAMBDA HANDLER (for AWS API Gateway)
# ============================================================================

def lambda_handler(event, context):
    """AWS Lambda handler for API Gateway integration"""
    try:
        from mangum import Mangum
        asgi_handler = Mangum(app)
        return asgi_handler(event, context)
    except ImportError:
        logger.warning("mangum not installed - Lambda support disabled")
        raise


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Stock Debate Advisor API Service...")
    logger.info(f"   Running on http://0.0.0.0:8000")
    logger.info(f"   OpenAPI Docs: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )
