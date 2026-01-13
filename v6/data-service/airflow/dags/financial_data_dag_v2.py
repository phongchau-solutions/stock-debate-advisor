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

# VN30 Stocks
VN30_SYMBOLS = [
    'ACB.VN', 'BCM.VN', 'BID.VN', 'BVH.VN', 'CTG.VN',
    'FPT.VN', 'GAS.VN', 'GVR.VN', 'HDB.VN', 'HPG.VN',
    'KDH.VN', 'MBB.VN', 'MSN.VN', 'MWG.VN', 'NVL.VN',
    'PDR.VN', 'PLX.VN', 'POW.VN', 'SAB.VN', 'SHB.VN',
    'SSB.VN', 'SSI.VN', 'STB.VN', 'TCB.VN', 'TPB.VN',
    'VCB.VN', 'VHM.VN', 'VIB.VN', 'VIC.VN', 'VJC.VN'
]


def fetch_company_data(symbol: str, **context):
    """Fetch company information."""
    from app.db.database import SessionLocal
    from app.services.integrated_data_service import IntegratedDataService
    
    db = SessionLocal()
    service = IntegratedDataService(db)
    
    try:
        result = service.fetch_and_store_company_info(symbol)
        logger.info(f"Fetched company info for {symbol}")
        return {'symbol': symbol, 'success': result is not None}
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise
    finally:
        db.close()


def fetch_financial_reports(symbol: str, **context):
    """Fetch financial reports (quarterly and annual)."""
    from app.db.database import SessionLocal
    from app.services.integrated_data_service import IntegratedDataService
    
    db = SessionLocal()
    service = IntegratedDataService(db)
    
    try:
        quarterly = service.fetch_and_store_quarterly_reports(symbol)
        annual = service.fetch_and_store_annual_reports(symbol)
        metrics = service.fetch_and_store_metrics(symbol)
        
        logger.info(f"Fetched {len(quarterly)} quarterly and {len(annual)} annual reports for {symbol}")
        
        return {
            'symbol': symbol,
            'quarterly_reports': len(quarterly),
            'annual_reports': len(annual),
            'metrics': metrics is not None
        }
    except Exception as e:
        logger.error(f"Error fetching financial reports for {symbol}: {e}")
        raise
    finally:
        db.close()


def fetch_stock_prices(symbol: str, **context):
    """Fetch stock prices and related data."""
    from app.db.database import SessionLocal
    from app.services.integrated_data_service import IntegratedDataService
    
    db = SessionLocal()
    service = IntegratedDataService(db)
    
    try:
        prices = service.fetch_and_store_stock_prices(symbol, period='1y')
        dividends = service.fetch_and_store_dividends(symbol)
        
        logger.info(f"Fetched {prices} price records and {dividends} dividend records for {symbol}")
        
        return {
            'symbol': symbol,
            'price_records': prices,
            'dividend_records': dividends
        }
    except Exception as e:
        logger.error(f"Error fetching stock prices for {symbol}: {e}")
        raise
    finally:
        db.close()


def fetch_news_articles(symbol: str, **context):
    """Fetch news articles from multiple sources."""
    from app.db.database import SessionLocal
    from app.services.integrated_data_service import IntegratedDataService
    
    db = SessionLocal()
    service = IntegratedDataService(db)
    
    try:
        news_count = service.fetch_and_store_news(symbol, days=30)
        logger.info(f"Fetched {news_count} news articles for {symbol}")
        
        return {
            'symbol': symbol,
            'news_articles': news_count
        }
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        raise
    finally:
        db.close()


# Create DAG
with DAG(
    'financial_data_pipeline_v2',
    default_args=default_args,
    description='Comprehensive financial data pipeline v2 - Company info, financials, prices, news',
    schedule_interval=timedelta(hours=12),  # Run twice daily
    catchup=False,
    tags=['finance', 'data-pipeline', 'vn30'],
) as dag:

    # Process each VN30 symbol
    for symbol in VN30_SYMBOLS:
        
        with TaskGroup(f"data_for_{symbol.replace('.VN', '')}") as symbol_tasks:
            
            # Task 1: Fetch company information
            company_task = PythonOperator(
                task_id='company_info',
                python_callable=fetch_company_data,
                op_kwargs={'symbol': symbol},
            )
            
            # Task 2: Fetch financial reports
            financial_task = PythonOperator(
                task_id='financial_reports',
                python_callable=fetch_financial_reports,
                op_kwargs={'symbol': symbol},
            )
            
            # Task 3: Fetch stock prices
            price_task = PythonOperator(
                task_id='stock_prices',
                python_callable=fetch_stock_prices,
                op_kwargs={'symbol': symbol},
            )
            
            # Task 4: Fetch news
            news_task = PythonOperator(
                task_id='news_articles',
                python_callable=fetch_news_articles,
                op_kwargs={'symbol': symbol},
            )
            
            # All tasks can run in parallel
            [company_task, financial_task, price_task, news_task]
