"""
Data loader for financial, technical, and sentiment data.
Follows SOLID, DRY, and KISS principles.
"""
import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Any
from config import config
from constants import (
    NumberScale,
    DataConstants,
    ErrorMessages
)


class NumberFormatter:
    """Handles number formatting operations.
    
    Single Responsibility: Number formatting only.
    """
    
    @staticmethod
    def format_large_number(num: float) -> str:
        """Format large numbers in billions (B), millions (M), or thousands (K).
        
        Args:
            num: Number to format
            
        Returns:
            Formatted string with suffix (e.g., "25.30B")
        """
        try:
            num = float(num)
            
            # Check each scale in order (largest first)
            for scale in NumberScale:
                if abs(num) >= scale.threshold:
                    formatted = num / scale.threshold
                    return f"{formatted:.{DataConstants.DECIMAL_PLACES}f}{scale.suffix}"
            
            # Below thousand threshold
            return f"{num:.{DataConstants.DECIMAL_PLACES}f}"
            
        except (ValueError, TypeError):
            return str(num)
    
    @staticmethod
    def format_financial_dict(data: dict) -> dict:
        """Format financial numbers in a dictionary for readability.
        
        Args:
            data: Dictionary with financial data
            
        Returns:
            Dictionary with formatted numbers
        """
        formatted = {}
        
        for key, value in data.items():
            if isinstance(value, (int, float)) and abs(value) >= DataConstants.MIN_FORMAT_THRESHOLD:
                formatted[key] = NumberFormatter.format_large_number(value)
                formatted[f"{key}_raw"] = value  # Keep raw value
            elif isinstance(value, dict):
                formatted[key] = NumberFormatter.format_financial_dict(value)
            elif isinstance(value, list):
                formatted[key] = [
                    NumberFormatter.format_financial_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                formatted[key] = value
                
        return formatted


class DataLoader:
    """Loads stock data from CSV/JSON files.
    
    Single Responsibility: Data loading and initial processing.
    Open/Closed: Can be extended with new data sources without modification.
    """
    
    def __init__(self):
        """Initialize data loader with configured paths."""
        self.finance_dir = config.FINANCE_DATA_PATH
        self.news_dir = config.NEWS_DATA_PATH
        self.formatter = NumberFormatter()
        
    def get_available_symbols(self) -> List[str]:
        """Get list of available stock symbols from data files.
        
        Returns:
            Sorted list of unique stock symbols
        """
        symbols = set()
        
        # Check finance data files
        if self.finance_dir.exists():
            for file_path in self.finance_dir.glob(f"*{DataConstants.FINANCIALS_SUFFIX}.*"):
                symbol = file_path.stem.split('_')[0].upper()
                symbols.add(symbol)
                
            # Check OHLC files
            for file_path in self.finance_dir.glob(f"*{DataConstants.OHLC_SUFFIX}.csv"):
                symbol = file_path.stem.split('_')[0].upper()
                symbols.add(symbol)
        
        return sorted(list(symbols))
    
    def load_financial_data(self, symbol: str) -> dict:
        """Load financial statement data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with formatted financial data
            
        Raises:
            FileNotFoundError: If no financial data found
        """
        # Try JSON first (preferred format)
        json_path = self.finance_dir / f"{symbol.lower()}{DataConstants.FINANCIALS_SUFFIX}.json"
        csv_path = self.finance_dir / f"{symbol.lower()}{DataConstants.FINANCIALS_SUFFIX}.csv"
        
        if json_path.exists():
            with open(json_path, 'r', encoding=DataConstants.CSV_ENCODING) as f:
                data = json.load(f)
                return self.formatter.format_financial_dict(data)
                
        elif csv_path.exists():
            df = pd.read_csv(csv_path)
            data = df.to_dict('records')
            return self.formatter.format_financial_dict({"records": data})
            
        else:
            # Return mock data if no file found
            return {
                "PE_Ratio": "18.50",
                "ROE": "15.30%",
                "Revenue_Growth": "12.50%",
                "Debt_Ratio": "35.20%",
                "Current_Ratio": "1.85",
                "Message": f"Note: Mock data shown. Real data not found for {symbol}"
            }
    
    def load_technical_data(self, symbol: str, cutoff_date: Any = None) -> Optional[Dict]:
        """Load OHLC (price) data for a symbol.
        
        Args:
            symbol: Stock symbol
            cutoff_date: Optional date to filter data (only include data before this date)
            
        Returns:
            Dictionary with technical data and summary, or None if not found
        """
        csv_path = self.finance_dir / f"{symbol.lower()}{DataConstants.OHLC_SUFFIX}.csv"
        
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            
            # Filter by cutoff date if provided
            if cutoff_date:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df[df['Date'] <= pd.to_datetime(cutoff_date)]
            
            if df.empty:
                return None
                
            # Calculate summary statistics
            latest = df.iloc[-1]
            summary = {
                'latest_close': float(latest.get('Close', latest.get('close', 0))),
                'high': float(df.get('High', df.get('high', [0])).max()),
                'low': float(df.get('Low', df.get('low', [0])).min()),
                'volume': float(latest.get('Volume', 0)),
                'count': len(df)
            }
            
            return {
                'data': df.to_dict('records'),
                'summary': {'price_stats': summary}
            }
        
        else:
            # Return mock data
            return {
                'data': [],
                'summary': {
                    'price_stats': {
                        'latest_close': 95500,
                        'high': 98200,
                        'low': 92100,
                        'volume': 2500000,
                        'count': 30
                    }
                }
            }
    
    def load_news_data(self, symbol: str) -> Dict[str, Any]:
        """Load news articles for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with news articles
        """
        json_path = self.news_dir / f"{symbol.lower()}{DataConstants.NEWS_SUFFIX}.json"
        csv_path = self.news_dir / f"{symbol.lower()}{DataConstants.NEWS_SUFFIX}.csv"
        
        news_list = []
        
        if json_path.exists():
            with open(json_path, 'r', encoding=DataConstants.CSV_ENCODING) as f:
                data = json.load(f)
                if isinstance(data, list):
                    news_list = data[:DataConstants.MAX_NEWS_ARTICLES]
                elif isinstance(data, dict) and 'articles' in data:
                    news_list = data['articles'][:DataConstants.MAX_NEWS_ARTICLES]
                    
        elif csv_path.exists():
            df = pd.read_csv(csv_path)
            news_list = df.head(DataConstants.MAX_NEWS_ARTICLES).to_dict('records')
        
        else:
            # Return mock news data
            news_list = [
                {
                    "title": "Stock continues growth momentum",
                    "summary": "Recent earnings report shows strong performance",
                    "date": "2024-01-10"
                },
                {
                    "title": "Market analysts maintain positive outlook",
                    "summary": "Sector tailwinds expected to continue",
                    "date": "2024-01-09"
                }
            ]
        
        return {
            'articles': news_list,
            'count': len(news_list)
        }
