"""
Test real news crawler integration
Validates VnEconomy and WSJ crawling with sector-based search
"""
import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from services.news_crawler import NewsCrawler


async def test_news_crawl():
    """Test news crawling for VNM stock with sector keywords"""
    print("=" * 80)
    print("NEWS CRAWLER TEST - SECTOR-BASED SEARCH")
    print("=" * 80)
    
    symbol = "VNM"
    sector_keywords = ['milk', 'dairy', 'food', 'vietnam']
    
    print(f"\n📰 Testing News Crawler for {symbol} (Vinamilk)")
    print(f"   Sector keywords: {sector_keywords}")
    print("=" * 80)
    
    async with NewsCrawler(rate_limit_delay=1.0) as crawler:
        # Show inferred keywords
        inferred = crawler._infer_sector_keywords(symbol)
        print(f"\n🔍 Auto-inferred keywords: {inferred}")
        
        # Fetch with explicit keywords
        print(f"\n⏳ Fetching articles...")
        articles = await crawler.fetch_news(symbol, sector_keywords=sector_keywords, max_articles=8)
        
        print(f"\n✅ Fetched {len(articles)} articles\n")
        print("=" * 80)
        
        if articles:
            # Group by source
            sources = {}
            for article in articles:
                source = article['source']
                if source not in sources:
                    sources[source] = []
                sources[source].append(article)
            
            print(f"ARTICLES BY SOURCE:")
            print("=" * 80)
            
            for source, arts in sources.items():
                print(f"\n📌 {source}: {len(arts)} articles")
                print("-" * 80)
                
                for i, article in enumerate(arts, 1):
                    print(f"\n  [{i}] {article['title'][:100]}")
                    print(f"      URL: {article['url'][:80]}")
                    print(f"      Published: {article['published'][:19]}")
                    if 'language' in article:
                        print(f"      Language: {article['language']}")
                    if 'note' in article:
                        print(f"      ⚠️  Note: {article['note']}")
                    if 'method' in article:
                        print(f"      Method: {article['method']}")
                    
                    # Show preview of text
                    text_preview = article.get('text', '')[:150]
                    if text_preview:
                        print(f"      Preview: {text_preview}...")
            
            print("\n" + "=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            
            validations = []
            validations.append(("Total articles", len(articles) > 0))
            validations.append(("Multiple sources", len(sources) > 1))
            validations.append(("VnEconomy/Vietnamese", any('vn' in s.lower() or 'cafe' in s.lower() for s in sources)))
            validations.append(("International (WSJ)", any('wsj' in s.lower() for s in sources)))
            validations.append(("Real crawling method", any(article.get('method') == 'google_news_proxy' for article in articles)))
            validations.append(("Not all demo", not all('demo' in article.get('source', '').lower() for article in articles)))
            
            for check, passed in validations:
                status = "✅" if passed else "⚠️ "
                print(f"{status} {check}")
            
            passed_count = sum(1 for _, p in validations if p)
            print(f"\nPassed: {passed_count}/{len(validations)} checks")
            
            # Check if real crawling worked
            real_articles = [a for a in articles if 'demo' not in a.get('source', '').lower()]
            demo_articles = [a for a in articles if 'demo' in a.get('source', '').lower()]
            
            if real_articles:
                print(f"\n✅ SUCCESS: {len(real_articles)} real articles crawled!")
                print(f"   Sources: {set(a['source'] for a in real_articles)}")
            
            if demo_articles:
                print(f"\n⚠️  INFO: {len(demo_articles)} demo/fallback articles")
                print(f"   (Real crawling may have encountered rate limits or access restrictions)")
        
        else:
            print("\n⚠️  NO ARTICLES FETCHED")
            print("\nPossible reasons:")
            print("  - VnEconomy or WSJ changed their HTML structure")
            print("  - Network issues or rate limiting")
            print("  - Google News proxy blocked request")
            print("  - WSJ requires subscription (401/403 errors)")
            print("\nThe system will gracefully use demo data as fallback.")
            print("Sentiment agent will still function with available data.")


async def test_multiple_stocks():
    """Test news crawling for multiple Vietnamese stocks"""
    print("\n\n")
    print("=" * 80)
    print("MULTI-STOCK NEWS CRAWLING TEST")
    print("=" * 80)
    
    test_symbols = [
        ("VNM", ['milk', 'dairy', 'food']),
        ("FPT", ['technology', 'IT services', 'software']),
        ("HPG", ['steel', 'manufacturing', 'construction']),
    ]
    
    results = []
    
    async with NewsCrawler(rate_limit_delay=2.0) as crawler:
        for symbol, keywords in test_symbols:
            print(f"\n📰 Fetching news for {symbol} ({', '.join(keywords[:2])})...", end=" ")
            try:
                articles = await crawler.fetch_news(symbol, sector_keywords=keywords, max_articles=4)
                sources = set(a['source'] for a in articles)
                real_count = sum(1 for a in articles if 'demo' not in a.get('source', '').lower())
                
                results.append({
                    'symbol': symbol,
                    'total': len(articles),
                    'real': real_count,
                    'sources': sources
                })
                print(f"✅ {len(articles)} articles ({real_count} real)")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    if results:
        print("\n" + "=" * 80)
        print("SUMMARY TABLE")
        print("=" * 80)
        print(f"{'Symbol':<10} {'Total':>8} {'Real':>8} {'Sources':<40}")
        print("-" * 80)
        for r in results:
            sources_str = ', '.join(list(r['sources'])[:3])
            print(f"{r['symbol']:<10} {r['total']:>8} {r['real']:>8} {sources_str:<40}")
        
        total_articles = sum(r['total'] for r in results)
        total_real = sum(r['real'] for r in results)
        print("-" * 80)
        print(f"{'TOTAL':<10} {total_articles:>8} {total_real:>8}")
        
        if total_real > 0:
            print(f"\n🎉 SUCCESS: Crawled {total_real} real articles across {len(results)} stocks!")
        else:
            print(f"\n⚠️  All articles are demo/fallback data")


async def test_sector_inference():
    """Test automatic sector keyword inference"""
    print("\n\n")
    print("=" * 80)
    print("SECTOR KEYWORD INFERENCE TEST")
    print("=" * 80)
    
    test_symbols = ['VNM', 'VCB', 'HPG', 'FPT', 'UNKNOWN123']
    
    async with NewsCrawler() as crawler:
        print(f"\n{'Symbol':<15} {'Inferred Keywords':<60}")
        print("-" * 80)
        
        for symbol in test_symbols:
            keywords = crawler._infer_sector_keywords(symbol)
            keywords_str = ', '.join(keywords[:5])
            print(f"{symbol:<15} {keywords_str:<60}")


if __name__ == "__main__":
    print("\n🧪 Starting News Crawler Tests...\n")
    
    # Run comprehensive test for VNM
    asyncio.run(test_news_crawl())
    
    # Test multiple stocks
    asyncio.run(test_multiple_stocks())
    
    # Test sector inference
    asyncio.run(test_sector_inference())
    
    print("\n\n✅ All news crawler tests completed!\n")

