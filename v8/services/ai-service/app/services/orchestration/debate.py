"""Multi-agent orchestration logic."""

import uuid
from typing import Optional

from app.schemas.ai import AIProvider, AgentRole
from app.services.providers.factory import get_ai_provider


class DebateOrchestrator:
    """Orchestrates multi-agent debates."""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize orchestrator.

        Args:
            provider: AI provider to use
        """
        self.provider = provider
        self.ai_client = get_ai_provider(provider)

    async def run_debate(self, stock_symbol: str) -> dict:
        """
        Run a full debate for a stock.

        Args:
            stock_symbol: Stock symbol to debate

        Returns:
            Debate results dictionary
        """
        debate_id = f"debate_{uuid.uuid4().hex[:12]}"

        # Generate bull argument
        bull_argument = await self.ai_client.analyze_stock(stock_symbol, "bull")

        # Generate bear argument
        bear_argument = await self.ai_client.analyze_stock(stock_symbol, "bear")

        return {
            "debate_id": debate_id,
            "stock_symbol": stock_symbol,
            "bull_argument": bull_argument,
            "bear_argument": bear_argument,
            "status": "completed",
        }

    async def judge_debate(
        self, debate_id: str, bull_argument: str, bear_argument: str
    ) -> dict:
        """
        Judge a debate.

        Args:
            debate_id: Debate identifier
            bull_argument: Bull case argument
            bear_argument: Bear case argument

        Returns:
            Verdict dictionary
        """
        verdict = await self.ai_client.judge_debate(bull_argument, bear_argument)

        return {
            "debate_id": debate_id,
            **verdict,
        }
