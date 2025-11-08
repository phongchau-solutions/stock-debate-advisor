"""
Sentiment Analysis Agent
Assesses market sentiment from news and social signals.
"""
import logging
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, DebateMessage

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):
    """Sentiment Analysis specialist."""
    
    def __init__(self, llm_service, system_prompt: Optional[str] = None):
        """Initialize sentiment analyst."""
        if system_prompt is None:
            try:
                with open("prompts/sentiment.txt", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = """You are a Sentiment Analysis Expert specializing in Vietnamese market sentiment.
Analyze news, social signals, and market mood to assess investment outlook."""
        
        super().__init__(
            name="SentimentAnalyst",
            role="Sentiment Analysis Expert",
            llm_service=llm_service,
            system_prompt=system_prompt,
        )
    
    def analyze(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Perform sentiment analysis.
        
        Args:
            stock_symbol: Stock ticker
            stock_data: News and sentiment data
            period_days: Analysis period
            
        Returns:
            Analysis with signal, confidence, rationale
        """
        sentiment_score = stock_data.get("sentiment_score", 0.0)  # -1.0 to 1.0
        article_count = stock_data.get("article_count", 0)
        positive_pct = stock_data.get("positive_pct", 0.5)
        key_themes = stock_data.get("key_themes", [])
        catalysts = stock_data.get("catalysts", [])
        
        # Determine signal
        signal, confidence = self._assess_sentiment(
            sentiment_score, article_count, positive_pct, catalysts
        )
        
        rationale = self._generate_rationale(
            signal, sentiment_score, article_count, positive_pct, key_themes, catalysts
        )
        
        return {
            "analysis_type": "sentiment",
            "stock_symbol": stock_symbol,
            "signal": signal,
            "confidence": confidence,
            "rationale": rationale,
            "metrics": {
                "sentiment_score": sentiment_score,
                "article_count": article_count,
                "positive_pct": positive_pct,
                "key_themes": key_themes,
                "catalysts": catalysts,
            },
        }
    
    def _assess_sentiment(
        self,
        sentiment: float,
        article_count: int,
        positive_pct: float,
        catalysts: list,
    ) -> tuple:
        """Assess sentiment signal."""
        score = 0
        
        # Sentiment score (-1 to 1)
        if sentiment > 0.3:
            score += 1.5
        elif sentiment > 0.0:
            score += 0.5
        elif sentiment < -0.3:
            score -= 1.5
        else:
            score -= 0.5
        
        # Article volume (higher = more attention)
        if article_count > 10:
            score += 0.3
        elif article_count < 3:
            score -= 0.2
        
        # Positive percentage
        if positive_pct > 0.65:
            score += 0.8
        elif positive_pct < 0.35:
            score -= 0.8
        
        # Catalysts assessment
        positive_catalysts = sum(1 for c in catalysts if c.get("type") == "positive")
        negative_catalysts = sum(1 for c in catalysts if c.get("type") == "negative")
        
        score += (positive_catalysts - negative_catalysts) * 0.3
        
        # Determine signal and confidence
        if score > 2.0:
            return "BUY", 0.70
        elif score > 0.5:
            return "BUY", 0.55
        elif score < -2.0:
            return "SELL", 0.70
        elif score < -0.5:
            return "SELL", 0.55
        else:
            return "HOLD", 0.65
    
    def _generate_rationale(
        self,
        signal: str,
        sentiment: float,
        article_count: int,
        positive_pct: float,
        themes: list,
        catalysts: list,
    ) -> str:
        """Generate sentiment rationale."""
        rationale = f"""
Sentiment Analysis for {signal} recommendation:

Market Sentiment:
- Overall Score: {sentiment:+.2f} (-1.0 = very negative, +1.0 = very positive)
- Article Count (7d): {article_count}
- Positive Articles: {positive_pct:.0%}

Recent Themes:
"""
        if themes:
            for theme in themes[:3]:
                rationale += f"• {theme}\n"
        else:
            rationale += "• Limited thematic data\n"
        
        if catalysts:
            rationale += "\nKey Catalysts:\n"
            for catalyst in catalysts[:3]:
                direction = "✓" if catalyst.get("type") == "positive" else "✗"
                rationale += f"{direction} {catalyst.get('description', 'No description')}\n"
        
        if sentiment > 0.3:
            rationale += "\n• Market sentiment is bullish with positive tone\n"
        elif sentiment < -0.3:
            rationale += "\n• Market sentiment is bearish with negative tone\n"
        else:
            rationale += "\n• Market sentiment is mixed - no clear direction\n"
        
        if positive_pct > 0.65:
            rationale += "• Majority of recent articles are positive\n"
        elif positive_pct < 0.35:
            rationale += "• Majority of recent articles are negative\n"
        
        return rationale.strip()
