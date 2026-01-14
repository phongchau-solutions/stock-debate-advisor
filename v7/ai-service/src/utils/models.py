from typing import Dict, Any
from pydantic import BaseModel, Field

class DebateRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(default="3 months", description="Investment timeframe (1 month, 3 months, 6 months, 1 year)")
    min_rounds: int = Field(default=1, ge=1, le=5)
    max_rounds: int = Field(default=5, ge=1, le=10)

class RoundResponse(BaseModel):
    round_num: int
    fundamental: str
    technical: str
    sentiment: str
    judge_decision: str

class DebateResponse(BaseModel):
    ticker: str
    timeframe: str
    actual_rounds: int
    rounds: list[RoundResponse]
    final_recommendation: str
    confidence: str
    rationale: str
    risks: str
    monitor: str

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "2.0"
