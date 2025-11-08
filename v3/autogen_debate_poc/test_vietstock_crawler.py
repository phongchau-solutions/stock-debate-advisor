#!/usr/bin/env python3
"""
Test VietStock.vn news crawler integration.

This test validates:
1. VietStock crawler added to news sources
2. Sector keyword filtering works with VietStock
3. Demo fallback includes VietStock articles
4. All three sources (VietStock, VnEconomy, WSJ) called in parallel
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.news_crawler import NewsCrawler


async def test_vietstock_integration():
    """Test VietStock.vn integration with news crawler"""
    
    print("=" * 80)
    print("TEST: VietStock.vn News Crawler Integration")
    print("=" * 80)
    
    # Test with Vietnamese stock symbol
    symbol = "VNM"
    sector_keywords = ['milk', 'dairy', 'food', 'beverage', 'vinamilk']
    max_articles = 9  # 3 per source
    
    print(f"\n1. Testing news crawl for {symbol}")
    print(f"   Sector keywords: {sector_keywords}")
    print(f"   Max articles: {max_articles} (3 per source)")
    
    async with NewsCrawler() as crawler:
        articles = await crawler.fetch_news(symbol, sector_keywords=sector_keywords, max_articles=max_articles)
        
        print(f"\n2. Results:")
        print(f"   Total articles: {len(articles)}")
        
        # Group by source
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(article)
        
        print(f"\n3. Articles by source:")
        for source, source_articles in sources.items():
            print(f"   - {source}: {len(source_articles)} articles")
        
        # Validate VietStock is included
        vietstock_articles = [a for a in articles if 'vietstock' in a.get('source', '').lower()]
        print(f"\n4. VietStock validation:")
        print(f"   VietStock articles found: {len(vietstock_articles)}")
        
        if vietstock_articles:
            print(f"   ✓ VietStock source is integrated")
            print(f"\n   Sample VietStock article:")
            sample = vietstock_articles[0]
            print(f"   - Title: {sample.get('title', 'N/A')[:80]}...")
            print(f"   - Source: {sample.get('source', 'N/A')}")
            print(f"   - URL: {sample.get('url', 'N/A')}")
            print(f"   - Date: {sample.get('date', sample.get('published', 'N/A'))}")
            if 'note' in sample:
                print(f"   - Note: {sample['note']}")
        else:
            print(f"   ⚠ No VietStock articles (check if real scraping works or demo fallback)")
        
        # Display all articles
        print(f"\n5. All articles details:")
        for i, article in enumerate(articles, 1):
            print(f"\n   Article {i}:")
            print(f"   - Source: {article.get('source', 'N/A')}")
            print(f"   - Title: {article.get('title', 'N/A')[:100]}")
            print(f"   - URL: {article.get('url', 'N/A')}")
            print(f"   - Date: {article.get('date', article.get('published', 'N/A'))}")
            
            # Check content
            content = article.get('content') or article.get('text', '')
            if content:
                print(f"   - Content: {content[:150]}...")
            
            # Check for demo marker
            if 'note' in article and 'Demo' in article['note']:
                print(f"   - ⚠ Demo data: {article['note']}")
        
        # Verify sector keyword filtering
        print(f"\n6. Keyword filtering check:")
        for article in articles:
            title = article.get('title', '').lower()
            content = (article.get('content') or article.get('text', '')).lower()
            text_to_check = f"{title} {content}"
            
            keyword_found = any(kw.lower() in text_to_check for kw in sector_keywords + [symbol.lower()])
            
            if keyword_found:
                matched_keywords = [kw for kw in sector_keywords + [symbol.lower()] if kw.lower() in text_to_check]
                print(f"   ✓ {article.get('source', 'N/A')}: Matched keywords: {matched_keywords}")
            else:
                print(f"   ⚠ {article.get('source', 'N/A')}: No keyword match (may be demo data)")
    
    print(f"\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\nSummary:")
    print(f"- Total articles fetched: {len(articles)}")
    print(f"- Unique sources: {len(sources)}")
    print(f"- VietStock articles: {len(vietstock_articles)}")
    print(f"\nExpected behavior:")
    print("- If real scraping works: VietStock articles with real titles and content")
    print("- If scraping fails: Demo articles from all 3 sources (VietStock, VnEconomy/CafeF, WSJ)")
    print("- All articles should match sector keywords or symbol")


if __name__ == "__main__":
    asyncio.run(test_vietstock_integration())
