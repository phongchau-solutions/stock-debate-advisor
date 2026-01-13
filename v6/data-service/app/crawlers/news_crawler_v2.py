"""
Comprehensive News Crawler for Vietnamese Financial Sites
Crawls news from: Yahoo Finance, CafeF, VnEconomy, VietStock
Handles both Vietnamese and English content
"""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import quote, urljoin
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class NewsSource:
    """Base class for news sources."""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def search_articles(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search for articles related to a stock symbol."""
        raise NotImplementedError
    
    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract full content from article URL."""
        raise NotImplementedError


class YahooFinanceNews(NewsSource):
    """Yahoo Finance news crawler - uses alternative approach."""
    
    def __init__(self):
        super().__init__("yahoo_finance", "https://finance.yahoo.com")
    
    def search_articles(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search Yahoo Finance news for a stock using yfinance."""
        articles = []
        try:
            import yfinance as yf
            
            # Clean symbol
            clean_symbol = symbol.replace('.VN', '')
            
            logger.info(f"Fetching news from Yahoo Finance for {clean_symbol}")
            
            # Create a Ticker object
            ticker = yf.Ticker(f"{clean_symbol}.VN")
            
            # Get news from ticker info
            info = ticker.info
            
            # Yahoo Finance also stores news in info dict
            if 'news' in info:
                for news_item in info.get('news', [])[:20]:
                    try:
                        article = {
                            'title': news_item.get('title', '')[:500],
                            'url': news_item.get('link', ''),
                            'source': 'yahoo_finance',
                            'source_name': 'Yahoo Finance',
                            'published_at': datetime.fromtimestamp(news_item.get('providerPublishTime', 0)) if news_item.get('providerPublishTime') else datetime.now(),
                        }
                        if article['url']:
                            articles.append(article)
                    except Exception as e:
                        logger.debug(f"Error parsing Yahoo Finance article: {e}")
                        continue
            
            logger.info(f"Found {len(articles)} articles on Yahoo Finance for {symbol}")
        
        except Exception as e:
            logger.debug(f"Yahoo Finance API fallback: {e}")
            articles = []
        
        # If yfinance didn't work, try direct web scraping
        if not articles:
            articles = self._web_scrape_fallback(symbol)
        
        return articles
    
    def _web_scrape_fallback(self, symbol: str) -> List[Dict[str, Any]]:
        """Fallback web scraping method."""
        articles = []
        try:
            clean_symbol = symbol.replace('.VN', '')
            # Try alternative Yahoo URLs
            urls = [
                f"https://finance.yahoo.com/quote/{clean_symbol}.VN",
                f"https://finance.yahoo.com/quote/{clean_symbol}",
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Look for any news-like content
                        news_items = soup.find_all(['article', 'div'], {'data-test': re.compile('news|story')})
                        
                        for item in news_items[:10]:
                            title = item.find(['h2', 'h3', 'a'])
                            if title:
                                articles.append({
                                    'title': title.get_text(strip=True)[:500],
                                    'url': url,
                                    'source': 'yahoo_finance',
                                    'source_name': 'Yahoo Finance',
                                    'published_at': datetime.now(),
                                })
                        
                        if articles:
                            break
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Yahoo Finance fallback scraping failed: {e}")
        
        return articles
    
    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract full article content from Yahoo Finance."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Yahoo Finance article structure
            article_body = soup.find('article') or soup.find('div', {'class': re.compile('article-body|caas-body')})
            
            if article_body:
                content = article_body.get_text(separator='\n', strip=True)
                return {
                    'content': content,
                    'length': len(content),
                }
            return None
        
        except Exception as e:
            logger.error(f"Error extracting Yahoo Finance article: {e}")
            return None


class CafeFNews(NewsSource):
    """CafeF news crawler (Vietnamese financial news)."""
    
    def __init__(self):
        super().__init__("cafef", "https://cafef.vn")
    
    def search_articles(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search CafeF news for a stock."""
        articles = []
        try:
            # CafeF search URL
            clean_symbol = symbol.replace('.VN', '')
            search_url = f"{self.base_url}/search/?q={quote(clean_symbol)}&type=news"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news items (CafeF structure may vary)
            news_items = soup.find_all('div', {'class': re.compile('item-news|news-item|article')})
            
            for item in news_items[:20]:
                try:
                    title_elem = item.find('h2') or item.find('h3') or item.find('a')
                    link_elem = item.find('a', href=True)
                    
                    if title_elem and link_elem:
                        article = {
                            'title': title_elem.get_text(strip=True),
                            'url': urljoin(self.base_url, link_elem.get('href', '')),
                            'published_at': datetime.now(),  # CafeF doesn't always show date clearly
                            'source': 'cafef',
                            'source_name': 'CafeF',
                        }
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing CafeF article: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} articles on CafeF for {symbol}")
        
        except Exception as e:
            logger.error(f"Error scraping CafeF for {symbol}: {e}")
        
        return articles
    
    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract full article content from CafeF."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Find article content
            article_body = soup.find('div', {'class': re.compile('article-content|news-detail|content-detail')})
            
            if article_body:
                content = article_body.get_text(separator='\n', strip=True)
                return {
                    'content': content,
                    'length': len(content),
                }
            return None
        
        except Exception as e:
            logger.error(f"Error extracting CafeF article: {e}")
            return None


class VnEconomyNews(NewsSource):
    """VnEconomy news crawler (Vietnamese financial news)."""
    
    def __init__(self):
        super().__init__("vneconomy", "https://vneconomy.vn")
    
    def search_articles(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search VnEconomy news for a stock."""
        articles = []
        try:
            # VnEconomy search URL
            clean_symbol = symbol.replace('.VN', '')
            search_url = f"{self.base_url}/search?q={quote(clean_symbol)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news items
            news_items = soup.find_all('div', {'class': re.compile('item|article|news')})
            
            for item in news_items[:20]:
                try:
                    title_elem = item.find('h2') or item.find('h3') or item.find(['a', 'span'])
                    link_elem = item.find('a', href=True)
                    
                    if title_elem and link_elem:
                        article = {
                            'title': title_elem.get_text(strip=True),
                            'url': urljoin(self.base_url, link_elem.get('href', '')),
                            'published_at': datetime.now(),
                            'source': 'vneconomy',
                            'source_name': 'VnEconomy',
                        }
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing VnEconomy article: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} articles on VnEconomy for {symbol}")
        
        except Exception as e:
            logger.error(f"Error scraping VnEconomy for {symbol}: {e}")
        
        return articles
    
    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract full article content from VnEconomy."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Find article content
            article_body = soup.find('div', {'class': re.compile('sapo|content|detail-content|article-content')})
            
            if article_body:
                content = article_body.get_text(separator='\n', strip=True)
                return {
                    'content': content,
                    'length': len(content),
                }
            return None
        
        except Exception as e:
            logger.error(f"Error extracting VnEconomy article: {e}")
            return None


class VietStockNews(NewsSource):
    """VietStock news crawler (Vietnamese stock exchange news)."""
    
    def __init__(self):
        super().__init__("vietstock", "https://vietstock.vn")
    
    def search_articles(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Search VietStock news for a stock."""
        articles = []
        try:
            # VietStock search URL
            clean_symbol = symbol.replace('.VN', '')
            search_url = f"{self.base_url}/search?keyword={quote(clean_symbol)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news items
            news_items = soup.find_all('div', {'class': re.compile('item|article|news-item')})
            
            for item in news_items[:20]:
                try:
                    title_elem = item.find('h2') or item.find('h3') or item.find('a')
                    link_elem = item.find('a', href=True)
                    
                    if title_elem and link_elem:
                        article = {
                            'title': title_elem.get_text(strip=True),
                            'url': urljoin(self.base_url, link_elem.get('href', '')),
                            'published_at': datetime.now(),
                            'source': 'vietstock',
                            'source_name': 'VietStock',
                        }
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing VietStock article: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} articles on VietStock for {symbol}")
        
        except Exception as e:
            logger.error(f"Error scraping VietStock for {symbol}: {e}")
        
        return articles
    
    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract full article content from VietStock."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Find article content
            article_body = soup.find('div', {'class': re.compile('content|detail|article-content|news-content')})
            
            if article_body:
                content = article_body.get_text(separator='\n', strip=True)
                return {
                    'content': content,
                    'length': len(content),
                }
            return None
        
        except Exception as e:
            logger.error(f"Error extracting VietStock article: {e}")
            return None


class NewsAggregator:
    """Aggregates news from multiple sources for Vietnamese stocks."""
    
    def __init__(self):
        self.sources = [
            YahooFinanceNews(),
            CafeFNews(),
            VnEconomyNews(),
            VietStockNews(),
        ]
    
    def crawl_for_symbol(self, symbol: str, days: int = 30, 
                        sources: Optional[List[str]] = None,
                        max_workers: int = 4) -> Dict[str, List[Dict]]:
        """
        Crawl news for a stock from all or specified sources.
        
        Args:
            symbol: Stock symbol (e.g., 'MBB.VN')
            days: Number of days back to search
            sources: List of source names to use (None = all)
            max_workers: Number of concurrent threads
        
        Returns:
            Dictionary with source names as keys and article lists as values
        """
        results = {}
        
        filtered_sources = self.sources
        if sources:
            filtered_sources = [s for s in self.sources if s.name in sources]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(source.search_articles, symbol, days): source.name
                for source in filtered_sources
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    articles = future.result()
                    results[source_name] = articles
                except Exception as e:
                    logger.error(f"Error fetching from {source_name}: {e}")
                    results[source_name] = []
                
                # Rate limiting
                time.sleep(0.5)
        
        return results
    
    def crawl_for_symbols(self, symbols: List[str], days: int = 30,
                         max_workers: int = 4) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Crawl news for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            days: Number of days back to search
            max_workers: Number of concurrent threads
        
        Returns:
            Dictionary with symbols as keys and source results as values
        """
        all_results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.crawl_for_symbol, symbol, days): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    results = future.result()
                    all_results[symbol] = results
                except Exception as e:
                    logger.error(f"Error crawling for {symbol}: {e}")
                    all_results[symbol] = {}
                
                # Rate limiting
                time.sleep(0.2)
        
        return all_results
    
    @staticmethod
    def normalize_articles(articles_by_source: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Normalize and deduplicate articles across sources.
        
        Args:
            articles_by_source: Articles grouped by source
        
        Returns:
            Normalized list of unique articles
        """
        normalized = []
        seen_urls = set()
        seen_titles = set()
        
        for source, articles in articles_by_source.items():
            for article in articles:
                # Deduplicate by URL and title
                url = article.get('url', '')
                title = article.get('title', '')
                
                if url in seen_urls or title in seen_titles:
                    continue
                
                seen_urls.add(url)
                seen_titles.add(title)
                
                # Add content hash for duplicate detection
                content_hash = hashlib.sha256(
                    (title + url).encode('utf-8')
                ).hexdigest()
                
                article['content_hash'] = content_hash
                normalized.append(article)
        
        return sorted(normalized, key=lambda x: x.get('published_at', datetime.now()), reverse=True)
