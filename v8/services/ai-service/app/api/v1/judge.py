"""Judge endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_optional_user
from app.schemas.ai import JudgeRequest, JudgeResponse
from app.services.orchestration.debate import DebateOrchestrator

router = APIRouter(prefix="/judge", tags=["judge"])


@router.post("", response_model=JudgeResponse, status_code=status.HTTP_200_OK)
async def judge_debate(
    request: JudgeRequest,
    user_id: str = Depends(get_optional_user),
):
    """
    Get a judge's verdict on a debate.

    The judge agent evaluates both bull and bear arguments and provides:
    - A verdict summary
    - Detailed reasoning
    - The winning side
    - Confidence score (0-1)
    """
    orchestrator = DebateOrchestrator(provider=request.provider)

    result = await orchestrator.judge_debate(
        request.debate_id,
        request.bull_argument,
        request.bear_argument,
    )

    return JudgeResponse(
        debate_id=result["debate_id"],
        verdict=result["verdict"],
        reasoning=result["reasoning"],
        winner=result["winner"],
        confidence=result["confidence"],
    )
