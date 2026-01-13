"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum


class InvestmentAction(str, Enum):
    """Investment recommendation actions"""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class ConfidenceLevel(str, Enum):
    """Confidence levels for recommendations"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DebateRequest(BaseModel):
    """Request model for starting a debate"""
    symbol: str
    rounds: int = 3
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "MBB",
                "rounds": 3
            }
        }


class DebateSessionResponse(BaseModel):
    """Response when debate session is created"""
    session_id: str
    symbol: str
    rounds: int
    status: str  # "pending", "in_progress", "completed"
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "symbol": "MBB",
                "rounds": 3,
                "status": "in_progress",
                "created_at": "2025-01-10T10:30:00Z"
            }
        }


class VerdictResponse(BaseModel):
    """Final verdict response"""
    recommendation: InvestmentAction
    confidence: ConfidenceLevel
    rationale: str
    score: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": "BUY",
                "confidence": "HIGH",
                "rationale": "Strong fundamentals and positive sentiment",
                "score": 8.5
            }
        }


class DebateResultResponse(BaseModel):
    """Complete debate result with all information"""
    session_id: str
    symbol: str
    status: str  # "completed", "failed", "in_progress"
    rounds: int
    verdict: Optional[VerdictResponse] = None
    debate_summary: Optional[str] = None
    financial_data: Optional[Dict[str, Any]] = None
    technical_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "symbol": "MBB",
                "status": "completed",
                "rounds": 3,
                "verdict": {
                    "recommendation": "BUY",
                    "confidence": "HIGH",
                    "rationale": "Strong growth indicators",
                    "score": 8.5
                },
                "debate_summary": "The analysts discussed...",
                "completed_at": "2025-01-10T10:40:00Z"
            }
        }


class SymbolListResponse(BaseModel):
    """Response with available symbols"""
    symbols: List[str]
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["MBB", "VCB", "ACB"],
                "count": 3
            }
        }


class DebateStatusResponse(BaseModel):
    """Response for checking debate status"""
    session_id: str
    symbol: str
    status: str  # "pending", "in_progress", "completed", "failed"
    progress: int  # percentage
    current_round: int
    total_rounds: int
    estimated_completion: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "symbol": "MBB",
                "status": "in_progress",
                "progress": 66,
                "current_round": 2,
                "total_rounds": 3,
                "estimated_completion": "2025-01-10T10:40:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid symbol",
                "detail": "Symbol MBB not found in database"
            }
        }
