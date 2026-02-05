"""Agents endpoints."""

from fastapi import APIRouter, status

from app.config import get_settings
from app.schemas.ai import AgentInfo, AgentListResponse, AgentRole, AIProvider

router = APIRouter(prefix="/agents", tags=["agents"])

settings = get_settings()


@router.get("", response_model=AgentListResponse, status_code=status.HTTP_200_OK)
async def list_agents():
    """
    List available AI agents and their configurations.

    Returns information about:
    - Available agent roles (bull, bear, judge)
    - Supported AI providers (Gemini, OpenAI, Claude)
    - Model configurations
    """
    agents = [
        AgentInfo(
            id="bull_gemini",
            name="Bull Agent (Gemini)",
            role=AgentRole.BULL,
            provider=AIProvider.GEMINI,
            model=settings.gemini_model,
            description="Bullish stock analyst powered by Google Gemini",
        ),
        AgentInfo(
            id="bear_gemini",
            name="Bear Agent (Gemini)",
            role=AgentRole.BEAR,
            provider=AIProvider.GEMINI,
            model=settings.gemini_model,
            description="Bearish stock analyst powered by Google Gemini",
        ),
        AgentInfo(
            id="judge_gemini",
            name="Judge (Gemini)",
            role=AgentRole.JUDGE,
            provider=AIProvider.GEMINI,
            model=settings.gemini_model,
            description="Impartial debate judge powered by Google Gemini",
        ),
        AgentInfo(
            id="bull_openai",
            name="Bull Agent (OpenAI)",
            role=AgentRole.BULL,
            provider=AIProvider.OPENAI,
            model=settings.openai_model,
            description="Bullish stock analyst powered by OpenAI GPT",
        ),
        AgentInfo(
            id="bear_openai",
            name="Bear Agent (OpenAI)",
            role=AgentRole.BEAR,
            provider=AIProvider.OPENAI,
            model=settings.openai_model,
            description="Bearish stock analyst powered by OpenAI GPT",
        ),
        AgentInfo(
            id="judge_openai",
            name="Judge (OpenAI)",
            role=AgentRole.JUDGE,
            provider=AIProvider.OPENAI,
            model=settings.openai_model,
            description="Impartial debate judge powered by OpenAI GPT",
        ),
    ]

    return AgentListResponse(agents=agents, total=len(agents))
