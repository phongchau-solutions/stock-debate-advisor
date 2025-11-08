"""Base adapter interface for financial data sources."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import pandas as pd


class BaseDataAdapter(ABC):
    """Abstract base class for financial data adapters."""
    
    def __init__(self, source_name: str):
        """
        Initialize the adapter.
        
        Args:
            source_name: Name of the data source (e.g., 'vietcap', 'yfinance')
        """
        self.source_name = source_name
    
    @abstractmethod
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval (default: '1d')
            
        Returns:
            DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
            Index: DatetimeIndex
        """
        pass
    
    @abstractmethod
    async def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company overview information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information (name, sector, market_cap, etc.)
        """
        pass
    
    @abstractmethod
    async def fetch_financials(self, symbol: str, period: str = 'annual') -> Dict[str, Any]:
        """
        Fetch financial statements and ratios.
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarterly'
            
        Returns:
            Dictionary with financial data (pe, roe, revenue, net_income, etc.)
        """
        pass
    
    async def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current stock price.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if unavailable
        """
        # Default implementation: try to get last close from OHLCV
        try:
            from datetime import datetime, timedelta
            end = datetime.now()
            start = end - timedelta(days=7)
            
            df = await self.fetch_ohlcv(
                symbol, 
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d')
            )
            
            if not df.empty:
                return float(df['close'].iloc[-1])
        except Exception:
            pass
        
        return None
    
    def is_available(self) -> bool:
        """
        Check if the adapter is available (API accessible).
        
        Returns:
            True if adapter can be used, False otherwise
        """
        return True
