"""
Sentiment Analysis Agent for Vietnamese Stock Market
"""
import json
import asyncio
import aiohttp
import logging
import concurrent.futures
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from . import BaseFinancialAgent


class SentimentAgent(BaseFinancialAgent):
    """Agent specialized in sentiment analysis from news sources."""
    
    def __init__(self, gemini_api_key: str, **kwargs):
        system_message = """
        You are a Sentiment Analysis Expert specializing in Vietnamese stock market news.
        
        Your role:
        - Analyze news sentiment from VnEconomy, WSJ, and other financial sources
        - Extract market sentiment signals from articles and social media
        - Assess impact of news on stock performance and investor psychology
        - Provide sentiment scores and confidence levels
        
        Output format should be structured JSON with:
        {
            "sentiment": "positive|negative|neutral",
            "sentiment_score": float (-1 to 1),
            "confidence": float (0-1),
            "news_impact": "high|medium|low",
            "key_themes": ["theme1", "theme2", "theme3"],
            "sources": [
                {
                    "title": "Article title",
                    "source": "VnEconomy|WSJ|etc",
                    "sentiment": "positive|negative|neutral",
                    "relevance": float (0-1)
                }
            ],
            "rationale": "Detailed sentiment reasoning"
        }
        
        Focus on Vietnamese market context and economic indicators affecting investor sentiment.
        """
        
        super().__init__(
            name="SentimentAnalyst",
            role="Sentiment Analysis Expert",
            system_message=system_message,
            gemini_api_key=gemini_api_key,
            **kwargs
        )
        self.logger = logging.getLogger(__name__)

    async def analyze(self, stock_symbol: str, period: str = "3mo", timeout: int = 30) -> Dict[str, Any]:
        """
        Standardized analyze method for sentiment analysis.
        
        Args:
            stock_symbol: Stock symbol to analyze (e.g., 'VNM', 'VIC')
            period: Analysis period ('1mo', '3mo', '6mo', '1y')
            timeout: Timeout in seconds for data fetching
            
        Returns:
            Dict containing structured sentiment analysis results
        """
        try:
            self.logger.info(f"Starting sentiment analysis for {stock_symbol}")
            
            # Use asyncio timeout for the entire analysis
            return await asyncio.wait_for(
                self._perform_sentiment_analysis(stock_symbol, period),
                timeout=timeout
            )
            
        except asyncio.TimeoutError:
            self.logger.error(f"Sentiment analysis timeout for {stock_symbol}")
            return self._create_error_response("Analysis timeout", stock_symbol)
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed for {stock_symbol}: {str(e)}")
            return self._create_error_response(str(e), stock_symbol)

    async def _perform_sentiment_analysis(self, stock_symbol: str, period: str) -> Dict[str, Any]:
        """Perform the actual sentiment analysis."""
        # Fetch news articles with timeout
        news_articles = await self._fetch_news_articles_async(stock_symbol, period)
        
        if not news_articles:
            return self._create_error_response("No news data available", stock_symbol)
        
        # Analyze sentiment from articles
        sentiment_analysis = await self._analyze_sentiment_async(stock_symbol, news_articles)
        
        # Generate AI-powered rationale
        ai_rationale = await self._generate_ai_sentiment_rationale(stock_symbol, news_articles, sentiment_analysis)
        
        # Extract key insights
        key_themes = self._extract_key_themes(news_articles)
        news_impact = self._assess_news_impact(news_articles, sentiment_analysis)
        confidence = self._calculate_confidence(news_articles, sentiment_analysis)
        
        # Structure the response
        return {
            "analysis_type": "sentiment",
            "stock_symbol": stock_symbol,
            "timestamp": datetime.now().isoformat(),
            "sentiment": sentiment_analysis.get("overall_sentiment", "neutral"),
            "sentiment_score": sentiment_analysis.get("sentiment_score", 0.0),
            "confidence": confidence,
            "news_impact": news_impact,
            "key_themes": key_themes,
            "sources": news_articles[:10],  # Top 10 sources
            "rationale": ai_rationale,
            "analysis_period": period,
            "articles_analyzed": len(news_articles),
            "sentiment_breakdown": {
                "positive_count": sentiment_analysis.get("positive_count", 0),
                "negative_count": sentiment_analysis.get("negative_count", 0),
                "neutral_count": sentiment_analysis.get("neutral_count", 0)
            },
            "data_quality": self._assess_data_quality(news_articles)
        }

    def _create_error_response(self, error_message: str, stock_symbol: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "analysis_type": "sentiment",
            "stock_symbol": stock_symbol,
            "timestamp": datetime.now().isoformat(),
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "confidence": 0.1,
            "news_impact": "low",
            "key_themes": [],
            "sources": [],
            "rationale": f"Sentiment analysis failed: {error_message}",
            "analysis_period": "unknown",
            "articles_analyzed": 0,
            "sentiment_breakdown": {"positive_count": 0, "negative_count": 0, "neutral_count": 0},
            "data_quality": "poor",
            "error": error_message
        }
    
    async def analyze_data(self, stock_symbol: str, period: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sentiment analysis on news and social media data."""
        try:
            # Fetch news articles
            news_articles = await self._fetch_news_articles(stock_symbol, period)
            
            if not news_articles:
                return {
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "confidence": 0.1,
                    "news_impact": "low",
                    "error": "No news data available for sentiment analysis"
                }
            
            # Analyze sentiment using Gemini
            sentiment_analysis = await self._analyze_sentiment(stock_symbol, news_articles)
            
            # Generate comprehensive analysis
            analysis_prompt = f"""
            Analyze the sentiment for {stock_symbol} based on the following news data:
            
            Number of articles analyzed: {len(news_articles)}
            Time period: {period}
            
            News Articles Summary:
            {json.dumps(news_articles[:5], indent=2, ensure_ascii=False)}  # Top 5 articles
            
            Sentiment Analysis Results:
            {json.dumps(sentiment_analysis, indent=2)}
            
            Vietnamese Market Context:
            - Consider VN-Index performance and market trends
            - Factor in government policy impacts
            - Assess foreign investment sentiment
            - Evaluate sector-specific news
            
            Provide comprehensive sentiment analysis with impact assessment.
            """
            
            response = self.generate_llm_response(analysis_prompt)
            
            # Structure the analysis
            structured_analysis = {
                "sentiment": sentiment_analysis.get("overall_sentiment", "neutral"),
                "sentiment_score": sentiment_analysis.get("sentiment_score", 0.0),
                "confidence": self._calculate_confidence(news_articles, sentiment_analysis),
                "news_impact": self._assess_news_impact(news_articles, sentiment_analysis),
                "key_themes": self._extract_key_themes(news_articles),
                "sources": news_articles[:10],  # Top 10 sources
                "rationale": response,
                "analysis_period": period,
                "articles_analyzed": len(news_articles)
            }
            
            return structured_analysis
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.1,
                "news_impact": "low",
                "error": str(e)
            }
    
    async def _fetch_news_articles_async(self, symbol: str, period: str, timeout: int = 15) -> Optional[List[Dict[str, Any]]]:
        """Async wrapper for fetching news articles with timeout."""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(executor, self._fetch_news_articles_sync, symbol, period)
                return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching news for {symbol}")
            return []
        except Exception as e:
            self.logger.error(f"Error in async news fetch for {symbol}: {e}")
            return []

    def _fetch_news_articles_sync(self, symbol: str, period: str) -> List[Dict[str, Any]]:
        """Synchronous news fetching for threading."""
        try:
            # For demo purposes, create realistic news articles
            # In production, this would scrape VnEconomy, WSJ, etc.
            return self._create_demo_news_articles(symbol)
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def _analyze_sentiment_async(self, symbol: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Async sentiment analysis with AI enhancement."""
        base_sentiment = await self._analyze_sentiment(symbol, articles)
        
        # Enhance with AI if we have articles
        if articles and len(articles) > 0:
            try:
                # Generate AI-powered sentiment insights
                ai_insights = await self._get_ai_sentiment_insights(symbol, articles)
                base_sentiment.update(ai_insights)
            except Exception as e:
                self.logger.error(f"Error in AI sentiment analysis: {e}")
        
        return base_sentiment

    async def _get_ai_sentiment_insights(self, symbol: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get AI-powered sentiment insights."""
        try:
            articles_summary = []
            for article in articles[:5]:  # Limit to top 5 for token efficiency
                articles_summary.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "sentiment": article.get("sentiment", "neutral"),
                    "relevance": article.get("relevance", 0.5)
                })
            
            prompt = f"""
            Analyze sentiment for {symbol} based on these news articles:
            {json.dumps(articles_summary, indent=2, ensure_ascii=False)}
            
            Provide insights on:
            1. Overall market sentiment direction
            2. Key sentiment drivers
            3. Confidence level (0-1)
            4. Expected impact on stock price
            
            Return a brief analysis focusing on Vietnamese market context.
            """
            
            ai_response = self.generate_llm_response(prompt)
            
            return {
                "ai_insights": ai_response,
                "enhanced_confidence": min(0.8, 0.6 + len(articles) * 0.02)  # Boost confidence with more articles
            }
            
        except Exception as e:
            self.logger.error(f"Error getting AI sentiment insights: {e}")
            return {"ai_insights": "AI analysis unavailable", "enhanced_confidence": 0.5}

    async def _generate_ai_sentiment_rationale(self, stock_symbol: str, articles: List[Dict[str, Any]], sentiment_analysis: Dict[str, Any]) -> str:
        """Generate comprehensive AI-powered sentiment rationale."""
        try:
            analysis_prompt = f"""
            Generate comprehensive sentiment analysis rationale for {stock_symbol}:
            
            Articles analyzed: {len(articles)}
            Overall sentiment: {sentiment_analysis.get('overall_sentiment', 'neutral')}
            Sentiment score: {sentiment_analysis.get('sentiment_score', 0.0)}
            
            Article breakdown:
            - Positive articles: {sentiment_analysis.get('positive_count', 0)}
            - Negative articles: {sentiment_analysis.get('negative_count', 0)}
            - Neutral articles: {sentiment_analysis.get('neutral_count', 0)}
            
            Key news samples:
            {json.dumps(articles[:3], indent=2, ensure_ascii=False)}
            
            Consider:
            1. Vietnamese market sentiment trends
            2. Foreign investor sentiment
            3. Sector-specific news impact
            4. Government policy implications
            5. Regional economic factors
            
            Provide detailed rationale for the sentiment assessment.
            """
            
            return self.generate_llm_response(analysis_prompt)
            
        except Exception as e:
            self.logger.error(f"Error generating AI sentiment rationale: {e}")
            return f"Sentiment analysis for {stock_symbol}: Unable to generate detailed rationale due to system error."

    def _assess_data_quality(self, articles: List[Dict[str, Any]]) -> str:
        """Assess the quality of news data available."""
        if not articles:
            return "poor"
        
        article_count = len(articles)
        
        # Check article completeness
        complete_articles = sum(1 for article in articles 
                              if all(article.get(field) for field in ['title', 'source', 'sentiment']))
        
        # Check source diversity
        sources = set(article.get('source', 'unknown') for article in articles)
        source_diversity = len(sources)
        
        # Check relevance scores
        avg_relevance = sum(article.get('relevance', 0.5) for article in articles) / article_count
        
        # Calculate quality score
        completeness_score = complete_articles / article_count if article_count > 0 else 0
        diversity_score = min(source_diversity / 3, 1.0)  # Normalize to max 3 sources
        relevance_score = avg_relevance
        
        overall_score = (completeness_score + diversity_score + relevance_score) / 3
        
        if overall_score >= 0.8 and article_count >= 5:
            return "excellent"
        elif overall_score >= 0.6 and article_count >= 3:
            return "good"
        elif overall_score >= 0.4:
            return "fair"
        else:
            return "poor"

    async def _fetch_news_articles(self, symbol: str, period: str) -> List[Dict[str, Any]]:
        """Fetch news articles from various sources."""
        try:
            # For demo purposes, create realistic news articles
            # In production, this would scrape VnEconomy, WSJ, etc.
            
            demo_articles = self._create_demo_news_articles(symbol)
            return demo_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def _create_demo_news_articles(self, symbol: str) -> List[Dict[str, Any]]:
        """Create demo news articles for testing."""
        
        # Company-specific news templates
        news_templates = {
            'VNM': [
                {
                    "title": "Vinamilk báo cáo lợi nhuận quý 3 tăng 12% so với cùng kỳ",
                    "source": "VnEconomy",
                    "content": "Vinamilk công bố kết quả kinh doanh quý 3 với doanh thu tăng trưởng mạnh...",
                    "sentiment": "positive",
                    "relevance": 0.95,
                    "date": "2024-10-28"
                },
                {
                    "title": "Vinamilk expands presence in Southeast Asian markets",
                    "source": "WSJ",
                    "content": "Vietnam's largest dairy company continues regional expansion strategy...",
                    "sentiment": "positive",
                    "relevance": 0.85,
                    "date": "2024-10-25"
                },
                {
                    "title": "Thị trường sữa Việt Nam đối mặt với thách thức cạnh tranh",
                    "source": "VnEconomy",
                    "content": "Áp lực cạnh tranh từ các thương hiệu quốc tế tăng cao...",
                    "sentiment": "negative",
                    "relevance": 0.75,
                    "date": "2024-10-20"
                }
            ],
            'VIC': [
                {
                    "title": "Vingroup đầu tư mạnh vào xe điện VinFast",
                    "source": "VnEconomy",
                    "content": "Vingroup tiếp tục đầu tư hàng tỷ USD vào mảng xe điện...",
                    "sentiment": "positive",
                    "relevance": 0.90,
                    "date": "2024-10-26"
                },
                {
                    "title": "VinFast faces challenges in US market penetration",
                    "source": "WSJ",
                    "content": "Vietnamese EV maker encounters competitive pressures in American market...",
                    "sentiment": "negative",
                    "relevance": 0.80,
                    "date": "2024-10-22"
                }
            ],
            'VCB': [
                {
                    "title": "Vietcombank duy trì tăng trưởng tín dụng ổn định",
                    "source": "VnEconomy",
                    "content": "Ngân hàng TMCP Ngoại thương Việt Nam báo cáo tăng trưởng tích cực...",
                    "sentiment": "positive",
                    "relevance": 0.90,
                    "date": "2024-10-27"
                },
                {
                    "title": "Vietnamese banks face margin pressure from rate environment",
                    "source": "WSJ",
                    "content": "Interest rate policies affecting profitability of major Vietnamese lenders...",
                    "sentiment": "negative",
                    "relevance": 0.70,
                    "date": "2024-10-18"
                }
            ]
        }
        
        generic_articles = [
            {
                "title": f"Cổ phiếu {symbol} được khuyến nghị mua với mục tiêu giá cao",
                "source": "VnEconomy",
                "content": f"Các nhà phân tích đưa ra khuyến nghị tích cực cho {symbol}...",
                "sentiment": "positive",
                "relevance": 0.85,
                "date": "2024-10-24"
            },
            {
                "title": f"{symbol} stock shows resilience amid market volatility",
                "source": "WSJ",
                "content": f"Despite market headwinds, {symbol} maintains stable performance...",
                "sentiment": "positive",
                "relevance": 0.75,
                "date": "2024-10-21"
            },
            {
                "title": "VN-Index tăng điểm phiên thứ 3 liên tiếp",
                "source": "VnEconomy",
                "content": "Thị trường chứng khoán Việt Nam duy trì đà tăng tích cực...",
                "sentiment": "positive",
                "relevance": 0.60,
                "date": "2024-10-29"
            },
            {
                "title": "Foreign investors continue net buying in Vietnamese equities",
                "source": "WSJ",
                "content": "International funds show renewed interest in Vietnam stock market...",
                "sentiment": "positive",
                "relevance": 0.65,
                "date": "2024-10-23"
            }
        ]
        
        # Get company-specific articles or use generic ones
        articles = news_templates.get(symbol, generic_articles)
        
        # Add some general market articles
        articles.extend(generic_articles[2:])
        
        return articles
    
    async def _analyze_sentiment(self, symbol: str, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from news articles."""
        if not articles:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            }
        
        # Count sentiment types
        positive_count = sum(1 for article in articles if article.get("sentiment") == "positive")
        negative_count = sum(1 for article in articles if article.get("sentiment") == "negative")
        neutral_count = len(articles) - positive_count - negative_count
        
        # Calculate weighted sentiment score
        total_relevance = sum(article.get("relevance", 0.5) for article in articles)
        if total_relevance == 0:
            sentiment_score = 0.0
        else:
            weighted_positive = sum(
                article.get("relevance", 0.5) for article in articles 
                if article.get("sentiment") == "positive"
            )
            weighted_negative = sum(
                article.get("relevance", 0.5) for article in articles 
                if article.get("sentiment") == "negative"
            )
            sentiment_score = (weighted_positive - weighted_negative) / total_relevance
        
        # Determine overall sentiment
        if sentiment_score > 0.2:
            overall_sentiment = "positive"
        elif sentiment_score < -0.2:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": sentiment_score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_articles": len(articles)
        }
    
    def _calculate_confidence(self, articles: List[Dict[str, Any]], sentiment_analysis: Dict[str, Any]) -> float:
        """Calculate confidence based on article count and consistency."""
        confidence = 0.5  # Base confidence
        
        article_count = len(articles)
        if article_count > 10:
            confidence += 0.2
        elif article_count > 5:
            confidence += 0.1
        
        # Check sentiment consistency
        total_articles = sentiment_analysis.get("total_articles", 1)
        dominant_sentiment_count = max(
            sentiment_analysis.get("positive_count", 0),
            sentiment_analysis.get("negative_count", 0),
            sentiment_analysis.get("neutral_count", 0)
        )
        
        consistency = dominant_sentiment_count / total_articles if total_articles > 0 else 0
        confidence += consistency * 0.3
        
        return min(confidence, 1.0)
    
    def _assess_news_impact(self, articles: List[Dict[str, Any]], sentiment_analysis: Dict[str, Any]) -> str:
        """Assess the potential impact of news on stock price."""
        total_articles = len(articles)
        avg_relevance = sum(article.get("relevance", 0.5) for article in articles) / total_articles if total_articles > 0 else 0
        
        sentiment_strength = abs(sentiment_analysis.get("sentiment_score", 0))
        
        # High impact: many articles with high relevance and strong sentiment
        if total_articles >= 5 and avg_relevance > 0.8 and sentiment_strength > 0.4:
            return "high"
        # Medium impact: moderate coverage or sentiment
        elif total_articles >= 3 and (avg_relevance > 0.6 or sentiment_strength > 0.2):
            return "medium"
        else:
            return "low"
    
    def _extract_key_themes(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract key themes from news articles."""
        themes = []
        
        # Simple keyword-based theme extraction
        theme_keywords = {
            "earnings": ["lợi nhuận", "earnings", "profit", "revenue", "doanh thu"],
            "expansion": ["mở rộng", "expansion", "new market", "thị trường mới"],
            "competition": ["cạnh tranh", "competition", "competitor", "đối thủ"],
            "regulation": ["quy định", "regulation", "policy", "chính sách"],
            "investment": ["đầu tư", "investment", "funding", "capital"],
            "market_sentiment": ["thị trường", "market", "investor", "nhà đầu tư"]
        }
        
        for theme, keywords in theme_keywords.items():
            theme_count = 0
            for article in articles:
                title = article.get("title", "").lower()
                content = article.get("content", "").lower()
                
                if any(keyword.lower() in title or keyword.lower() in content for keyword in keywords):
                    theme_count += 1
            
            if theme_count >= 2:  # Theme appears in at least 2 articles
                themes.append(theme)
        
        return themes[:5]  # Return top 5 themes