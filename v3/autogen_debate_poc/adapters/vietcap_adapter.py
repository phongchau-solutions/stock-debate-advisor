"""Vietcap adapter for Vietnamese stock data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'ref' / 'zstock'))

from typing import Dict, Any, Optional
import pandas as pd
import logging
from datetime import datetime, timedelta

from zstock import ZStock
from adapters.base_adapter import BaseDataAdapter

logger = logging.getLogger(__name__)


class VietcapAdapter(BaseDataAdapter):
    """Adapter for Vietcap API using the ref/zstock library."""
    
    def __init__(self):
        super().__init__('vietcap')
        self._available = None
        self._test_availability()
    
    def _test_availability(self):
        """Test if Vietcap API is accessible."""
        try:
            # Quick test with a simple query
            test_stock = ZStock(symbols='VNM', source='VIETCAP')
            end = datetime.now()
            start = end - timedelta(days=5)
            
            history = test_stock.history(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d')
            )
            
            # If we get data, API is available
            self._available = bool(history and 'VNM' in history and not history['VNM'].empty)
            
            if not self._available:
                logger.warning("Vietcap API test returned empty data - API may be blocked")
            else:
                logger.info("Vietcap API is available")
                
        except Exception as e:
            self._available = False
            logger.warning(f"Vietcap API is not available: {str(e)[:100]}")
    
    def is_available(self) -> bool:
        """Check if Vietcap API is accessible."""
        return self._available if self._available is not None else False
    
    async def fetch_ohlcv(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Vietcap.
        
        Args:
            symbol: Vietnamese stock symbol (e.g., 'VNM', 'VIC')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Time interval (default: '1d')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = ZStock(symbols=symbol, source='VIETCAP')
            history = stock.history(start=start_date, end=end_date, interval=interval)
            
            if history and symbol in history:
                df = history[symbol]
                if not df.empty:
                    # Ensure standard column names
                    return df[['open', 'high', 'low', 'close', 'volume']]
            
            logger.warning(f"No OHLCV data from Vietcap for {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Vietcap fetch_ohlcv failed for {symbol}: {str(e)[:200]}")
            return pd.DataFrame()
    
    async def fetch_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information from Vietcap.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company info
        """
        try:
            stock = ZStock(symbols=symbol, source='VIETCAP')
            company_data = stock.companies[symbol].overview()
            
            return {
                'symbol': symbol,
                'company_name': company_data.get('company_name', ''),
                'sector': company_data.get('sector', ''),
                'industry': company_data.get('industry', ''),
                'market_cap': company_data.get('market_cap', 0),
                'pe': company_data.get('pe', 0),
                'pb': company_data.get('pb', 0),
                'eps': company_data.get('eps', 0),
                'source': 'vietcap'
            }
            
        except Exception as e:
            logger.error(f"Vietcap fetch_company_info failed for {symbol}: {str(e)[:200]}")
            return {'symbol': symbol, 'error': str(e), 'source': 'vietcap'}
    
    async def fetch_financials(self, symbol: str, period: str = 'annual') -> Dict[str, Any]:
        """
        Fetch financial statements and ratios from Vietcap.
        
        Args:
            symbol: Stock symbol
            period: 'annual' or 'quarterly'
            
        Returns:
            Dictionary with financial data
        """
        try:
            stock = ZStock(symbols=symbol, source='VIETCAP')
            
            # Fetch company overview for ratios
            company_info = stock.companies[symbol].overview()
            
            # Try to fetch balance sheet
            try:
                balance_sheet = stock.finances[symbol].balance_sheet(period=period, lang='en')
                has_balance_sheet = not balance_sheet.empty
            except Exception:
                has_balance_sheet = False
            
            return {
                'symbol': symbol,
                'pe': float(company_info.get('pe', 0)),
                'pb': float(company_info.get('pb', 0)),
                'roe': float(company_info.get('roe', 0)),
                'roa': float(company_info.get('roa', 0)),
                'eps': float(company_info.get('eps', 0)),
                'dividend_yield': float(company_info.get('dividend_yield', 0)),
                'revenue': float(company_info.get('revenue', 0)),
                'net_income': float(company_info.get('net_income', 0)),
                'market_cap': float(company_info.get('market_cap', 0)),
                'has_detailed_financials': has_balance_sheet,
                'source': 'vietcap'
            }
            
        except Exception as e:
            logger.error(f"Vietcap fetch_financials failed for {symbol}: {str(e)[:200]}")
            return {'symbol': symbol, 'error': str(e), 'source': 'vietcap'}
