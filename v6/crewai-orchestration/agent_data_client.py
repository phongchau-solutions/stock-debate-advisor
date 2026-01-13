"""
Agent Data Service Client
Agents use this to fetch data from the data service API
"""

import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentDataServiceClient:
    """Client for agents to fetch data from the data service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session_cache = {}
    
    def get_fundamental_knowledge(self, session_id: str) -> str:
        """
        Fetch fundamental analysis knowledge for a session
        
        Args:
            session_id: Debate session ID
            
        Returns:
            Formatted fundamental knowledge string
        """
        try:
            url = f"{self.base_url}/api/session/{session_id}/knowledge/fundamental"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("knowledge", "")
        except Exception as e:
            logger.error(f"Error fetching fundamental knowledge: {e}")
            return ""
    
    def get_technical_knowledge(self, session_id: str) -> str:
        """
        Fetch technical analysis knowledge for a session
        
        Args:
            session_id: Debate session ID
            
        Returns:
            Formatted technical knowledge string
        """
        try:
            url = f"{self.base_url}/api/session/{session_id}/knowledge/technical"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("knowledge", "")
        except Exception as e:
            logger.error(f"Error fetching technical knowledge: {e}")
            return ""
    
    def get_sentiment_knowledge(self, session_id: str) -> str:
        """
        Fetch sentiment analysis knowledge for a session
        
        Args:
            session_id: Debate session ID
            
        Returns:
            Formatted sentiment knowledge string
        """
        try:
            url = f"{self.base_url}/api/session/{session_id}/knowledge/sentiment"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("knowledge", "")
        except Exception as e:
            logger.error(f"Error fetching sentiment knowledge: {e}")
            return ""
    
    def get_all_knowledge(self, session_id: str) -> Dict[str, str]:
        """
        Fetch all knowledge types for a session
        
        Args:
            session_id: Debate session ID
            
        Returns:
            Dictionary with fundamental, technical, sentiment knowledge
        """
        try:
            url = f"{self.base_url}/api/session/{session_id}/knowledge/all"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("knowledge", {})
        except Exception as e:
            logger.error(f"Error fetching all knowledge: {e}")
            return {}
    
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch financial data for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Financial data dictionary
        """
        try:
            url = f"{self.base_url}/api/data/{symbol}/financials"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
            return {}
    
    def get_technical_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch technical data for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Technical data dictionary
        """
        try:
            url = f"{self.base_url}/api/data/{symbol}/technical"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching technical data: {e}")
            return {}
    
    def get_news_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch news data for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            News data dictionary
        """
        try:
            url = f"{self.base_url}/api/data/{symbol}/news"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return {}
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Fetch session information
        
        Args:
            session_id: Debate session ID
            
        Returns:
            Session information dictionary
        """
        try:
            url = f"{self.base_url}/api/session/{session_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching session info: {e}")
            return {}


# Global instance
_client = None


def get_agent_data_client() -> AgentDataServiceClient:
    """Get or create the global agent data service client"""
    global _client
    if _client is None:
        _client = AgentDataServiceClient()
    return _client
