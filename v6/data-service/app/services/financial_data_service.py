"""
Financial Data Service - Aggregates data from multiple sources
Provides unified interface for fetching, storing, and retrieving financial data
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np

from app.clients.yahoo_finance_client import YahooFinanceClient

logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles pandas and numpy types."""
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, (pd.Series, pd.Index)):
            return obj.to_list()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)


class FinancialDataService:
    """Service for managing financial data retrieval and storage."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize Financial Data Service.
        
        Args:
            cache_dir: Directory for caching data locally
        """
        self.client = YahooFinanceClient()
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / 'data' / 'financial'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def save_to_cache(self, symbol: str, data: Dict[str, Any]) -> Path:
        """
        Save financial data to local JSON cache.
        
        Args:
            symbol: Stock symbol
            data: Financial data dict
            
        Returns:
            Path to cached file
        """
        try:
            cache_file = self.cache_dir / f"{symbol}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=EnhancedJSONEncoder)
            logger.info(f"Cached data for {symbol} at {cache_file}")
            return cache_file
        except Exception as e:
            logger.error(f"Failed to cache data for {symbol}: {e}")
            raise

    def load_from_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Load financial data from local cache.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Cached data or None if not found
        """
        try:
            cache_file = self.cache_dir / f"{symbol}.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load cache for {symbol}: {e}")
            return None

    def fetch_and_cache(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch financial data from Yahoo Finance and cache locally.
        
        Args:
            symbol: Stock symbol (supports VN stocks with .VN suffix)
            
        Returns:
            Financial data dict
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            data = self.client.get_all_financial_data(symbol)
            self.save_to_cache(symbol, data)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise

    def fetch_batch(self, symbols: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """
        Fetch financial data for multiple symbols in parallel.
        
        Args:
            symbols: List of stock symbols
            max_workers: Max parallel workers
            
        Returns:
            Dict with fetch results
        """
        results = {}
        errors = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.fetch_and_cache, symbol): symbol
                for symbol in symbols
            }
            
            for future in futures:
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                    logger.info(f"✅ Successfully fetched {symbol}")
                except Exception as e:
                    errors[symbol] = str(e)
                    logger.error(f"❌ Failed to fetch {symbol}: {e}")
        
        return {
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
        }

    def get_cached_or_fetch(self, symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get cached data or fetch fresh data if not cached.
        
        Args:
            symbol: Stock symbol
            force_refresh: Force fresh fetch even if cached
            
        Returns:
            Financial data dict
        """
        if not force_refresh:
            cached = self.load_from_cache(symbol)
            if cached:
                logger.info(f"Using cached data for {symbol}")
                return cached
        
        return self.fetch_and_cache(symbol)

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains meaningful financial information.
        
        Args:
            data: Financial data dict
            
        Returns:
            True if data is valid and contains real information
        """
        if not data or 'symbol' not in data:
            return False
        
        # Check if at least one data category has content
        data_categories = ['info', 'prices', 'quarterly', 'annual', 'metrics', 'dividends', 'splits']
        
        for category in data_categories:
            if category in data and data[category]:
                # Check if the category has actual values
                if isinstance(data[category], dict):
                    # Filter out empty nested dicts
                    non_empty = {k: v for k, v in data[category].items() if v}
                    if non_empty:
                        return True
        
        return False

    def get_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Get summary of available data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Summary dict with data availability
        """
        data = self.load_from_cache(symbol)
        if not data:
            return {
                'symbol': symbol,
                'status': 'not_cached',
                'message': 'No cached data available',
            }
        
        summary = {
            'symbol': symbol,
            'timestamp': data.get('timestamp'),
            'data_available': {},
        }
        
        # Check what data categories are available
        for category in ['info', 'prices', 'quarterly', 'annual', 'metrics', 'dividends', 'splits']:
            if category in data and data[category]:
                if isinstance(data[category], dict):
                    # Count non-empty entries
                    non_empty = {k: v for k, v in data[category].items() if v}
                    summary['data_available'][category] = len(non_empty) > 0
                elif isinstance(data[category], list):
                    summary['data_available'][category] = len(data[category]) > 0
        
        return summary
