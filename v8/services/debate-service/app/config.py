from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Debate Service"
    app_version: str = "8.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/stock_debate"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
