"""
Sentiment Analysis Module
Analyzes news and social media sentiment.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Performs sentiment analysis on news and text data."""

    def __init__(self):
        """Initialize sentiment analyzer."""
        # Sentiment keywords for Vietnamese financial news
        self.positive_keywords = [
            'tăng', 'tăng trưởng', 'lợi nhuận', 'thành công', 'khả quan',
            'tích cực', 'phát triển', 'cải thiện', 'vượt', 'cao', 'tốt',
            'strong', 'growth', 'profit', 'positive', 'increase', 'success'
        ]
        
        self.negative_keywords = [
            'giảm', 'sụt', 'lỗ', 'khó khăn', 'tiêu cực', 'rủi ro',
            'thất bại', 'kém', 'yếu', 'thấp', 'xấu',
            'decline', 'loss', 'negative', 'decrease', 'risk', 'weak'
        ]

    def analyze(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive sentiment analysis.
        
        Args:
            articles: List of news articles with title, content, source
        
        Returns:
            Dict with sentiment scores, summary, and recommendations
        """
        try:
            if not articles:
                return self._default_sentiment()

            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": "sentiment",
                "article_count": len(articles),
            }

            # Analyze each article
            article_sentiments = []
            for article in articles:
                sentiment = self._analyze_article(article)
                article_sentiments.append(sentiment)
            
            result["articles"] = article_sentiments
            
            # Aggregate sentiment
            result["aggregate"] = self._aggregate_sentiment(article_sentiments)
            
            # Calculate sentiment score
            result["overall_score"] = self._calculate_overall_score(result["aggregate"])
            
            # Generate recommendation
            result["recommendation"] = self._generate_recommendation(result)
            
            # Extract key themes
            result["themes"] = self._extract_themes(articles)
            
            return result

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            raise

    def _analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a single article."""
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
        
        # Calculate sentiment score (-1 to 1)
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total_keywords
        
        # Classify sentiment
        if sentiment_score > 0.3:
            sentiment_label = "positive"
        elif sentiment_score < -0.3:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return {
            "title": article.get('title', ''),
            "source": article.get('source', ''),
            "url": article.get('url', ''),
            "sentiment_score": round(sentiment_score, 3),
            "sentiment_label": sentiment_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "published_at": article.get('published_at'),
        }

    def _aggregate_sentiment(self, article_sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate sentiment across all articles."""
        if not article_sentiments:
            return {
                "average_score": 0.0,
                "positive_articles": 0,
                "negative_articles": 0,
                "neutral_articles": 0,
                "positive_ratio": 0.0,
            }
        
        scores = [a["sentiment_score"] for a in article_sentiments]
        average_score = sum(scores) / len(scores)
        
        positive_count = len([a for a in article_sentiments if a["sentiment_label"] == "positive"])
        negative_count = len([a for a in article_sentiments if a["sentiment_label"] == "negative"])
        neutral_count = len([a for a in article_sentiments if a["sentiment_label"] == "neutral"])
        
        total = len(article_sentiments)
        
        return {
            "average_score": round(average_score, 3),
            "positive_articles": positive_count,
            "negative_articles": negative_count,
            "neutral_articles": neutral_count,
            "positive_ratio": round(positive_count / total, 3) if total > 0 else 0,
            "negative_ratio": round(negative_count / total, 3) if total > 0 else 0,
        }

    def _calculate_overall_score(self, aggregate: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall sentiment score (0-100 scale)."""
        avg_score = aggregate["average_score"]  # -1 to 1
        positive_ratio = aggregate["positive_ratio"]
        
        # Convert to 0-100 scale
        # Base score from average sentiment
        base_score = ((avg_score + 1) / 2) * 100  # Convert -1,1 to 0,100
        
        # Adjust based on positive ratio
        ratio_adjustment = (positive_ratio - 0.5) * 20  # -10 to +10 adjustment
        
        final_score = max(0, min(100, base_score + ratio_adjustment))
        
        # Determine rating
        if final_score >= 75:
            rating = "Very Positive"
        elif final_score >= 60:
            rating = "Positive"
        elif final_score >= 45:
            rating = "Neutral"
        elif final_score >= 30:
            rating = "Negative"
        else:
            rating = "Very Negative"
        
        # Confidence based on article count
        article_count = aggregate["positive_articles"] + aggregate["negative_articles"] + aggregate["neutral_articles"]
        if article_count >= 10:
            confidence = "High"
        elif article_count >= 5:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            "score": round(final_score, 2),
            "rating": rating,
            "confidence": confidence,
        }

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate recommendation based on sentiment."""
        score = analysis["overall_score"]["score"]
        rating = analysis["overall_score"]["rating"]
        article_count = analysis["article_count"]
        
        positive_articles = analysis["aggregate"]["positive_articles"]
        negative_articles = analysis["aggregate"]["negative_articles"]
        
        if score >= 70:
            return f"{rating}: Overwhelmingly positive sentiment across {article_count} articles. {positive_articles} positive vs {negative_articles} negative. Market sentiment supports bullish outlook."
        elif score >= 55:
            return f"{rating}: Generally favorable sentiment. {positive_articles} positive articles indicate market confidence."
        elif score >= 45:
            return f"{rating}: Mixed sentiment with no clear bias. Monitor news flow for emerging trends."
        else:
            return f"{rating}: Predominantly negative sentiment. {negative_articles} negative articles suggest caution."

    def _extract_themes(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract common themes from articles."""
        # Simple keyword-based theme extraction
        themes = []
        
        all_text = ' '.join([
            f"{a.get('title', '')} {a.get('content', '')}"
            for a in articles
        ]).lower()
        
        # Define theme keywords
        theme_keywords = {
            "Earnings & Profitability": ['lợi nhuận', 'doanh thu', 'earnings', 'profit', 'revenue'],
            "Market Performance": ['thị trường', 'giá', 'cổ phiếu', 'market', 'stock', 'price'],
            "Growth & Expansion": ['tăng trưởng', 'mở rộng', 'phát triển', 'growth', 'expansion'],
            "Financial Health": ['tài chính', 'nợ', 'vốn', 'financial', 'debt', 'capital'],
            "Industry Trends": ['ngành', 'cạnh tranh', 'industry', 'sector', 'competition'],
            "Management & Strategy": ['quản lý', 'chiến lược', 'management', 'strategy', 'leadership'],
            "Regulatory & Policy": ['chính sách', 'quy định', 'policy', 'regulation', 'government'],
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Return top 5 themes

    def _default_sentiment(self) -> Dict[str, Any]:
        """Return default sentiment when no articles available."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "sentiment",
            "article_count": 0,
            "articles": [],
            "aggregate": {
                "average_score": 0.0,
                "positive_articles": 0,
                "negative_articles": 0,
                "neutral_articles": 0,
                "positive_ratio": 0.0,
            },
            "overall_score": {
                "score": 50.0,
                "rating": "Neutral",
                "confidence": "Low",
            },
            "recommendation": "Neutral: Insufficient news data for sentiment analysis.",
            "themes": [],
        }
