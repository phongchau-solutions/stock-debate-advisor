"""
CrewAI Tools for Data Service Integration
Tools that agents can use to fetch and analyze data
"""

from crewai.tools import tool
from agent_data_client import get_agent_data_client
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Fundamental Analysis Tools

@tool
def fetch_financial_reports(session_id: str) -> str:
    """
    Fetch financial reports and metrics for the debate session.
    
    Args:
        session_id: The debate session ID
        
    Returns:
        Formatted financial knowledge for analysis
    """
    client = get_agent_data_client()
    knowledge = client.get_fundamental_knowledge(session_id)
    
    if not knowledge:
        return "Unable to fetch financial data. Please check session ID."
    
    return knowledge


@tool
def analyze_financial_metrics(symbol: str) -> str:
    """
    Get detailed financial metrics for a specific symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'TPB', 'MBB')
        
    Returns:
        Detailed financial metrics and analysis
    """
    client = get_agent_data_client()
    data = client.get_financial_data(symbol)
    
    if not data:
        return f"No financial data available for {symbol}"
    
    # Format the response
    response = f"Financial Data for {symbol}\n"
    response += "=" * 50 + "\n"
    
    if "reports" in data:
        for report in data["reports"]:
            response += f"\nPeriod: {report.get('period', 'Unknown')}\n"
            response += f"Company: {report.get('company', 'Unknown')}\n"
            response += "Key Metrics:\n"
            
            metrics = report.get("metrics", {})
            for key, value in list(metrics.items())[:15]:  # Top 15 metrics
                if not key.startswith("_"):
                    if isinstance(value, float) and 0 < value < 1:
                        response += f"  {key}: {value*100:.2f}%\n"
                    else:
                        response += f"  {key}: {value}\n"
    
    return response


# Technical Analysis Tools

@tool
def fetch_technical_data(session_id: str) -> str:
    """
    Fetch technical analysis data for the debate session.
    
    Args:
        session_id: The debate session ID
        
    Returns:
        Formatted technical knowledge with price data and indicators
    """
    client = get_agent_data_client()
    knowledge = client.get_technical_knowledge(session_id)
    
    if not knowledge:
        return "Unable to fetch technical data. Please check session ID."
    
    return knowledge


@tool
def analyze_price_action(symbol: str) -> str:
    """
    Get technical price data and analysis.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Price action analysis and OHLCV data
    """
    client = get_agent_data_client()
    data = client.get_technical_data(symbol)
    
    if not data:
        return f"No technical data available for {symbol}"
    
    response = f"Technical Analysis for {symbol}\n"
    response += "=" * 50 + "\n"
    response += f"Current Price: {data.get('current_price', 'N/A'):,} VND\n"
    response += f"Data Points: {data.get('data_points', 0)}\n"
    response += f"Period: {data.get('period', 'N/A')}\n"
    
    if "latest_ohlc" in data:
        ohlc = data["latest_ohlc"]
        response += f"\nLatest OHLCV ({ohlc.get('date', 'N/A')}):\n"
        response += f"  Open:   {ohlc.get('open', 0):,.0f} VND\n"
        response += f"  High:   {ohlc.get('high', 0):,.0f} VND\n"
        response += f"  Low:    {ohlc.get('low', 0):,.0f} VND\n"
        response += f"  Close:  {ohlc.get('close', 0):,.0f} VND\n"
        response += f"  Volume: {ohlc.get('volume', 0):,} shares\n"
    
    return response


# Sentiment Analysis Tools

@tool
def fetch_sentiment_data(session_id: str) -> str:
    """
    Fetch sentiment analysis data and news for the debate session.
    
    Args:
        session_id: The debate session ID
        
    Returns:
        Formatted sentiment knowledge with news articles and sentiment summary
    """
    client = get_agent_data_client()
    knowledge = client.get_sentiment_knowledge(session_id)
    
    if not knowledge:
        return "Unable to fetch sentiment data. Please check session ID."
    
    return knowledge


@tool
def analyze_news_sentiment(symbol: str) -> str:
    """
    Get recent news articles and sentiment analysis.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        News articles with sentiment classification
    """
    client = get_agent_data_client()
    data = client.get_news_data(symbol)
    
    if not data:
        return f"No news data available for {symbol}"
    
    response = f"News and Sentiment Analysis for {symbol}\n"
    response += "=" * 50 + "\n"
    response += f"Total Articles: {data.get('total_articles', 0)}\n"
    response += "\nRecent News:\n"
    
    for i, article in enumerate(data.get("articles", [])[:10], 1):
        sentiment = article.get("sentiment", "neutral").upper()
        emoji = "📈" if sentiment == "POSITIVE" else "📉" if sentiment == "NEGATIVE" else "➡️"
        
        response += f"\n{i}. {emoji} [{article.get('date', 'N/A')}] {article.get('title', 'Unknown')}\n"
        response += f"   Sentiment: {sentiment}\n"
        response += f"   Summary: {article.get('summary', 'N/A')}\n"
        response += f"   Source: {article.get('source', 'Unknown')}\n"
    
    return response


# Session Context Tools

@tool
def get_session_context(session_id: str) -> str:
    """
    Get the debate session context and available data.
    
    Args:
        session_id: The debate session ID
        
    Returns:
        Session information and data availability
    """
    client = get_agent_data_client()
    info = client.get_session_info(session_id)
    
    if not info:
        return f"Session {session_id} not found"
    
    response = f"Session Context\n"
    response += "=" * 50 + "\n"
    response += f"Symbol: {info.get('symbol', 'N/A')}\n"
    response += f"Created: {info.get('created_at', 'N/A')}\n"
    response += f"Current Round: {info.get('current_round', 0)}\n"
    
    data = info.get("data", {})
    response += f"\nAvailable Data:\n"
    response += f"  Financial Reports: {data.get('financial_reports', 0)}\n"
    response += f"  Technical Data Points: {data.get('technical_datapoints', 0)}\n"
    response += f"  News Articles: {data.get('news_articles', 0)}\n"
    response += f"  Current Price: {data.get('current_price', 'N/A')} VND\n"
    
    return response


# Comparative Analysis Tool

@tool
def compare_all_perspectives(session_id: str) -> str:
    """
    Get all analysis perspectives (fundamental, technical, sentiment) for comparison.
    
    Args:
        session_id: The debate session ID
        
    Returns:
        Combined perspective from all analysis types
    """
    client = get_agent_data_client()
    
    knowledge = client.get_all_knowledge(session_id)
    
    response = "COMPREHENSIVE ANALYSIS - ALL PERSPECTIVES\n"
    response += "=" * 70 + "\n\n"
    
    # Fundamental
    response += "📊 FUNDAMENTAL PERSPECTIVE\n"
    response += "-" * 70 + "\n"
    response += knowledge.get("fundamental", "No fundamental data available") + "\n\n"
    
    # Technical
    response += "📈 TECHNICAL PERSPECTIVE\n"
    response += "-" * 70 + "\n"
    response += knowledge.get("technical", "No technical data available") + "\n\n"
    
    # Sentiment
    response += "📰 SENTIMENT PERSPECTIVE\n"
    response += "-" * 70 + "\n"
    response += knowledge.get("sentiment", "No sentiment data available") + "\n"
    
    return response


# Tool registry for CrewAI
AGENT_TOOLS = [
    fetch_financial_reports,
    analyze_financial_metrics,
    fetch_technical_data,
    analyze_price_action,
    fetch_sentiment_data,
    analyze_news_sentiment,
    get_session_context,
    compare_all_perspectives
]
