"""
ZStock-style Financial Data Client - Direct adaptation from successful reference.

This module closely follows the zstock architecture for proven reliability.
"""

from __future__ import annotations

import logging
import requests
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

from .vietcap_client import VietcapClient

logger = logging.getLogger(__name__)


class Quote:
    """Quote class adapted from zstock reference."""
    
    def __init__(self, symbol: str, client: VietcapClient):
        self.symbol = symbol
        self.client = client
        
    def history(self, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
        """Fetch historical OHLC data - zstock compatible method."""
        try:
            # Calculate range from dates
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")  
            days = (end_dt - start_dt).days
            
            range_str = "1w" if days <= 7 else "1m" if days <= 30 else "1y"
            
            raw_data = self.client.get_prices(
                ticker=self.symbol, 
                range_=range_str, 
                interval=interval
            )
            
            # Process response similar to zstock
            if 'data' in raw_data and raw_data['data']:
                data = raw_data['data']
                if isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    if all(k in item for k in ['t', 'o', 'h', 'l', 'c', 'v']):
                        df = pd.DataFrame({
                            'timestamp': pd.to_datetime([int(t) for t in item['t']], unit='s'),
                            'open': item['o'],
                            'high': item['h'],
                            'low': item['l'], 
                            'close': item['c'],
                            'volume': item['v'],
                            'symbol': self.symbol
                        })
                        return df.set_index('timestamp')
                        
        except Exception as e:
            logger.error(f"Error fetching history for {self.symbol}: {e}")
            
        return pd.DataFrame()


class Finance:
    """Finance class adapted from zstock reference."""
    
    def __init__(self, symbol: str, client: VietcapClient):
        self.symbol = symbol
        self.client = client
        self._cache = {}
        
    def ratios(self, period: str = 'quarterly') -> pd.DataFrame:
        """Get financial ratios - zstock compatible method."""
        cache_key = f"ratios_{period}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            raw_data = self.client.get_balance_sheet(ticker=self.symbol, period=period)
            
            if ('data' in raw_data and 
                'data' in raw_data['data'] and
                'CompanyFinancialRatio' in raw_data['data']['data']):
                
                ratio_data = raw_data['data']['data']['CompanyFinancialRatio']['ratio']
                if ratio_data:
                    df = pd.DataFrame(ratio_data)
                    # Extract key ratios
                    ratio_cols = [col for col in df.columns 
                                 if col in ['ticker', 'yearReport', 'revenue', 'netProfit', 
                                           'roe', 'pe', 'pb', 'eps', 'currentRatio', 
                                           'netProfitMargin', 'ebitMargin']]
                    
                    result = df[ratio_cols].rename(columns={'yearReport': 'year'}).set_index('year')
                    self._cache[cache_key] = result
                    return result
                    
        except Exception as e:
            logger.error(f"Error fetching ratios for {self.symbol}: {e}")
            
        return pd.DataFrame()
        
    def balance_sheet(self, period: str = 'quarterly') -> pd.DataFrame:
        """Get balance sheet - zstock compatible method."""
        cache_key = f"balance_{period}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            raw_data = self.client.get_balance_sheet(ticker=self.symbol, period=period)
            
            if ('data' in raw_data and 
                'data' in raw_data['data'] and
                'CompanyFinancialRatio' in raw_data['data']['data']):
                
                ratio_data = raw_data['data']['data']['CompanyFinancialRatio']['ratio']
                if ratio_data:
                    df = pd.DataFrame(ratio_data)
                    # Extract balance sheet items (BSA prefix)
                    balance_cols = ['ticker', 'yearReport'] + [col for col in df.columns if col.startswith('BSA')]
                    
                    result = df[balance_cols].rename(columns={'yearReport': 'year'}).set_index('year')
                    self._cache[cache_key] = result
                    return result
                    
        except Exception as e:
            logger.error(f"Error fetching balance sheet for {self.symbol}: {e}")
            
        return pd.DataFrame()


class Listing:
    """Listing class adapted from zstock reference."""
    
    def __init__(self, client: VietcapClient):
        self.client = client
        self._symbols_cache = None
        
    def all_symbols(self) -> List[str]:
        """Get all available symbols - zstock compatible method."""
        if self._symbols_cache is not None:
            return self._symbols_cache
            
        try:
            # Use market indices as a proxy for available symbols
            indices = self.client.get_indexes(['VNINDEX', 'VN30'])
            
            # For now, return major Vietnamese stocks
            symbols = ['VCB', 'VNM', 'MSN', 'VIC', 'HPG', 'GAS', 'VJC', 'PLX', 'CTG', 'BID']
            self._symbols_cache = symbols
            return symbols
            
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []


class ZStock:
    """Main ZStock class - exact adaptation from reference implementation."""
    
    def __init__(self, symbol: str, source: str = 'VIETCAP', db_path: Optional[str] = None):
        """Initialize ZStock instance - zstock compatible constructor.
        
        Args:
            symbol: Stock symbol (e.g., 'VCB')
            source: Data source (default: 'VIETCAP')
            db_path: Path to SQLite database (optional, not implemented)
        """
        self.symbol = symbol
        self.source = source.upper()
        
        # Initialize HTTP session
        self.session = requests.Session()
        
        # Initialize Vietcap client (using trading.vietcap.com.vn)
        self.client = VietcapClient(base_url="https://trading.vietcap.com.vn")
        
        # Initialize components - zstock compatible properties
        self.quote = Quote(symbol=symbol, client=self.client)
        self.finance = Finance(symbol=symbol, client=self.client) 
        self.listing = Listing(client=self.client)
        
        logger.info(f"Initialized ZStock for {symbol} using {source}")

    def history(self, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
        """Convenience method for price history - zstock compatible."""
        return self.quote.history(start=start, end=end, interval=interval)


class MultiAssetZStock:
    """Multi-asset version adapted from zstock reference."""
    
    def __init__(self, symbols: List[str], source: str = 'VIETCAP'):
        """Initialize for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            source: Data source
        """
        self.symbols = symbols
        self.source = source.upper()
        
        # Initialize client
        self.client = VietcapClient(base_url="https://trading.vietcap.com.vn")
        
        # Create ZStock instances for each symbol
        self.stocks = {symbol: ZStock(symbol, source) for symbol in symbols}
        
        # Store price data
        self.price_data: Dict[str, pd.DataFrame] = {}
        
    def history(self, start: str, end: str, interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """Fetch historical data for all symbols - zstock compatible."""
        for symbol in self.symbols:
            try:
                df = self.stocks[symbol].history(start=start, end=end, interval=interval)
                self.price_data[symbol] = df
                logger.info(f"Fetched data for {symbol}: {len(df)} records")
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                self.price_data[symbol] = pd.DataFrame()
                
        return self.price_data
        
    def get_close_prices(self) -> pd.DataFrame:
        """Return DataFrame of closing prices for all symbols - zstock compatible."""
        close_prices = {}
        for symbol, data in self.price_data.items():
            if not data.empty and 'close' in data.columns:
                close_prices[symbol] = data['close']
                
        return pd.DataFrame(close_prices).dropna()


def configure_logging(level=logging.INFO, log_file: Optional[str] = None):
    """Configure logging - zstock compatible utility."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file
    )