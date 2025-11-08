"""
Configuration loader for the Gemini Multi-Agent Stock Debate PoC.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the debate system."""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Data paths
    BASE_DIR = Path(__file__).parent
    FINANCE_DATA_PATH: Path = BASE_DIR / os.getenv("FINANCE_DATA_PATH", "../../data/finance")
    NEWS_DATA_PATH: Path = BASE_DIR / os.getenv("NEWS_DATA_PATH", "../../data/news")
    
    # Debate configuration
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", "4"))
    AGENTS_PER_ROUND: int = int(os.getenv("AGENTS_PER_ROUND", "3"))
    
    # System prompts directory
    PROMPTS_DIR: Path = BASE_DIR / "prompts"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configurations are set."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        if not cls.FINANCE_DATA_PATH.exists():
            raise FileNotFoundError(f"Finance data path does not exist: {cls.FINANCE_DATA_PATH}")
        if not cls.NEWS_DATA_PATH.exists():
            raise FileNotFoundError(f"News data path does not exist: {cls.NEWS_DATA_PATH}")
        return True

config = Config()
