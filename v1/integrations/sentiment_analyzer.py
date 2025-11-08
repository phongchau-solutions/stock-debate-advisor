"""
Sentiment analysis for financial news using both Vietnamese and English text processing.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple, Protocol, Any, TypedDict, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NewsItemDict(TypedDict):
    """Typed dictionary for news item data."""
    title: str
    content: str
    url: str
    source: str
    symbols_mentioned: List[str]


class NewsItemProtocol(Protocol):
    """Protocol for news item objects."""
    title: str
    content: str
    url: str
    source: str
    symbols_mentioned: List[str]


@dataclass
class SentimentScore:
    """Sentiment analysis result."""
    positive: float  # 0-1 score
    negative: float  # 0-1 score  
    neutral: float   # 0-1 score
    compound: float  # -1 to 1 overall sentiment
    confidence: float  # 0-1 confidence in analysis
    

class FinancialSentimentAnalyzer:
    """Financial sentiment analyzer for Vietnamese and English news."""
    
    def __init__(self):
        # Vietnamese financial sentiment keywords
        self.vietnamese_positive = [
            'tăng', 'tăng trưởng', 'lợi nhuận', 'thành công', 'phát triển', 
            'khả quan', 'tích cực', 'ưu việt', 'vượt trội', 'cải thiện',
            'thu hút', 'đầu tư', 'mở rộng', 'hiệu quả', 'bứt phá',
            'kỷ lục', 'cao nhất', 'tăng cao', 'tăng mạnh', 'khởi sắc'
        ]
        
        self.vietnamese_negative = [
            'giảm', 'sụt giảm', 'thua lỗ', 'khó khăn', 'thất bại',
            'suy thoái', 'khủng hoảng', 'rủi ro', 'bất ổn', 'lo ngại',
            'đình trệ', 'suy yếu', 'thấp nhất', 'giảm mạnh', 'lao dốc',
            'phá sản', 'nợ xấu', 'thua lỗ', 'sa thải', 'cảnh báo'
        ]
        
        # English financial sentiment keywords
        self.english_positive = [
            'growth', 'profit', 'gain', 'increase', 'rise', 'surge', 'rally',
            'bullish', 'optimistic', 'strong', 'robust', 'solid', 'impressive',
            'record', 'highest', 'outperform', 'beat', 'exceed', 'upgrade',
            'buy', 'recommend', 'positive', 'favorable', 'improving'
        ]
        
        self.english_negative = [
            'loss', 'decline', 'fall', 'drop', 'crash', 'plunge', 'slump',
            'bearish', 'pessimistic', 'weak', 'poor', 'disappointing',
            'concern', 'worry', 'risk', 'crisis', 'recession', 'downturn',
            'sell', 'downgrade', 'negative', 'unfavorable', 'deteriorating'
        ]
        
        # Financial context multipliers
        self.financial_amplifiers = {
            # Vietnamese
            'mạnh': 1.3, 'rất': 1.2, 'khá': 1.1, 'nhẹ': 0.8,
            # English  
            'strong': 1.3, 'very': 1.2, 'quite': 1.1, 'slightly': 0.8,
            'significant': 1.4, 'major': 1.3, 'minor': 0.7
        }
        
    def analyze_sentiment(self, text: str, title: str = "") -> SentimentScore:
        """Analyze sentiment of financial news text."""
        try:
            # Combine title and content with title weighted more
            combined_text = f"{title} {title} {text}".lower()  # Title twice for emphasis
            
            # Get language-specific scores
            vn_score = self._analyze_vietnamese_sentiment(combined_text)
            en_score = self._analyze_english_sentiment(combined_text)
            
            # Combine scores (weighted by detected content)
            vn_weight = self._estimate_vietnamese_content(combined_text)
            en_weight = 1.0 - vn_weight
            
            positive = (vn_score[0] * vn_weight + en_score[0] * en_weight)
            negative = (vn_score[1] * vn_weight + en_score[1] * en_weight)
            
            # Normalize
            total = positive + negative
            if total > 0:
                positive = positive / total
                negative = negative / total
                neutral = max(0, 1 - positive - negative)
            else:
                positive = negative = 0
                neutral = 1
                
            # Compound score (-1 to 1)
            compound = positive - negative
            
            # Confidence based on keyword matches and text length
            confidence = min(1.0, (total * 0.1) + (len(combined_text) / 2000))
            
            return SentimentScore(
                positive=positive,
                negative=negative, 
                neutral=neutral,
                compound=compound,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return SentimentScore(0.33, 0.33, 0.34, 0.0, 0.0)
            
    def _analyze_vietnamese_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze Vietnamese text sentiment."""
        positive_score = 0
        negative_score = 0
        
        # Count positive keywords
        for keyword in self.vietnamese_positive:
            count = len(re.findall(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE))
            multiplier = self._get_context_multiplier(text, keyword)
            positive_score += count * multiplier
            
        # Count negative keywords  
        for keyword in self.vietnamese_negative:
            count = len(re.findall(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE))
            multiplier = self._get_context_multiplier(text, keyword)
            negative_score += count * multiplier
            
        return positive_score, negative_score
        
    def _analyze_english_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze English text sentiment."""
        positive_score = 0
        negative_score = 0
        
        # Count positive keywords
        for keyword in self.english_positive:
            count = len(re.findall(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE))
            multiplier = self._get_context_multiplier(text, keyword)
            positive_score += count * multiplier
            
        # Count negative keywords
        for keyword in self.english_negative:
            count = len(re.findall(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE))
            multiplier = self._get_context_multiplier(text, keyword)
            negative_score += count * multiplier
            
        return positive_score, negative_score
        
    def _get_context_multiplier(self, text: str, keyword: str) -> float:
        """Get context multiplier for sentiment keywords."""
        base_multiplier = 1.0
        
        # Look for amplifiers near the keyword
        keyword_pos = text.find(keyword.lower())
        if keyword_pos > 0:
            # Check 50 characters before and after
            context = text[max(0, keyword_pos-50):keyword_pos+50]
            
            for amplifier, multiplier in self.financial_amplifiers.items():
                if amplifier in context:
                    base_multiplier = max(base_multiplier, multiplier)
                    
        return base_multiplier
        
    def _estimate_vietnamese_content(self, text: str) -> float:
        """Estimate proportion of Vietnamese content."""
        vietnamese_chars = len(re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]', text))
        total_chars = len(re.findall(r'[a-zA-ZàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]', text))
        
        if total_chars == 0:
            return 0.5
            
        vietnamese_ratio = vietnamese_chars / total_chars
        return min(1.0, vietnamese_ratio * 3)  # Amplify Vietnamese detection
        
    def analyze_news_batch(self, news_items: List[Union[NewsItemProtocol, NewsItemDict]]) -> Dict[str, Any]:
        """Analyze sentiment for a batch of news items."""
        if not news_items:
            return {
                "overall_sentiment": SentimentScore(0.33, 0.33, 0.34, 0.0, 0.0).__dict__,
                "article_sentiments": [],
                "summary": {
                    "total_articles": 0,
                    "avg_compound": 0.0,
                    "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0}
                }
            }
            
        article_sentiments: List[Dict[str, Any]] = []
        compound_scores: List[float] = []
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for item in news_items:
            try:
                # Extract fields safely from either object or dict
                title = ""
                content = ""
                url = ""
                source = ""
                
                if hasattr(item, 'title') and hasattr(item, 'content'):
                    # NewsItem object that implements the protocol
                    title = str(getattr(item, 'title', ''))
                    content = str(getattr(item, 'content', ''))
                    url = str(getattr(item, 'url', ''))
                    source = str(getattr(item, 'source', ''))
                elif isinstance(item, dict):
                    # Dictionary - typed for clearer typing
                    d: NewsItemDict = item  # type: ignore[arg-type]
                    title = str(d.get('title', ''))
                    content = str(d.get('content', ''))
                    url = str(d.get('url', ''))
                    source = str(d.get('source', ''))
                
                sentiment = self.analyze_sentiment(content, title)
                
                # Classify overall sentiment
                if sentiment.compound > 0.1:
                    overall_sentiment = "positive"
                    sentiment_counts["positive"] += 1
                elif sentiment.compound < -0.1:
                    overall_sentiment = "negative"
                    sentiment_counts["negative"] += 1
                else:
                    overall_sentiment = "neutral"
                    sentiment_counts["neutral"] += 1
                    
                article_sentiments.append({
                    "title": title,
                    "url": url,
                    "source": source,
                    "sentiment": sentiment.__dict__,
                    "classification": overall_sentiment,
                    "key_phrases": self._extract_key_phrases(title + " " + content)
                })
                
                compound_scores.append(sentiment.compound)
                
            except Exception as e:
                logger.error(f"Error analyzing news item: {e}")
                
        # Calculate overall metrics
        avg_compound = sum(compound_scores) / len(compound_scores) if compound_scores else 0.0
        
        # Overall sentiment based on average compound score
        if avg_compound > 0.1:
            overall_class = "positive"
        elif avg_compound < -0.1:
            overall_class = "negative"
        else:
            overall_class = "neutral"
            
        # Create overall sentiment score
        positive_ratio = sentiment_counts["positive"] / len(news_items) if news_items else 0
        negative_ratio = sentiment_counts["negative"] / len(news_items) if news_items else 0
        neutral_ratio = sentiment_counts["neutral"] / len(news_items) if news_items else 1
        
        overall_sentiment = SentimentScore(
            positive=positive_ratio,
            negative=negative_ratio,
            neutral=neutral_ratio,
            compound=avg_compound,
            confidence=min(1.0, len(news_items) / 10)  # More articles = more confidence
        )
        
        return {
            "overall_sentiment": overall_sentiment.__dict__,
            "overall_classification": overall_class,
            "article_sentiments": article_sentiments,
            "summary": {
                "total_articles": len(news_items),
                "avg_compound": avg_compound,
                "sentiment_distribution": sentiment_counts,
                "confidence_level": "high" if overall_sentiment.confidence > 0.7 else 
                                  "medium" if overall_sentiment.confidence > 0.4 else "low"
            }
        }
        
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key financial phrases from text."""
        phrases: List[str] = []
        
        # Financial terms to highlight
        financial_terms = [
            # Vietnamese
            'lợi nhuận', 'doanh thu', 'tăng trưởng', 'đầu tư', 'cổ phiếu',
            'thị trường', 'ngân hàng', 'tài chính', 'kinh doanh',
            # English
            'profit', 'revenue', 'growth', 'investment', 'stock', 'market',
            'banking', 'financial', 'business', 'earnings', 'performance'
        ]
        
        text_lower = text.lower()
        for term in financial_terms:
            if term in text_lower:
                # Find context around the term
                pos = text_lower.find(term)
                if pos >= 0:
                    start = max(0, pos - 30)
                    end = min(len(text), pos + len(term) + 30)
                    context = text[start:end].strip()
                    if len(context) > 10:
                        phrases.append(context)
                        
        return phrases[:5]  # Return top 5 key phrases