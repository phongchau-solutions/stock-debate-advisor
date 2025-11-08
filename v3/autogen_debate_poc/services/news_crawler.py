"""
News Crawler Service for Vietnamese and International Financial News
Crawls VnEconomy and Wall Street Journal for stock-related articles.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class NewsCrawler:
    """
    Crawls financial news from VnEconomy (Vietnamese) and WSJ (International).
    
    Features:
    - Async HTTP requests with timeout
    - Politeness: rate limiting and user-agent
    - Robust error handling
    - Caching to avoid redundant requests
    """
    
    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize news crawler.
        
        Args:
            rate_limit_delay: Seconds to wait between requests (politeness)
        """
        self.rate_limit_delay = rate_limit_delay
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # User agent for polite crawling
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; FinancialAnalysisBot/1.0; +http://example.com/bot)'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_news(self, symbol: str, sector_keywords: List[str] = None, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news for a stock by searching sector/domain keywords.
        
        Args:
            symbol: Stock symbol (e.g., 'VNM')
            sector_keywords: Domain/sector keywords (e.g., ['milk', 'dairy', 'food'])
                           If None, will attempt to infer from symbol
            max_articles: Maximum articles to fetch per source
            
        Returns:
            List of news articles with source, title, text, url, published date
        """
        # Infer sector keywords if not provided
        if not sector_keywords:
            sector_keywords = self._infer_sector_keywords(symbol)
        
        cache_key = f"{symbol}_{'_'.join(sector_keywords)}_{datetime.now().strftime('%Y%m%d')}"
        if cache_key in self.cache:
            logger.info(f"Returning cached news for {symbol} (sector: {sector_keywords})")
            return self.cache[cache_key]
        
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        articles = []
        
        # Fetch from VietStock (Vietnamese stock news site)
        try:
            vietstock_articles = await self._fetch_vietstock(symbol, sector_keywords, max_articles // 3)
            articles.extend(vietstock_articles)
            await asyncio.sleep(self.rate_limit_delay)  # Politeness
        except Exception as e:
            logger.warning(f"VietStock crawl failed for {symbol}: {e}")
        
        # Fetch from VnEconomy using sector keywords
        try:
            vne_articles = await self._fetch_vneconomy(symbol, sector_keywords, max_articles // 3)
            articles.extend(vne_articles)
            await asyncio.sleep(self.rate_limit_delay)  # Politeness
        except Exception as e:
            logger.warning(f"VnEconomy crawl failed for {symbol}: {e}")
        
        # Fetch from WSJ using sector keywords
        try:
            wsj_articles = await self._fetch_wsj(symbol, sector_keywords, max_articles // 3)
            articles.extend(wsj_articles)
        except Exception as e:
            logger.warning(f"WSJ crawl failed for {symbol}: {e}")
        
        # Cache results
        self.cache[cache_key] = articles
        logger.info(f"Fetched {len(articles)} articles for {symbol} using keywords: {sector_keywords}")
        
        return articles
    
    def _infer_sector_keywords(self, symbol: str) -> List[str]:
        """
        Infer sector keywords from stock symbol.
        Returns basic fallback keywords - caller should provide explicit keywords when possible.
        """
        # Simple fallback: symbol + generic Vietnamese market terms
        keywords = [symbol.lower(), 'vietnam', 'stock', 'market']
        logger.info(f"Using fallback sector keywords for {symbol}: {keywords}")
        return keywords
    
    async def _fetch_vietstock(self, symbol: str, sector_keywords: List[str], max_articles: int) -> List[Dict[str, Any]]:
        """
        Fetch news articles from VietStock.vn for a given symbol.
        VietStock is a major Vietnamese financial news website.
        
        Args:
            symbol: Stock symbol (e.g., 'VNM')
            sector_keywords: List of sector-related keywords
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries with title, content, date, source, url
        """
        articles = []
        
        try:
            # VietStock stock page structure: https://vietstock.vn/{SYMBOL}
            stock_url = f"https://vietstock.vn/{symbol}"
            
            if not self.session:
                logger.warning("HTTP session not initialized")
                return articles
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            
            async with self.session.get(stock_url, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.warning(f"VietStock returned status {response.status} for {symbol}")
                    return articles
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try to find news sections - VietStock has various layouts
                # Approach 1: Look for news container divs
                news_containers = soup.find_all('div', class_=['news-item', 'news-list-item', 'article-item'])
                
                # Approach 2: Look for article links with 'tin-tuc' (news) in URL
                if not news_containers:
                    news_links = soup.find_all('a', href=lambda x: x and 'tin-tuc' in x)
                    news_containers = [link.parent for link in news_links[:max_articles]]
                
                # Approach 3: Search for div elements containing stock news patterns
                if not news_containers:
                    all_divs = soup.find_all('div', class_=True)
                    news_containers = [d for d in all_divs if any(kw in str(d.get('class')).lower() for kw in ['news', 'article', 'post'])][:max_articles]
                
                for container in news_containers[:max_articles]:
                    try:
                        # Extract title
                        title_tag = container.find('a') or container.find('h3') or container.find('h4')
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text(strip=True)
                        article_url = title_tag.get('href', '')
                        
                        # Make URL absolute
                        if article_url and not article_url.startswith('http'):
                            article_url = f"https://vietstock.vn{article_url}"
                        
                        # Extract content/summary
                        content_tag = container.find('p') or container.find('div', class_=['summary', 'description', 'excerpt'])
                        content = content_tag.get_text(strip=True) if content_tag else ""
                        
                        # Extract date
                        date_tag = container.find('time') or container.find('span', class_=['date', 'time', 'publish-date'])
                        date_str = date_tag.get_text(strip=True) if date_tag else "N/A"
                        
                        # Filter by sector keywords (case-insensitive)
                        text_to_check = f"{title} {content}".lower()
                        keyword_match = any(kw.lower() in text_to_check for kw in sector_keywords)
                        
                        if title and (keyword_match or symbol.lower() in text_to_check):
                            articles.append({
                                'title': title,
                                'content': content or title,
                                'date': date_str,
                                'source': 'VietStock.vn',
                                'url': article_url or stock_url
                            })
                    
                    except Exception as e:
                        logger.debug(f"Error parsing VietStock article container: {e}")
                        continue
            
            logger.info(f"VietStock: Fetched {len(articles)} articles for {symbol}")
            
        except asyncio.TimeoutError:
            logger.warning(f"VietStock request timeout for {symbol}")
        except Exception as e:
            logger.error(f"VietStock crawl error for {symbol}: {e}")
        
        return articles

    async def _fetch_vneconomy(self, symbol: str, sector_keywords: List[str], max_articles: int) -> List[Dict[str, Any]]:
        """
        Crawl VnEconomy for Vietnamese market news using sector keywords.
        
        Uses Google News as proxy since direct VnEconomy requires complex JS rendering.
        Searches by sector/domain keywords rather than stock symbol for better relevance.
        """
        articles = []
        
        try:
            # Build search query with sector keywords
            keyword_query = ' OR '.join(sector_keywords[:3])  # Use top 3 keywords
            query = f"({keyword_query}) Vietnam (site:vneconomy.vn OR site:cafef.vn OR site:ndh.vn)"
            search_url = f"https://www.google.com/search?q={quote(query)}&tbm=nws&num={max_articles}"
            logger.info(f"VnEconomy search query: {query}")
            
            async with self.session.get(search_url, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Google News search returned status {response.status}")
                    # Fallback to demo data with clear labeling
                    return self._get_demo_vneconomy(symbol, max_articles)
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse Google News results
                # Google News structure: <div class="SoaBEf"> or similar containers
                news_items = soup.find_all('div', class_='SoaBEf')
                if not news_items:
                    # Try alternative selectors
                    news_items = soup.find_all('div', {'role': 'article'})
                
                for item in news_items[:max_articles]:
                    try:
                        title_tag = item.find('div', class_='n0jPhd') or item.find('a')
                        link_tag = item.find('a')
                        
                        if title_tag and link_tag:
                            article = {
                                "source": "VnEconomy/CafeF",
                                "title": title_tag.get_text(strip=True),
                                "url": link_tag.get('href', ''),
                                "text": title_tag.get_text(strip=True),  # Summary from title
                                "published": datetime.now().isoformat(),
                                "language": "vi",
                                "method": "google_news_proxy"
                            }
                            
                            # Clean Google redirect URL
                            if 'google.com/url?q=' in article["url"]:
                                actual_url = article["url"].split('google.com/url?q=')[1].split('&')[0]
                                article["url"] = actual_url
                            
                            articles.append(article)
                    except Exception as e:
                        logger.debug(f"Failed to parse news item: {e}")
                        continue
            
            # If no results, use demo data
            if not articles:
                articles = self._get_demo_vneconomy(symbol, max_articles)
                
        except asyncio.TimeoutError:
            logger.warning("VnEconomy/Google News request timed out")
            articles = self._get_demo_vneconomy(symbol, max_articles)
        except Exception as e:
            logger.error(f"VnEconomy crawl error: {e}")
            articles = self._get_demo_vneconomy(symbol, max_articles)
        
        return articles
    
    def _get_demo_vneconomy(self, symbol: str, max_articles: int) -> List[Dict[str, Any]]:
        """Provide demo Vietnamese news when real crawl fails"""
        logger.info(f"Using demo Vietnamese news data for {symbol}")
        return [
            {
                "source": "VietStock (Demo)",
                "title": f"{symbol} - Báo cáo phân tích kỹ thuật chi tiết",
                "text": f"VietStock phân tích xu hướng giá cổ phiếu {symbol} với các chỉ báo kỹ thuật và khuyến nghị đầu tư.",
                "url": f"https://vietstock.vn/{symbol}",
                "published": (datetime.now() - timedelta(hours=1)).isoformat(),
                "language": "vi",
                "note": "Demo data - VietStock scraper needs real site structure analysis"
            },
            {
                "source": "VnEconomy (Demo)",
                "title": f"Cổ phiếu {symbol}: Phân tích triển vọng quý IV/2024",
                "text": f"Các chuyên gia đánh giá triển vọng tích cực cho cổ phiếu {symbol} trong quý tới dựa trên kết quả kinh doanh và xu hướng thị trường.",
                "url": f"https://vneconomy.vn/search?q={symbol}",
                "published": (datetime.now() - timedelta(hours=2)).isoformat(),
                "language": "vi",
                "note": "Demo data - Enable real crawl by updating HTML selectors"
            },
            {
                "source": "CafeF (Demo)",
                "title": f"{symbol} - Cập nhật thị trường chứng khoán",
                "text": f"Thị trường giao dịch sôi động với {symbol} trong phiên hôm nay. Nhà đầu tư quan tâm đến báo cáo tài chính sắp tới.",
                "url": f"https://cafef.vn/search?q={symbol}",
                "published": (datetime.now() - timedelta(hours=5)).isoformat(),
                "language": "vi",
                "note": "Demo data - Real news crawler needs API access"
            }
        ][:max_articles]
    
    async def _fetch_wsj(self, symbol: str, sector_keywords: List[str], max_articles: int) -> List[Dict[str, Any]]:
        """
        Crawl Wall Street Journal for international market news using sector keywords.
        
        Searches by sector/domain keywords for broader industry news rather than
        specific stock symbols.
        """
        articles = []
        
        try:
            # Build search query with sector keywords
            keyword_query = ' '.join(sector_keywords[:2])  # Use top 2 keywords
            search_url = f"https://www.wsj.com/search?query={quote(keyword_query)}&isToggleOn=true&operator=AND&sort=date-desc"
            logger.info(f"WSJ search query: {keyword_query}")
            
            async with self.session.get(search_url, timeout=10) as response:
                if response.status == 403:
                    logger.warning("WSJ blocked request (403). May need subscription or different approach.")
                    return self._fetch_wsj_fallback(symbol, max_articles)
                
                if response.status != 200:
                    logger.warning(f"WSJ returned status {response.status}")
                    return articles
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse search results
                # Note: WSJ structure changes frequently. This is a generic parser.
                article_items = soup.find_all('article', limit=max_articles)
                if not article_items:
                    article_items = soup.find_all('div', class_='WSJTheme--headline', limit=max_articles)
                
                for item in article_items:
                    try:
                        title_tag = item.find('h3') or item.find('h2') or item.find('span', class_='WSJTheme--headline')
                        link_tag = item.find('a')
                        desc_tag = item.find('p')
                        
                        if title_tag and link_tag:
                            article = {
                                "source": "WSJ",
                                "title": title_tag.get_text(strip=True),
                                "url": link_tag.get('href', ''),
                                "text": desc_tag.get_text(strip=True) if desc_tag else title_tag.get_text(strip=True),
                                "published": datetime.now().isoformat(),
                                "language": "en"
                            }
                            
                            # Make URL absolute if relative
                            if article["url"] and not article["url"].startswith('http'):
                                article["url"] = f"https://www.wsj.com{article['url']}"
                            
                            articles.append(article)
                    except Exception as e:
                        logger.debug(f"Failed to parse WSJ article: {e}")
                        continue
                
        except asyncio.TimeoutError:
            logger.warning("WSJ request timed out")
        except Exception as e:
            logger.error(f"WSJ crawl error: {e}")
        
        return articles
    
    def _fetch_wsj_fallback(self, symbol: str, max_articles: int) -> List[Dict[str, Any]]:
        """
        Fallback: Use WSJ RSS feed or public API if available.
        For now, returns demo data with disclaimer.
        """
        logger.info("Using WSJ fallback (demo) data")
        return [
            {
                "source": "WSJ",
                "title": f"Markets Watch: {symbol} Analysis",
                "text": f"Analysts provide mixed outlook on {symbol} amid market volatility.",
                "url": f"https://www.wsj.com/search?query={symbol}",
                "published": (datetime.now() - timedelta(days=1)).isoformat(),
                "language": "en",
                "note": "Demo data - WSJ requires subscription for full access"
            }
        ]
    
    async def fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch full article content from URL.
        
        Args:
            url: Article URL
            
        Returns:
            Full article text or None if failed
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url, timeout=15) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try to find article body
                article_body = soup.find('article') or soup.find('div', class_='article-body') or soup.find('div', class_='content')
                
                if article_body:
                    # Extract paragraphs
                    paragraphs = article_body.find_all('p')
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    return text
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch article content from {url}: {e}")
            return None


# Convenience function for simple usage
async def get_stock_news(symbol: str, max_articles: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch news for a stock symbol.
    
    Usage:
        news = await get_stock_news("VNM", max_articles=5)
    """
    async with NewsCrawler() as crawler:
        return await crawler.fetch_news(symbol, max_articles)
