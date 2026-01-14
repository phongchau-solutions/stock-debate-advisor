"""
Knowledge Manager for Debate Sessions
Manages loading, caching, and serving domain knowledge to agents
"""

import json
import os
import pandas as pd
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class FinancialReport:
    """Quarterly/Annual financial report data"""
    period: str  # e.g., "Q3 2023" or "FY 2023"
    company: str
    metrics: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class TechnicalData:
    """OHLCV price data"""
    symbol: str
    dates: List[str]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[int]
    current_price: float = None
    
    def __post_init__(self):
        if self.current_price is None and self.closes:
            self.current_price = self.closes[0]


@dataclass
class NewsArticle:
    """News article with sentiment"""
    title: str
    summary: str
    date: str
    sentiment: str  # positive, negative, neutral
    source: str = "unknown"


@dataclass
class DebateSessionKnowledge:
    """Complete knowledge base for a debate session"""
    session_id: str
    symbol: str
    financial_reports: List[FinancialReport]
    technical_data: TechnicalData
    news_articles: List[NewsArticle]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class KnowledgeManager:
    """Manages loading and serving knowledge to debate agents"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache: Dict[str, DebateSessionKnowledge] = {}
    
    def load_financial_reports(self, symbol: str) -> List[FinancialReport]:
        """Load financial reports for a symbol"""
        reports = []
        
        # Load from JSON file if exists
        financials_file = self.data_dir / f"{symbol.lower()}_financials.json"
        if financials_file.exists():
            with open(financials_file, 'r') as f:
                data = json.load(f)
            
            # Handle both single object and list formats
            if isinstance(data, list):
                for item in data:
                    report = FinancialReport(
                        period=item.get("period", "Latest"),
                        company=item.get("company", symbol),
                        metrics=item
                    )
                    reports.append(report)
            else:
                report = FinancialReport(
                    period=data.get("period", "Latest"),
                    company=data.get("company", symbol),
                    metrics=data
                )
                reports.append(report)
        
        return reports
    
    def load_technical_data(self, symbol: str) -> Optional[TechnicalData]:
        """Load OHLCV data for a symbol"""
        ohlc_file = self.data_dir / f"{symbol.lower()}_ohlc.csv"
        
        if not ohlc_file.exists():
            return None
        
        df = pd.read_csv(ohlc_file)
        
        # Sort by date (most recent first)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date', ascending=False)
        
        technical_data = TechnicalData(
            symbol=symbol,
            dates=df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            opens=df['Open'].tolist(),
            highs=df['High'].tolist(),
            lows=df['Low'].tolist(),
            closes=df['Close'].tolist(),
            volumes=df['Volume'].tolist(),
            current_price=df['Close'].iloc[0]
        )
        
        return technical_data
    
    def load_news_articles(self, symbol: str) -> List[NewsArticle]:
        """Load news articles for a symbol"""
        articles = []
        
        news_file = self.data_dir / f"{symbol.lower()}_news.json"
        if not news_file.exists():
            return articles
        
        with open(news_file, 'r') as f:
            data = json.load(f)
        
        # Handle both single articles and list format
        article_list = data.get("articles", []) if isinstance(data, dict) else data
        
        for item in article_list:
            article = NewsArticle(
                title=item.get("title", ""),
                summary=item.get("summary", ""),
                date=item.get("date", ""),
                sentiment=item.get("sentiment", "neutral"),
                source=item.get("source", "unknown")
            )
            articles.append(article)
        
        return articles
    
    def load_session_knowledge(self, session_id: str, symbol: str) -> DebateSessionKnowledge:
        """
        Load complete knowledge for a debate session
        This data persists throughout the session
        """
        # Check cache first
        if session_id in self.cache:
            return self.cache[session_id]
        
        # Load all knowledge sources
        financial_reports = self.load_financial_reports(symbol)
        technical_data = self.load_technical_data(symbol)
        news_articles = self.load_news_articles(symbol)
        
        knowledge = DebateSessionKnowledge(
            session_id=session_id,
            symbol=symbol,
            financial_reports=financial_reports,
            technical_data=technical_data,
            news_articles=news_articles
        )
        
        # Cache it for the session
        self.cache[session_id] = knowledge
        
        return knowledge
    
    def get_fundamental_knowledge(self, session_id: str) -> str:
        """Get formatted knowledge for fundamental analyst"""
        if session_id not in self.cache:
            return ""
        
        knowledge = self.cache[session_id]
        text = "=== FINANCIAL ANALYSIS KNOWLEDGE ===\n\n"
        
        for report in knowledge.financial_reports:
            text += f"Period: {report.period}\n"
            text += f"Company: {report.company}\n"
            text += "Key Metrics:\n"
            
            for key, value in report.metrics.items():
                if key not in ['company', 'period']:
                    # Format the value nicely
                    if isinstance(value, float):
                        if 0 < value < 1:
                            text += f"  - {key}: {value*100:.2f}%\n"
                        elif value > 1000000:
                            text += f"  - {key}: {value/1e9:.2f}B VND\n"
                        else:
                            text += f"  - {key}: {value:.2f}\n"
                    else:
                        text += f"  - {key}: {value}\n"
            text += "\n"
        
        return text
    
    def get_technical_knowledge(self, session_id: str) -> str:
        """Get formatted knowledge for technical analyst"""
        if session_id not in self.cache:
            return ""
        
        knowledge = self.cache[session_id]
        text = "=== TECHNICAL ANALYSIS KNOWLEDGE ===\n\n"
        
        if knowledge.technical_data:
            tech = knowledge.technical_data
            text += f"Symbol: {tech.symbol}\n"
            text += f"Current Price: {tech.current_price:,.0f} VND\n"
            text += f"Data Points: {len(tech.closes)}\n"
            text += f"Period: {tech.dates[-1]} to {tech.dates[0]}\n\n"
            
            # Calculate basic indicators
            closes = tech.closes
            if len(closes) > 1:
                price_change = closes[0] - closes[-1]
                price_change_pct = (price_change / closes[-1]) * 100
                text += f"Price Change (Period): {price_change:+,.0f} VND ({price_change_pct:+.2f}%)\n"
                
                # 20-day average
                avg_20 = sum(closes[:20]) / min(20, len(closes)) if len(closes) >= 20 else sum(closes) / len(closes)
                text += f"20-Day Average: {avg_20:,.0f} VND\n"
                
                # Volatility
                volatility = (max(closes) - min(closes)) / (sum(closes) / len(closes)) * 100
                text += f"Volatility (Period): {volatility:.2f}%\n"
            
            text += f"\nRecent Price Data (Last 10 days):\n"
            for i in range(min(10, len(tech.dates))):
                text += f"  {tech.dates[i]}: O:{tech.opens[i]:.0f} H:{tech.highs[i]:.0f} L:{tech.lows[i]:.0f} C:{tech.closes[i]:.0f} V:{tech.volumes[i]:,}\n"
        
        return text
    
    def get_sentiment_knowledge(self, session_id: str) -> str:
        """Get formatted knowledge for sentiment analyst"""
        if session_id not in self.cache:
            return ""
        
        knowledge = self.cache[session_id]
        text = "=== SENTIMENT ANALYSIS KNOWLEDGE ===\n\n"
        
        # Count sentiments
        positive = sum(1 for a in knowledge.news_articles if a.sentiment == 'positive')
        negative = sum(1 for a in knowledge.news_articles if a.sentiment == 'negative')
        neutral = sum(1 for a in knowledge.news_articles if a.sentiment == 'neutral')
        
        total = len(knowledge.news_articles)
        if total > 0:
            text += f"Sentiment Summary:\n"
            text += f"  - Positive: {positive} ({positive/total*100:.1f}%)\n"
            text += f"  - Negative: {negative} ({negative/total*100:.1f}%)\n"
            text += f"  - Neutral: {neutral} ({neutral/total*100:.1f}%)\n\n"
        
        text += "Recent News & Market Sentiment:\n"
        for article in knowledge.news_articles[:10]:  # Last 10 articles
            sentiment_emoji = "📈" if article.sentiment == 'positive' else "📉" if article.sentiment == 'negative' else "➡️"
            text += f"\n{sentiment_emoji} [{article.date}] {article.title}\n"
            text += f"   Summary: {article.summary}\n"
            text += f"   Sentiment: {article.sentiment}\n"
        
        return text
    
    def get_context_for_moderator(self, session_id: str) -> str:
        """Get context for moderator"""
        if session_id not in self.cache:
            return ""
        
        knowledge = self.cache[session_id]
        text = "=== DEBATE SESSION CONTEXT ===\n\n"
        text += f"Symbol: {knowledge.symbol}\n"
        text += f"Session: {knowledge.session_id}\n"
        text += f"Knowledge loaded at: {knowledge.created_at}\n\n"
        
        text += f"Available Data:\n"
        text += f"  - Financial Reports: {len(knowledge.financial_reports)}\n"
        text += f"  - Technical Data Points: {len(knowledge.technical_data.closes) if knowledge.technical_data else 0}\n"
        text += f"  - News Articles: {len(knowledge.news_articles)}\n"
        
        return text
    
    def clear_session(self, session_id: str):
        """Clear cached knowledge for a session"""
        if session_id in self.cache:
            del self.cache[session_id]
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from data directory"""
        symbols = set()
        
        for file in self.data_dir.glob("*_financials.json"):
            symbol = file.stem.replace("_financials", "").upper()
            symbols.add(symbol)
        
        for file in self.data_dir.glob("*_ohlc.csv"):
            symbol = file.stem.replace("_ohlc", "").upper()
            symbols.add(symbol)
        
        for file in self.data_dir.glob("*_news.json"):
            symbol = file.stem.replace("_news", "").upper()
            symbols.add(symbol)
        
        return sorted(list(symbols))


# Global instance
_knowledge_manager = None


def get_knowledge_manager() -> KnowledgeManager:
    """Get or create the global knowledge manager instance"""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager()
    return _knowledge_manager
