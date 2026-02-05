"""Base AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional


class AIProviderBase(ABC):
    """Base class for AI providers."""

    def __init__(self, api_key: str, model: str):
        """
        Initialize AI provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: System/instruction prompt (optional)

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def analyze_stock(self, stock_symbol: str, role: str) -> str:
        """
        Analyze a stock from a specific role perspective.

        Args:
            stock_symbol: Stock symbol to analyze
            role: Role perspective ('bull' or 'bear')

        Returns:
            Analysis text
        """
        pass

    @abstractmethod
    async def judge_debate(self, bull_argument: str, bear_argument: str) -> dict:
        """
        Judge a debate between bull and bear arguments.

        Args:
            bull_argument: Bull case argument
            bear_argument: Bear case argument

        Returns:
            Dictionary with verdict, reasoning, winner, and confidence
        """
        pass
