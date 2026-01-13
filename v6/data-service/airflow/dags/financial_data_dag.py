"""
Airflow DAG for comprehensive financial data pipeline v2.
Orchestrates fetching of:
- Company Information
- Quarterly and Annual Financial Reports  
- Stock Price Data (OHLCV, Dividends, Splits)
- News Articles from multiple sources
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def fetch_yahoo_finance_data(symbol: str, **context):
    """Fetch data from Yahoo Finance API."""
    from app.clients.yahoo_finance_client import YahooFinanceClient
    from app.services.financial_data_service import FinancialDataService
    from app.db.database import get_db
    from app.db.models import FinancialData
    import json
    
    yahoo_client = YahooFinanceClient()
    financial_service = FinancialDataService(yahoo_client)
    
    # Fetch and cache data
    data = financial_service.fetch_and_cache(symbol)
    
    # Store in database
    with get_db() as db:
        # Store each type of financial data
        for data_type in ['info', 'prices', 'quarterly', 'annual', 'metrics', 'dividends', 'splits']:
            if data.get(data_type):
                financial_record = FinancialData(
                    symbol=symbol,
                    data_type=data_type,
                    data=data[data_type]
                )
                db.add(financial_record)
        
        db.commit()
    
    print(f"Fetched Yahoo Finance data for {symbol}")
    return data


def fetch_vietcap_data(symbol: str, **context):
    """Fetch data from Yahoo Finance API (deprecated: use fetch_yahoo_finance_data)."""
    # Delegate to Yahoo Finance
    return fetch_yahoo_finance_data(symbol, **context)


def crawl_news_data(symbol: str, **context):
    """Crawl news articles."""
    from app.crawlers.news_crawler import NewsCrawler
    from app.db.database import get_db
    from app.db.models import NewsArticle
    
    crawler = NewsCrawler()
    articles = crawler.crawl_all_sources(symbol, max_per_source=5)
    
    # Store in database
    with get_db() as db:
        for article in articles:
            news_record = NewsArticle(
                symbol=article['symbol'],
                title=article['title'],
                url=article['url'],
                content=article['content'],
                source=article['source'],
                published_at=article['published_at']
            )
            db.add(news_record)
        
        db.commit()
    
    print(f"Crawled {len(articles)} news articles for {symbol}")
    return articles


def fetch_price_history(symbol: str, **context):
    """Fetch historical price data."""
    import yfinance as yf
    from app.db.database import get_db
    from app.db.models import PriceData
    
    # Add .VN suffix for Vietnamese stocks
    ticker_symbol = f"{symbol}.VN" if not symbol.endswith('.VN') else symbol
    
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1mo")
    
    # Store in database
    with get_db() as db:
        for date, row in hist.iterrows():
            price_record = PriceData(
                symbol=symbol,
                date=date,
                open_price=row['Open'],
                high_price=row['High'],
                low_price=row['Low'],
                close_price=row['Close'],
                volume=row['Volume']
            )
            db.add(price_record)
        
        db.commit()
    
    print(f"Fetched price history for {symbol}: {len(hist)} records")
    return hist.to_dict()


# Create DAG
with DAG(
    'financial_data_pipeline',
    default_args=default_args,
    description='Fetch financial data, news, and price history',
    schedule_interval=timedelta(hours=6),  # Run every 6 hours
    catchup=False,
    tags=['finance', 'data-pipeline'],
) as dag:

    # List of symbols to process
    symbols = ['MBB', 'VNM', 'VCB', 'HPG', 'VHM']

    for symbol in symbols:
        # Task 1: Fetch Yahoo Finance data
        fetch_yahoo = PythonOperator(
            task_id=f'fetch_yahoo_{symbol}',
            python_callable=fetch_yahoo_finance_data,
            op_kwargs={'symbol': symbol},
        )

        # Task 2: Crawl news
        crawl_news = PythonOperator(
            task_id=f'crawl_news_{symbol}',
            python_callable=crawl_news_data,
            op_kwargs={'symbol': symbol},
        )

        # Task 3: Fetch price history
        fetch_prices = PythonOperator(
            task_id=f'fetch_prices_{symbol}',
            python_callable=fetch_price_history,
            op_kwargs={'symbol': symbol},
        )

        # Set task dependencies - all can run in parallel
        [fetch_yahoo, crawl_news, fetch_prices]
