import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
        # Bedrock configuration - Claude Sonnet 3.5
        self.BEDROCK_MODEL: str = os.getenv("BEDROCK_MODEL", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.BEDROCK_REGION: str = os.getenv("AWS_REGION", "us-east-1")
        # Model parameters
        self.TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
        self.MIN_ROUNDS: int = int(os.getenv("MIN_ROUNDS", "1"))
        self.MAX_ROUNDS: int = int(os.getenv("MAX_ROUNDS", "5"))
        self.VERBOSE: bool = os.getenv("VERBOSE", "false").lower() == "true"
        
        # Data store configuration - try to find it relative to project root
        data_store_env = os.getenv("DATA_STORE_PATH")
        if data_store_env:
            self.DATA_STORE_PATH: Path = Path(data_store_env)
        else:
            # Try to find data_store relative to project root (v7/)
            # Points to v7/data_store/data/2026 where actual stock data is stored
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent.parent.parent  # Go up to v7/
            self.DATA_STORE_PATH: Path = project_root / "data_store" / "data" / "2026"
        
        # DynamoDB table names
        self.COMPANIES_TABLE: str = os.getenv("COMPANIES_TABLE", "companies")
        self.FINANCIAL_REPORTS_TABLE: str = os.getenv("FINANCIAL_REPORTS_TABLE", "financial_reports")
        self.OHLC_PRICES_TABLE: str = os.getenv("OHLC_PRICES_TABLE", "ohlc_prices")
        self.DEBATE_RESULTS_TABLE: str = os.getenv("DEBATE_RESULTS_TABLE", "debate_results")

    def validate(self):
        if self.ENVIRONMENT == "dev":
            if not self.DATA_STORE_PATH.exists():
                raise ValueError(f"Data store path not found: {self.DATA_STORE_PATH}")
        # Bedrock is available in Lambda automatically via IAM role

settings = Settings()

