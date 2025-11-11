"""
VietCap API Client for fetching financial data.
"""
import requests
import backoff
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VietCapClient:
    """Client for VietCap IQ API."""

    BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize VietCap client."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company basic information."""
        url = f"{self.BASE_URL}/company/{symbol}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_financial_statements(
        self,
        symbol: str,
        section: str = "BALANCE_SHEET",
        length_report: int = 10
    ) -> Dict[str, Any]:
        """
        Get financial statements.
        
        Args:
            symbol: Stock symbol
            section: BALANCE_SHEET, INCOME_STATEMENT, CASH_FLOW, NOTE
            length_report: Number of periods to retrieve
        """
        url = f"{self.BASE_URL}/company/{symbol}/financial-statement"
        params = {
            "section": section,
            "lengthReport": length_report
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_financial_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get financial metrics."""
        url = f"{self.BASE_URL}/company/{symbol}/financial-statement/metrics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_price_chart(
        self,
        symbol: str,
        length_report: int = 10,
        to_current: bool = True
    ) -> Dict[str, Any]:
        """Get historical price data."""
        url = f"{self.BASE_URL}/company/{symbol}/price-chart"
        params = {
            "lengthReport": length_report,
            "toCurrent": str(to_current).lower()
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_company_ratios(
        self,
        symbol: str,
        length_report: int = 10
    ) -> Dict[str, Any]:
        """Get company financial ratios."""
        url = f"{self.BASE_URL}/company-ratio-daily/{symbol}"
        params = {"lengthReport": length_report}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def get_technical_indicators(
        self,
        symbol: str,
        time_range: str = "ONE_DAY"
    ) -> Dict[str, Any]:
        """Get technical indicators."""
        url = f"{self.BASE_URL}/company/{symbol}/technical/{time_range}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_all_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a symbol.
        
        Returns:
            Dict with company_info, balance_sheet, income_statement, 
            cash_flow, metrics, prices, ratios, technical
        """
        try:
            data = {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Company info
            try:
                data["company_info"] = self.get_company_info(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch company info: {e}")
                data["company_info"] = {}

            # Financial statements
            for section in ["BALANCE_SHEET", "INCOME_STATEMENT", "CASH_FLOW"]:
                try:
                    data[section.lower()] = self.get_financial_statements(symbol, section)
                except Exception as e:
                    logger.warning(f"Failed to fetch {section}: {e}")
                    data[section.lower()] = {}

            # Metrics
            try:
                data["metrics"] = self.get_financial_metrics(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch metrics: {e}")
                data["metrics"] = {}

            # Price data
            try:
                data["prices"] = self.get_price_chart(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch prices: {e}")
                data["prices"] = {}

            # Ratios
            try:
                data["ratios"] = self.get_company_ratios(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch ratios: {e}")
                data["ratios"] = {}

            # Technical indicators
            try:
                data["technical"] = self.get_technical_indicators(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch technical indicators: {e}")
                data["technical"] = {}

            return data

        except Exception as e:
            logger.error(f"Error fetching financial data for {symbol}: {e}")
            raise
