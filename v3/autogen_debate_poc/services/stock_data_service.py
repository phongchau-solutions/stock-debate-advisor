"""
Unified Stock Data Service with adapter pattern.
Provides clean interface for fetching Vietnamese stock data with automatic fallback.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from adapters.vietcap_adapter import VietcapAdapter
from adapters.yfinance_adapter import YFinanceAdapter
from services.news_crawler import NewsCrawler
from services.data_cache_service import DataCacheService

logger = logging.getLogger(__name__)


class StockDataService:
    """
    Unified service for fetching stock data from multiple sources.
    Implements adapter pattern with automatic fallback:
    1. Try Vietcap (primary source for Vietnamese stocks)
    2. Fallback to YFinance if Vietcap unavailable
    3. Generate synthetic data for unavailable metrics
    """
    
    def __init__(self, use_cache: bool = True, cache_max_age_hours: int = 24):
        """
        Initialize adapters and cache.
        
        Args:
            use_cache: Whether to use database cache
            cache_max_age_hours: Maximum age of cached data in hours
        """
        self.vietcap = VietcapAdapter()
        self.yfinance = YFinanceAdapter()
        self.use_cache = use_cache
        self.cache_max_age_hours = cache_max_age_hours
        
        if use_cache:
            self.cache = DataCacheService()
        else:
            self.cache = None
        
        # Log adapter availability
        logger.info(f"Vietcap available: {self.vietcap.is_available()}")
        logger.info(f"YFinance available: {self.yfinance.is_available()}")
        logger.info(f"Cache enabled: {use_cache}")
    
    async def fetch_stock_data(
        self, 
        symbol: str, 
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch complete stock data for analysis.
        Uses cache if enabled and available.
        
        Args:
            symbol: Stock symbol (e.g., 'VNM', 'VIC')
            period_days: Historical period in days
            
        Returns:
            Dictionary with OHLCV, financials, news, and metadata
        """
        logger.info(f"Fetching data for {symbol} ({period_days} days)")
        
        # Try cache first
        if self.use_cache and self.cache:
            cached_data = await self._try_cache(symbol, period_days)
            if cached_data:
                logger.info(f"✓ Using cached data for {symbol}")
                return cached_data
        
        # Fetch fresh data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Try primary adapter (Vietcap)
        if self.vietcap.is_available():
            result = await self._fetch_from_vietcap(symbol, start_date, end_date, period_days)
            if result:
                logger.info(f"✓ Data fetched from Vietcap for {symbol}")
                return result
        
        # Fallback to YFinance
        logger.info(f"Falling back to YFinance for {symbol}")
        result = await self._fetch_from_yfinance(symbol, start_date, end_date, period_days)
        
        if result:
            logger.info(f"✓ Data fetched from YFinance for {symbol}")
            return result
        
        # Last resort: synthetic data
        logger.warning(f"All adapters failed for {symbol}, using synthetic data")
        return self._generate_synthetic_data(symbol, period_days)
    
    async def _try_cache(self, symbol: str, period_days: int) -> Optional[Dict[str, Any]]:
        """Try to get data from cache."""
        try:
            # Get cached prices
            ohlcv = self.cache.get_cached_prices(
                symbol, 
                days=period_days,
                max_age_hours=self.cache_max_age_hours
            )
            
            if ohlcv is None or ohlcv.empty:
                return None
            
            # Get cached financials
            financials = self.cache.get_cached_financials(
                symbol,
                max_age_hours=self.cache_max_age_hours
            )
            
            if not financials:
                return None
            
            # Get cached news
            news = self.cache.get_cached_news(
                symbol,
                max_articles=10,
                max_age_hours=self.cache_max_age_hours
            )
            
            current_price = float(ohlcv['close'].iloc[-1])
            current_volume = int(ohlcv['volume'].iloc[-1])
            
            return {
                'symbol': symbol,
                'price': current_price,
                'volume': current_volume,
                'ohlcv': ohlcv,
                'financials': financials,
                'news': news,
                'data_source': 'cache',
                'days_of_data': len(ohlcv)
            }
            
        except Exception as e:
            logger.warning(f"Cache lookup failed for {symbol}: {e}")
            return None
    
    async def _fetch_from_vietcap(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        period_days: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch data using Vietcap adapter."""
        try:
            # Fetch OHLCV
            ohlcv = await self.vietcap.fetch_ohlcv(
                symbol,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if ohlcv.empty:
                return None
            
            current_price = float(ohlcv['close'].iloc[-1])
            current_volume = int(ohlcv['volume'].iloc[-1])
            
            # Fetch financials (may partially fail)
            financials = await self.vietcap.fetch_financials(symbol)
            
            # If financials failed, generate synthetic
            if 'error' in financials:
                logger.warning(f"Vietcap financials blocked for {symbol}, using synthetic")
                financials = self._generate_synthetic_financials(symbol, current_price)
            
            # Fetch news
            news_articles = await self._fetch_news(symbol)
            
            result = {
                'symbol': symbol,
                'price': current_price,
                'volume': current_volume,
                'ohlcv': ohlcv,
                'financials': financials,
                'news': news_articles,
                'data_source': 'vietcap',
                'days_of_data': len(ohlcv)
            }
            
            # Save to cache
            if self.use_cache and self.cache:
                self.cache.cache_stock_prices(symbol, ohlcv, 'vietcap')
                self.cache.cache_financials(symbol, financials)
                self.cache.cache_news(symbol, news_articles)
            
            return result
            
        except Exception as e:
            logger.error(f"Vietcap adapter error for {symbol}: {e}")
            return None
    
    async def _fetch_from_yfinance(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        period_days: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch data using YFinance adapter."""
        try:
            # Fetch OHLCV
            ohlcv = await self.yfinance.fetch_ohlcv(
                symbol,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if ohlcv.empty:
                return None
            
            current_price = float(ohlcv['close'].iloc[-1])
            current_volume = int(ohlcv['volume'].iloc[-1])
            
            # Fetch financials
            financials = await self.yfinance.fetch_financials(symbol)
            
            # If financials incomplete, supplement with synthetic
            if 'error' in financials or financials.get('pe', 0) == 0:
                synthetic = self._generate_synthetic_financials(symbol, current_price)
                financials = {**synthetic, **{k: v for k, v in financials.items() if v and k != 'error'}}
            
            # Fetch news
            news_articles = await self._fetch_news(symbol)
            
            result = {
                'symbol': symbol,
                'price': current_price,
                'volume': current_volume,
                'ohlcv': ohlcv,
                'financials': financials,
                'news': news_articles,
                'data_source': 'yfinance',
                'days_of_data': len(ohlcv)
            }
            
            # Save to cache
            if self.use_cache and self.cache:
                self.cache.cache_stock_prices(symbol, ohlcv, 'yfinance')
                self.cache.cache_financials(symbol, financials)
                self.cache.cache_news(symbol, news_articles)
            
            return result
            
        except Exception as e:
            logger.error(f"YFinance adapter error for {symbol}: {e}")
            return None
    
    async def _fetch_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch news articles for symbol."""
        try:
            sector_keywords = self._get_sector_keywords(symbol)
            async with NewsCrawler() as crawler:
                articles = await crawler.fetch_news(
                    symbol,
                    sector_keywords=sector_keywords,
                    max_articles=10
                )
            return articles
        except Exception as e:
            logger.warning(f"News fetch failed for {symbol}: {e}")
            return []
    
    def _get_sector_keywords(self, symbol: str) -> List[str]:
        """Get sector-specific keywords for news filtering."""
        # Static mapping for common Vietnamese stocks
        sector_map = {
            'VNM': ['milk', 'dairy', 'food', 'vinamilk', 'beverage'],
            'VIC': ['real estate', 'property', 'vingroup', 'developer', 'construction'],
            'VCB': ['bank', 'banking', 'finance', 'vietcombank', 'lending'],
            'HPG': ['steel', 'manufacturing', 'hoa phat', 'industrial', 'metal'],
            'VHM': ['real estate', 'property', 'vinhomes', 'housing', 'developer'],
            'MSN': ['retail', 'consumer', 'masan', 'food', 'distribution'],
            'GAS': ['gas', 'energy', 'petrovietnam', 'oil', 'petroleum'],
            'TCB': ['bank', 'banking', 'techcombank', 'finance', 'fintech'],
            'VPB': ['bank', 'banking', 'vpbank', 'finance', 'lending'],
            'MBB': ['bank', 'banking', 'military bank', 'finance', 'lending']
        }
        
        return sector_map.get(symbol, ['stock', 'market', 'vietnam', symbol.lower()])
    
    def _generate_synthetic_financials(
        self, 
        symbol: str, 
        current_price: float
    ) -> Dict[str, Any]:
        """Generate synthetic financial ratios when real data unavailable."""
        import random
        
        # Generate plausible synthetic data based on symbol and price
        random.seed(hash(symbol) % 10000)
        
        return {
            'symbol': symbol,
            'pe': round(random.uniform(8, 25), 2),
            'pb': round(random.uniform(1.0, 4.0), 2),
            'roe': round(random.uniform(10, 30), 2),
            'roa': round(random.uniform(5, 15), 2),
            'eps': round(current_price / random.uniform(10, 20), 2),
            'dividend_yield': round(random.uniform(1, 5), 2),
            'revenue': int(random.uniform(1e9, 50e9)),
            'net_income': int(random.uniform(1e8, 5e9)),
            'market_cap': int(current_price * random.uniform(1e8, 1e10)),
            'has_detailed_financials': False,
            'source': 'synthetic',
            'note': 'Generated due to API unavailability'
        }
    
    def _generate_synthetic_data(self, symbol: str, period_days: int) -> Dict[str, Any]:
        """Generate complete synthetic dataset as last resort."""
        import random
        import numpy as np
        
        logger.warning(f"Generating synthetic data for {symbol}")
        
        # Generate random walk for price
        random.seed(hash(symbol) % 10000)
        base_price = random.uniform(10000, 100000)
        
        dates = pd.date_range(end=datetime.now(), periods=period_days, freq='D')
        prices = [base_price]
        
        for _ in range(period_days - 1):
            change = random.uniform(-0.05, 0.05)
            prices.append(prices[-1] * (1 + change))
        
        ohlcv = pd.DataFrame({
            'open': [p * random.uniform(0.98, 1.02) for p in prices],
            'high': [p * random.uniform(1.0, 1.05) for p in prices],
            'low': [p * random.uniform(0.95, 1.0) for p in prices],
            'close': prices,
            'volume': [int(random.uniform(1e5, 1e7)) for _ in prices]
        }, index=dates)
        
        current_price = prices[-1]
        financials = self._generate_synthetic_financials(symbol, current_price)
        
        return {
            'symbol': symbol,
            'price': current_price,
            'volume': int(ohlcv['volume'].iloc[-1]),
            'ohlcv': ohlcv,
            'financials': financials,
            'news': [],
            'data_source': 'synthetic',
            'days_of_data': len(ohlcv),
            'warning': 'All data is synthetic - API sources unavailable'
        }
