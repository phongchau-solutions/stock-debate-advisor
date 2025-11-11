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
            raise FileNotFoundError(
                ErrorMessages.FILE_NOT_FOUND.format(symbol=symbol)
            )
    
    def load_technical_data(self, symbol: str, cutoff_date: Any = None) -> Optional[Dict]:
        """Load OHLC (price) data for a symbol.
        
        Args:
            symbol: Stock symbol
            cutoff_date: Optional date to filter data (only include data before this date)
            
        Returns:
            Dictionary with technical data and summary, or None if not found
        """
        file_paths = [
            self.finance_dir / f"{symbol.lower()}{DataConstants.OHLC_SUFFIX}.csv",
            self.news_dir / f"{symbol.lower()}{DataConstants.OHLC_SUFFIX}.csv"
        ]
        
        for file_path in file_paths:
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    
                    # Filter by cutoff date if provided
                    if cutoff_date is not None and 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        cutoff_datetime = pd.to_datetime(cutoff_date)
                        df = df[df['date'] <= cutoff_datetime].copy()
                    
                    if len(df) == 0:
                        return None
                    
                    return {
                        "symbol": symbol,
                        "data": df.to_dict(orient="records"),
                        "summary": self._summarize_technical(df)
                    }
                except Exception as e:
                    print(ErrorMessages.LOAD_ERROR.format(error=str(e)))
        
        return None
    
    def load_sentiment_data(self, symbol: str, cutoff_date: Any = None) -> Optional[Dict]:
        """Load news/sentiment data for a symbol.
        
        Args:
            symbol: Stock symbol
            cutoff_date: Optional date to filter data (only include data before this date)
            
        Returns:
            Dictionary with sentiment data and summary, or None if not found
        """
        file_paths = [
            self.news_dir / f"{symbol.lower()}{DataConstants.NEWS_SUFFIX}.csv",
            self.finance_dir / f"{symbol.lower()}{DataConstants.NEWS_SUFFIX}.csv"
        ]
        
        for file_path in file_paths:
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    
                    # Filter by cutoff date if provided
                    if cutoff_date is not None and 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        cutoff_datetime = pd.to_datetime(cutoff_date)
                        df = df[df['date'] <= cutoff_datetime].copy()
                    
                    if len(df) == 0:
                        return None
                    
                    return {
                        "symbol": symbol,
                        "articles": df.to_dict(orient="records"),
                        "summary": self._summarize_sentiment(df)
                    }
                except Exception as e:
                    print(ErrorMessages.LOAD_ERROR.format(error=str(e)))
        
        return None
    
    def _summarize_technical(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics from OHLC data."""
        try:
            return {
                "total_records": len(df),
                "date_range": {
                    "start": str(df['date'].min()),
                    "end": str(df['date'].max())
                },
                "price_stats": {
                    "latest_close": float(df['close'].iloc[-1]),
                    "high": float(df['high'].max()),
                    "low": float(df['low'].min()),
                    "avg_volume": float(df['volume'].mean()) if 'volume' in df.columns else None
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _summarize_sentiment(self, df: pd.DataFrame) -> Dict:
        """Generate summary from news data."""
        try:
            return {
                "total_articles": len(df),
                "sources": df['source'].unique().tolist() if 'source' in df.columns else [],
                "date_range": {
                    "start": str(df['date'].min()) if 'date' in df.columns else None,
                    "end": str(df['date'].max()) if 'date' in df.columns else None
                }
            }
        except Exception as e:
            return {"error": str(e)}
