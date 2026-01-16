"""
Data service for fetching and caching stock data
Provides unified access to company, financial, and price data
"""

import logging
from typing import Dict, Any, Optional, List
from .database import DynamoDBClient
from .models import CompanyRecord, FinancialReportRecord, OhlcPriceRecord

logger = logging.getLogger(__name__)


class DataService:
    """Service for accessing stock and financial data"""

    def __init__(self, db_client: DynamoDBClient):
        """
        Initialize data service
        
        Args:
            db_client: DynamoDB client for data access
        """
        self.db = db_client

    def get_company_info(
        self,
        symbol: str,
        companies_table: str = "Companies"
    ) -> Optional[Dict[str, Any]]:
        """
        Get company information
        
        Args:
            symbol: Stock symbol
            companies_table: DynamoDB table name
            
        Returns:
            Company info dict or None
        """
        try:
            record = self.db.get_company_record(companies_table, symbol)
            if record:
                return {
                    "symbol": record.symbol,
                    "name": record.name,
                    "sector": record.sector,
                    "industry": record.industry,
                    "market_cap": record.market_cap
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            raise

    def get_financial_data(
        self,
        symbol: str,
        financial_reports_table: str = "FinancialReports",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get financial data for a symbol
        
        Args:
            symbol: Stock symbol
            financial_reports_table: DynamoDB table name
            limit: Max number of records
            
        Returns:
            List of financial data dicts
        """
        try:
            records = self.db.query_financial_reports(
                financial_reports_table,
                symbol,
                limit
            )
            return [
                {
                    "symbol": r.symbol,
                    "date": r.report_date,
                    "type": r.report_type,
                    "metrics": r.metrics
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"Failed to get financial data for {symbol}: {e}")
            raise

    def get_price_data(
        self,
        symbol: str,
        ohlc_prices_table: str = "OHLCPrices",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get OHLC price data for a symbol
        
        Args:
            symbol: Stock symbol
            ohlc_prices_table: DynamoDB table name
            limit: Max number of records
            
        Returns:
            List of OHLC price dicts
        """
        try:
            records = self.db.query_ohlc_prices(
                ohlc_prices_table,
                symbol,
                limit
            )
            return [
                {
                    "date": r.date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"Failed to get price data for {symbol}: {e}")
            raise

    def get_all_company_data(
        self,
        symbol: str,
        companies_table: str = "Companies",
        financial_reports_table: str = "FinancialReports",
        ohlc_prices_table: str = "OHLCPrices"
    ) -> Dict[str, Any]:
        """
        Get comprehensive data for a symbol
        
        Args:
            symbol: Stock symbol
            companies_table: Companies table name
            financial_reports_table: Financial reports table name
            ohlc_prices_table: OHLC prices table name
            
        Returns:
            Dict with all available data
        """
        try:
            company = self.get_company_info(symbol, companies_table)
            financial = self.get_financial_data(symbol, financial_reports_table)
            prices = self.get_price_data(symbol, ohlc_prices_table)

            return {
                "symbol": symbol,
                "company": company,
                "financial": financial,
                "prices": prices
            }
        except Exception as e:
            logger.error(f"Failed to get all company data for {symbol}: {e}")
            raise
