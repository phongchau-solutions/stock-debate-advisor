"""
News crawler for Vietnamese financial news websites.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class NewsCrawler:
    """Crawler for Vietnamese financial news sites."""

    def __init__(self):
        """Initialize news crawler."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def crawl_vietstock(self, symbol: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Crawl news from VietStock."""
        articles = []
        try:
            # Search page
            url = f"https://vietstock.vn/search?q={symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article links (adjust selectors based on actual site structure)
            article_elements = soup.find_all('a', class_=re.compile(r'news|article'), limit=max_articles)
            
            for elem in article_elements:
                try:
                    title = elem.get_text(strip=True)
                    link = elem.get('href', '')
                    
                    if not link:
                        continue
                    
                    # Make absolute URL
                    full_url = urljoin(url, link)
                    
                    # Get article content
                    content = self._fetch_article_content(full_url)
                    
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'vietstock',
                        'symbol': symbol,
                        'published_at': datetime.utcnow(),
                    })
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to crawl VietStock for {symbol}: {e}")
        
        return articles

    def crawl_cafef(self, symbol: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Crawl news from CafeF."""
        articles = []
        try:
            url = f"https://cafef.vn/tim-kiem.chn?keywords={symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find articles
            article_elements = soup.find_all('h3', limit=max_articles)
            
            for elem in article_elements:
                try:
                    link_elem = elem.find('a')
                    if not link_elem:
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    
                    if not link:
                        continue
                    
                    full_url = urljoin(url, link)
                    content = self._fetch_article_content(full_url)
                    
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'cafef',
                        'symbol': symbol,
                        'published_at': datetime.utcnow(),
                    })
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to crawl CafeF for {symbol}: {e}")
        
        return articles

    def crawl_vneconomy(self, symbol: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Crawl news from VnEconomy."""
        articles = []
        try:
            url = f"https://vneconomy.vn/tim-kiem.html?Text={symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find articles
            article_elements = soup.find_all('h2', limit=max_articles)
            
            for elem in article_elements:
                try:
                    link_elem = elem.find('a')
                    if not link_elem:
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    
                    if not link:
                        continue
                    
                    full_url = urljoin(url, link)
                    content = self._fetch_article_content(full_url)
                    
                    articles.append({
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'vneconomy',
                        'symbol': symbol,
                        'published_at': datetime.utcnow(),
                    })
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to crawl VnEconomy for {symbol}: {e}")
        
        return articles

    def crawl_all_sources(self, symbol: str, max_per_source: int = 5) -> List[Dict[str, Any]]:
        """Crawl news from all sources."""
        all_articles = []
        
        logger.info(f"Crawling news for {symbol}...")
        
        # VietStock
        articles = self.crawl_vietstock(symbol, max_per_source)
        all_articles.extend(articles)
        logger.info(f"  VietStock: {len(articles)} articles")
        
        # CafeF
        articles = self.crawl_cafef(symbol, max_per_source)
        all_articles.extend(articles)
        logger.info(f"  CafeF: {len(articles)} articles")
        
        # VnEconomy
        articles = self.crawl_vneconomy(symbol, max_per_source)
        all_articles.extend(articles)
        logger.info(f"  VnEconomy: {len(articles)} articles")
        
        logger.info(f"Total articles crawled: {len(all_articles)}")
        return all_articles

    def _fetch_article_content(self, url: str) -> str:
        """Fetch full article content."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find main content (adjust selectors as needed)
            content_div = soup.find('article') or soup.find('div', class_=re.compile(r'content|article'))
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                return content[:5000]  # Limit content length
            else:
                # Fallback: get all paragraphs
                paragraphs = soup.find_all('p')
                content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:10])
                return content[:5000]
                
        except Exception as e:
            logger.warning(f"Failed to fetch article content from {url}: {e}")
            return ""
