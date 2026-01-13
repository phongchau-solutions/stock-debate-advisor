"""
File-based data store manager.
Organizes data by year and stock symbol, with append-only timeseries files.

Structure:
  data_store/
  ├── 2026/
  │   ├── MBB.VN/
  │   │   ├── financial_reports.json  (timeseries, append-only)
  │   │   ├── ohlc_prices.json        (timeseries, append-only)
  │   │   └── news.json               (timeseries, append-only)
  │   ├── VCB.VN/
  │   │   ├── financial_reports.json
  │   │   ├── ohlc_prices.json
  │   │   └── news.json
  │   ...
  ├── 2027/
  │   ...
"""
import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)

# Thread-safe file locking
file_locks = {}


class DataStoreManager:
    """Manages file-based data storage organized by stock and year."""
    
    def __init__(self, base_path: str = "./data_store"):
        """Initialize data store manager.
        
        Args:
            base_path: Root directory for data store
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data store initialized at: {self.base_path}")
    
    def _get_lock(self, file_path: str) -> Lock:
        """Get thread lock for a file (create if not exists)."""
        if file_path not in file_locks:
            file_locks[file_path] = Lock()
        return file_locks[file_path]
    
    def _get_stock_year_dir(self, symbol: str, year: Optional[int] = None) -> Path:
        """Get directory for a stock in a given year.
        
        Args:
            symbol: Stock symbol (e.g., MBB.VN)
            year: Year (defaults to current year)
            
        Returns:
            Path to stock's year directory
        """
        if year is None:
            year = datetime.now().year
        
        stock_dir = self.base_path / str(year) / symbol
        stock_dir.mkdir(parents=True, exist_ok=True)
        return stock_dir
    
    def _get_file_path(self, symbol: str, file_type: str, year: Optional[int] = None) -> Path:
        """Get file path for a specific data type.
        
        Args:
            symbol: Stock symbol
            file_type: 'financial_reports', 'ohlc_prices', or 'news'
            year: Year (defaults to current)
            
        Returns:
            Path to the file
        """
        valid_types = {'financial_reports', 'ohlc_prices', 'news'}
        if file_type not in valid_types:
            raise ValueError(f"Invalid file type. Must be one of {valid_types}")
        
        stock_dir = self._get_stock_year_dir(symbol, year)
        return stock_dir / f"{file_type}.json"
    
    def _read_json_lines(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read JSONL (JSON Lines) format file.
        
        Each line is a separate JSON object, enabling append-only writes.
        """
        records = []
        
        if not file_path.exists():
            return records
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num} of {file_path}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        
        return records
    
    def _append_json_line(self, file_path: Path, record: Dict[str, Any]) -> bool:
        """Append a JSON record as a line to file.
        
        Thread-safe append operation. Each record is a separate line.
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Thread-safe file write
            lock = self._get_lock(str(file_path))
            with lock:
                with open(file_path, 'a', encoding='utf-8') as f:
                    json.dump(record, f, ensure_ascii=False)
                    f.write('\n')
            
            return True
        except Exception as e:
            logger.error(f"Error appending to {file_path}: {e}")
            return False
    
    # ========================================================================
    # OHLC PRICES - Daily stock prices
    # ========================================================================
    
    def append_ohlc_price(self, symbol: str, price_data: Dict[str, Any], 
                         year: Optional[int] = None) -> bool:
        """Append a daily OHLC price record.
        
        Args:
            symbol: Stock symbol
            price_data: {date, open, high, low, close, adj_close, volume}
            year: Year (defaults to current)
            
        Returns:
            True if successful
        """
        # Ensure timestamp
        if 'timestamp' not in price_data and 'date' in price_data:
            price_data['timestamp'] = price_data['date']
        
        file_path = self._get_file_path(symbol, 'ohlc_prices', year)
        logger.debug(f"Appending OHLC price for {symbol}: {price_data}")
        return self._append_json_line(file_path, price_data)
    
    def append_ohlc_prices(self, symbol: str, prices: List[Dict[str, Any]], 
                          year: Optional[int] = None) -> int:
        """Append multiple OHLC price records.
        
        Args:
            symbol: Stock symbol
            prices: List of price records
            year: Year
            
        Returns:
            Number of records appended
        """
        count = 0
        for price in prices:
            if self.append_ohlc_price(symbol, price, year):
                count += 1
        
        logger.info(f"Appended {count} OHLC records for {symbol}")
        return count
    
    def get_ohlc_prices(self, symbol: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all OHLC prices for a symbol in a year.
        
        Args:
            symbol: Stock symbol
            year: Year (defaults to current)
            
        Returns:
            List of price records (chronologically ordered)
        """
        file_path = self._get_file_path(symbol, 'ohlc_prices', year)
        records = self._read_json_lines(file_path)
        logger.info(f"Retrieved {len(records)} OHLC records for {symbol} in {year or datetime.now().year}")
        return records
    
    # ========================================================================
    # FINANCIAL REPORTS - Quarterly and annual reports
    # ========================================================================
    
    def append_financial_report(self, symbol: str, report: Dict[str, Any], 
                               year: Optional[int] = None) -> bool:
        """Append a financial report (quarterly or annual).
        
        Args:
            symbol: Stock symbol
            report: {fiscal_year, fiscal_quarter, period_end_date, revenue, ...}
            year: Year (defaults to current)
            
        Returns:
            True if successful
        """
        # Ensure timestamp
        if 'timestamp' not in report:
            report['timestamp'] = datetime.utcnow().isoformat()
        
        file_path = self._get_file_path(symbol, 'financial_reports', year)
        logger.debug(f"Appending financial report for {symbol}: FY{report.get('fiscal_year')} Q{report.get('fiscal_quarter')}")
        return self._append_json_line(file_path, report)
    
    def append_financial_reports(self, symbol: str, reports: List[Dict[str, Any]], 
                                year: Optional[int] = None) -> int:
        """Append multiple financial reports.
        
        Args:
            symbol: Stock symbol
            reports: List of report records
            year: Year
            
        Returns:
            Number of records appended
        """
        count = 0
        for report in reports:
            if self.append_financial_report(symbol, report, year):
                count += 1
        
        logger.info(f"Appended {count} financial reports for {symbol}")
        return count
    
    def get_financial_reports(self, symbol: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all financial reports for a symbol.
        
        Args:
            symbol: Stock symbol
            year: Year (defaults to current)
            
        Returns:
            List of financial report records
        """
        file_path = self._get_file_path(symbol, 'financial_reports', year)
        records = self._read_json_lines(file_path)
        logger.info(f"Retrieved {len(records)} financial reports for {symbol}")
        return records
    
    # ========================================================================
    # NEWS - News articles and press releases
    # ========================================================================
    
    def append_news_article(self, symbol: str, article: Dict[str, Any], 
                           year: Optional[int] = None) -> bool:
        """Append a news article.
        
        Args:
            symbol: Stock symbol
            article: {title, url, source, published_at, content, ...}
            year: Year (defaults to current)
            
        Returns:
            True if successful
        """
        # Ensure timestamp
        if 'timestamp' not in article:
            article['timestamp'] = datetime.utcnow().isoformat()
        
        file_path = self._get_file_path(symbol, 'news', year)
        logger.debug(f"Appending news article for {symbol}: {article.get('title', 'N/A')[:50]}")
        return self._append_json_line(file_path, article)
    
    def append_news_articles(self, symbol: str, articles: List[Dict[str, Any]], 
                            year: Optional[int] = None) -> int:
        """Append multiple news articles.
        
        Args:
            symbol: Stock symbol
            articles: List of article records
            year: Year
            
        Returns:
            Number of records appended
        """
        count = 0
        for article in articles:
            if self.append_news_article(symbol, article, year):
                count += 1
        
        logger.info(f"Appended {count} news articles for {symbol}")
        return count
    
    def get_news_articles(self, symbol: str, year: Optional[int] = None, 
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get news articles for a symbol.
        
        Args:
            symbol: Stock symbol
            year: Year (defaults to current)
            limit: Max number of articles to return
            
        Returns:
            List of news articles (most recent first)
        """
        file_path = self._get_file_path(symbol, 'news', year)
        records = self._read_json_lines(file_path)
        
        # Sort by timestamp (most recent first)
        try:
            records = sorted(records, key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            logger.warning(f"Could not sort news articles: {e}")
        
        if limit:
            records = records[:limit]
        
        logger.info(f"Retrieved {len(records)} news articles for {symbol}")
        return records
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_stock_years(self, symbol: str) -> List[int]:
        """Get all years that have data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of years (sorted)
        """
        years = []
        for year_dir in self.base_path.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                stock_dir = year_dir / symbol
                if stock_dir.exists():
                    years.append(int(year_dir.name))
        
        return sorted(years)
    
    def get_symbols(self, year: Optional[int] = None) -> List[str]:
        """Get all symbols with data in a year.
        
        Args:
            year: Year (defaults to current)
            
        Returns:
            List of stock symbols
        """
        if year is None:
            year = datetime.now().year
        
        year_dir = self.base_path / str(year)
        if not year_dir.exists():
            return []
        
        symbols = [d.name for d in year_dir.iterdir() if d.is_dir()]
        return sorted(symbols)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about the data store.
        
        Returns:
            Dict with storage stats
        """
        total_files = 0
        total_size_mb = 0
        years = {}
        
        for year_dir in self.base_path.iterdir():
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = year_dir.name
                years[year] = {}
                
                for stock_dir in year_dir.iterdir():
                    if stock_dir.is_dir():
                        symbol = stock_dir.name
                        file_count = len(list(stock_dir.glob('*.json')))
                        size_mb = sum(f.stat().st_size for f in stock_dir.glob('*.json')) / (1024 * 1024)
                        
                        if file_count > 0:
                            years[year][symbol] = {
                                'files': file_count,
                                'size_mb': round(size_mb, 2)
                            }
                            total_files += file_count
                            total_size_mb += size_mb
        
        return {
            'base_path': str(self.base_path),
            'total_files': total_files,
            'total_size_mb': round(total_size_mb, 2),
            'years': years
        }
    
    def clear_year(self, year: int) -> bool:
        """Clear all data for a specific year (dangerous!).
        
        Args:
            year: Year to clear
            
        Returns:
            True if successful
        """
        year_dir = self.base_path / str(year)
        if not year_dir.exists():
            logger.warning(f"Year directory {year} does not exist")
            return False
        
        try:
            import shutil
            shutil.rmtree(year_dir)
            logger.warning(f"Cleared all data for year {year}")
            return True
        except Exception as e:
            logger.error(f"Error clearing year {year}: {e}")
            return False
