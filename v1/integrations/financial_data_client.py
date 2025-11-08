"""
Enhanced Financial Data Client - Adapted from zstock reference implementation.

This module provides a high-level interface for financial data access,
combining OHLC prices, fundamentals, and market indices in a clean API.
"""

from __future__ import annotations

import logging
import requests
from typing import Any, Dict, List, Optional, Union, cast
from datetime import datetime, timedelta

from .vietcap_client import VietcapClient
import pandas as pd

logger = logging.getLogger(__name__)


class FinancialDataClient:
    """High-level client for comprehensive financial data access.
    
    Adapted from the successful zstock reference implementation patterns:
    - Multi-asset support (single symbol or list of symbols)
    - Caching for expensive operations  
    - Clean separation of concerns (prices, fundamentals, market data)
    - Robust error handling with fallbacks
    """

    def __init__(
        self,
        symbols: Union[str, List[str]],
        source: str = "VIETCAP",
        base_url: Optional[str] = None,
        timeout: float = 20.0,
    ):
        """Initialize with single symbol or multiple symbols.
        
        Args:
            symbols: Stock symbol (str) or list of symbols (List[str])
            source: Data source identifier
            base_url: Optional custom base URL for Vietcap
            timeout: Request timeout in seconds
        """
        # Convert single symbol to list for consistency
        self.symbols = [symbols] if isinstance(symbols, str) else symbols
        self.source = source.upper()
        
        # Initialize Vietcap client
        self.vietcap = VietcapClient(base_url=base_url, timeout=timeout)
        
        # Initialize HTTP session with headers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Referer": "https://trading.vietcap.com.vn/",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        # Cache for expensive operations
        self._price_cache: Dict[str, Dict[str, pd.DataFrame]] = {}
        self._fundamentals_cache: Dict[str, Dict[str, pd.DataFrame]] = {}
        self._market_cache: Dict[str, Dict[str, pd.DataFrame]] = {}

    # ====================
    # PRICE DATA (Technical Analysis)
    # ====================
    
    def get_prices(
        self,
        symbols: Optional[Union[str, List[str]]] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1d",
        force_refresh: bool = False,
    ) -> Dict[str, pd.DataFrame]:
        """Fetch OHLC price data for symbols.
        
        Args:
            symbols: Override symbols (default: use instance symbols)
            start: Start date YYYY-MM-DD (default: 1 month ago)
            end: End date YYYY-MM-DD (default: today)
            interval: Time interval (1d, 1h, etc.)
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Dict mapping symbol -> DataFrame with OHLC data
        """
        symbols = symbols or self.symbols
        if isinstance(symbols, str):
            symbols = [symbols]
            
        # Default date range
        if not start:
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")
            
        cache_key = f"{start}_{end}_{interval}"
        results = {}
        
        for symbol in symbols:
            try:
                # Check cache first
                if (symbol in self._price_cache and 
                    cache_key in self._price_cache[symbol] and 
                    not force_refresh):
                    results[symbol] = self._price_cache[symbol][cache_key]
                    continue
                
                # Fetch from API
                raw_data = self.vietcap.get_prices(
                    ticker=symbol,
                    range_=self._calculate_range(start, end),
                    interval=interval
                )
                
                # Process into DataFrame
                df = self._process_ohlc_data(raw_data, symbol)
                
                # Cache result
                if symbol not in self._price_cache:
                    self._price_cache[symbol] = {}
                self._price_cache[symbol][cache_key] = df
                
                results[symbol] = df
                logger.info(f"Fetched price data for {symbol}: {len(df)} records")
                
            except Exception as e:
                logger.error(f"Failed to fetch prices for {symbol}: {e}")
                results[symbol] = pd.DataFrame()  # Empty DataFrame on failure
                
        return results

    def get_close_prices(
        self,
        symbols: Optional[Union[str, List[str]]] = None,
        **kwargs: Any
    ) -> pd.DataFrame:
        """Get closing prices as a multi-column DataFrame.
        
        Returns:
            DataFrame with symbols as columns, dates as index
        """
        price_data = self.get_prices(symbols=symbols, **kwargs)
        close_prices = {}
        
        for symbol, df in price_data.items():
            if not df.empty and 'close' in df.columns:
                close_prices[symbol] = df['close']
                
        return pd.DataFrame(close_prices).dropna()

    # ====================
    # FUNDAMENTAL DATA (Balance Sheet Analysis)  
    # ====================
    
    def get_fundamentals(
        self,
        symbols: Optional[Union[str, List[str]]] = None,
        period: str = "quarterly",
        force_refresh: bool = False,
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Fetch comprehensive financial fundamentals.
        
        Args:
            symbols: Override symbols (default: use instance symbols)
            period: 'quarterly' or 'annual'
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Dict mapping symbol -> {'balance_sheet': df, 'income_statement': df, 
                                   'cash_flow': df, 'ratios': df}
        """
        symbols = symbols or self.symbols
        if isinstance(symbols, str):
            symbols = [symbols]
            
        results = {}
        
        for symbol in symbols:
            try:
                cache_key = f"{symbol}_{period}"
                
                # Check cache first
                if (cache_key in self._fundamentals_cache and not force_refresh):
                    results[symbol] = self._fundamentals_cache[cache_key]
                    continue
                
                # Fetch from API
                raw_data = self.vietcap.get_balance_sheet(
                    ticker=symbol,
                    period=period
                )
                
                # Process into structured format
                fundamentals = self._process_fundamentals_data(raw_data, symbol)
                
                # Cache result
                self._fundamentals_cache[cache_key] = fundamentals
                results[symbol] = fundamentals
                
                logger.info(f"Fetched fundamentals for {symbol}: {period}")
                
            except Exception as e:
                logger.error(f"Failed to fetch fundamentals for {symbol}: {e}")
                results[symbol] = {
                    'balance_sheet': pd.DataFrame(),
                    'income_statement': pd.DataFrame(), 
                    'cash_flow': pd.DataFrame(),
                    'ratios': pd.DataFrame()
                }
                
        return results

    def get_key_ratios(
        self,
        symbols: Optional[Union[str, List[str]]] = None,
        fields: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, pd.DataFrame]:
        """Get key financial ratios as clean DataFrames.
        
        Args:
            symbols: Override symbols
            fields: Specific fields to extract (default: common ratios)
            
        Returns:
            Dict mapping symbol -> DataFrame with key ratios
        """
        if not fields:
            fields = ['revenue', 'netProfit', 'roe', 'pe', 'pb', 'eps', 
                     'currentRatio', 'netProfitMargin', 'ebitMargin']
                     
        fundamentals = self.get_fundamentals(symbols=symbols, **kwargs)
        results = {}
        
        for symbol, data in fundamentals.items():
            ratios_df = data.get('ratios', pd.DataFrame())
            if not ratios_df.empty:
                # Extract only requested fields that exist
                available_fields = [f for f in fields if f in ratios_df.columns]
                results[symbol] = ratios_df[available_fields]
            else:
                results[symbol] = pd.DataFrame()
                
        return results

    # ====================
    # MARKET DATA (Context & Beta)
    # ====================
    
    def get_market_indices(
        self,
        indices: Optional[List[str]] = None,
        force_refresh: bool = False,
        **kwargs: Any
    ) -> Dict[str, pd.DataFrame]:
        """Fetch market index data for correlation and beta analysis.
        
        Args:
            indices: List of index symbols (default: ['VNINDEX', 'VN30'])
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Dict mapping index -> DataFrame with OHLC data
        """
        if not indices:
            indices = ['VNINDEX', 'VN30', 'HNXINDEX']
            
        cache_key = '_'.join(sorted(indices))
        
        # Check cache first
        if cache_key in self._market_cache and not force_refresh:
            return self._market_cache[cache_key]
            
        try:
            raw_data = self.vietcap.get_indexes(indices)
            processed_data = self._process_index_data(raw_data)
            
            # Cache result
            self._market_cache[cache_key] = processed_data
            
            logger.info(f"Fetched market indices: {list(processed_data.keys())}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to fetch market indices: {e}")
            return {idx: pd.DataFrame() for idx in indices}

    # ====================
    # HELPER METHODS
    # ====================
    
    def _calculate_range(self, start: str, end: str) -> str:
        """Convert start/end dates to range string."""
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            days = (end_dt - start_dt).days
            
            if days <= 7:
                return "1w"
            elif days <= 30:
                return "1m"
            elif days <= 90:
                return "3m"
            elif days <= 365:
                return "1y"
            else:
                return "2y"
        except Exception:
            return "1m"  # Default fallback

    def _process_ohlc_data(self, raw_data: Dict[str, Any], symbol: str) -> pd.DataFrame:
        """Convert raw OHLC API response to clean DataFrame."""
        try:
            if 'data' not in raw_data or not raw_data['data']:
                return pd.DataFrame()
                
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
                        'symbol': symbol
                    })
                    return df.set_index('timestamp')
                    
        except Exception as e:
            logger.error(f"Error processing OHLC data for {symbol}: {e}")
            
        return pd.DataFrame()

    def _process_fundamentals_data(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, pd.DataFrame]:
        """Convert raw fundamentals API response to structured DataFrames."""
        try:
            if ('data' not in raw_data or 
                'data' not in raw_data['data'] or
                'CompanyFinancialRatio' not in raw_data['data']['data']):
                return self._empty_fundamentals()
                
            ratio_data = raw_data['data']['data']['CompanyFinancialRatio']['ratio']
            if not ratio_data:
                return self._empty_fundamentals()
                
            df = pd.DataFrame(ratio_data)
            
            # Categorize fields
            balance_sheet_cols = [col for col in df.columns if col.startswith('BSA')]
            income_statement_cols = [col for col in df.columns if col.startswith('ISA')]
            cash_flow_cols = [col for col in df.columns if col.startswith('CFA')]
            ratio_cols = [col for col in df.columns 
                         if col in ['revenue', 'netProfit', 'roe', 'pe', 'pb', 'eps',
                                   'currentRatio', 'netProfitMargin', 'ebitMargin']]
            
            # Create separate DataFrames
            base_cols = ['ticker', 'yearReport']
            
            return {
                'balance_sheet': df[base_cols + balance_sheet_cols].rename(columns={'yearReport': 'year'}).set_index('year'),
                'income_statement': df[base_cols + income_statement_cols].rename(columns={'yearReport': 'year'}).set_index('year'),
                'cash_flow': df[base_cols + cash_flow_cols].rename(columns={'yearReport': 'year'}).set_index('year'),
                'ratios': df[base_cols + ratio_cols].rename(columns={'yearReport': 'year'}).set_index('year')
            }
            
        except Exception as e:
            logger.error(f"Error processing fundamentals for {symbol}: {e}")
            
        return self._empty_fundamentals()

    def _process_index_data(self, raw_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Convert raw index API response to clean DataFrames."""
        results = {}
        
        try:
            if 'data' in raw_data and isinstance(raw_data['data'], dict):
                for index_name, index_data in raw_data['data'].items():
                    try:
                        if isinstance(index_data, list) and len(index_data) > 0:
                            df = self._process_ohlc_data({'data': index_data}, index_name)
                            results[index_name] = df
                        else:
                            results[index_name] = pd.DataFrame()
                    except Exception as e:
                        logger.warning(f"Error processing index {index_name}: {e}")
                        results[index_name] = pd.DataFrame()
                        
        except Exception as e:
            logger.error(f"Error processing index data: {e}")
            
        return results

    def _empty_fundamentals(self) -> Dict[str, pd.DataFrame]:
        """Return empty fundamentals structure."""
        return {
            'balance_sheet': pd.DataFrame(),
            'income_statement': pd.DataFrame(),
            'cash_flow': pd.DataFrame(), 
            'ratios': pd.DataFrame()
        }

    # ====================
    # CONVENIENCE METHODS (zstock-style API)
    # ====================
    
    @property 
    def quote(self):
        """zstock-style quote access for single symbol."""
        if len(self.symbols) == 1:
            return QuoteProxy(self, self.symbols[0])
        raise ValueError("quote property only available for single symbol instances")
        
    @property
    def finance(self):
        """zstock-style finance access for single symbol."""
        if len(self.symbols) == 1:
            return FinanceProxy(self, self.symbols[0])
        raise ValueError("finance property only available for single symbol instances")


class QuoteProxy:
    """Proxy for zstock-style quote access."""
    
    def __init__(self, client: FinancialDataClient, symbol: str):
        self.client = client
        self.symbol = symbol
        
    def history(self, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
        """Get price history for single symbol."""
        results = self.client.get_prices([self.symbol], start=start, end=end, interval=interval)
        return results.get(self.symbol, pd.DataFrame())


class FinanceProxy:
    """Proxy for zstock-style finance access."""
    
    def __init__(self, client: FinancialDataClient, symbol: str):
        self.client = client
        self.symbol = symbol
        
    def ratios(self, period: str = 'quarterly') -> pd.DataFrame:
        """Get financial ratios for single symbol."""
        results = self.client.get_fundamentals([self.symbol], period=period)
        return results.get(self.symbol, {}).get('ratios', pd.DataFrame())
        
    def balance_sheet(self, period: str = 'quarterly') -> pd.DataFrame:
        """Get balance sheet for single symbol."""
        results = self.client.get_fundamentals([self.symbol], period=period)
        return results.get(self.symbol, {}).get('balance_sheet', pd.DataFrame())