"""
Integration layer to write data to both database and file store.
Wraps IntegratedDataService to provide dual storage capability.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.integrated_data_service import IntegratedDataService
from app.storage.data_store_manager import DataStoreManager
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)


class DualStorageService:
    """Service that stores data in both SQLite database and file-based store."""
    
    def __init__(self, db_session=None, data_store_path: str = "./data_store"):
        """Initialize dual storage service.
        
        Args:
            db_session: SQLAlchemy database session
            data_store_path: Path to file-based data store
        """
        self.db = db_session or SessionLocal()
        self.db_service = IntegratedDataService(self.db)
        self.file_store = DataStoreManager(data_store_path)
        logger.info("Dual storage service initialized")
    
    def fetch_and_store_company_info(self, symbol: str) -> bool:
        """Fetch and store company info in both stores."""
        try:
            # Store in database
            company_info = self.db_service.fetch_and_store_company_info(symbol)
            
            if company_info:
                # Store in file store
                info_record = {
                    'symbol': symbol,
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': company_info
                }
                # Create a financial_reports file with company metadata
                self.file_store.append_financial_report(symbol, info_record)
                logger.info(f"✓ Company info stored for {symbol} (DB + File)")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error storing company info for {symbol}: {e}")
            return False
    
    def fetch_and_store_stock_prices(self, symbol: str, period: str = '1y') -> int:
        """Fetch stock prices and store in both stores."""
        try:
            # Get prices from database (this fetches from Yahoo Finance)
            count = self.db_service.fetch_and_store_stock_prices(symbol, period)
            
            if count > 0:
                # Also write to file store
                from app.db import models
                prices = self.db.query(models.StockPrice).filter_by(symbol=symbol).all()
                
                for price in prices:
                    price_record = {
                        'date': price.price_date.isoformat(),
                        'timestamp': (price.updated_at or price.created_at).isoformat(),
                        'symbol': symbol,
                        'open': price.open_price,
                        'high': price.high_price,
                        'low': price.low_price,
                        'close': price.close_price,
                        'adj_close': price.adj_close_price,
                        'volume': price.volume
                    }
                    self.file_store.append_ohlc_price(symbol, price_record)
                
                logger.info(f"✓ {count} prices stored for {symbol} (DB + File)")
            
            return count
        except Exception as e:
            logger.error(f"Error storing prices for {symbol}: {e}")
            return 0
    
    def fetch_and_store_dividends(self, symbol: str) -> int:
        """Fetch dividends and store in database and file store."""
        try:
            count = self.db_service.fetch_and_store_dividends(symbol)
            
            if count > 0:
                # Store in file store as financial reports (separate section)
                from app.db import models
                dividends = self.db.query(models.Dividend).filter_by(symbol=symbol).all()
                
                for div in dividends:
                    div_record = {
                        'type': 'dividend',
                        'timestamp': (div.created_at).isoformat(),
                        'symbol': symbol,
                        'ex_date': div.ex_date.isoformat(),
                        'payment_date': div.payment_date.isoformat() if div.payment_date else None,
                        'amount_per_share': div.dividend_per_share,
                        'dividend_type': div.dividend_type
                    }
                    self.file_store.append_financial_report(symbol, div_record)
                
                logger.info(f"✓ {count} dividends stored for {symbol} (DB + File)")
            
            return count
        except Exception as e:
            logger.error(f"Error storing dividends for {symbol}: {e}")
            return 0
    
    def fetch_and_store_metrics(self, symbol: str) -> bool:
        """Fetch financial metrics and store in both stores."""
        try:
            result = self.db_service.fetch_and_store_metrics(symbol)
            
            if result:
                # Store in file store
                from app.db import models
                metrics = self.db.query(models.FinancialMetrics).filter_by(symbol=symbol).first()
                
                if metrics:
                    metrics_record = {
                        'type': 'metrics',
                        'timestamp': (metrics.updated_at or metrics.created_at).isoformat(),
                        'symbol': symbol,
                        'metric_date': metrics.metric_date.isoformat(),
                        'pe_ratio': metrics.pe_ratio,
                        'pb_ratio': metrics.pb_ratio,
                        'ps_ratio': metrics.ps_ratio,
                        'peg_ratio': metrics.peg_ratio,
                        'roe': metrics.roe,
                        'roa': metrics.roa,
                        'roic': metrics.roic,
                        'gross_margin': metrics.gross_margin,
                        'operating_margin': metrics.operating_margin,
                        'net_margin': metrics.net_margin,
                        'current_ratio': metrics.current_ratio,
                        'quick_ratio': metrics.quick_ratio,
                        'debt_to_equity': metrics.debt_to_equity,
                        'revenue_growth': metrics.revenue_growth,
                        'earnings_growth': metrics.earnings_growth
                    }
                    self.file_store.append_financial_report(symbol, metrics_record)
                    logger.info(f"✓ Metrics stored for {symbol} (DB + File)")
            
            return result
        except Exception as e:
            logger.error(f"Error storing metrics for {symbol}: {e}")
            return False
    
    def fetch_and_store_news(self, symbol: str, days: int = 30) -> int:
        """Fetch news and store in both stores."""
        try:
            count = self.db_service.fetch_and_store_news(symbol, days)
            
            if count > 0:
                # Store in file store
                from app.db import models
                news_articles = self.db.query(models.CompanyNews).filter_by(symbol=symbol).all()
                
                for article in news_articles:
                    news_record = {
                        'symbol': symbol,
                        'timestamp': (article.updated_at or article.created_at).isoformat(),
                        'title': article.title,
                        'url': article.url,
                        'source': article.source,
                        'published_at': article.published_at.isoformat() if article.published_at else None,
                        'content': article.content[:1000] if article.content else None,  # First 1000 chars
                        'sentiment_score': article.sentiment_score,
                        'sentiment_label': article.sentiment_label,
                        'keywords': article.keywords
                    }
                    self.file_store.append_news_article(symbol, news_record)
                
                logger.info(f"✓ {count} news articles stored for {symbol} (DB + File)")
            
            return count
        except Exception as e:
            logger.error(f"Error storing news for {symbol}: {e}")
            return 0
    
    def fetch_all_data_for_symbol(self, symbol: str, include_news: bool = True) -> Dict[str, Any]:
        """Fetch all data and store in both database and file store."""
        logger.info(f"Fetching all data for {symbol} (dual storage)")
        
        results = {
            'symbol': symbol,
            'timestamp': datetime.utcnow().isoformat(),
            'company_info': self.fetch_and_store_company_info(symbol),
            'quarterly_reports': 0,  # Not available from Yahoo Finance
            'annual_reports': 0,     # Not available from Yahoo Finance
            'metrics': self.fetch_and_store_metrics(symbol),
            'stock_prices': self.fetch_and_store_stock_prices(symbol),
            'dividends': self.fetch_and_store_dividends(symbol),
            'news': self.fetch_and_store_news(symbol) if include_news else 0,
            'errors': []
        }
        
        logger.info(f"✓ Completed {symbol}: {results['stock_prices']} prices, {results['dividends']} dividends, {results['news']} news")
        return results
    
    def fetch_all_data_batch(self, symbols: List[str], max_workers: int = 3,
                            include_news: bool = True) -> Dict[str, Any]:
        """Fetch data for multiple symbols using dual storage."""
        logger.info(f"Starting batch fetch for {len(symbols)} symbols with dual storage")
        
        batch_results = {
            'total_symbols': len(symbols),
            'successful': 0,
            'failed': 0,
            'results': {},
            'start_time': datetime.now().isoformat(),
        }
        
        # Use the database service's batch method (which we'll enhance)
        # For now, fetch sequentially
        for symbol in symbols:
            try:
                result = self.fetch_all_data_for_symbol(symbol, include_news)
                batch_results['results'][symbol] = result
                
                if not result.get('errors'):
                    batch_results['successful'] += 1
                else:
                    batch_results['failed'] += 1
            
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                batch_results['results'][symbol] = {'symbol': symbol, 'error': str(e), 'errors': [str(e)]}
                batch_results['failed'] += 1
        
        batch_results['end_time'] = datetime.now().isoformat()
        
        # Get file store stats
        batch_results['storage_stats'] = self.file_store.get_storage_stats()
        
        return batch_results
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about both storage systems."""
        return {
            'database': {
                'type': 'SQLite',
                'location': 'stock_debate_data.db',
                'purpose': 'Fast queries, indexing, API access'
            },
            'file_store': self.file_store.get_storage_stats(),
            'description': 'File store organized by year/stock for timeseries append operations'
        }
    
    def close(self):
        """Close database session."""
        if self.db:
            self.db.close()
