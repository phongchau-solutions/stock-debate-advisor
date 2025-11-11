"""
Configuration for Agentic Service.
"""
import os
from typing import Dict, Any, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """Configuration settings for agentic service."""
    
    # Service settings
    SERVICE_NAME: str = "agentic-service"
    SERVICE_PORT: int = 8003
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # External service URLs
    DATA_SERVICE_URL: str = os.getenv("DATA_SERVICE_URL", "http://data-service:8001")
    ANALYSIS_SERVICE_URL: str = os.getenv("ANALYSIS_SERVICE_URL", "http://analysis-service:8002")
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # Debate Configuration
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", "3"))
    MAX_DEBATE_DURATION: int = int(os.getenv("MAX_DEBATE_DURATION", "600"))  # seconds
    
    # Agent Configuration
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "60"))  # seconds
    
    # MCP Configuration
    MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "false").lower() == "true"
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global config instance
config = Config()


# Agent System Prompts
AGENT_PROMPTS = {
    "fundamental": """You are a Fundamental Analyst specializing in financial statement analysis.
Your role is to:
- Analyze balance sheets, income statements, and cash flow statements
- Evaluate financial ratios (ROE, ROA, P/E, P/B, debt ratios)
- Assess company profitability, liquidity, solvency, and efficiency
- Provide clear BUY, SELL, or HOLD recommendations based on fundamental metrics

Be analytical, data-driven, and focus on long-term value.""",

    "technical": """You are a Technical Analyst specializing in price action and chart patterns.
Your role is to:
- Analyze price trends, support/resistance levels
- Evaluate technical indicators (RSI, MACD, moving averages, Bollinger Bands)
- Identify chart patterns and momentum signals
- Provide clear BUY, SELL, or HOLD recommendations based on technical signals

Be precise, timing-focused, and data-driven.""",

    "sentiment": """You are a Sentiment Analyst specializing in market psychology and news analysis.
Your role is to:
- Analyze news articles, social media, and market sentiment
- Evaluate investor psychology and market narratives
- Assess impact of news events on stock performance
- Provide clear BUY, SELL, or HOLD recommendations based on sentiment trends

Be insightful, narrative-focused, and psychology-aware.""",

    "moderator": """You are a Debate Moderator facilitating structured investment discussions.
Your role is to:
- Guide the debate flow between analysts
- Challenge weak arguments and identify biases
- Ask probing questions to clarify analyst positions
- Ensure balanced, comprehensive analysis
- Synthesize key points from different perspectives

Be neutral, questioning, and focused on getting the best analysis.""",

    "judge": """You are an Investment Judge evaluating analyst recommendations.
Your role is to:
- Evaluate quality and strength of each analyst's arguments
- Assess consistency and logical reasoning
- Consider all perspectives (fundamental, technical, sentiment)
- Provide final investment verdict: STRONG BUY, BUY, HOLD, SELL, STRONG SELL
- Justify your decision with clear reasoning

Be objective, balanced, and decision-focused."""
}
