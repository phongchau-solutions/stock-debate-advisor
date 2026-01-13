"""
Constants and enums for the CrewAI Stock Debate System.
Following SOLID, DRY, and KISS principles.
"""
from enum import Enum, auto
from typing import Final


# ============================================================================
# ENUMS
# ============================================================================

class AgentRole(Enum):
    """Agent role types."""
    FUNDAMENTAL = "Fundamental Analyst"
    TECHNICAL = "Technical Analyst"
    SENTIMENT = "Sentiment Analyst"
    MODERATOR = "Moderator"
    JUDGE = "Judge"


class InvestmentAction(Enum):
    """Investment recommendation actions."""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class ConfidenceLevel(Enum):
    """Confidence levels for recommendations."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DebateDecision(Enum):
    """Judge's decision on debate continuation."""
    CONTINUE = "CONTINUE"
    CONCLUDE = "CONCLUDE"


class AgentColor(Enum):
    """UI colors for different agents."""
    FUNDAMENTAL = "#e3f2fd"
    TECHNICAL = "#f3e5f5"
    SENTIMENT = "#e8f5e9"
    MODERATOR = "#fff3e0"
    JUDGE = "#fce4ec"


class AgentBorderColor(Enum):
    """UI border colors for different agents."""
    FUNDAMENTAL = "#1976d2"
    TECHNICAL = "#7b1fa2"
    SENTIMENT = "#388e3c"
    MODERATOR = "#f57c00"
    JUDGE = "#c2185b"


class AgentEmoji(Enum):
    """Emoji for different agents."""
    FUNDAMENTAL = "📊"
    TECHNICAL = "📈"
    SENTIMENT = "📰"
    MODERATOR = "🎭"
    JUDGE = "⚖️"


# ============================================================================
# NUMBER FORMATTING
# ============================================================================

class NumberScale(Enum):
    """Number scales with thresholds and suffixes."""
    TRILLION = (1_000_000_000_000, "T")
    BILLION = (1_000_000_000, "B")
    MILLION = (1_000_000, "M")
    THOUSAND = (1_000, "K")
    
    def __init__(self, threshold: int, suffix: str):
        self.threshold = threshold
        self.suffix = suffix


# ============================================================================
# UI CONSTANTS
# ============================================================================

class UIConstants:
    """UI-related constants."""
    PAGE_TITLE: Final[str] = "Stock Debate AI - CrewAI Edition"
    PAGE_ICON: Final[str] = "📊"
    LAYOUT: Final[str] = "wide"
    
    # Chat styling
    CHAT_MESSAGE_WIDTH: Final[str] = "70%"
    BORDER_RADIUS: Final[str] = "10px"
    BORDER_WIDTH: Final[str] = "4px"
    
    # Default port
    DEFAULT_PORT: Final[int] = 8501


# ============================================================================
# DATA CONSTANTS
# ============================================================================

class DataConstants:
    """Data loading and formatting constants."""
    # File naming
    FINANCIALS_SUFFIX: Final[str] = "_financials"
    OHLC_SUFFIX: Final[str] = "_ohlc"
    NEWS_SUFFIX: Final[str] = "_news"
    
    # Formatting
    DECIMAL_PLACES: Final[int] = 2
    MIN_FORMAT_THRESHOLD: Final[int] = 1000
    CSV_ENCODING: Final[str] = "utf-8"
    
    # Data limits
    MAX_NEWS_ARTICLES: Final[int] = 10
    MAX_HISTORICAL_DAYS: Final[int] = 365


# ============================================================================
# DEBATE CONSTANTS
# ============================================================================

class DebateConstants:
    """Debate orchestration constants."""
    MIN_ROUNDS: Final[int] = 2
    DEFAULT_ROUNDS: Final[int] = 3
    MAX_ROUNDS: Final[int] = 5
    ANALYST_COUNT: Final[int] = 3  # Fundamental, Technical, Sentiment
    CONTEXT_WINDOW: Final[int] = 5  # Recent statements to include in context
    
    # Verbosity settings
    VERBOSE: Final[bool] = True
    
    # Task timeout in seconds
    TASK_TIMEOUT: Final[int] = 60


# ============================================================================
# PROMPT CONSTANTS
# ============================================================================

class PromptConstants:
    """Prompt-related constants and templates."""
    PROMPTS_DIR: Final[str] = "prompts"
    
    # Prompt instructions
    FIRST_STATEMENT: Final[str] = "This is your first statement in this debate. Provide a comprehensive analysis without worrying about repetition."
    
    MEMORY_HEADER: Final[str] = "Your previous statements in this debate:\n"
    NO_REPETITION_WARNING: Final[str] = "Do NOT repeat what you've already said. Build upon your previous points, respond to critiques, or provide new insights."
    
    DEBATE_CONTEXT_HEADER: Final[str] = "Recent debate context from other analysts:\n"
    BUILD_ON_CONTEXT: Final[str] = "\n\nUse this context to build on, critique, or support other analysts' points. Show how your analysis relates to what others have said."
    
    CRITICAL_INSTRUCTIONS_HEADER: Final[str] = "CRITICAL INSTRUCTIONS:"
    SENTENCE_REQUIREMENT: Final[str] = "Keep your response to 3-5 sentences maximum for clarity and impact."
    CRITICISM_RESPONSE_REQUIREMENT: Final[str] = "If another analyst criticized your previous point, respond to that criticism directly."
    NUMBER_SUPPORT_REQUIREMENT: Final[str] = "Support your recommendation with specific numbers or data points."
    
    # Data length limit
    MAX_DATA_LENGTH: Final[int] = 2000


# ============================================================================
# LLM CONSTANTS
# ============================================================================

class LLMConstants:
    """LLM configuration constants."""
    DEFAULT_MODEL: Final[str] = "gemini-1.5-flash"
    CREWAI_MODEL: Final[str] = "gemini-1.5-pro"
    DEFAULT_TEMPERATURE: Final[float] = 0.7
    DEFAULT_MAX_TOKENS: Final[int] = 1024
    DEBATE_MAX_TOKENS: Final[int] = 500  # Shorter outputs for debate


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Error message templates."""
    NO_API_KEY: Final[str] = "GEMINI_API_KEY environment variable not set"
    NO_FINANCE_DATA: Final[str] = "Finance data directory not found: {path}"
    NO_NEWS_DATA: Final[str] = "News data directory not found: {path}"
    NO_DATA_AVAILABLE: Final[str] = "No data available for analysis"
    FILE_NOT_FOUND: Final[str] = "Data file not found for symbol: {symbol}"
    LLM_GENERATION_ERROR: Final[str] = "Error generating response: {error}"
    ANALYSIS_ERROR: Final[str] = "Error during analysis: {error}"


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Success message templates."""
    DEBATE_STARTED: Final[str] = "🚀 Debate started for {symbol}"
    ROUND_STARTED: Final[str] = "📍 Round {round} started"
    ANALYSIS_COMPLETE: Final[str] = "✅ Analysis complete: {agent}"
    DEBATE_CONCLUDED: Final[str] = "🎉 Debate concluded with verdict: {verdict}"


# ============================================================================
# REGEX PATTERNS
# ============================================================================

class RegexPatterns:
    """Regular expression patterns for parsing."""
    INVESTMENT_ACTION: Final[str] = r"(BUY|HOLD|SELL)"
    CONFIDENCE_LEVEL: Final[str] = r"(LOW|MEDIUM|HIGH|Low|Medium|High)"
    PERCENTAGE: Final[str] = r"(\d+(?:\.\d+)?%)"
