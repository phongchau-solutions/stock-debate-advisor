"""
Vietcap API Service Integration using ref/zstock library
Provides real-time Vietnamese stock market data with retry logic and caching.
"""
import asyncio
import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json

import aiohttp
import requests
import requests_cache
import pandas as pd
import yfinance as yf

# Add zstock to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'ref' / 'zstock'))

try:
    from zstock import ZStock
    ZSTOCK_AVAILABLE = True
except ImportError:
    ZSTOCK_AVAILABLE = False
    logging.warning("zstock library not available, falling back to yfinance")

# Import news crawler
from services.news_crawler import NewsCrawler

# Setup requests cache (1 hour expiry for market data)
requests_cache.install_cache('vietcap_cache', expire_after=3600)

logger = logging.getLogger(__name__)


class VietcapService:
    """
    Service for fetching Vietnamese stock market data.
    
    Primary source: Vietcap API (when available)
    Fallback: yfinance with .VN suffix for HOSE/HNX stocks
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.vietcap.com.vn"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_stock_data(self, symbol: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Fetch comprehensive stock data including OHLCV, financials, and news.
        
        Uses zstock library (ref/zstock) for real Vietcap API access when available.
        Falls back to yfinance + synthetic data if zstock unavailable.
        
        Returns structured data:
        {
            "symbol": "VNM",
            "price": float,
            "PE_ratio": float,
            "ROE": float,
            "dividend_yield": float,
            "volume": int,
            "ohlcv": pd.DataFrame,
            "financials": {...},
            "news": [...]
        }
        """
        logger.info(f"Fetching stock data for {symbol} using {'zstock' if ZSTOCK_AVAILABLE else 'fallback'}")
        
        # Try zstock (real Vietcap API) first
        if ZSTOCK_AVAILABLE:
            try:
                data = await self._fetch_from_zstock(symbol, period_days)
                if data:
                    logger.info(f"Successfully fetched {symbol} from zstock/Vietcap API")
                    return data
            except Exception as e:
                logger.warning(f"zstock fetch failed for {symbol}: {e}")
        
        # Fallback to yfinance + synthetic data
        logger.info(f"Using fallback data sources for {symbol}")
        return await self._fetch_fallback_data(symbol, period_days)
    
    async def _fetch_from_zstock(self, symbol: str, period_days: int) -> Optional[Dict[str, Any]]:
        """Fetch data using zstock library with real Vietcap API."""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Initialize ZStock with Vietcap source (symbols parameter, not symbol)
            stock = ZStock(symbols=symbol, source='VIETCAP')
            
            # Fetch historical OHLCV data
            history_data = stock.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            ohlcv_df = history_data.get(symbol, pd.DataFrame())
            
            if ohlcv_df.empty:
                logger.warning(f"No OHLCV data from zstock for {symbol}, API may be blocked")
                return None
            
            current_price = float(ohlcv_df['close'].iloc[-1])
            current_volume = int(ohlcv_df['volume'].iloc[-1])
            logger.info(f"zstock OHLCV: {symbol} = {current_price:,.0f} VND, {len(ohlcv_df)} days")
            
            # Try to fetch financials (may fail with 403)
            financials = {}
            try:
                # Use dictionary access: stock.companies[symbol] not stock.company
                company_info = stock.companies[symbol].overview()
                logger.info(f"zstock company info fetched for {symbol}")
                
                # Get financial ratios - note: method may vary in zstock API
                balance_sheet = stock.finances[symbol].balance_sheet(period='annual', lang='en')
                
                financials = {
                    "pe": float(company_info.get('pe', 0)),
                    "pb": float(company_info.get('pb', 0)),
                    "roe": float(company_info.get('roe', 0)),
                    "eps": float(company_info.get('eps', 0)),
                    "dividend_yield": float(company_info.get('dividend_yield', 0)),
                    "revenue": float(company_info.get('revenue', 0)),
                    "net_income": float(company_info.get('net_income', 0)),
                    "market_cap": float(company_info.get('market_cap', 0)),
                }
            except Exception as e:
                logger.warning(f"Vietcap API blocked for {symbol} financials (403), using synthetic: {str(e)[:100]}")
                financials = self._generate_synthetic_financials(symbol, current_price)
            
            # Fetch news with sector keywords
            news_articles = []
            try:
                sector_keywords = self._get_sector_keywords(symbol)
                async with NewsCrawler() as crawler:
                    news_articles = await crawler.fetch_news(
                        symbol, 
                        sector_keywords=sector_keywords,
                        max_articles=10
                    )
                logger.info(f"News: {len(news_articles)} articles for {symbol}")
            except Exception as e:
                logger.warning(f"News crawl failed for {symbol}: {e}")
            
            return {
                "symbol": symbol,
                "price": current_price,
                "PE_ratio": financials.get("pe", 0),
                "ROE": financials.get("roe", 0),
                "dividend_yield": financials.get("dividend_yield", 0),
                "volume": current_volume,
                "ohlcv": ohlcv_df,
                "financials": financials,
                "news": news_articles,
                "data_source": "zstock_vietcap" if financials else "zstock_vietcap_partial"
            }
            
        except Exception as e:
            logger.error(f"zstock error for {symbol}: {str(e)[:200]}")
            return None
    
    async def _fetch_from_vietcap(self, symbol: str, period_days: int) -> Optional[Dict[str, Any]]:
        """Fetch data from Vietcap API with retry logic."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        endpoints = {
            "price": f"{self.base_url}/v1/stock/{symbol}/price",
            "financials": f"{self.base_url}/v1/stock/{symbol}/financials",
            "ohlcv": f"{self.base_url}/v1/stock/{symbol}/ohlcv?period={period_days}",
            "news": f"{self.base_url}/v1/stock/{symbol}/news?limit=10"
        }
        
        results = {}
        for key, url in endpoints.items():
            for attempt in range(self.retry_attempts):
                try:
                    headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                    async with self.session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            results[key] = await response.json()
                            break
                        elif response.status == 404:
                            logger.warning(f"{key} endpoint not found for {symbol}")
                            break
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on {key} for {symbol}, attempt {attempt + 1}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"Error fetching {key} for {symbol}: {e}")
                    break
        
        if not results:
            return None
        
        # Parse and structure Vietcap response
        return self._parse_vietcap_response(symbol, results)
    
    def _parse_vietcap_response(self, symbol: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Vietcap API responses into standardized format."""
        price_data = results.get("price", {})
        financials = results.get("financials", {})
        ohlcv_data = results.get("ohlcv", {})
        news_data = results.get("news", [])
        
        # Build OHLCV dataframe
        ohlcv_df = pd.DataFrame()
        if ohlcv_data and isinstance(ohlcv_data, dict) and "data" in ohlcv_data:
            ohlcv_df = pd.DataFrame(ohlcv_data["data"])
            if "date" in ohlcv_df.columns:
                ohlcv_df["date"] = pd.to_datetime(ohlcv_df["date"])
                ohlcv_df.set_index("date", inplace=True)
        
        return {
            "symbol": symbol,
            "price": float(price_data.get("close", 0) or 0),
            "PE_ratio": float(financials.get("pe", 0) or 0),
            "ROE": float(financials.get("roe", 0) or 0),
            "dividend_yield": float(financials.get("dividend_yield", 0) or 0),
            "volume": int(price_data.get("volume", 0) or 0),
            "ohlcv": ohlcv_df,
            "financials": financials,
            "news": news_data,
            "data_source": "vietcap"
        }
    
    async def _fetch_fallback_data(self, symbol: str, period_days: int) -> Dict[str, Any]:
        """Fallback to yfinance and synthetic data."""
        # Try yfinance with .VN suffix
        ticker_symbol = symbol if symbol.endswith('.VN') else f"{symbol}.VN"
        
        try:
            end = datetime.now()
            start = end - timedelta(days=period_days * 2)  # Fetch extra for safety
            
            df = yf.download(ticker_symbol, start=start, end=end, progress=False)
            
            if df.empty:
                # Try without .VN
                df = yf.download(symbol, start=start, end=end, progress=False)
            
            if not df.empty:
                current_price = float(df['Close'].iloc[-1])
                volume = int(df['Volume'].iloc[-1])
            else:
                logger.warning(f"No data from yfinance for {symbol}")
                current_price = 0.0
                volume = 0
                df = pd.DataFrame()
            
        except Exception as e:
            logger.error(f"yfinance failed for {symbol}: {e}")
            current_price = 0.0
            volume = 0
            df = pd.DataFrame()
        
        # Generate synthetic financial ratios (production: fetch from real source)
        synthetic_financials = self._generate_synthetic_financials(symbol, current_price)
        
        # Fetch news with sector keywords (already in async context, just await)
        news_articles = []
        try:
            sector_keywords = self._get_sector_keywords(symbol)
            async with NewsCrawler() as crawler:
                news_articles = await crawler.fetch_news(
                    symbol,
                    sector_keywords=sector_keywords,
                    max_articles=10
                )
            logger.info(f"Fetched {len(news_articles)} news articles for {symbol} (fallback)")
        except Exception as e:
            logger.warning(f"News crawl failed in fallback for {symbol}: {e}")
        
        return {
            "symbol": symbol,
            "price": current_price,
            "PE_ratio": synthetic_financials["pe"],
            "ROE": synthetic_financials["roe"],
            "dividend_yield": synthetic_financials["dividend_yield"],
            "volume": volume,
            "ohlcv": df,
            "financials": synthetic_financials,
            "news": news_articles,  # REAL crawled news
            "data_source": "fallback"
        }
    
    def _generate_synthetic_financials(self, symbol: str, price: float) -> Dict[str, Any]:
        """Generate realistic synthetic financial data for demo purposes."""
        # Use symbol hash for reproducible but varied data
        seed = sum(ord(c) for c in symbol) % 100
        
        return {
            "pe": 12.5 + (seed % 20),
            "pb": 1.8 + (seed % 10) / 5,
            "roe": 10.0 + (seed % 15),
            "eps": price / (12.5 + (seed % 20)) if price > 0 else 0,
            "revenue": 1000000 * (1 + seed / 50),
            "net_income": 150000 * (1 + seed / 50),
            "total_assets": 500000 * (1 + seed / 50),
            "total_debt": 200000 * (1 + seed / 50),
            "book_value": 300000 * (1 + seed / 50),
            "dividend_yield": 2.5 + (seed % 5),
            "market_cap": price * 1000000 if price > 0 else 0
        }
    
    def _get_sector_keywords(self, symbol: str) -> List[str]:
        """
        Get sector/domain keywords for news crawling.
        Simple fallback since Vietcap API is currently blocked (403).
        """
        # Common Vietnamese stock sector mappings
        sector_map = {
            'VNM': ['milk', 'dairy', 'food', 'vinamilk', 'beverage'],
            'VCB': ['banking', 'finance', 'vietcombank', 'financial'],
            'HPG': ['steel', 'manufacturing', 'hoa phat', 'construction'],
            'FPT': ['technology', 'IT', 'software', 'telecommunications'],
            'VIC': ['real estate', 'vingroup', 'property', 'development'],
            'VHM': ['real estate', 'vinhomes', 'property', 'housing'],
            'TCB': ['banking', 'techcombank', 'finance', 'financial'],
            'MWG': ['retail', 'mobile world', 'electronics', 'consumer'],
            'VRE': ['real estate', 'vincom retail', 'commercial', 'shopping'],
            'SAB': ['beverage', 'beer', 'sabeco', 'alcohol'],
        }
        
        # Try known mapping first
        if symbol.upper() in sector_map:
            keywords = sector_map[symbol.upper()]
            logger.info(f"Using mapped sector keywords for {symbol}: {keywords}")
            return keywords
        
        # Fallback for unknown symbols
        keywords = [symbol.lower(), 'vietnam', 'stock', 'market']
        logger.info(f"Using generic keywords for {symbol}: {keywords}")
        return keywords
    
    def _generate_synthetic_news(self, symbol: str) -> List[Dict[str, str]]:
        """Generate synthetic news articles for demo purposes."""
        return [
            {
                "source": "VnEconomy",
                "title": f"{symbol} Reports Strong Q3 Earnings",
                "text": f"{symbol} has posted solid quarterly results with revenue beating expectations.",
                "url": f"https://vneconomy.vn/articles/{symbol.lower()}-q3-2024",
                "published": datetime.now().isoformat()
            },
            {
                "source": "WSJ",
                "title": f"Vietnam Market: {symbol} Analysis",
                "text": "Analysts provide mixed signals on the stock's near-term performance.",
                "url": f"https://wsj.com/articles/{symbol.lower()}-analysis",
                "published": (datetime.now() - timedelta(days=2)).isoformat()
            }
        ]
    
    def save_to_staging(self, symbol: str, data: Dict[str, Any], staging_dir: str = "data/staging"):
        """Save fetched data to staging directory for agent preprocessing."""
        import os
        os.makedirs(staging_dir, exist_ok=True)
        
        filepath = os.path.join(staging_dir, f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Serialize dataframe to dict
        data_copy = data.copy()
        if isinstance(data_copy.get("ohlcv"), pd.DataFrame):
            data_copy["ohlcv"] = data_copy["ohlcv"].to_dict(orient="records")
        
        with open(filepath, "w") as f:
            json.dump(data_copy, f, indent=2, default=str)
        
        logger.info(f"Saved staging data to {filepath}")
        return filepath
