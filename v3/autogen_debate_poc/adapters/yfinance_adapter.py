"""YFinance adapter for fallback stock data."""

from typing import Dict, Any, Optional
import pandas as pd
import logging
from datetime import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    
from adapters.base_adapter import BaseDataAdapter

logger = logging.getLogger(__name__)


class YFinanceAdapter(BaseDataAdapter):
    """Adapter for Yahoo Finance API (fallback data source)."""
    
    def __init__(self):
        super().__init__('yfinance')
    
    def is_available(self) -> bool:
        """Check if yfinance library is installed."""
        return YFINANCE_AVAILABLE
    
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol with .VN suffix for Vietnamese stocks
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval (default: '1d')
            
        Returns:
            DataFrame with OHLCV data
        """
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance library not installed")
            return pd.DataFrame()
        
        try:
            # Add .VN suffix for Vietnamese stocks if not present
            ticker_symbol = f"{symbol}.VN" if not symbol.endswith('.VN') else symbol
            
            df = yf.download(
                ticker_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False
            )
            
            if df.empty:
                logger.warning(f"No data from yfinance for {ticker_symbol}")
                return pd.DataFrame()
            
            # Standardize column names (yfinance uses title case)
            df.columns = [col.lower() for col in df.columns]
            
            # Select only OHLCV columns
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"yfinance fetch_ohlcv failed for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    async def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company info
        """
        if not YFINANCE_AVAILABLE:
            return {'symbol': symbol, 'error': 'yfinance not available', 'source': 'yfinance'}
        
        try:
            ticker_symbol = f"{symbol}.VN" if not symbol.endswith('.VN') else symbol
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName', '')),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'pe': info.get('trailingPE', 0),
                'pb': info.get('priceToBook', 0),
                'eps': info.get('trailingEps', 0),
                'source': 'yfinance'
            }
            
        except Exception as e:
            logger.error(f"yfinance fetch_company_info failed for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e), 'source': 'yfinance'}
    
    async def fetch_financials(self, symbol: str, period: str = 'annual') -> Dict[str, Any]:
        """
        Fetch financial data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarterly'
            
        Returns:
            Dictionary with financial data
        """
        if not YFINANCE_AVAILABLE:
            return {'symbol': symbol, 'error': 'yfinance not available', 'source': 'yfinance'}
        
        try:
            ticker_symbol = f"{symbol}.VN" if not symbol.endswith('.VN') else symbol
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Get basic financial ratios from info
            return {
                'symbol': symbol,
                'pe': float(info.get('trailingPE', 0)),
                'pb': float(info.get('priceToBook', 0)),
                'roe': float(info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0),
                'roa': float(info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0),
                'eps': float(info.get('trailingEps', 0)),
                'dividend_yield': float(info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0),
                'revenue': float(info.get('totalRevenue', 0)),
                'net_income': float(info.get('netIncomeToCommon', 0)),
                'market_cap': float(info.get('marketCap', 0)),
                'has_detailed_financials': False,
                'source': 'yfinance'
            }
            
        except Exception as e:
            logger.error(f"yfinance fetch_financials failed for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e), 'source': 'yfinance'}
