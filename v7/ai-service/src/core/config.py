import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    MIN_ROUNDS: int = int(os.getenv("MIN_ROUNDS", "1"))
    MAX_ROUNDS: int = int(os.getenv("MAX_ROUNDS", "5"))
    VERBOSE: bool = os.getenv("VERBOSE", "false").lower() == "true"
    DATA_STORE_PATH: Path = Path(os.getenv("DATA_STORE_PATH", "data_store/data"))

    def validate(self):
        if self.ENVIRONMENT not in ("lambda", "dev"):
            if not self.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")
        if self.ENVIRONMENT == "dev":
            if not self.DATA_STORE_PATH.exists():
                raise ValueError(f"Data store path not found: {self.DATA_STORE_PATH}")

settings = Settings()
