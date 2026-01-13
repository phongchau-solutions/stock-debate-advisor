"""
CrewAI Agents for the Stock Debate System.

This module implements five specialized agents using CrewAI:
- FundamentalAgent: Analyzes financial statements and metrics
- TechnicalAgent: Analyzes price data and technical indicators
- SentimentAgent: Analyzes news sentiment and market psychology
- ModeratorAgent: Facilitates debate and synthesis
- JudgeAgent: Makes final investment decision

Design Principles:
- CrewAI framework for orchestration
- Memory management built into CrewAI
- Collaborative problem-solving
- Agents access data via data service tools
"""
from typing import Dict, Any, List
from pathlib import Path
from crewai import Agent, Task, Crew
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from data_loader import DataLoader
from constants import (
    AgentRole, InvestmentAction, ConfidenceLevel,
    PromptConstants, ErrorMessages, LLMConstants, DebateConstants
)
from agent_tools import (
    fetch_financial_reports, analyze_financial_metrics,
    fetch_technical_data, analyze_price_action,
    fetch_sentiment_data, analyze_news_sentiment,
    get_session_context, compare_all_perspectives
)


def get_llm():
    """Get configured LLM instance for CrewAI."""
    return ChatGoogleGenerativeAI(
        model=config.CREWAI_MODEL,
        temperature=config.TEMPERATURE,
        api_key=config.GEMINI_API_KEY,
        max_output_tokens=config.MAX_TOKENS,
    )


def load_prompt(agent_name: str) -> str:
    """
    Load system prompt from prompts directory.
    
    Args:
        agent_name: Name of the agent (e.g., 'fundamental_analyst')
    
    Returns:
        Loaded prompt text or default fallback
    """
    prompt_file = Path(__file__).parent / PromptConstants.PROMPTS_DIR / f"{agent_name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"You are a {agent_name.replace('_', ' ')}."


class DebateAgents:
    """
    Factory class for creating CrewAI agents for the debate system.
    
    Responsibilities:
    - Create agents with proper roles and backstories
    - Configure agent-specific parameters
    - Handle agent initialization
    """
    
    def __init__(self):
        """Initialize the agents factory."""
        self.loader = DataLoader()
        self.stock_data = {}  # Cache for stock data
        self.llm = get_llm()  # Initialize LLM
    
    def create_fundamental_agent(self, context_data: str = "", session_id: str = "") -> Agent:
        """
        Create the Fundamental Analyst agent with data service tools.
        
        Args:
            context_data: Optional context about the stock
            session_id: Session ID for data service calls
            
        Returns:
            Configured CrewAI Agent with tools
        """
        backstory = load_prompt("fundamental_analyst")
        if session_id:
            backstory += f"\n\nYou have access to a data service with financial data for the current debate session ({session_id}). You can fetch financial reports and detailed metrics using your tools."
        
        return Agent(
            role="Fundamental Analyst",
            goal="Provide insightful fundamental analysis of stocks based on financial statements, ratios, and valuation metrics. Use data service tools to fetch and analyze financial data.",
            backstory=backstory,
            tools=[fetch_financial_reports, analyze_financial_metrics, get_session_context],
            verbose=config.VERBOSE,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            max_iter=3,
            max_retry_limit=1
        )
    
    def create_technical_agent(self, context_data: str = "", session_id: str = "") -> Agent:
        """
        Create the Technical Analyst agent with data service tools.
        
        Args:
            context_data: Optional context about the stock
            session_id: Session ID for data service calls
            
        Returns:
            Configured CrewAI Agent with tools
        """
        backstory = load_prompt("technical_analyst")
        if session_id:
            backstory += f"\n\nYou have access to a data service with technical data for the current debate session ({session_id}). You can fetch price data and technical indicators using your tools."
        
        return Agent(
            role="Technical Analyst",
            goal="Provide technical analysis insights focusing on price trends, technical indicators, and chart patterns. Use data service tools to fetch and analyze technical data.",
            backstory=backstory,
            tools=[fetch_technical_data, analyze_price_action, get_session_context],
            verbose=config.VERBOSE,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            max_iter=3,
            max_retry_limit=1
        )
    
    def create_sentiment_agent(self, context_data: str = "", session_id: str = "") -> Agent:
        """
        Create the Sentiment Analyst agent with data service tools.
        
        Args:
            context_data: Optional context about the stock
            session_id: Session ID for data service calls
            
        Returns:
            Configured CrewAI Agent with tools
        """
        backstory = load_prompt("sentiment_analyst")
        if session_id:
            backstory += f"\n\nYou have access to a data service with news and sentiment data for the current debate session ({session_id}). You can fetch news articles and sentiment analysis using your tools."
        
        return Agent(
            role="Sentiment Analyst",
            goal="Assess market sentiment, news impact, and investor psychology regarding the stock. Use data service tools to fetch and analyze sentiment data.",
            backstory=backstory,
            tools=[fetch_sentiment_data, analyze_news_sentiment, get_session_context],
            verbose=config.VERBOSE,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            max_iter=3,
            max_retry_limit=1
        )
    
    def create_moderator_agent(self, session_id: str = "") -> Agent:
        """
        Create the Moderator agent with tools for data access.
        
        Args:
            session_id: Session ID for data service calls
        
        Returns:
            Configured CrewAI Agent
        """
        backstory = load_prompt("moderator")
        if session_id:
            backstory += f"\n\nYou can access comprehensive debate data using your tools to help synthesize perspectives."
        
        return Agent(
            role="Debate Moderator",
            goal="Facilitate productive discussion between analysts and help them reach consensus by understanding all available data.",
            backstory=backstory,
            tools=[get_session_context, compare_all_perspectives],
            verbose=config.VERBOSE,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            max_iter=5,
            max_retry_limit=2
        )
    
    def create_judge_agent(self, session_id: str = "") -> Agent:
        """
        Create the Judge agent with tools for comprehensive review.
        
        Args:
            session_id: Session ID for data service calls
        
        Returns:
            Configured CrewAI Agent
        """
        backstory = load_prompt("judge")
        if session_id:
            backstory += f"\n\nYou can access the complete debate data and all analysis perspectives using your tools."
        
        return Agent(
            role="Investment Judge",
            goal="Evaluate the debate quality and make a final BUY/HOLD/SELL recommendation based on all perspectives and data.",
            backstory=backstory,
            tools=[get_session_context, compare_all_perspectives],
            verbose=config.VERBOSE,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            max_iter=3,
            max_retry_limit=1
        )


class AnalysisTasks:
    """
    Factory class for creating analysis tasks in CrewAI.
    
    Responsibilities:
    - Create tasks for each agent
    - Define task descriptions and expected outputs
    - Handle task sequencing
    """
    
    @staticmethod
    def create_fundamental_analysis_task(
        agent: Agent, 
        symbol: str, 
        financial_data: str,
        debate_round: int = 1,
        session_id: str = ""
    ) -> Task:
        """
        Create a fundamental analysis task with data service integration.
        
        Args:
            agent: The fundamental analyst agent
            symbol: Stock symbol
            financial_data: Formatted financial data
            debate_round: Current debate round
            session_id: Session ID for data service calls
            
        Returns:
            CrewAI Task
        """
        round_context = f" (Round {debate_round})" if debate_round > 1 else ""
        
        data_instructions = ""
        if session_id:
            data_instructions = f"""

IMPORTANT - You have data service tools available:
- Use 'fetch_financial_reports' to get the latest financial data for session {session_id}
- Use 'analyze_financial_metrics' to get detailed metrics for {symbol}
- Use 'get_session_context' to understand the debate session status

Please call these tools to fetch fresh data for your analysis."""
        
        description = f"""Analyze the stock {symbol} from a fundamental perspective{round_context}.

Financial Data:
{financial_data}

Provide your analysis in 3-5 sentences. Reference specific metrics and numbers. End with your recommendation: BUY, HOLD, or SELL.

If this is Round 2 or later, respond to any critiques from other analysts and provide new insights without repeating yourself.{data_instructions}"""
        
        return Task(
            description=description,
            agent=agent,
            expected_output="A detailed fundamental analysis with specific metrics, numbers, and a clear BUY/HOLD/SELL recommendation.",
            async_execution=False
        )
    
    @staticmethod
    def create_technical_analysis_task(
        agent: Agent,
        symbol: str,
        technical_data: str,
        debate_round: int = 1,
        session_id: str = ""
    ) -> Task:
        """
        Create a technical analysis task with data service integration.
        
        Args:
            agent: The technical analyst agent
            symbol: Stock symbol
            technical_data: Formatted technical/OHLC data
            debate_round: Current debate round
            session_id: Session ID for data service calls
            
        Returns:
            CrewAI Task
        """
        round_context = f" (Round {debate_round})" if debate_round > 1 else ""
        
        data_instructions = ""
        if session_id:
            data_instructions = f"""

IMPORTANT - You have data service tools available:
- Use 'fetch_technical_data' to get the latest technical data for session {session_id}
- Use 'analyze_price_action' to get detailed price analysis for {symbol}
- Use 'get_session_context' to understand the debate session status

Please call these tools to fetch fresh data for your analysis."""
        
        description = f"""Analyze the stock {symbol} from a technical perspective{round_context}.

Technical Data:
{technical_data}

Provide your analysis in 3-5 sentences. Reference specific price levels, chart patterns, and technical indicators. End with your recommendation: BUY, HOLD, or SELL.

If this is Round 2 or later, respond to any critiques from other analysts and provide new technical insights without repeating yourself.{data_instructions}"""
        
        return Task(
            description=description,
            agent=agent,
            expected_output="A detailed technical analysis with specific price levels, indicators, patterns, and a clear BUY/HOLD/SELL recommendation.",
            async_execution=False
        )
    
    @staticmethod
    def create_sentiment_analysis_task(
        agent: Agent,
        symbol: str,
        news_data: str,
        debate_round: int = 1,
        session_id: str = ""
    ) -> Task:
        """
        Create a sentiment analysis task with data service integration.
        
        Args:
            agent: The sentiment analyst agent
            symbol: Stock symbol
            news_data: Formatted news and sentiment data
            debate_round: Current debate round
            session_id: Session ID for data service calls
            
        Returns:
            CrewAI Task
        """
        round_context = f" (Round {debate_round})" if debate_round > 1 else ""
        
        data_instructions = ""
        if session_id:
            data_instructions = f"""

IMPORTANT - You have data service tools available:
- Use 'fetch_sentiment_data' to get the latest sentiment data for session {session_id}
- Use 'analyze_news_sentiment' to get detailed news analysis for {symbol}
- Use 'get_session_context' to understand the debate session status

Please call these tools to fetch fresh data for your analysis."""
        
        description = f"""Analyze the stock {symbol} from a sentiment perspective{round_context}.

News and Sentiment Data:
{news_data}

Provide your analysis in 3-5 sentences. Reference specific news items and sentiment indicators. End with your recommendation: BUY, HOLD, or SELL.

If this is Round 2 or later, respond to any critiques from other analysts and provide new sentiment insights without repeating yourself.{data_instructions}"""
        
        return Task(
            description=description,
            agent=agent,
            expected_output="A detailed sentiment analysis with specific news references, sentiment assessment, and a clear BUY/HOLD/SELL recommendation.",
            async_execution=False
        )
    
    @staticmethod
    def create_moderation_task(
        agent: Agent,
        symbol: str,
        analysts_input: str
    ) -> Task:
        """
        Create a moderation/synthesis task.
        
        Args:
            agent: The moderator agent
            symbol: Stock symbol
            analysts_input: Summary of all analysts' views
            
        Returns:
            CrewAI Task
        """
        description = f"""As the moderator, synthesize the debate on stock {symbol}.

Analysts' Perspectives:
{analysts_input}

Your role is to:
1. Identify areas of agreement and disagreement
2. Ask probing questions about conflicting points
3. Help the team move toward consensus
4. Highlight the strongest and weakest arguments

Provide a 4-6 sentence synthesis that moves the debate forward."""
        
        return Task(
            description=description,
            agent=agent,
            expected_output="A synthesis of the debate highlighting areas of agreement, disagreement, and paths toward consensus.",
            async_execution=False
        )
    
    @staticmethod
    def create_final_judgment_task(
        agent: Agent,
        symbol: str,
        debate_summary: str
    ) -> Task:
        """
        Create the final judgment task.
        
        Args:
            agent: The judge agent
            symbol: Stock symbol
            debate_summary: Summary of the entire debate
            
        Returns:
            CrewAI Task
        """
        description = f"""Make the final investment recommendation for {symbol} based on the debate.

Debate Summary:
{debate_summary}

Evaluate all three perspectives and make a final decision. Format your response as:

**FINAL RECOMMENDATION: [BUY/HOLD/SELL]**
**Confidence: [High/Medium/Low]**
**Key Rationale:**
- [Reason 1]
- [Reason 2]  
- [Reason 3]"""
        
        return Task(
            description=description,
            agent=agent,
            expected_output="A final investment recommendation with confidence level and clear rationale based on the debate.",
            async_execution=False
        )
