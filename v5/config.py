"""
Configuration loader for the Gemini Multi-Agent Stock Debate PoC.
Follows SOLID principles with proper separation of concerns.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from constants import (
    LLMConstants,
    DebateConstants,
    PromptConstants,
    ErrorMessages
)

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the debate system.
    
    Single Responsibility: Manages all configuration settings.
    Open/Closed: Can be extended without modification.
    """
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", LLMConstants.DEFAULT_MODEL)
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", str(LLMConstants.DEFAULT_TEMPERATURE)))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", str(LLMConstants.DEFAULT_MAX_TOKENS)))
    
    # Data paths
    BASE_DIR = Path(__file__).parent
    FINANCE_DATA_PATH: Path = BASE_DIR / os.getenv("FINANCE_DATA_PATH", "./data/finance")
    NEWS_DATA_PATH: Path = BASE_DIR / os.getenv("NEWS_DATA_PATH", "./data/news")
    
    # Debate configuration
    MIN_ROUNDS: int = int(os.getenv("MIN_ROUNDS", str(DebateConstants.MIN_ROUNDS)))
    MAX_ROUNDS: int = int(os.getenv("MAX_ROUNDS", str(DebateConstants.MAX_ROUNDS)))
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", str(DebateConstants.DEFAULT_ROUNDS)))
    AGENTS_PER_ROUND: int = DebateConstants.ANALYST_COUNT
    
    # System prompts directory
    PROMPTS_DIR: Path = BASE_DIR / PromptConstants.PROMPTS_DIR
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configurations are set.
        
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If API key is missing
            FileNotFoundError: If required directories don't exist
        """
        if not cls.GEMINI_API_KEY:
            raise ValueError(ErrorMessages.NO_API_KEY)
            
        if not cls.FINANCE_DATA_PATH.exists():
            raise FileNotFoundError(
                ErrorMessages.NO_FINANCE_DATA.format(path=cls.FINANCE_DATA_PATH)
            )
            
        if not cls.NEWS_DATA_PATH.exists():
            raise FileNotFoundError(
                ErrorMessages.NO_NEWS_DATA.format(path=cls.NEWS_DATA_PATH)
            )
            
        return True


config = Config()

