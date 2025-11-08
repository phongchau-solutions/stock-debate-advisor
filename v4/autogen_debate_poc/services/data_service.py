"""
Data Service
Fetches financial, technical, and sentiment data for stock analysis.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
import os
from bs4 import BeautifulSoup
import requests

try:
    import pandas as pd
    import yfinance as yf
except ImportError:
    pd = None
    yf = None

logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "data/stock_data.db"

# Ensure the database directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def initialize_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fundamental_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_symbol TEXT NOT NULL,
            pe_ratio REAL,
            market_cap REAL,
            dividend_yield REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS technical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_symbol TEXT NOT NULL,
            rsi REAL,
            sma_50 REAL,
            sma_200 REAL,
            macd REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sentiment_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_symbol TEXT NOT NULL,
            sentiment_score REAL,
            sentiment_summary TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def insert_fundamental_data(data: Dict[str, Any]):
    """Insert fundamental data into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO fundamental_data (stock_symbol, pe_ratio, market_cap, dividend_yield)
        VALUES (:stock_symbol, :pe_ratio, :market_cap, :dividend_yield)
        """,
        data,
    )

    conn.commit()
    conn.close()


def insert_technical_data(data: Dict[str, Any]):
    """Insert technical data into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO technical_data (stock_symbol, rsi, sma_50, sma_200, macd)
        VALUES (:stock_symbol, :rsi, :sma_50, :sma_200, :macd)
        """,
        data,
    )

    conn.commit()
    conn.close()


def insert_sentiment_data(data: Dict[str, Any]):
    """Insert sentiment data into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO sentiment_data (stock_symbol, sentiment_score, sentiment_summary)
        VALUES (:stock_symbol, :sentiment_score, :sentiment_summary)
        """,
        data,
    )

    conn.commit()
    conn.close()


def fetch_overview(stock_symbol: str) -> Dict[str, Any]:
    """Fetch top overview data for a stock."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch fundamental data
    cursor.execute(
        """
        SELECT pe_ratio, market_cap, dividend_yield
        FROM fundamental_data
        WHERE stock_symbol = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (stock_symbol,),
    )
    fundamental = cursor.fetchone()

    # Fetch technical data
    cursor.execute(
        """
        SELECT rsi, sma_50, sma_200
        FROM technical_data
        WHERE stock_symbol = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (stock_symbol,),
    )
    technical = cursor.fetchone()

    # Fetch sentiment data
    cursor.execute(
        """
        SELECT sentiment_summary
        FROM sentiment_data
        WHERE stock_symbol = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (stock_symbol,),
    )
    sentiment = cursor.fetchone()

    conn.close()

    return {
        "fundamental": {
            "pe_ratio": fundamental[0] if fundamental else None,
            "market_cap": fundamental[1] if fundamental else None,
            "dividend_yield": fundamental[2] if fundamental else None,
        },
        "technical": {
            "rsi": technical[0] if technical else None,
            "sma_50": technical[1] if technical else None,
            "sma_200": technical[2] if technical else None,
        },
        "sentiment": sentiment[0] if sentiment else None,
    }


class DataService:
    """Fetches and aggregates stock analysis data."""

    def __init__(self):
        """Initialize data service."""
        if yf is None or pd is None:
            logger.warning("yfinance or pandas not available - using demo data")

    def fetch_stock_data(
        self,
        stock_symbol: str,
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Fetch complete stock data for debate.

        Args:
            stock_symbol: Stock ticker (e.g., VNM.VN for Vietnam)
            period_days: Historical period

        Returns:
            Dict with price, OHLCV, fundamentals, technicals, sentiment
        """
        data = {
            "symbol": stock_symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "period_days": period_days,
        }

        # Fetch price and OHLCV
        if yf is not None and pd is not None:
            try:
                data.update(self._fetch_yfinance_data(stock_symbol, period_days))
            except Exception as e:
                logger.error(f"Error fetching yfinance data: {e}")
                data.update(self._demo_stock_data(stock_symbol))
        else:
            data.update(self._demo_stock_data(stock_symbol))

        # Compute technical indicators
        data.update(self._compute_technicals(data.get("ohlcv", pd.DataFrame())))

        # Fetch sentiment data
        data.update(self._fetch_sentiment_data(stock_symbol))

        logger.info(f"Fetched data for {stock_symbol}: {len(data)} fields")
        return data

    def _fetch_yfinance_data(
        self,
        stock_symbol: str,
        period_days: int,
    ) -> Dict[str, Any]:
        """Fetch price and OHLCV from yfinance."""
        # Normalize symbol (e.g., VNM -> VNM.VN)
        if not stock_symbol.endswith(".VN"):
            ticker = f"{stock_symbol}.VN"
        else:
            ticker = stock_symbol

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        try:
            # Get historical data
            hist = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                quiet=True,
            )

            # Get current info
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info or {}

            # Extract latest price
            latest_price = hist["Close"].iloc[-1] if len(hist) > 0 else 0

            return {
                "price": float(latest_price),
                "ohlcv": hist.copy(),
                "volume": float(hist["Volume"].iloc[-1]) if len(hist) > 0 else 0,
                "financials": {
                    "pe_ratio": float(info.get("trailingPE", 15.0)),
                    "roe": float(info.get("returnOnEquity", 0.15)) * 100,
                    "debt_ratio": float(info.get("debtToEquity", 0.5)) / 100,
                    "dividend_yield": float(info.get("dividendYield", 0.03)) * 100,
                },
            }

        except Exception as e:
            logger.warning(f"yfinance fetch failed: {e}")
            raise

    def _compute_technicals(self, ohlcv: pd.DataFrame) -> Dict[str, Any]:
        """Compute technical indicators from OHLCV."""
        if ohlcv.empty or pd is None:
            return self._demo_technicals()

        try:
            close = ohlcv["Close"]

            # Moving averages
            ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else close.iloc[-1]
            ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else close.iloc[-1]

            # RSI calculation
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_val = rsi.iloc[-1] if len(rsi) > 0 else 50

            # MACD
            exp1 = close.ewm(span=12).mean()
            exp2 = close.ewm(span=26).mean()
            macd = exp1 - exp2
            macd_val = macd.iloc[-1] if len(macd) > 0 else 0

            # Volume trend
            vol = ohlcv["Volume"]
            vol_avg = vol.mean()
            vol_recent = vol.iloc[-5:].mean()
            volume_trend = "increasing" if vol_recent > vol_avg else "decreasing"

            return {
                "ma_50": float(ma_50) if pd.notna(ma_50) else 0,
                "ma_200": float(ma_200) if pd.notna(ma_200) else 0,
                "rsi": float(rsi_val) if pd.notna(rsi_val) else 50,
                "macd": float(macd_val) if pd.notna(macd_val) else 0,
                "volume_trend": volume_trend,
            }

        except Exception as e:
            logger.warning(f"Technical calculation failed: {e}")
            return self._demo_technicals()

    def _fetch_sentiment_data(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch sentiment data from news sources."""
        # Demo sentiment data
        # In production, integrate with news APIs, RSS feeds, sentiment models
        return {
            "sentiment_score": 0.15,  # -1 to 1
            "article_count": 5,
            "positive_pct": 0.60,
            "key_themes": [
                "Strong quarterly earnings",
                "Competitive market dynamics",
                "Regulatory tailwinds",
            ],
            "catalysts": [
                {
                    "description": "Q3 2025 earnings beat",
                    "type": "positive",
                    "timeline": "This month",
                },
                {
                    "description": "New competitor entry",
                    "type": "negative",
                    "timeline": "Q4 2025",
                },
            ],
        }

    @staticmethod
    def _demo_stock_data(stock_symbol: str) -> Dict[str, Any]:
        """Return demo stock data for testing."""
        return {
            "price": 58000.0,
            "volume": 3837352,
            "ohlcv": pd.DataFrame(),  # Empty for now
            "financials": {
                "pe_ratio": 13.5,
                "roe": 21.0,
                "debt_ratio": 0.35,
                "dividend_yield": 3.5,
            },
        }

    @staticmethod
    def _demo_technicals() -> Dict[str, Any]:
        """Return demo technical indicators."""
        return {
            "ma_50": 56000.0,
            "ma_200": 55000.0,
            "rsi": 55.0,
            "macd": 250.0,
            "volume_trend": "increasing",
        }

    # Function to scrape sentiment news from a website
    def scrape_sentiment_news(url: str) -> str:
        print(f"Scraping sentiment news from: {url}")
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Example: Extract all paragraph text
                paragraphs = soup.find_all('p')
                news_content = "\n".join(p.get_text() for p in paragraphs)
                return news_content
            else:
                print(f"Failed to scrape {url}: HTTP {response.status_code}")
                return ""
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""


if __name__ == "__main__":
    # Initialize the database
    print("Initializing the database...")
    initialize_database()

    # Insert sample data
    print("Inserting sample data...")
    insert_fundamental_data({
        "stock_symbol": "AAPL",
        "pe_ratio": 28.5,
        "market_cap": 2500000000000,
        "dividend_yield": 0.6
    })

    insert_technical_data({
        "stock_symbol": "AAPL",
        "rsi": 55.2,
        "sma_50": 150.3,
        "sma_200": 145.8,
        "macd": 1.2
    })

    insert_sentiment_data({
        "stock_symbol": "AAPL",
        "sentiment_score": 0.8,
        "sentiment_summary": "Positive outlook with strong growth potential."
    })

    # Fetch and display overview
    print("Fetching overview for AAPL...")
    overview = fetch_overview("AAPL")
    print("Overview:", overview)

    # Scrape sentiment news as a test
    url = "https://example.com/sentiment-news"
    news = scrape_sentiment_news(url)
    print("Scraped news content:", news)
