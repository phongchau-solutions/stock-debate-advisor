"""
Data Integration Module for Vietnamese Stock Market
Handles Vietcap API, VnEconomy, and WSJ data fetching
"""
import aiohttp
import asyncio
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
import yfinance as yf


class VietcapClient:
    """Client for Vietcap API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.vietcap.com.vn"  # Placeholder URL
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_stock_data(self, symbol: str, period: str = "30d") -> Dict[str, Any]:
        """Fetch OHLCV data from Vietcap API."""
        try:
            # For demo purposes, we'll use yfinance as fallback
            # In production, this would call actual Vietcap API
            
            return await self._fetch_demo_stock_data(symbol, period)
            
        except Exception as e:
            self.logger.error(f"Error fetching Vietcap data for {symbol}: {e}")
            return {}
    
    async def _fetch_demo_stock_data(self, symbol: str, period: str) -> Dict[str, Any]:
        """Fetch demo stock data using yfinance."""
        try:
            vn_symbol = f"{symbol}.VN"
            stock = yf.Ticker(vn_symbol)
            
            # Convert period to yfinance format
            if "day" in period.lower():
                days = int(period.split()[0])
                yf_period = f"{days}d" if days <= 60 else "3mo"
            else:
                yf_period = "1mo"
            
            hist = stock.history(period=yf_period)
            info = stock.info
            
            if hist.empty:
                # Generate demo data
                return self._generate_demo_data(symbol)
            
            return {
                "symbol": symbol,
                "ohlcv": hist.to_dict('index'),
                "info": info,
                "current_price": float(hist['Close'].iloc[-1]),
                "volume": int(hist['Volume'].iloc[-1]),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "data_source": "yfinance"
            }
            
        except Exception as e:
            self.logger.error(f"Error with yfinance for {symbol}: {e}")
            return self._generate_demo_data(symbol)
    
    def _generate_demo_data(self, symbol: str) -> Dict[str, Any]:
        """Generate realistic demo stock data."""
        base_prices = {
            'VNM': 52000,
            'VIC': 38000,
            'VCB': 95000,
            'FPT': 78000,
            'GAS': 85000
        }
        
        base_price = base_prices.get(symbol, 50000)
        
        # Generate 30 days of data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        data = {}
        
        current_price = base_price
        for date in dates:
            # Random walk with slight volatility
            change = pd.np.random.normal(0.001, 0.02)  # 0.1% daily drift, 2% volatility
            current_price *= (1 + change)
            
            high = current_price * (1 + abs(pd.np.random.normal(0, 0.01)))
            low = current_price * (1 - abs(pd.np.random.normal(0, 0.01)))
            open_price = current_price * pd.np.random.normal(1, 0.005)
            volume = pd.np.random.randint(100000, 2000000)
            
            data[date.strftime('%Y-%m-%d %H:%M:%S%z')] = {
                'Open': float(open_price),
                'High': float(high),
                'Low': float(low),
                'Close': float(current_price),
                'Volume': int(volume)
            }
        
        return {
            "symbol": symbol,
            "ohlcv": data,
            "current_price": float(current_price),
            "volume": int(volume),
            "market_cap": int(current_price * 1000000000),  # Assume 1B shares
            "pe_ratio": pd.np.random.uniform(10, 25),
            "data_source": "demo"
        }


class VnEconomyCrawler:
    """Crawler for VnEconomy news."""
    
    def __init__(self):
        self.base_url = "https://vneconomy.vn"
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news articles related to a stock symbol."""
        try:
            # For demo purposes, return realistic Vietnamese stock news
            return self._get_demo_news(symbol, limit)
            
        except Exception as e:
            self.logger.error(f"Error fetching VnEconomy news for {symbol}: {e}")
            return []
    
    def _get_demo_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Generate demo Vietnamese news articles."""
        
        news_templates = {
            'VNM': [
                {
                    "title": "Vinamilk công bố kết quả kinh doanh quý 3/2024 tích cực",
                    "content": "Tập đoàn Vinamilk báo cáo doanh thu quý 3 đạt 15.8 nghìn tỷ đồng, tăng 8.2% so với cùng kỳ năm trước...",
                    "url": f"{self.base_url}/vinamilk-q3-2024-earnings",
                    "published_date": "2024-10-28",
                    "sentiment": "positive"
                },
                {
                    "title": "Thị trường sữa Việt Nam: Cạnh tranh gay gắt từ thương hiệu nước ngoài",
                    "content": "Các thương hiệu sữa quốc tế đang tăng cường đầu tư vào thị trường Việt Nam, tạo áp lực cạnh tranh...",
                    "url": f"{self.base_url}/dairy-market-competition-vietnam",
                    "published_date": "2024-10-25",
                    "sentiment": "negative"
                },
                {
                    "title": "Vinamilk mở rộng thị trường xuất khẩu sang ASEAN",
                    "content": "Công ty tiếp tục chiến lược mở rộng ra các thị trường khu vực Đông Nam Á với các sản phẩm cao cấp...",
                    "url": f"{self.base_url}/vinamilk-asean-expansion",
                    "published_date": "2024-10-22",
                    "sentiment": "positive"
                }
            ],
            'VIC': [
                {
                    "title": "Vingroup đầu tư 2 tỷ USD vào VinFast trong năm 2024",
                    "content": "Tập đoàn Vingroup tiếp tục cam kết đầu tư mạnh vào mảng xe điện VinFast để cạnh tranh quốc tế...",
                    "url": f"{self.base_url}/vingroup-vinfast-investment-2024",
                    "published_date": "2024-10-29",
                    "sentiment": "positive"
                },
                {
                    "title": "Thị trường bất động sản: Vingroup điều chỉnh chiến lược phát triển",
                    "content": "Vingroup thông báo tạm dừng một số dự án bất động sản để tập trung nguồn lực cho VinFast...",
                    "url": f"{self.base_url}/vingroup-real-estate-strategy",
                    "published_date": "2024-10-26",
                    "sentiment": "neutral"
                }
            ],
            'VCB': [
                {
                    "title": "Vietcombank báo lãi 9 tháng đầu năm đạt 21.5 nghìn tỷ đồng",
                    "content": "Ngân hàng TMCP Ngoại thương Việt Nam công bố kết quả kinh doanh 9 tháng với lợi nhuận tăng trưởng mạnh...",
                    "url": f"{self.base_url}/vietcombank-9m-2024-results",
                    "published_date": "2024-10-27",
                    "sentiment": "positive"
                },
                {
                    "title": "Ngân hàng Việt Nam đối mặt áp lực từ lãi suất thế giới",
                    "content": "Các ngân hàng lớn như Vietcombank cần điều chỉnh chính sách lãi suất theo diễn biến quốc tế...",
                    "url": f"{self.base_url}/vietnam-banks-interest-rate-pressure",
                    "published_date": "2024-10-24",
                    "sentiment": "negative"
                }
            ]
        }
        
        # Get company specific news or generic market news
        company_news = news_templates.get(symbol, [])
        
        # Add some general market news
        general_news = [
            {
                "title": "VN-Index tăng điểm phiên thứ 3 liên tiếp",
                "content": "Chỉ số VN-Index đóng cửa tăng 12.5 điểm lên 1,245.3 điểm trong phiên giao dịch ngày 29/10...",
                "url": f"{self.base_url}/vn-index-gains-third-session",
                "published_date": "2024-10-29",
                "sentiment": "positive"
            },
            {
                "title": "Nhà đầu tư nước ngoài tiếp tục mua ròng trên HOSE",
                "content": "Khối ngoại mua ròng 850 tỷ đồng trên sàn HOSE, tập trung vào nhóm cổ phiếu ngân hàng và bất động sản...",
                "url": f"{self.base_url}/foreign-net-buying-hose",
                "published_date": "2024-10-28",
                "sentiment": "positive"
            },
            {
                "title": "Lạm phát tháng 10 tăng nhẹ, tác động đến thị trường chứng khoán",
                "content": "Chỉ số giá tiêu dùng tháng 10 tăng 0.3% so với tháng trước, gây lo ngại về chính sách tiền tệ...",
                "url": f"{self.base_url}/inflation-october-2024",
                "published_date": "2024-10-26",
                "sentiment": "negative"
            }
        ]
        
        all_news = company_news + general_news
        return all_news[:limit]


class WSJCrawler:
    """Crawler for Wall Street Journal international news."""
    
    def __init__(self):
        self.base_url = "https://www.wsj.com"
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_vietnam_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch Vietnam market news from WSJ."""
        try:
            # For demo purposes, return realistic international news
            return self._get_demo_international_news(limit)
            
        except Exception as e:
            self.logger.error(f"Error fetching WSJ news: {e}")
            return []
    
    def _get_demo_international_news(self, limit: int) -> List[Dict[str, Any]]:
        """Generate demo international news articles."""
        
        international_news = [
            {
                "title": "Vietnam's Stock Market Attracts Growing International Interest",
                "content": "Foreign institutional investors are increasingly looking at Vietnamese equities as the country's economy shows resilience...",
                "url": f"{self.base_url}/vietnam-stock-market-international-interest",
                "published_date": "2024-10-28",
                "sentiment": "positive",
                "source": "WSJ"
            },
            {
                "title": "VinFast's US Market Challenges Highlight EV Competition",
                "content": "Vietnamese electric vehicle maker VinFast faces significant hurdles in establishing market share in the competitive US EV landscape...",
                "url": f"{self.base_url}/vinfast-us-market-challenges",
                "published_date": "2024-10-25",
                "sentiment": "negative",
                "source": "WSJ"
            },
            {
                "title": "Southeast Asian Markets Outperform Amid Global Uncertainty",
                "content": "Vietnam and other ASEAN markets show relative strength as global investors seek diversification opportunities...",
                "url": f"{self.base_url}/southeast-asia-markets-outperform",
                "published_date": "2024-10-23",
                "sentiment": "positive",
                "source": "WSJ"
            },
            {
                "title": "Rising Interest Rates Impact Emerging Market Banking Sector",
                "content": "Vietnamese banks among those facing margin pressure as global interest rate environment remains challenging...",
                "url": f"{self.base_url}/emerging-market-banks-interest-rates",
                "published_date": "2024-10-20",
                "sentiment": "negative",
                "source": "WSJ"
            },
            {
                "title": "Vietnam's Manufacturing Sector Shows Resilience",
                "content": "Despite global supply chain challenges, Vietnam's manufacturing PMI remains above 50, indicating expansion...",
                "url": f"{self.base_url}/vietnam-manufacturing-resilience",
                "published_date": "2024-10-18",
                "sentiment": "positive",
                "source": "WSJ"
            }
        ]
        
        return international_news[:limit]


class DataIntegrationManager:
    """Manages all data sources for the financial analysis."""
    
    def __init__(self, vietcap_api_key: Optional[str] = None):
        self.vietcap_api_key = vietcap_api_key
        self.logger = logging.getLogger(__name__)
    
    async def fetch_all_data(self, symbol: str, period: str = "30d") -> Dict[str, Any]:
        """Fetch data from all sources."""
        
        data = {
            "symbol": symbol,
            "period": period,
            "timestamp": datetime.now().isoformat(),
            "stock_data": {},
            "news_data": {
                "vneconomy": [],
                "wsj": []
            },
            "data_sources": []
        }
        
        try:
            # Fetch stock data
            async with VietcapClient(self.vietcap_api_key) as vietcap:
                stock_data = await vietcap.get_stock_data(symbol, period)
                data["stock_data"] = stock_data
                data["data_sources"].append("vietcap")
            
            # Fetch Vietnamese news
            async with VnEconomyCrawler() as vneconomy:
                vn_news = await vneconomy.get_stock_news(symbol, limit=10)
                data["news_data"]["vneconomy"] = vn_news
                data["data_sources"].append("vneconomy")
            
            # Fetch international news
            async with WSJCrawler() as wsj:
                intl_news = await wsj.get_vietnam_market_news(limit=10)
                data["news_data"]["wsj"] = intl_news
                data["data_sources"].append("wsj")
            
            self.logger.info(f"Successfully fetched data for {symbol} from {len(data['data_sources'])} sources")
            
        except Exception as e:
            self.logger.error(f"Error fetching integrated data for {symbol}: {e}")
            data["error"] = str(e)
        
        return data
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get general market overview data."""
        
        overview = {
            "timestamp": datetime.now().isoformat(),
            "market_indices": {},
            "market_news": [],
            "economic_indicators": {}
        }
        
        try:
            # Mock market data
            overview["market_indices"] = {
                "vn_index": {
                    "value": 1245.3,
                    "change": 12.5,
                    "change_percent": 1.01
                },
                "hnx_index": {
                    "value": 235.8,
                    "change": -2.1,
                    "change_percent": -0.88
                },
                "upcom_index": {
                    "value": 78.9,
                    "change": 0.5,
                    "change_percent": 0.64
                }
            }
            
            # Get general market news
            async with VnEconomyCrawler() as vneconomy:
                market_news = await vneconomy.get_stock_news("MARKET", limit=5)
                overview["market_news"].extend(market_news)
            
            async with WSJCrawler() as wsj:
                intl_news = await wsj.get_vietnam_market_news(limit=5)
                overview["market_news"].extend(intl_news)
            
            # Mock economic indicators
            overview["economic_indicators"] = {
                "gdp_growth": 6.8,
                "inflation_rate": 3.2,
                "interest_rate": 4.5,
                "usd_vnd_rate": 24750
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching market overview: {e}")
            overview["error"] = str(e)
        
        return overview


# Helper functions for data processing
def process_ohlcv_data(ohlcv_dict: Dict[str, Any]) -> pd.DataFrame:
    """Convert OHLCV dictionary to pandas DataFrame."""
    try:
        df = pd.DataFrame.from_dict(ohlcv_dict, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    except Exception as e:
        logging.error(f"Error processing OHLCV data: {e}")
        return pd.DataFrame()


def calculate_price_metrics(ohlcv_data: pd.DataFrame) -> Dict[str, float]:
    """Calculate basic price metrics from OHLCV data."""
    if ohlcv_data.empty:
        return {}
    
    try:
        current_price = float(ohlcv_data['Close'].iloc[-1])
        start_price = float(ohlcv_data['Close'].iloc[0])
        
        return {
            "current_price": current_price,
            "start_price": start_price,
            "price_change": current_price - start_price,
            "price_change_percent": ((current_price / start_price) - 1) * 100,
            "high_52w": float(ohlcv_data['High'].max()),
            "low_52w": float(ohlcv_data['Low'].min()),
            "avg_volume": float(ohlcv_data['Volume'].mean()),
            "latest_volume": float(ohlcv_data['Volume'].iloc[-1])
        }
    except Exception as e:
        logging.error(f"Error calculating price metrics: {e}")
        return {}


def aggregate_news_sentiment(news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate sentiment from news articles."""
    if not news_list:
        return {"sentiment": "neutral", "score": 0.0, "count": 0}
    
    sentiment_scores = {"positive": 1, "negative": -1, "neutral": 0}
    
    total_score = 0
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    
    for article in news_list:
        sentiment = article.get("sentiment", "neutral")
        sentiment_counts[sentiment] += 1
        total_score += sentiment_scores.get(sentiment, 0)
    
    avg_score = total_score / len(news_list) if news_list else 0
    
    # Determine overall sentiment
    if avg_score > 0.2:
        overall_sentiment = "positive"
    elif avg_score < -0.2:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    return {
        "sentiment": overall_sentiment,
        "score": avg_score,
        "count": len(news_list),
        "breakdown": sentiment_counts
    }