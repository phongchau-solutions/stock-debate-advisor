"""
News crawlers for sentiment analysis from VnEconomy and The Wall Street Journal.
"""

from __future__ import annotations

import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class NewsItem:
    """Structured news item for sentiment analysis."""
    
    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        published_date: Optional[datetime] = None,
        source: str = "",
        symbols_mentioned: Optional[List[str]] = None
    ):
        self.title = title
        self.content = content
        self.url = url
        self.published_date = published_date or datetime.now()
        self.source = source
        self.symbols_mentioned = symbols_mentioned or []


class VnEconomyCrawler:
    """Crawler for VnEconomy Vietnamese financial news."""
    
    def __init__(self):
        self.base_url = "https://vneconomy.vn"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        
    def search_by_symbols(self, symbols: List[str], days_back: int = 7) -> List[NewsItem]:
        """Search for news mentioning specific stock symbols."""
        news_items = []
        
        for symbol in symbols:
            try:
                # VnEconomy search for stock symbol
                search_urls = [
                    f"{self.base_url}/tim-kiem.htm?q={symbol}",
                    f"{self.base_url}/chung-khoan.htm",  # Stock section
                    f"{self.base_url}/doanh-nghiep.htm"  # Business section
                ]
                
                for search_url in search_urls:
                    try:
                        response = self.session.get(search_url, timeout=10)
                        if response.status_code == 200:
                            articles = self._parse_vneconomy_articles(
                                response.text, symbol, search_url
                            )
                            news_items.extend(articles[:5])  # Limit per search
                    except Exception as e:
                        logger.warning(f"Failed to fetch {search_url}: {e}")
                        
            except Exception as e:
                logger.error(f"Error searching VnEconomy for {symbol}: {e}")
                
        return news_items[:20]  # Overall limit
        
    def _parse_vneconomy_articles(self, html: str, symbol: str, base_url: str) -> List[NewsItem]:
        """Parse VnEconomy HTML for article links and content."""
        articles: List[NewsItem] = []
        
        try:
            # Simple regex-based parsing for Vietnamese news
            # Look for article patterns in VnEconomy structure
            title_pattern = r'<h[1-6][^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(title_pattern, html, re.IGNORECASE | re.DOTALL)
            
            for url_path, title in matches[:10]:
                try:
                    # Clean and validate URL
                    if url_path.startswith('/'):
                        article_url = urljoin(self.base_url, url_path)
                    elif url_path.startswith('http'):
                        article_url = url_path
                    else:
                        continue
                        
                    # Check if title or URL mentions the symbol
                    if (symbol.upper() in title.upper() or 
                        symbol.upper() in article_url.upper() or
                        self._mentions_finance_keywords(title)):
                        
                        # Fetch article content
                        content = self._fetch_article_content(article_url)
                        
                        articles.append(NewsItem(
                            title=title.strip(),
                            content=content,
                            url=article_url,
                            source="VnEconomy",
                            symbols_mentioned=[symbol] if symbol.upper() in (title + content).upper() else []
                        ))
                        
                except Exception as e:
                    logger.debug(f"Error parsing VnEconomy article: {e}")
                    
        except Exception as e:
            logger.error(f"Error parsing VnEconomy HTML: {e}")
            
        return articles
        
    def _fetch_article_content(self, url: str) -> str:
        """Fetch full article content from URL."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Extract main content using common Vietnamese news patterns
                content_patterns = [
                    r'<div[^>]*class="[^"]*detail-content[^"]*"[^>]*>(.*?)</div>',
                    r'<div[^>]*class="[^"]*article-body[^"]*"[^>]*>(.*?)</div>',
                    r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                    r'<p[^>]*>(.*?)</p>'
                ]
                
                for pattern in content_patterns:
                    matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
                    if matches:
                        # Take first substantial match
                        content = ' '.join(matches[:3])  # First 3 paragraphs
                        # Clean HTML tags
                        content = re.sub(r'<[^>]+>', ' ', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                        if len(content) > 100:  # Substantial content
                            return content[:1000]  # Limit length
                            
        except Exception as e:
            logger.debug(f"Error fetching article content from {url}: {e}")
            
        return "Content not available"
        
    def _mentions_finance_keywords(self, text: str) -> bool:
        """Check if text mentions financial keywords in Vietnamese."""
        finance_keywords = [
            'chứng khoán', 'cổ phiếu', 'thị trường', 'đầu tư', 'tài chính',
            'ngân hàng', 'lợi nhuận', 'doanh thu', 'kinh doanh', 'công ty',
            'stock', 'market', 'finance', 'bank', 'profit', 'revenue'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in finance_keywords)


class WSJCrawler:
    """Crawler for Wall Street Journal financial news."""
    
    def __init__(self):
        self.base_url = "https://www.wsj.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        
    def search_by_symbols(self, symbols: List[str], days_back: int = 7) -> List[NewsItem]:
        """Search WSJ for news mentioning specific symbols or sectors."""
        news_items = []
        
        # WSJ sections relevant to Vietnamese/Asian markets
        search_sections = [
            "/news/world/asia",
            "/news/markets", 
            "/news/business",
            "/news/economy"
        ]
        
        for symbol in symbols:
            try:
                # Search for company/sector news
                search_terms = [
                    symbol,
                    f"{symbol} Vietnam",
                    "Vietnam banking" if symbol in ['VCB', 'CTG', 'BID'] else f"Vietnam {symbol}",
                    "Southeast Asia markets"
                ]
                
                for term in search_terms:
                    try:
                        # Use WSJ search (may be limited without subscription)
                        search_url = f"{self.base_url}/search?query={term.replace(' ', '%20')}"
                        response = self.session.get(search_url, timeout=10)
                        
                        if response.status_code == 200:
                            articles = self._parse_wsj_articles(
                                response.text, symbol, search_url
                            )
                            news_items.extend(articles[:3])  # Limit per search
                            
                    except Exception as e:
                        logger.warning(f"Failed WSJ search for {term}: {e}")
                        
                # Also try section pages for general market sentiment
                for section in search_sections[:2]:  # Limit sections
                    try:
                        section_url = f"{self.base_url}{section}"
                        response = self.session.get(section_url, timeout=10)
                        
                        if response.status_code == 200:
                            articles = self._parse_wsj_section(
                                response.text, symbol, section_url
                            )
                            news_items.extend(articles[:2])  # Few from each section
                            
                    except Exception as e:
                        logger.warning(f"Failed WSJ section {section}: {e}")
                        
            except Exception as e:
                logger.error(f"Error searching WSJ for {symbol}: {e}")
                
        return news_items[:15]  # Overall limit
        
    def _parse_wsj_articles(self, html: str, symbol: str, base_url: str) -> List[NewsItem]:
        """Parse WSJ search results."""
        articles: List[NewsItem] = []
        
        try:
            # WSJ article patterns
            patterns = [
                r'<h[1-6][^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',
                r'<a[^>]*href="(/articles/[^"]*)"[^>]*>([^<]+)</a>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                
                for url_path, title in matches[:8]:
                    try:
                        # Build full URL
                        if url_path.startswith('/'):
                            article_url = urljoin(self.base_url, url_path)
                        elif url_path.startswith('http'):
                            article_url = url_path
                        else:
                            continue
                            
                        # Check relevance to symbol or Asian markets
                        if (self._mentions_symbol_or_market(title, symbol) or
                            self._mentions_asian_markets(title)):
                            
                            # Get article preview (full content may require subscription)
                            content = self._fetch_wsj_preview(article_url)
                            
                            articles.append(NewsItem(
                                title=title.strip(),
                                content=content,
                                url=article_url,
                                source="Wall Street Journal",
                                symbols_mentioned=[symbol] if symbol.upper() in title.upper() else []
                            ))
                            
                    except Exception as e:
                        logger.debug(f"Error parsing WSJ article: {e}")
                        
        except Exception as e:
            logger.error(f"Error parsing WSJ HTML: {e}")
            
        return articles
        
    def _parse_wsj_section(self, html: str, symbol: str, section_url: str) -> List[NewsItem]:
        """Parse WSJ section page for relevant articles."""
        articles: List[NewsItem] = []
        
        try:
            # Look for headlines in section pages
            headline_pattern = r'<h[1-6][^>]*class="[^"]*headline[^"]*"[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(headline_pattern, html, re.IGNORECASE | re.DOTALL)
            
            for url_path, title in matches[:5]:
                try:
                    if self._mentions_asian_markets(title) or "Vietnam" in title:
                        article_url = urljoin(self.base_url, url_path)
                        content = self._fetch_wsj_preview(article_url)
                        
                        articles.append(NewsItem(
                            title=title.strip(),
                            content=content,
                            url=article_url,
                            source="WSJ",
                            symbols_mentioned=[]
                        ))
                        
                except Exception as e:
                    logger.debug(f"Error parsing WSJ section article: {e}")
                    
        except Exception as e:
            logger.error(f"Error parsing WSJ section: {e}")
            
        return articles
        
    def _fetch_wsj_preview(self, url: str) -> str:
        """Fetch WSJ article preview (may be limited by paywall)."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Extract preview/summary content
                preview_patterns = [
                    r'<div[^>]*class="[^"]*article-wrap[^"]*"[^>]*>(.*?)</div>',
                    r'<p[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</p>',
                    r'<div[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</div>',
                    r'<p[^>]*>(.*?)</p>'  # First paragraph
                ]
                
                for pattern in preview_patterns:
                    matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
                    if matches:
                        content = ' '.join(matches[:2])  # First 2 matches
                        content = re.sub(r'<[^>]+>', ' ', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                        if len(content) > 50:
                            return content[:800]  # Limit length
                            
        except Exception as e:
            logger.debug(f"Error fetching WSJ preview from {url}: {e}")
            
        return "Preview not available"
        
    def _mentions_symbol_or_market(self, text: str, symbol: str) -> bool:
        """Check if text mentions the symbol or relevant market terms."""
        text_upper = text.upper()
        return (symbol.upper() in text_upper or
                any(term in text_upper for term in ['VIETNAM', 'BANKING', 'ASIA', 'EMERGING']))
                
    def _mentions_asian_markets(self, text: str) -> bool:
        """Check if text mentions Asian markets."""
        asian_keywords = [
            'Vietnam', 'Asia', 'Asian', 'Southeast Asia', 'emerging markets',
            'ASEAN', 'Ho Chi Minh', 'Hanoi', 'Vietnamese'
        ]
        text_upper = text.upper()
        return any(keyword.upper() in text_upper for keyword in asian_keywords)


class NewsCrawler:
    """Unified news crawler for sentiment analysis."""
    
    def __init__(self):
        self.vneconomy = VnEconomyCrawler()
        self.wsj = WSJCrawler()
        
    def crawl_news_for_symbols(
        self, 
        symbols: List[str], 
        days_back: int = 7,
        max_articles_per_source: int = 10
    ) -> Dict[str, Any]:
        """Crawl news from both sources for given symbols."""
        vneconomy_articles: List[NewsItem] = []
        wsj_articles: List[NewsItem] = []
        sources_used: List[str] = []
        symbols_covered: set[str] = set()
        crawl_errors: List[str] = []
        
        results: Dict[str, Any] = {
            "vneconomy": vneconomy_articles,
            "wsj": wsj_articles,
            "summary": {
                "total_articles": 0,
                "sources_used": sources_used,
                "symbols_covered": symbols_covered,
                "crawl_errors": crawl_errors
            }
        }
        
        # Crawl VnEconomy
        try:
            logger.info(f"Crawling VnEconomy for symbols: {symbols}")
            vn_articles_raw = self.vneconomy.search_by_symbols(symbols, days_back)
            vneconomy_articles.extend(vn_articles_raw[:max_articles_per_source])
            results["vneconomy"] = vneconomy_articles
            sources_used.append("VnEconomy")
            
            for article in vneconomy_articles:
                symbols_covered.update(article.symbols_mentioned)
                
        except Exception as e:
            error_msg = f"VnEconomy crawl failed: {e}"
            logger.error(error_msg)
            crawl_errors.append(error_msg)
            
        # Crawl WSJ
        try:
            logger.info(f"Crawling WSJ for symbols: {symbols}")
            wsj_articles_raw = self.wsj.search_by_symbols(symbols, days_back)
            wsj_articles.extend(wsj_articles_raw[:max_articles_per_source])
            results["wsj"] = wsj_articles
            sources_used.append("Wall Street Journal")
            
            for article in wsj_articles:
                symbols_covered.update(article.symbols_mentioned)
                
        except Exception as e:
            error_msg = f"WSJ crawl failed: {e}"
            logger.error(error_msg)
            crawl_errors.append(error_msg)
            
        # Update summary
        results["summary"]["total_articles"] = len(vneconomy_articles) + len(wsj_articles)
        results["summary"]["symbols_covered"] = list(symbols_covered)
        
        logger.info(f"News crawl complete: {results['summary']['total_articles']} articles from {len(sources_used)} sources")
        
        return results