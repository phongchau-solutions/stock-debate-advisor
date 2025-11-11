"""
Debate agents for the Gemini Multi-Agent Stock Debate PoC.
Simplified implementation for v5 following SOLID principles.

This module implements the five specialized agents:
- FundamentalAgent: Analyzes financial statements and metrics
- TechnicalAgent: Analyzes price data and technical indicators
- SentimentAgent: Analyzes news sentiment and market psychology
- ModeratorAgent: Synthesizes all arguments and manages debate flow
- JudgeAgent: Makes final investment decision

Design Principles:
- Single Responsibility: Each agent has one clear purpose
- Open/Closed: Extensible through inheritance
- Dependency Inversion: Depends on abstractions (config, constants)
"""
from typing import Dict, Any, List
from pathlib import Path
import google.generativeai as genai
from config import config
from data_loader import DataLoader
from constants import (
    AgentRole, InvestmentAction, ConfidenceLevel,
    PromptConstants, ErrorMessages, LLMConstants
)


def load_prompt(agent_name: str) -> str:
    """
    Load system prompt from prompts directory.
    
    Args:
        agent_name: Name of the agent (e.g., 'fundamental_agent')
    
    Returns:
        Loaded prompt text or default fallback
    """
    prompt_file = Path(__file__).parent / PromptConstants.PROMPTS_DIR / f"{agent_name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"You are a {agent_name.replace('_', ' ')}."


class BaseAgent:
    """
    Base class for all debate agents with conversation memory.
    
    Implements:
    - Conversation history tracking (prevents repetition)
    - Gemini API integration
    - Memory-aware response generation
    """
    
    def __init__(self, name: str, role: str, prompt_file: str = None):
        """
        Initialize base agent.
        
        Args:
            name: Display name of the agent
            role: Role description
            prompt_file: Optional prompt file name (without .txt extension)
        """
        self.name = name
        self.role = role
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        # Conversation memory - stores all previous statements from this agent
        self.conversation_history: List[str] = []
        
        # Load system prompt
        if prompt_file:
            self.system_prompt = load_prompt(prompt_file)
        else:
            self.system_prompt = f"You are {role}."
    
    def add_to_memory(self, statement: str):
        """
        Add a statement to this agent's conversation history.
        
        Args:
            statement: Statement to remember
        """
        self.conversation_history.append(statement)
    
    def get_memory_context(self) -> str:
        """
        Get formatted memory context for prompt.
        
        Returns:
            Formatted string of previous statements with anti-repetition warning
        """
        if not self.conversation_history:
            return PromptConstants.FIRST_STATEMENT
        
        memory_text = PromptConstants.MEMORY_HEADER
        for i, stmt in enumerate(self.conversation_history, 1):
            memory_text += f"{i}. {stmt}\n"
        memory_text += f"\n{PromptConstants.NO_REPETITION_WARNING}"
        return memory_text
    
    def reset_memory(self):
        """Reset conversation history (for new debates)."""
        self.conversation_history = []
        
    def generate_response(self, prompt: str, include_memory: bool = True) -> str:
        """
        Generate response using Gemini with conversation memory.
        
        Args:
            prompt: User prompt to send to LLM
            include_memory: Whether to include conversation history
        
        Returns:
            Generated response text
        """
        try:
            # Build full prompt with system prompt, memory, and user prompt
            full_prompt = f"{self.system_prompt}\n\n"
            
            if include_memory:
                full_prompt += f"{self.get_memory_context()}\n\n"
            
            full_prompt += prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config.TEMPERATURE,
                    max_output_tokens=config.MAX_TOKENS,
                )
            )
            
            # Store the response in memory
            response_text = response.text
            if include_memory:
                self.add_to_memory(response_text)
            
            return response_text
        except Exception as e:
            return ErrorMessages.LLM_GENERATION_ERROR.format(error=e)


class FundamentalAgent(BaseAgent):
    """
    Analyzes fundamental data (financial statements and metrics).
    
    Focuses on:
    - Financial ratios (P/E, ROE, etc.)
    - Revenue and profit trends
    - Balance sheet health
    """
    
    def __init__(self, name: str = None):
        """Initialize Fundamental Agent."""
        if name is None:
            name = AgentRole.FUNDAMENTAL.value
        super().__init__(name, "Fundamental Analysis Expert", "fundamental_agent")
        self.loader = DataLoader()
        self.orchestrator_data = None  # Data provided by orchestrator
        self.cutoff_date = None  # Analysis cutoff date
        
    def analyze(self, symbol: str, debate_context: str = "", data: Dict = None, cutoff_date: Any = None, timeframe: str = "3 months") -> Dict[str, Any]:
        """
        Analyze fundamental data with debate context.
        
        Args:
            symbol: Stock ticker symbol
            debate_context: Previous debate rounds context
            data: Optional pre-loaded data from orchestrator
            cutoff_date: Optional cutoff date for historical analysis
            timeframe: Analysis timeframe (e.g., "1 month", "3 months", "6 months", "1 year")
        
        Returns:
            Dictionary with agent name, analysis, and data source
        """
        try:
            # Use provided data if available, otherwise load it
            if data and 'financial' in data:
                financial_data = data['financial']
                cutoff_date = data.get('cutoff_date')
            else:
                financial_data = self.loader.load_financial_data(symbol)
            
            # Add date context if analyzing historical data
            date_context = ""
            if cutoff_date:
                date_context = f"\n\n**IMPORTANT**: You are analyzing as of {cutoff_date}. You do NOT have access to any data or events after this date. Make your analysis based solely on information available up to {cutoff_date}."
            
            # Add timeframe context
            timeframe_context = f"\n\n**ANALYSIS TIMEFRAME: {timeframe}**\nYour recommendation must be specifically valid for the {timeframe} timeframe. Consider how fundamentals will play out over this specific period. A stock may be a BUY for 1 year but HOLD for 1 month - be specific to this {timeframe} timeframe."
            
            # Build investment action options for prompt
            action_options = "/".join([action.value for action in InvestmentAction])
            
            prompt = f"""Stock Symbol: {symbol}

Financial Data (latest available):
{str(financial_data)[:PromptConstants.MAX_DATA_LENGTH]}
{date_context}{timeframe_context}

{debate_context}

{PromptConstants.CRITICAL_INSTRUCTIONS_HEADER}
1. {PromptConstants.SENTENCE_REQUIREMENT}
2. End with "{action_options} because [specific reason for {timeframe} timeframe]"
3. {PromptConstants.CRITICISM_RESPONSE_REQUIREMENT}
4. {PromptConstants.NUMBER_SUPPORT_REQUIREMENT}

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "financial_statements"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": ErrorMessages.ANALYSIS_ERROR.format(error=e),
                "error": str(e)
            }


class TechnicalAgent(BaseAgent):
    """
    Analyzes technical indicators and price data.
    
    Focuses on:
    - Price trends and momentum
    - Support and resistance levels
    - Volume analysis
    """
    
    def __init__(self, name: str = None):
        """Initialize Technical Agent."""
        if name is None:
            name = AgentRole.TECHNICAL.value
        super().__init__(name, "Technical Analysis Expert", "technical_agent")
        self.loader = DataLoader()
        
    def analyze(self, symbol: str, debate_context: str = "", data: Dict = None, cutoff_date: Any = None, timeframe: str = "3 months") -> Dict[str, Any]:
        """
        Analyze technical data (OHLC) with debate context.
        
        Args:
            symbol: Stock ticker symbol
            debate_context: Previous debate rounds context
            data: Optional pre-loaded data from orchestrator
            cutoff_date: Optional cutoff date for historical analysis
            timeframe: Analysis timeframe (e.g., "1 month", "3 months", "6 months", "1 year")
        
        Returns:
            Dictionary with agent name, analysis, and data source
        """
        try:
            # Use provided data if available, otherwise load it
            if data and 'technical' in data:
                ohlc_data = data['technical']
                cutoff_date = data.get('cutoff_date')
            else:
                ohlc_data = self.loader.load_technical_data(symbol)
            
            if not ohlc_data:
                return {
                    "agent": self.name,
                    "analysis": ErrorMessages.NO_DATA_AVAILABLE,
                    "error": "Data not found"
                }
            
            # Add date context if analyzing historical data
            date_context = ""
            if cutoff_date:
                date_context = f"\n\n**IMPORTANT**: You are analyzing as of {cutoff_date}. You do NOT have access to any price data or market events after this date. Base your technical analysis only on data available up to {cutoff_date}."
            
            # Add timeframe context
            timeframe_context = f"\n\n**ANALYSIS TIMEFRAME: {timeframe}**\nYour technical analysis and recommendation must be valid specifically for the {timeframe} timeframe. Consider appropriate indicators for this period - daily RSI for 1 month vs weekly trends for 1 year. Your BUY/HOLD/SELL is for {timeframe}, not indefinite."
            
            summary = ohlc_data.get('summary', {})
            latest = summary.get('price_stats', {}).get('latest_close', 0)
            high = summary.get('price_stats', {}).get('high', 0)
            low = summary.get('price_stats', {}).get('low', 0)
            
            # Build investment action options for prompt
            action_options = "/".join([action.value for action in InvestmentAction])
            
            prompt = f"""Stock Symbol: {symbol}

Technical Data (as of {cutoff_date if cutoff_date else 'latest'}):
- Latest: {latest:,.0f} VND
- High: {high:,.0f} VND  
- Low: {low:,.0f} VND
{date_context}{timeframe_context}

{debate_context}

{PromptConstants.CRITICAL_INSTRUCTIONS_HEADER}
1. {PromptConstants.SENTENCE_REQUIREMENT}
2. End with "{action_options} because [specific technical reason for {timeframe}]"
3. {PromptConstants.CRITICISM_RESPONSE_REQUIREMENT}
4. Use specific price points and trends relevant for {timeframe}

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "ohlc_prices"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": ErrorMessages.ANALYSIS_ERROR.format(error=e),
                "error": str(e)
            }


class SentimentAgent(BaseAgent):
    """
    Analyzes sentiment from news and market psychology.
    
    Focuses on:
    - News headlines and sentiment
    - Market psychology indicators
    - Public perception trends
    """
    
    def __init__(self, name: str = None):
        """Initialize Sentiment Agent."""
        if name is None:
            name = AgentRole.SENTIMENT.value
        super().__init__(name, "Sentiment Analysis Expert", "sentiment_agent")
        self.loader = DataLoader()
        
    def analyze(self, symbol: str, debate_context: str = "", data: Dict = None, cutoff_date: Any = None, timeframe: str = "3 months") -> Dict[str, Any]:
        """
        Analyze sentiment from news data with debate context.
        
        Args:
            symbol: Stock ticker symbol
            debate_context: Previous debate rounds context
            data: Optional pre-loaded data from orchestrator
            cutoff_date: Optional cutoff date for historical analysis
            timeframe: Analysis timeframe (e.g., "1 month", "3 months", "6 months", "1 year")
        
        Returns:
            Dictionary with agent name, analysis, and data source
        """
        try:
            # Use provided data if available, otherwise load it
            if data and 'sentiment' in data:
                news_data = data['sentiment']
                cutoff_date = data.get('cutoff_date')
            else:
                news_data = self.loader.load_sentiment_data(symbol)
            
            if not news_data:
                return {
                    "agent": self.name,
                    "analysis": ErrorMessages.NO_DATA_AVAILABLE,
                    "error": "Data not found"
                }
            
            # Add date context if analyzing historical data
            date_context = ""
            if cutoff_date:
                date_context = f"\n\n**IMPORTANT**: You are analyzing as of {cutoff_date}. You do NOT have access to any news or market sentiment after this date. Base your analysis only on information available up to {cutoff_date}."
            
            # Add timeframe context
            timeframe_context = f"\n\n**ANALYSIS TIMEFRAME: {timeframe}**\nYour sentiment analysis must be valid for the {timeframe} timeframe. News sentiment can be fleeting - distinguish between short-term noise and trends meaningful for {timeframe}. A negative headline today may not matter for a 1-year outlook. Your recommendation is for {timeframe}."
            
            articles = news_data.get('articles', [])
            summary = news_data.get('summary', {})
            
            # Get first article title
            first_title = articles[0].get('title', 'N/A') if articles else 'No news'
            
            # Build investment action options for prompt
            action_options = "/".join([action.value for action in InvestmentAction])
            
            prompt = f"""Stock Symbol: {symbol}

News Headlines (as of {cutoff_date if cutoff_date else 'latest'}):
{first_title}

Total articles: {summary.get('total_articles', 0)}
{date_context}{timeframe_context}

{debate_context}

{PromptConstants.CRITICAL_INSTRUCTIONS_HEADER}
1. {PromptConstants.SENTENCE_REQUIREMENT}
2. End with "{action_options} because [sentiment reason relevant for {timeframe}]"
3. {PromptConstants.CRITICISM_RESPONSE_REQUIREMENT}
4. Use specific headlines or trends as evidence, considering {timeframe} relevance

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "news_articles"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": ErrorMessages.ANALYSIS_ERROR.format(error=e),
                "error": str(e)
            }


class ModeratorAgent(BaseAgent):
    """
    Moderates the debate and synthesizes arguments.
    
    Responsibilities:
    - Summarize key points from all analysts
    - Identify areas of agreement and disagreement
    - Highlight strongest arguments
    - Guide debate flow
    """
    
    def __init__(self, name: str = None):
        """Initialize Moderator Agent."""
        if name is None:
            name = AgentRole.MODERATOR.value
        super().__init__(name, "Debate Moderator", "moderator_agent")
        
    def synthesize(self, analyses: list[Dict[str, Any]], debate_context: str = "") -> str:
        """
        Synthesize all agent analyses with debate context.
        
        Args:
            analyses: List of agent analysis results
            debate_context: Previous debate rounds context
        
        Returns:
            Synthesized summary text
        """
        prompt = f"""You are a debate moderator. Review these investment analyses and provide:
1. Summary of key points
2. Areas of agreement and disagreement
3. Which arguments are most compelling

Analyses:
{chr(10).join([f"{a.get('agent', 'Unknown')}: {a.get('analysis', 'N/A')}" for a in analyses])}

{debate_context}

Provide a balanced summary highlighting the strongest arguments.
"""
        
        return self.generate_response(prompt)


class JudgeAgent(BaseAgent):
    """
    Makes final investment decision.
    
    Responsibilities:
    - Review all analyst arguments
    - Consider moderator synthesis
    - Make BUY/HOLD/SELL decision
    - Provide confidence level (1-10)
    - Explain rationale with key factors
    """
    
    def __init__(self, name: str = None):
        """Initialize Judge Agent."""
        if name is None:
            name = AgentRole.JUDGE.value
        super().__init__(name, "Investment Decision Judge", "judge_agent")
        self.loader = DataLoader()
        
    def make_decision(
        self, 
        analyses: list[Dict[str, Any]], 
        moderator_summary: str, 
        debate_context: str = "",
        full_data: Dict = None,
        cutoff_date: Any = None,
        timeframe: str = "3 months"
    ) -> Dict[str, Any]:
        """
        Make final investment decision with debate context.
        
        Args:
            analyses: List of agent analysis results
            moderator_summary: Moderator's synthesis
            debate_context: Previous debate rounds context
            full_data: Full unfiltered data (including future data for verification)
            cutoff_date: The cutoff date that was used for the debate
            timeframe: Analysis timeframe (e.g., "1 month", "3 months", "6 months", "1 year")
        
        Returns:
            Dictionary with final decision, confidence, rationale, and key factors
        """
        # Build investment action options for prompt
        action_options = "/".join([action.value for action in InvestmentAction])
        
        # Add timeframe context
        timeframe_context = f"""

**CRITICAL - ANALYSIS TIMEFRAME: {timeframe}**
Your final verdict (BUY/HOLD/SELL) must be SPECIFICALLY valid for the {timeframe} timeframe.
- Consider how trends and catalysts will play out over {timeframe}
- A stock may be BUY for 1 year but HOLD for 1 month - be precise
- State clearly: "For {timeframe}: BUY/HOLD/SELL"
- Your reasoning must explain why this decision is right for THIS {timeframe} period
"""
        
        # Add verification context if we have future data
        verification_context = ""
        if cutoff_date and full_data:
            verification_context = f"""

**VERIFICATION CONTEXT**:
The analysts made their recommendations based on data available as of {cutoff_date}.
You now have access to ALL data, including events AFTER {cutoff_date}.

You should:
1. Make the final investment decision based on the debate arguments
2. Note whether subsequent actual data (after {cutoff_date}) validates or contradicts the analysts' predictions
3. This verification helps assess the quality of the analysis methodology

"""
            # Extract actual outcome if available
            if full_data.get('technical'):
                tech_data = full_data['technical']
                if 'data' in tech_data:
                    import pandas as pd
                    df = pd.DataFrame(tech_data['data'])
                    if 'date' in df.columns and 'close' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        cutoff_dt = pd.to_datetime(cutoff_date)
                        
                        # Get price at cutoff date
                        historical = df[df['date'] <= cutoff_dt]
                        future = df[df['date'] > cutoff_dt]
                        
                        if len(historical) > 0 and len(future) > 0:
                            cutoff_price = historical['close'].iloc[-1]
                            latest_price = future['close'].iloc[-1]
                            price_change = ((latest_price - cutoff_price) / cutoff_price) * 100
                            
                            verification_context += f"""
Actual Market Performance After {cutoff_date}:
- Price at cutoff: {cutoff_price:,.0f} VND
- Latest price: {latest_price:,.0f} VND
- Actual change: {price_change:+.2f}%

Compare this actual outcome with the analysts' recommendations to evaluate their accuracy.
"""
        
        prompt = f"""You are an investment judge. Based on all analyses, make a FINAL investment decision:

All Analyses:
{chr(10).join([f"{a.get('agent', 'Unknown')}: {a.get('analysis', 'N/A')[:500]}" for a in analyses])}

Moderator Summary:
{moderator_summary}

{debate_context}
{verification_context}

Provide your FINAL decision in this EXACT format with proper structure:

**FINAL DECISION**: [{action_options}]

**CONFIDENCE**: [1-10]

**RATIONALE**: 
[Write 2-3 clear sentences explaining your decision. Each sentence should address a different aspect of the analysis.]

**KEY FACTORS**:
• [Factor 1 - Be specific with data/numbers]
• [Factor 2 - Be specific with data/numbers]
• [Factor 3 - Be specific with data/numbers]
• [Factor 4 - Optional, if relevant]
• [Factor 5 - Optional, if relevant]
{f'''
**VERIFICATION**: 
[Analyze how the actual outcome compared to analyst predictions. Were they accurate? Which analyst was closest to the truth? What can we learn from this?]
''' if verification_context else ""}

Use bullet points (•) for lists, bold formatting (**text**) for headers, and clear paragraph breaks for readability.
"""
        
        response = self.generate_response(prompt)
        
        return {
            "agent": self.name,
            "decision": response,
            "role": "judge"
        }

