"""
Integrated Data Service - Orchestrates data fetching and storage
Manages financial reports, stock prices, company info, and news
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.clients.yahoo_finance_client import YahooFinanceClient
from app.crawlers.news_crawler_v2 import NewsAggregator
from app.db import models

logger = logging.getLogger(__name__)


class IntegratedDataService:
    """Orchestrates all data retrieval and storage operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the integrated data service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.yahoo_client = YahooFinanceClient()
        self.news_aggregator = NewsAggregator()
        self.cache_dir = Path(__file__).parent.parent.parent / 'data' / 'financial'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # COMPANY INFO
    # ========================================================================
    
    def fetch_and_store_company_info(self, symbol: str) -> Optional[models.CompanyInfo]:
        """Fetch company info from Yahoo Finance and store in database."""
        try:
            logger.info(f"Fetching company info for {symbol}")
            info_data = self.yahoo_client.get_ticker_info(symbol)
            
            if not info_data:
                logger.warning(f"No company info found for {symbol}")
                return None
            
            # Check if already exists
            existing = self.db.query(models.CompanyInfo).filter(
                models.CompanyInfo.symbol == symbol
            ).first()
            
            company_info = existing or models.CompanyInfo(symbol=symbol)
            
            # Update fields
            company_info.name = info_data.get('longName', '')
            company_info.english_name = info_data.get('longName', '')
            company_info.industry = info_data.get('industry', '')
            company_info.sector = info_data.get('sector', '')
            company_info.market_cap = info_data.get('marketCap')
            company_info.market_cap_usd = info_data.get('marketCap')  # Already in USD from Yahoo
            company_info.employees = info_data.get('fullTimeEmployees')
            company_info.website = info_data.get('website')
            company_info.description = info_data.get('longBusinessSummary', '')
            company_info.company_info_raw = info_data
            
            if not existing:
                self.db.add(company_info)
            
            self.db.commit()
            logger.info(f"Stored company info for {symbol}")
            return company_info
        
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            self.db.rollback()
            return None
    
    # ========================================================================
    # FINANCIAL REPORTS
    # ========================================================================
    
    def fetch_and_store_quarterly_reports(self, symbol: str) -> List[models.QuarterlyFinancialReport]:
        """Fetch quarterly financial reports from Yahoo Finance."""
        stored_reports = []
        
        try:
            logger.info(f"Fetching quarterly financial reports for {symbol}")
            quarterly_data = self.yahoo_client.get_quarterly_financials(symbol)
            
            if not quarterly_data:
                logger.warning(f"No quarterly data found for {symbol}")
                return stored_reports
            
            # Parse quarterly statements
            quarterly_statements = quarterly_data.get('quarterly_income_stmt', [])
            quarterly_balance = quarterly_data.get('quarterly_balance_sheet', [])
            quarterly_cashflow = quarterly_data.get('quarterly_cash_flow', [])
            
            for stmt in quarterly_statements[:8]:  # Last 8 quarters
                try:
                    period_end = stmt.index[0] if hasattr(stmt, 'index') else None
                    if not period_end:
                        continue
                    
                    fiscal_year = period_end.year
                    fiscal_quarter = (period_end.month - 1) // 3 + 1
                    
                    # Check if already exists
                    existing = self.db.query(models.QuarterlyFinancialReport).filter(
                        and_(
                            models.QuarterlyFinancialReport.symbol == symbol,
                            models.QuarterlyFinancialReport.fiscal_year == fiscal_year,
                            models.QuarterlyFinancialReport.fiscal_quarter == fiscal_quarter
                        )
                    ).first()
                    
                    report = existing or models.QuarterlyFinancialReport(
                        symbol=symbol,
                        fiscal_year=fiscal_year,
                        fiscal_quarter=fiscal_quarter,
                        period_end_date=period_end
                    )
                    
                    # Extract values from DataFrames
                    revenue = stmt.get('Total Revenue', [None])[0] if 'Total Revenue' in stmt else None
                    net_income = stmt.get('Net Income', [None])[0] if 'Net Income' in stmt else None
                    operating_income = stmt.get('Operating Income', [None])[0] if 'Operating Income' in stmt else None
                    
                    report.revenue = float(revenue) if revenue else None
                    report.net_income = float(net_income) if net_income else None
                    report.operating_income = float(operating_income) if operating_income else None
                    report.raw_data = json.dumps(stmt.to_dict(), default=str)
                    
                    if not existing:
                        self.db.add(report)
                    
                    stored_reports.append(report)
                
                except Exception as e:
                    logger.debug(f"Error processing quarterly report for {symbol}: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {len(stored_reports)} quarterly reports for {symbol}")
        
        except Exception as e:
            logger.error(f"Error fetching quarterly reports for {symbol}: {e}")
            self.db.rollback()
        
        return stored_reports
    
    def fetch_and_store_annual_reports(self, symbol: str) -> List[models.AnnualFinancialReport]:
        """Fetch annual financial reports from Yahoo Finance."""
        stored_reports = []
        
        try:
            logger.info(f"Fetching annual financial reports for {symbol}")
            annual_data = self.yahoo_client.get_annual_financials(symbol)
            
            if not annual_data:
                logger.warning(f"No annual data found for {symbol}")
                return stored_reports
            
            # Parse annual statements
            annual_statements = annual_data.get('yearly_income_stmt', [])
            
            for stmt in annual_statements[:5]:  # Last 5 years
                try:
                    period_end = stmt.index[0] if hasattr(stmt, 'index') else None
                    if not period_end:
                        continue
                    
                    fiscal_year = period_end.year
                    
                    # Check if already exists
                    existing = self.db.query(models.AnnualFinancialReport).filter(
                        and_(
                            models.AnnualFinancialReport.symbol == symbol,
                            models.AnnualFinancialReport.fiscal_year == fiscal_year
                        )
                    ).first()
                    
                    report = existing or models.AnnualFinancialReport(
                        symbol=symbol,
                        fiscal_year=fiscal_year,
                        period_end_date=period_end
                    )
                    
                    # Extract values
                    revenue = stmt.get('Total Revenue', [None])[0] if 'Total Revenue' in stmt else None
                    net_income = stmt.get('Net Income', [None])[0] if 'Net Income' in stmt else None
                    
                    report.revenue = float(revenue) if revenue else None
                    report.net_income = float(net_income) if net_income else None
                    report.raw_data = json.dumps(stmt.to_dict(), default=str)
                    
                    if not existing:
                        self.db.add(report)
                    
                    stored_reports.append(report)
                
                except Exception as e:
                    logger.debug(f"Error processing annual report for {symbol}: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {len(stored_reports)} annual reports for {symbol}")
        
        except Exception as e:
            logger.error(f"Error fetching annual reports for {symbol}: {e}")
            self.db.rollback()
        
        return stored_reports
    
    def fetch_and_store_metrics(self, symbol: str) -> Optional[models.FinancialMetrics]:
        """Fetch key financial metrics from Yahoo Finance."""
        try:
            logger.info(f"Fetching financial metrics for {symbol}")
            metrics_data = self.yahoo_client.get_key_metrics(symbol)
            
            if not metrics_data:
                logger.warning(f"No metrics found for {symbol}")
                return None
            
            metric = models.FinancialMetrics(
                symbol=symbol,
                metric_date=datetime.now(),
                pe_ratio=metrics_data.get('trailingPE'),
                pb_ratio=metrics_data.get('priceToBook'),
                ps_ratio=metrics_data.get('priceToSalesTrailing12Months'),
                roe=metrics_data.get('returnOnEquity'),
                roa=metrics_data.get('returnOnAssets'),
                gross_margin=metrics_data.get('grossMargins', [None])[-1],
                operating_margin=metrics_data.get('operatingMargins', [None])[-1],
                net_margin=metrics_data.get('profitMargins', [None])[-1],
                current_ratio=metrics_data.get('currentRatio'),
                debt_to_equity=metrics_data.get('debtToEquity'),
                raw_data=metrics_data
            )
            
            self.db.add(metric)
            self.db.commit()
            logger.info(f"Stored metrics for {symbol}")
            return metric
        
        except Exception as e:
            logger.error(f"Error fetching metrics for {symbol}: {e}")
            self.db.rollback()
            return None
    
    # ========================================================================
    # STOCK PRICES
    # ========================================================================
    
    def fetch_and_store_stock_prices(self, symbol: str, period: str = '1y') -> int:
        """Fetch and store historical stock prices."""
        stored_count = 0
        
        try:
            logger.info(f"Fetching stock prices for {symbol} (period: {period})")
            result = self.yahoo_client.get_historical_prices(symbol, period=period)
            
            if result is None or not isinstance(result, dict):
                logger.warning(f"No price data found for {symbol}")
                return 0
            
            prices_list = result.get('prices', [])
            if not prices_list:
                logger.warning(f"No price data found for {symbol}")
                return 0
            
            for price_data in prices_list:
                try:
                    # Parse date
                    from datetime import datetime
                    if isinstance(price_data['date'], str):
                        price_date = datetime.fromisoformat(price_data['date'].replace('Z', '+00:00'))
                    else:
                        price_date = price_data['date']
                    
                    # Check if already exists
                    existing = self.db.query(models.StockPrice).filter(
                        and_(
                            models.StockPrice.symbol == symbol,
                            models.StockPrice.price_date == price_date
                        )
                    ).first()
                    
                    if existing:
                        continue
                    
                    price = models.StockPrice(
                        symbol=symbol,
                        price_date=price_date,
                        open_price=float(price_data.get('open', 0)),
                        high_price=float(price_data.get('high', 0)),
                        low_price=float(price_data.get('low', 0)),
                        close_price=float(price_data.get('close', 0)),
                        adj_close_price=float(price_data.get('adj_close', 0)) if price_data.get('adj_close') else None,
                        volume=float(price_data.get('volume', 0)) if price_data.get('volume') else None
                    )
                    
                    self.db.add(price)
                    stored_count += 1
                
                except Exception as e:
                    logger.debug(f"Error storing price for {symbol}: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {stored_count} price records for {symbol}")
        
        except Exception as e:
            logger.error(f"Error fetching stock prices for {symbol}: {e}")
            self.db.rollback()
        
        return stored_count
    
    def fetch_and_store_dividends(self, symbol: str) -> int:
        """Fetch and store dividend history."""
        stored_count = 0
        
        try:
            logger.info(f"Fetching dividends for {symbol}")
            result = self.yahoo_client.get_dividends(symbol)
            
            if result is None or not isinstance(result, dict):
                logger.info(f"No dividend data found for {symbol}")
                return 0
            
            dividends_list = result.get('dividends', [])
            if not dividends_list:
                logger.info(f"No dividend data found for {symbol}")
                return 0
            
            for div_data in dividends_list:
                try:
                    # Parse date
                    from datetime import datetime
                    if isinstance(div_data['date'], str):
                        div_date = datetime.fromisoformat(div_data['date'].replace('Z', '+00:00'))
                    else:
                        div_date = div_data['date']
                    
                    # Check if already exists
                    existing = self.db.query(models.Dividend).filter(
                        and_(
                            models.Dividend.symbol == symbol,
                            models.Dividend.ex_date == div_date
                        )
                    ).first()
                    
                    if existing:
                        continue
                    
                    dividend = models.Dividend(
                        symbol=symbol,
                        ex_date=div_date,
                        dividend_per_share=float(div_data.get('amount', 0)),
                        dividend_type='cash'
                    )
                    
                    self.db.add(dividend)
                    stored_count += 1
                
                except Exception as e:
                    logger.debug(f"Error storing dividend for {symbol}: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {stored_count} dividend records for {symbol}")
        
        except Exception as e:
            logger.error(f"Error fetching dividends for {symbol}: {e}")
            self.db.rollback()
        
        return stored_count
    
    # ========================================================================
    # NEWS
    # ========================================================================
    
    def fetch_and_store_news(self, symbol: str, days: int = 30) -> int:
        """Fetch and store news articles for a stock."""
        stored_count = 0
        
        try:
            logger.info(f"Fetching news for {symbol}")
            
            # Crawl from all sources
            articles_by_source = self.news_aggregator.crawl_for_symbol(symbol, days=days)
            
            # Normalize and deduplicate
            normalized = self.news_aggregator.normalize_articles(articles_by_source)
            
            for article in normalized:
                try:
                    # Check if already exists by URL
                    existing = self.db.query(models.CompanyNews).filter(
                        models.CompanyNews.url == article.get('url')
                    ).first()
                    
                    if existing:
                        continue
                    
                    news = models.CompanyNews(
                        symbol=symbol,
                        title=article.get('title', '')[:500],
                        url=article.get('url', ''),
                        source=article.get('source', 'unknown'),
                        source_name=article.get('source_name', ''),
                        published_at=article.get('published_at'),
                        crawled_at=datetime.now(),
                        content_hash=article.get('content_hash', ''),
                        language='vi'
                    )
                    
                    self.db.add(news)
                    stored_count += 1
                
                except Exception as e:
                    logger.debug(f"Error storing news article: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {stored_count} news articles for {symbol}")
        
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            self.db.rollback()
        
        return stored_count
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def fetch_all_data_for_symbol(self, symbol: str, include_news: bool = True) -> Dict[str, Any]:
        """Fetch all available data for a single stock."""
        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'company_info': None,
            'quarterly_reports': 0,
            'annual_reports': 0,
            'metrics': None,
            'stock_prices': 0,
            'dividends': 0,
            'news': 0,
            'errors': []
        }
        
        try:
            # Company Info
            try:
                results['company_info'] = self.fetch_and_store_company_info(symbol) is not None
            except Exception as e:
                results['errors'].append(f"Company info error: {str(e)}")
            
            # Financial Reports
            try:
                quarterly = self.fetch_and_store_quarterly_reports(symbol)
                results['quarterly_reports'] = len(quarterly)
            except Exception as e:
                results['errors'].append(f"Quarterly reports error: {str(e)}")
            
            try:
                annual = self.fetch_and_store_annual_reports(symbol)
                results['annual_reports'] = len(annual)
            except Exception as e:
                results['errors'].append(f"Annual reports error: {str(e)}")
            
            # Metrics
            try:
                results['metrics'] = self.fetch_and_store_metrics(symbol) is not None
            except Exception as e:
                results['errors'].append(f"Metrics error: {str(e)}")
            
            # Stock Prices
            try:
                results['stock_prices'] = self.fetch_and_store_stock_prices(symbol)
            except Exception as e:
                results['errors'].append(f"Stock prices error: {str(e)}")
            
            # Dividends
            try:
                results['dividends'] = self.fetch_and_store_dividends(symbol)
            except Exception as e:
                results['errors'].append(f"Dividends error: {str(e)}")
            
            # News
            if include_news:
                try:
                    results['news'] = self.fetch_and_store_news(symbol)
                except Exception as e:
                    results['errors'].append(f"News error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error processing {symbol}: {e}")
            results['errors'].append(f"Unexpected error: {str(e)}")
        
        return results
    
    def _fetch_symbol_worker(self, symbol: str, include_news: bool) -> Dict[str, Any]:
        """Worker function for batch processing - creates its own session."""
        from app.db.database import SessionLocal
        
        # Create new session for this thread
        worker_db = SessionLocal()
        try:
            # Create a new service instance with this thread's session
            worker_service = IntegratedDataService(worker_db)
            
            # Fetch all data
            result = worker_service.fetch_all_data_for_symbol(symbol, include_news=include_news)
            return result
        except Exception as e:
            logger.error(f"Error in worker for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e), 'errors': [str(e)]}
        finally:
            worker_db.close()
    
    def fetch_all_data_batch(self, symbols: List[str], max_workers: int = 3,
                             include_news: bool = True) -> Dict[str, Any]:
        """Fetch all data for multiple symbols in parallel."""
        batch_results = {
            'total_symbols': len(symbols),
            'successful': 0,
            'failed': 0,
            'results': {},
            'start_time': datetime.now().isoformat(),
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._fetch_symbol_worker, symbol, include_news): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    batch_results['results'][symbol] = result
                    
                    if not result.get('errors', []):
                        batch_results['successful'] += 1
                    else:
                        batch_results['failed'] += 1
                    
                    logger.info(f"Completed {symbol}: {batch_results['successful']}/{len(symbols)}")
                
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    batch_results['results'][symbol] = {
                        'error': str(e),
                        'symbol': symbol,
                        'errors': [str(e)]
                    }
                    batch_results['failed'] += 1
                
                # Rate limiting
                time.sleep(0.5)
        
        batch_results['end_time'] = datetime.now().isoformat()
        return batch_results
