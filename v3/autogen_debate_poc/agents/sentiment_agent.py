"""
Sentiment Analysis Agent for stock market analysis.
Analyzes news sentiment from Vietnamese and international sources.
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SentimentAgent:
    """Sentiment Analysis Agent for PoC."""
    
    name = "SentimentAnalyst"
    role = "Market Sentiment Analyst"

    def __init__(
        self,
        system_prompt: str,
        llm_config: Optional[Dict[str, Any]] = None,
        stock_data: Optional[Dict[str, Any]] = None
    ):
        self.system_prompt = system_prompt
        self.llm_config = llm_config or {}
        self.stock_data = stock_data or {}
        
        logger.info(f"Initialized {self.name} in PoC mode (rule-based analysis)")
    
    def analyze(self, stock_symbol: str, period_days: int = 30) -> Dict[str, Any]:
        """Analyze sentiment from news articles."""
        news = self.stock_data.get("news", [])
        
        if not news:
            return self._create_error_response(stock_symbol)
        
        sentiment_score, sentiment_label = self._calculate_sentiment(news)
        key_themes = self._extract_themes(news)
        bias = self._determine_bias(sentiment_label)
        
        return {
            "analysis_type": "sentiment",
            "stock_symbol": stock_symbol,
            "sentiment_score": float(sentiment_score),
            "sentiment_label": sentiment_label,
            "bias": bias,
            "confidence": 0.6,
            "sources": list(set([n.get("source", "Unknown") for n in news])),
            "news_analysis": {
                "total_articles": len(news),
                "positive_count": sum(1 for n in news if self._is_positive(n)),
                "negative_count": sum(1 for n in news if self._is_negative(n))
            },
            "key_themes": key_themes,
            "rationale": self._generate_rationale(sentiment_label, len(news), key_themes)
        }
    
    def _calculate_sentiment(self, news: List[Dict]) -> tuple:
        """Calculate overall sentiment from news articles."""
        if not news:
            return 0.0, "neutral"
        
        positive = sum(1 for n in news if self._is_positive(n))
        negative = sum(1 for n in news if self._is_negative(n))
        
        score = (positive - negative) / len(news)
        
        if score > 0.3:
            label = "positive"
        elif score < -0.3:
            label = "negative"
        else:
            label = "neutral"
        
        return score, label
    
    def _is_positive(self, article: Dict) -> bool:
        """Check if article has positive sentiment."""
        text = f"{article.get('title', '')} {article.get('text', '')}".lower()
        positive_words = ["beat", "strong", "growth", "positive", "up", "gain", "profit", "success"]
        return any(word in text for word in positive_words)
    
    def _is_negative(self, article: Dict) -> bool:
        """Check if article has negative sentiment."""
        text = f"{article.get('title', '')} {article.get('text', '')}".lower()
        negative_words = ["miss", "weak", "down", "fall", "concern", "loss", "decline", "risk"]
        return any(word in text for word in negative_words)
    
    def _extract_themes(self, news: List[Dict]) -> List[str]:
        """Extract key themes from news articles."""
        themes = []
        for article in news[:3]:
            title = article.get("title", "")
            if title:
                themes.append(title)
        return themes if themes else ["No major themes identified"]
    
    def _determine_bias(self, sentiment_label: str) -> str:
        """Map sentiment to trading bias."""
        if sentiment_label == "positive":
            return "buy"
        elif sentiment_label == "negative":
            return "sell"
        else:
            return "hold"
    
    def _generate_rationale(self, sentiment: str, article_count: int, themes: List[str]) -> str:
        """Generate rationale for sentiment analysis."""
        return f"Overall market sentiment is {sentiment} based on {article_count} articles. Key themes: {', '.join(themes[:2])}."
    
    def _create_error_response(self, stock_symbol: str) -> Dict[str, Any]:
        """Create error response when data unavailable."""
        return {
            "analysis_type": "sentiment",
            "stock_symbol": stock_symbol,
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "bias": "hold",
            "confidence": 0.1,
            "sources": [],
            "news_analysis": {"total_articles": 0, "positive_count": 0, "negative_count": 0},
            "key_themes": [],
            "rationale": "No news data available",
            "error": "no_data"
        }

