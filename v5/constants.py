"""
Constants and enums for the stock debate system.
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
    PAGE_TITLE: Final[str] = "Stock Debate AI"
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
    FILE_EXTENSIONS: Final[tuple] = ('.json', '.csv')
    CSV_ENCODING: Final[str] = 'utf-8'
    
    # File naming patterns
    FINANCIALS_SUFFIX: Final[str] = "_financials"
    OHLC_SUFFIX: Final[str] = "_ohlc"
    NEWS_SUFFIX: Final[str] = "_news"
    
    # Number formatting
    DECIMAL_PLACES: Final[int] = 2
    MIN_FORMAT_THRESHOLD: Final[int] = 1_000_000  # Format numbers >= 1M


# ============================================================================
# DEBATE CONSTANTS
# ============================================================================

class DebateConstants:
    """Constants for debate flow control."""
    MIN_ROUNDS: Final[int] = 2
    DEFAULT_ROUNDS: Final[int] = 10
    MAX_ROUNDS: Final[int] = 20
    ANALYST_COUNT: Final[int] = 3  # Number of analyst agents (Fundamental, Technical, Sentiment)
    CONTEXT_WINDOW: Final[int] = 6  # Last N statements to include in context
    SUMMARY_LENGTH: Final[int] = 100  # Characters to show in summaries
    FULL_DEBATE_LENGTH: Final[int] = 9  # Last N entries for full debate summary


# ============================================================================
# LLM CONSTANTS
# ============================================================================

class LLMConstants:
    """LLM configuration constants."""
    DEFAULT_MODEL: Final[str] = "gemini-2.0-flash"
    DEFAULT_TEMPERATURE: Final[float] = 0.7
    DEFAULT_MAX_TOKENS: Final[int] = 2048
    
    # Alternative models
    FLASH_MODEL: Final[str] = "gemini-1.5-flash"
    PRO_MODEL: Final[str] = "gemini-1.5-pro"


# ============================================================================
# PROMPT CONSTANTS
# ============================================================================

class PromptConstants:
    """Prompt templates and instructions for agents."""
    PROMPTS_DIR: Final[str] = "prompts"
    
    # Memory-related prompts
    FIRST_STATEMENT: Final[str] = "This is your first statement in the debate."
    MEMORY_HEADER: Final[str] = "YOUR PREVIOUS STATEMENTS IN THIS DEBATE:\n"
    NO_REPETITION_WARNING: Final[str] = (
        "⚠️ CRITICAL: You MUST NOT repeat any of these points. "
        "Introduce NEW analysis, data, or perspectives."
    )
    
    # Critical instructions for analysts
    CRITICAL_INSTRUCTIONS_HEADER: Final[str] = "CRITICAL INSTRUCTIONS:"
    SENTENCE_REQUIREMENT: Final[str] = "Provide EXACTLY 1-2 sentences with specific numbers"
    CRITICISM_RESPONSE_REQUIREMENT: Final[str] = "If responding to criticism, address it directly"
    NUMBER_SUPPORT_REQUIREMENT: Final[str] = "Use numbers to support your position"
    
    # Debate context building
    DEBATE_CONTEXT_HEADER: Final[str] = "RECENT DEBATE CONTEXT:\n"
    BUILD_ON_CONTEXT: Final[str] = "\nBuild on these points with NEW insights. Do not repeat.\n"
    
    # Data truncation
    MAX_DATA_LENGTH: Final[int] = 1500


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Standardized error messages with placeholders."""
    # Configuration errors
    NO_API_KEY: Final[str] = "GEMINI_API_KEY is not set in environment variables"
    NO_FINANCE_DATA: Final[str] = "Finance data path does not exist: {path}"
    NO_NEWS_DATA: Final[str] = "News data path does not exist: {path}"
    CONFIGURATION_ERROR: Final[str] = "Configuration error: {error}"
    
    # Data errors
    FILE_NOT_FOUND: Final[str] = "No data file found for symbol: {symbol}"
    INVALID_SYMBOL: Final[str] = "Invalid stock symbol: {symbol}"
    DATA_LOAD_ERROR: Final[str] = "Failed to load data: {error}"
    NO_DATA_AVAILABLE: Final[str] = "No data available"
    LOAD_ERROR: Final[str] = "Error loading data: {error}"
    
    # LLM errors
    LLM_GENERATION_ERROR: Final[str] = "Error generating response: {error}"
    ANALYSIS_ERROR: Final[str] = "Unable to analyze: {error}"


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Standardized success messages."""
    DATA_LOADED: Final[str] = "✅ Data loaded for {symbol}"
    DEBATE_STARTED: Final[str] = "🔍 Starting multi-agent debate for {symbol}..."
    ROUND_STARTED: Final[str] = "🔄 Round {round}..."
    DEBATE_CONCLUDED: Final[str] = "✅ Debate concluded with verdict: {verdict}"


# ============================================================================
# AGENT EMOJIS
# ============================================================================

class AgentEmoji:
    """Emojis for different agents."""
    FUNDAMENTAL: Final[str] = "💼"
    TECHNICAL: Final[str] = "📈"
    SENTIMENT: Final[str] = "💭"
    MODERATOR: Final[str] = "⚖️"
    JUDGE: Final[str] = "👨‍⚖️"


# ============================================================================
# REGEX PATTERNS
# ============================================================================

class RegexPatterns:
    """Common regex patterns."""
    CRITIQUE_DETECTION: Final[str] = r"(Technical|Fundamental|Sentiment)\s+(Analyst|Agent)"
    SYMBOL_VALIDATION: Final[str] = r"^[A-Z]{3,5}$"
    NUMBER_EXTRACTION: Final[str] = r"\d+\.?\d*"
