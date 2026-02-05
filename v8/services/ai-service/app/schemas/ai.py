"""AI-related schemas."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AIProvider(str, Enum):
    """AI provider enumeration."""

    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


class AgentRole(str, Enum):
    """Agent role enumeration."""

    BULL = "bull"
    BEAR = "bear"
    JUDGE = "judge"


class AnalysisRequest(BaseModel):
    """Request schema for stock debate analysis."""

    stock_symbol: str = Field(..., min_length=1, max_length=10)
    provider: Optional[AIProvider] = None
    bull_agent_config: Optional[dict] = None
    bear_agent_config: Optional[dict] = None


class AnalysisResponse(BaseModel):
    """Response schema for stock debate analysis."""

    debate_id: str
    stock_symbol: str
    status: str
    bull_argument: Optional[str] = None
    bear_argument: Optional[str] = None
    message: str


class JudgeRequest(BaseModel):
    """Request schema for judge verdict."""

    debate_id: str = Field(..., min_length=1)
    bull_argument: str = Field(..., min_length=1)
    bear_argument: str = Field(..., min_length=1)
    provider: Optional[AIProvider] = None


class JudgeResponse(BaseModel):
    """Response schema for judge verdict."""

    debate_id: str
    verdict: str
    reasoning: str
    winner: AgentRole
    confidence: float = Field(..., ge=0.0, le=1.0)


class AgentInfo(BaseModel):
    """Information about an AI agent."""

    id: str
    name: str
    role: AgentRole
    provider: AIProvider
    model: str
    description: str


class AgentListResponse(BaseModel):
    """Response schema for listing agents."""

    agents: list[AgentInfo]
    total: int
