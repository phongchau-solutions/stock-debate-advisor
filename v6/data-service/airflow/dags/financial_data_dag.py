"""
Airflow DAG for financial data pipeline.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


def fetch_vietcap_data(symbol: str, **context):
    """Fetch data from VietCap API."""
    from app.clients.vietcap_client import VietCapClient
    from app.db.database import get_db
    from app.db.models import FinancialData
    import json
    
    client = VietCapClient()
    data = client.get_all_financial_data(symbol)
    
    # Store in database
    with get_db() as db:
        # Store each type of financial data
        for data_type in ['balance_sheet', 'income_statement', 'cash_flow', 'metrics']:
            if data.get(data_type):
                financial_record = FinancialData(
                    symbol=symbol,
                    data_type=data_type,
                    data=data[data_type]
                )
                db.add(financial_record)
        
        db.commit()
    
    print(f"Fetched VietCap data for {symbol}")
    return data


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
        # Task 1: Fetch VietCap financial data
        fetch_vietcap = PythonOperator(
            task_id=f'fetch_vietcap_{symbol}',
            python_callable=fetch_vietcap_data,
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
        [fetch_vietcap, crawl_news, fetch_prices]
