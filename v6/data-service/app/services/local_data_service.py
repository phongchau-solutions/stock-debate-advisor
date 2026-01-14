"""
Local Data Service
Provides access to JSON-based financial data from data_store directory.
Loads company_info, financial_reports, and ohlc_prices for stocks.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalDataService:
    """Service for loading and managing local JSON data from data_store."""
    
    def __init__(self, data_store_path: Optional[str] = None):
        """
        Initialize the service with data_store path.
        
        Args:
            data_store_path: Path to data_store directory. If None, uses default.
        """
        if data_store_path is None:
            # Default to data_store/2026 in the project
            self.data_store_path = Path(__file__).parent.parent.parent / "data_store" / "2026"
        else:
            self.data_store_path = Path(data_store_path)
        
        logger.info(f"Initialized LocalDataService with path: {self.data_store_path}")
    
    def get_available_stocks(self) -> List[str]:
        """Get list of all available stock symbols."""
        if not self.data_store_path.exists():
            logger.warning(f"Data store path does not exist: {self.data_store_path}")
            return []
        
        stocks = []
        for stock_dir in self.data_store_path.iterdir():
            if stock_dir.is_dir() and (stock_dir / "company_info.json").exists():
                stocks.append(stock_dir.name)
        
        return sorted(stocks)
    
    def _load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse a JSON file."""
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def get_stock_path(self, symbol: str) -> Optional[Path]:
        """Get the directory path for a stock symbol."""
        # Normalize symbol (remove spaces, uppercase)
        symbol = symbol.upper().strip()
        
        # Support both 'ACB' and 'ACB.VN' formats
        if not symbol.endswith('.VN'):
            symbol = f"{symbol}.VN"
        
        stock_path = self.data_store_path / symbol
        if stock_path.exists():
            return stock_path
        
        # Try without .VN suffix if it fails
        if symbol.endswith('.VN'):
            alternative = self.data_store_path / symbol[:-3]
            if alternative.exists():
                return alternative
        
        return None
    
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company information for a stock.
        
        Args:
            symbol: Stock symbol (e.g., 'ACB' or 'ACB.VN')
        
        Returns:
            Dictionary with company information or None if not found.
        """
        stock_path = self.get_stock_path(symbol)
        if not stock_path:
            logger.warning(f"Stock not found: {symbol}")
            return None
        
        data = self._load_json_file(stock_path / "company_info.json")
        if data:
            return data
        
        return None
    
    def get_financial_reports(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get financial reports for a stock (quarterly, annual, metrics, dividends, splits).
        
        Args:
            symbol: Stock symbol (e.g., 'ACB' or 'ACB.VN')
        
        Returns:
            Dictionary with financial reports or None if not found.
        """
        stock_path = self.get_stock_path(symbol)
        if not stock_path:
            logger.warning(f"Stock not found: {symbol}")
            return None
        
        data = self._load_json_file(stock_path / "financial_reports.json")
        if data:
            return data
        
        return None
    
    def get_quarterly_reports(self, symbol: str, limit: int = 8) -> Optional[Dict[str, Any]]:
        """
        Get quarterly financial reports for a stock.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of quarters to return
        
        Returns:
            Dictionary with quarterly financial reports
        """
        reports = self.get_financial_reports(symbol)
        if not reports or 'quarterly' not in reports:
            return None
        
        quarterly_data = reports['quarterly'].get('quarterly_financials', {})
        
        # Convert to list, sort by period (reverse chronological), limit
        quarters = list(quarterly_data.items())
        quarters.reverse()
        quarters = quarters[:limit]
        
        return {
            'symbol': symbol,
            'data_type': 'quarterly',
            'report_count': len(quarters),
            'periods': dict(quarters),
            'timestamp': reports.get('timestamp')
        }
    
    def get_annual_reports(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get annual financial reports for a stock.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of years to return
        
        Returns:
            Dictionary with annual financial reports
        """
        reports = self.get_financial_reports(symbol)
        if not reports or 'annual' not in reports:
            return None
        
        annual_data = reports['annual'].get('annual_financials', {})
        
        # Convert to list, sort by year (reverse chronological), limit
        years = list(annual_data.items())
        years.reverse()
        years = years[:limit]
        
        return {
            'symbol': symbol,
            'data_type': 'annual',
            'report_count': len(years),
            'periods': dict(years),
            'timestamp': reports.get('timestamp')
        }
    
    def get_financial_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get financial metrics for a stock (PE ratio, dividend yield, etc.).
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with financial metrics
        """
        reports = self.get_financial_reports(symbol)
        if not reports or 'metrics' not in reports:
            return None
        
        metrics = reports['metrics']
        return {
            'symbol': symbol,
            'data_type': 'metrics',
            'metrics': {k: v for k, v in metrics.items() if k not in ['symbol', 'timestamp']},
            'timestamp': reports.get('timestamp')
        }
    
    def get_dividends(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get dividend history for a stock.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with dividend records
        """
        reports = self.get_financial_reports(symbol)
        if not reports or 'dividends' not in reports:
            return None
        
        dividends = reports['dividends'].get('dividends', [])
        return {
            'symbol': symbol,
            'data_type': 'dividends',
            'dividend_count': len(dividends),
            'dividends': dividends,
            'timestamp': reports.get('timestamp')
        }
    
    def get_stock_splits(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock split history for a stock.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with stock split records
        """
        reports = self.get_financial_reports(symbol)
        if not reports or 'splits' not in reports:
            return None
        
        splits = reports['splits'].get('splits', [])
        return {
            'symbol': symbol,
            'data_type': 'splits',
            'split_count': len(splits),
            'splits': splits,
            'timestamp': reports.get('timestamp')
        }
    
    def get_ohlc_prices(self, symbol: str, limit: int = 249) -> Optional[Dict[str, Any]]:
        """
        Get OHLC price data for a stock.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of days to return (max 249)
        
        Returns:
            Dictionary with OHLC price data
        """
        stock_path = self.get_stock_path(symbol)
        if not stock_path:
            logger.warning(f"Stock not found: {symbol}")
            return None
        
        data = self._load_json_file(stock_path / "ohlc_prices.json")
        if not data or 'prices' not in data:
            return None
        
        prices = data['prices']
        
        # Limit and sort by date (most recent first)
        if limit and len(prices) > limit:
            prices = prices[:limit]
        
        return {
            'symbol': symbol,
            'data_type': 'ohlc_prices',
            'price_count': len(prices),
            'period': data.get('period', '1-day'),
            'interval': data.get('interval', 'daily'),
            'prices': prices,
            'timestamp': data.get('timestamp')
        }
    
    def get_news_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get news data for a stock (if available).
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with news data or None if not available
        """
        stock_path = self.get_stock_path(symbol)
        if not stock_path:
            return None
        
        news_file = stock_path / "news_data.json"
        if not news_file.exists():
            return None
        
        return self._load_json_file(news_file)
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for companies by name or symbol.
        
        Args:
            query: Search query (searches symbol and company name)
            limit: Maximum number of results
        
        Returns:
            List of matching companies
        """
        query_lower = query.lower().strip()
        results = []
        
        for symbol in self.get_available_stocks():
            if len(results) >= limit:
                break
            
            company = self.get_company_info(symbol)
            if not company or 'info' not in company:
                continue
            
            info = company['info']
            name = info.get('name', '').lower()
            
            # Check if query matches symbol or name
            if query_lower in symbol.lower() or query_lower in name:
                results.append({
                    'symbol': symbol,
                    'name': info.get('name'),
                    'sector': info.get('sector'),
                    'industry': info.get('industry')
                })
        
        return results
    
    def get_all_stocks_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary information for all stocks.
        
        Returns:
            List of all stocks with basic info
        """
        stocks = []
        for symbol in self.get_available_stocks():
            company = self.get_company_info(symbol)
            if company and 'info' in company:
                info = company['info']
                stocks.append({
                    'symbol': symbol,
                    'name': info.get('name'),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                    'market_cap': info.get('market_cap')
                })
        
        return stocks
