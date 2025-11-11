"""
Analysis Tools for Autogen Agents.
These tools allow agents to fetch data from other microservices.
"""
import requests
from typing import Dict, Any, Optional
import logging
from app.config import config

logger = logging.getLogger(__name__)


class AnalysisTools:
    """Tools for agents to fetch analysis data."""
    
    def __init__(self):
        """Initialize analysis tools."""
        self.data_service_url = config.DATA_SERVICE_URL
        self.analysis_service_url = config.ANALYSIS_SERVICE_URL
    
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch financial data for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Financial data dict
        """
        try:
            response = requests.get(
                f"{self.data_service_url}/api/v1/financial/{symbol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            return {}
    
    def get_price_data(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Fetch price data for a symbol.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history
        
        Returns:
            Price data dict
        """
        try:
            response = requests.get(
                f"{self.data_service_url}/api/v1/prices/{symbol}",
                params={"days": days},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            return {}
    
    def get_news_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch news articles for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            News data dict
        """
        try:
            response = requests.get(
                f"{self.data_service_url}/api/v1/news/{symbol}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return {}
    
    def get_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get fundamental analysis from analysis service.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Fundamental analysis dict
        """
        try:
            response = requests.post(
                f"{self.analysis_service_url}/api/v1/fundamental/{symbol}",
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting fundamental analysis: {e}")
            return {}
    
    def get_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get technical analysis from analysis service.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Technical analysis dict
        """
        try:
            response = requests.post(
                f"{self.analysis_service_url}/api/v1/technical/{symbol}",
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting technical analysis: {e}")
            return {}
    
    def get_sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment analysis from analysis service.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Sentiment analysis dict
        """
        try:
            response = requests.post(
                f"{self.analysis_service_url}/api/v1/sentiment/{symbol}",
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting sentiment analysis: {e}")
            return {}
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive analysis from analysis service.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Comprehensive analysis dict
        """
        try:
            response = requests.post(
                f"{self.analysis_service_url}/api/v1/analyze/{symbol}",
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting comprehensive analysis: {e}")
            return {}


# Singleton instance
analysis_tools = AnalysisTools()
