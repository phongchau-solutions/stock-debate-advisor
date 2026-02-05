"""Analysis endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_optional_user
from app.schemas.ai import AnalysisRequest, AnalysisResponse
from app.services.orchestration.debate import DebateOrchestrator

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_stock(
    request: AnalysisRequest,
    user_id: str = Depends(get_optional_user),
):
    """
    Run a stock debate analysis with bull and bear agents.

    This endpoint orchestrates a multi-agent debate for a stock symbol.
    The bull agent provides bullish arguments while the bear agent provides bearish arguments.
    """
    orchestrator = DebateOrchestrator(provider=request.provider)

    result = await orchestrator.run_debate(request.stock_symbol)

    return AnalysisResponse(
        debate_id=result["debate_id"],
        stock_symbol=result["stock_symbol"],
        status=result["status"],
        bull_argument=result.get("bull_argument"),
        bear_argument=result.get("bear_argument"),
        message="Debate analysis completed successfully",
    )
