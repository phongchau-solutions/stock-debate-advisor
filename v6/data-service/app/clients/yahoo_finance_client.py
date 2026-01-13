"""
Yahoo Finance API Client for fetching stock data and financial reports.
Provides access to historical prices, fundamentals, and quarterly/annual reports.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
import backoff
import json
import numpy as np

logger = logging.getLogger(__name__)


def convert_to_serializable(obj):
    """Convert pandas/numpy objects to JSON-serializable types."""
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (pd.Series, pd.Index)):
        return obj.to_list()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        # Convert all keys to strings and recursively convert values
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj


class YahooFinanceClient:
    """Client for Yahoo Finance data retrieval."""

    def __init__(self):
        """Initialize Yahoo Finance client."""
        # No session initialization needed for yfinance
        pass

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic ticker information.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'VCB.VN')
            
        Returns:
            Dict containing company info, industry, sector, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap'),
                'employees': info.get('fullTimeEmployees'),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', ''),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker info for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get historical price data.
        
        Args:
            symbol: Stock symbol
            period: Period of data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            
        Returns:
            Dict with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise ValueError(f"No historical data found for {symbol}")
            
            # Convert DataFrame to dict format
            prices = []
            for date, row in hist.iterrows():
                prices.append({
                    'date': convert_to_serializable(date),
                    'open': float(row.get('Open', 0)),
                    'high': float(row.get('High', 0)),
                    'low': float(row.get('Low', 0)),
                    'close': float(row.get('Close', 0)),
                    'volume': int(row.get('Volume', 0)),
                    'adj_close': float(row.get('Adj Close', 0)),
                })
            
            return {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'records': len(prices),
                'prices': prices,
            }
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_quarterly_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Get quarterly financial data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with quarterly income statement, balance sheet, cash flow
        """
        try:
            ticker = yf.Ticker(symbol)
            
            quarterly_data = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'quarterly_financials': {},
                'quarterly_balance_sheet': {},
                'quarterly_cash_flow': {},
            }
            
            # Quarterly Income Statement
            try:
                q_income = ticker.quarterly_financials
                if not q_income.empty:
                    quarterly_data['quarterly_financials'] = convert_to_serializable(q_income.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch quarterly financials for {symbol}: {e}")
            
            # Quarterly Balance Sheet
            try:
                q_balance = ticker.quarterly_balance_sheet
                if not q_balance.empty:
                    quarterly_data['quarterly_balance_sheet'] = convert_to_serializable(q_balance.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch quarterly balance sheet for {symbol}: {e}")
            
            # Quarterly Cash Flow
            try:
                q_cashflow = ticker.quarterly_cashflow
                if not q_cashflow.empty:
                    quarterly_data['quarterly_cash_flow'] = convert_to_serializable(q_cashflow.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch quarterly cash flow for {symbol}: {e}")
            
            return quarterly_data
        except Exception as e:
            logger.error(f"Error fetching quarterly financials for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_annual_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Get annual financial data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with annual income statement, balance sheet, cash flow
        """
        try:
            ticker = yf.Ticker(symbol)
            
            annual_data = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'annual_financials': {},
                'annual_balance_sheet': {},
                'annual_cash_flow': {},
            }
            
            # Annual Income Statement
            try:
                a_income = ticker.financials
                if not a_income.empty:
                    annual_data['annual_financials'] = convert_to_serializable(a_income.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch annual financials for {symbol}: {e}")
            
            # Annual Balance Sheet
            try:
                a_balance = ticker.balance_sheet
                if not a_balance.empty:
                    annual_data['annual_balance_sheet'] = convert_to_serializable(a_balance.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch annual balance sheet for {symbol}: {e}")
            
            # Annual Cash Flow
            try:
                a_cashflow = ticker.cashflow
                if not a_cashflow.empty:
                    annual_data['annual_cash_flow'] = convert_to_serializable(a_cashflow.to_dict())
            except Exception as e:
                logger.warning(f"Failed to fetch annual cash flow for {symbol}: {e}")
            
            return annual_data
        except Exception as e:
            logger.error(f"Error fetching annual financials for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Get key financial metrics and ratios.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with PE, PB, dividend yield, beta, etc.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            metrics = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'eps': info.get('trailingEps'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'free_cashflow': info.get('freeCashflow'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'revenue': info.get('totalRevenue'),
                'gross_profit': info.get('grossProfits'),
                'operating_income': info.get('operatingCashflow'),
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error fetching key metrics for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_dividends(self, symbol: str) -> Dict[str, Any]:
        """
        Get dividend history.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with dividend dates and amounts
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            dividend_list = []
            if not dividends.empty:
                for date, amount in dividends.items():
                    dividend_list.append({
                        'date': convert_to_serializable(date),
                        'amount': float(amount),
                    })
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'total_records': len(dividend_list),
                'dividends': dividend_list,
            }
        except Exception as e:
            logger.error(f"Error fetching dividends for {symbol}: {e}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_splits(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock split history.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with stock split dates and ratios
        """
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            
            splits_list = []
            if not splits.empty:
                for date, ratio in splits.items():
                    splits_list.append({
                        'date': convert_to_serializable(date),
                        'ratio': float(ratio),
                    })
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'total_records': len(splits_list),
                'splits': splits_list,
            }
        except Exception as e:
            logger.error(f"Error fetching splits for {symbol}: {e}")
            raise

    def get_all_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a symbol.
        
        Returns:
            Dict with all available financial information
        """
        try:
            data = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
            }

            # Ticker info
            try:
                data['info'] = self.get_ticker_info(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch ticker info: {e}")
                data['info'] = {}

            # Historical prices (1 year)
            try:
                data['prices'] = self.get_historical_prices(symbol, period="1y")
            except Exception as e:
                logger.warning(f"Failed to fetch historical prices: {e}")
                data['prices'] = {}

            # Quarterly financials
            try:
                data['quarterly'] = self.get_quarterly_financials(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch quarterly financials: {e}")
                data['quarterly'] = {}

            # Annual financials
            try:
                data['annual'] = self.get_annual_financials(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch annual financials: {e}")
                data['annual'] = {}

            # Key metrics
            try:
                data['metrics'] = self.get_key_metrics(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch key metrics: {e}")
                data['metrics'] = {}

            # Dividends
            try:
                data['dividends'] = self.get_dividends(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch dividends: {e}")
                data['dividends'] = {}

            # Stock splits
            try:
                data['splits'] = self.get_splits(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch splits: {e}")
                data['splits'] = {}

            return data

        except Exception as e:
            logger.error(f"Error fetching comprehensive financial data for {symbol}: {e}")
            raise
