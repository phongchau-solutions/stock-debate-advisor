"""
Data loader for financial, technical, and sentiment data.
"""
import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from config import config


class DataLoader:
    """Loads stock data from CSV/JSON files."""
    
    def __init__(self):
        """Initialize data loader with configured paths."""
        self.finance_dir = config.FINANCE_DATA_PATH
        self.news_dir = config.NEWS_DATA_PATH
        
    def get_available_symbols(self) -> List[str]:
        """Get list of available stock symbols from data files."""
        symbols = set()
        
        # Check finance data files
        for file_path in self.finance_dir.glob("*_financials.*"):
            symbol = file_path.stem.split('_')[0].upper()
            symbols.add(symbol)
            
        # Check OHLC files
        for file_path in self.finance_dir.glob("*_ohlc.csv"):
            symbol = file_path.stem.split('_')[0].upper()
            symbols.add(symbol)
            
        return sorted(list(symbols))
    
    def load_financial_data(self, symbol: str) -> dict:
        """Load financial statement data for a symbol."""
        # Try JSON first (preferred format)
        json_path = self.finance_dir / f"{symbol.lower()}_financials.json"
        csv_path = self.finance_dir / f"{symbol.lower()}_financials.csv"
        
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif csv_path.exists():
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        else:
            raise FileNotFoundError(f"Financial data not found for {symbol}")
        
        return {}
    
    def load_technical_data(self, symbol: str) -> Optional[Dict]:
        """Load OHLC (price) data for a symbol."""
        file_paths = [
            self.finance_dir / f"{symbol.lower()}_ohlc.csv",
            self.news_dir / f"{symbol.lower()}_ohlc.csv"
        ]
        
        for file_path in file_paths:
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    return {
                        "symbol": symbol,
                        "data": df.to_dict(orient="records"),
                        "summary": self._summarize_technical(df)
                    }
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return None
    
    def load_sentiment_data(self, symbol: str) -> Optional[Dict]:
        """Load news/sentiment data for a symbol."""
        file_paths = [
            self.news_dir / f"{symbol.lower()}_news.csv",
            self.finance_dir / f"{symbol.lower()}_news.csv"
        ]
        
        for file_path in file_paths:
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    return {
                        "symbol": symbol,
                        "articles": df.to_dict(orient="records"),
                        "summary": self._summarize_sentiment(df)
                    }
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
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
