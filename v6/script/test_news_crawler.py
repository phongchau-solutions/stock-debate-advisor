#!/usr/bin/env python3
"""
Test script for news crawler
Tests each crawler independently and shows sample results
"""
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_individual_crawlers() -> Dict[str, Dict[str, Any]]:
    """Test each news crawler individually."""
    from app.crawlers.news_crawler_v2 import (
        YahooFinanceNews, CafeFNews, VnEconomyNews, VietStockNews
    )
    
    test_symbol = 'MBB.VN'
    crawlers = [
        YahooFinanceNews(),
        CafeFNews(),
        VnEconomyNews(),
        VietStockNews(),
    ]
    
    results = {}
    
    logger.info("=" * 80)
    logger.info("TESTING INDIVIDUAL CRAWLERS")
    logger.info(f"Test Symbol: {test_symbol}")
    logger.info("=" * 80)
    
    for crawler in crawlers:
        logger.info(f"\n{crawler.name.upper()}")
        logger.info("-" * 40)
        
        try:
            articles = crawler.search_articles(test_symbol, days=7)
            
            logger.info(f"✓ Found {len(articles)} articles")
            results[crawler.name] = {
                'success': True,
                'articles_found': len(articles),
                'sample_articles': []
            }
            
            # Show top 3 articles
            for i, article in enumerate(articles[:3], 1):
                title = article.get('title', 'N/A')
                url = article.get('url', 'N/A')[:60]
                source = article.get('source', 'N/A')
                
                logger.info(f"  {i}. {title[:70]}")
                logger.info(f"     URL: {url}...")
                logger.info(f"     Source: {source}")
                
                results[crawler.name]['sample_articles'].append({
                    'title': title,
                    'url': url,
                })
        
        except Exception as e:
            logger.error(f"✗ Error: {str(e)[:100]}")
            results[crawler.name] = {
                'success': False,
                'error': str(e)
            }
    
    return results


def test_news_aggregator() -> Dict[str, Any]:
    """Test news aggregator."""
    from app.crawlers.news_crawler_v2 import NewsAggregator
    
    logger.info("\n" + "=" * 80)
    logger.info("TESTING NEWS AGGREGATOR")
    logger.info("=" * 80)
    
    aggregator = NewsAggregator()
    test_symbols = ['MBB.VN', 'VCB.VN', 'HPG.VN']
    
    results = {}
    
    for symbol in test_symbols:
        logger.info(f"\nAggregating news for {symbol}...")
        
        try:
            articles_by_source = aggregator.crawl_for_symbol(symbol, days=7)
            
            # Show results per source
            total_articles = 0
            for source, articles in articles_by_source.items():
                logger.info(f"  {source}: {len(articles)} articles")
                total_articles += len(articles)
            
            # Normalize and deduplicate
            normalized = aggregator.normalize_articles(articles_by_source)
            logger.info(f"  Total (deduplicated): {len(normalized)} articles")
            
            results[symbol] = {
                'success': True,
                'total_articles': len(normalized),
                'by_source': {src: len(arts) for src, arts in articles_by_source.items()}
            }
        
        except Exception as e:
            logger.error(f"  ✗ Error: {str(e)}")
            results[symbol] = {
                'success': False,
                'error': str(e)
            }
    
    return results


def test_integrated_service() -> Dict[str, Any]:
    """Test integrated data service."""
    from app.db.database import SessionLocal
    from app.db import models
    from app.services.integrated_data_service import IntegratedDataService
    
    logger.info("\n" + "=" * 80)
    logger.info("TESTING INTEGRATED DATA SERVICE")
    logger.info("=" * 80)
    
    db = SessionLocal()
    service = IntegratedDataService(db)
    
    test_symbol = 'MBB.VN'
    results = {}
    
    try:
        logger.info(f"\nFetching company info for {test_symbol}...")
        company = service.fetch_and_store_company_info(test_symbol)
        if company:
            logger.info(f"✓ Company: {company.name}")
            results['company_info'] = True
        
        logger.info(f"Fetching stock prices for {test_symbol}...")
        price_count = service.fetch_and_store_stock_prices(test_symbol, period='3mo')
        logger.info(f"✓ Stored {price_count} price records")
        results['stock_prices'] = price_count
        
        logger.info(f"Fetching quarterly reports for {test_symbol}...")
        quarterly = service.fetch_and_store_quarterly_reports(test_symbol)
        logger.info(f"✓ Stored {len(quarterly)} quarterly reports")
        results['quarterly_reports'] = len(quarterly)
        
        logger.info(f"Fetching annual reports for {test_symbol}...")
        annual = service.fetch_and_store_annual_reports(test_symbol)
        logger.info(f"✓ Stored {len(annual)} annual reports")
        results['annual_reports'] = len(annual)
        
        logger.info(f"Fetching metrics for {test_symbol}...")
        metrics = service.fetch_and_store_metrics(test_symbol)
        if metrics:
            logger.info(f"✓ Stored metrics")
            results['metrics'] = True
        
        logger.info(f"Fetching dividends for {test_symbol}...")
        div_count = service.fetch_and_store_dividends(test_symbol)
        logger.info(f"✓ Stored {div_count} dividend records")
        results['dividends'] = div_count
        
        logger.info(f"Fetching news for {test_symbol}...")
        news_count = service.fetch_and_store_news(test_symbol, days=7)
        logger.info(f"✓ Stored {news_count} news articles")
        results['news'] = news_count
    
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
    
    finally:
        db.close()
    
    return results


def print_test_summary(crawler_results: Dict, aggregator_results: Dict, 
                       service_results: Dict) -> None:
    """Print test summary."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    logger.info("\nIndividual Crawlers:")
    for crawler, result in crawler_results.items():
        status = "✓" if result.get('success') else "✗"
        if result.get('success'):
            logger.info(f"  {status} {crawler:20s} - {result.get('articles_found', 0)} articles")
        else:
            logger.info(f"  {status} {crawler:20s} - ERROR: {result.get('error', 'Unknown')[:50]}")
    
    logger.info("\nNews Aggregator:")
    for symbol, result in aggregator_results.items():
        status = "✓" if result.get('success') else "✗"
        if result.get('success'):
            logger.info(f"  {status} {symbol:10s} - {result.get('total_articles', 0)} total articles")
        else:
            logger.info(f"  {status} {symbol:10s} - ERROR: {result.get('error', 'Unknown')[:50]}")
    
    logger.info("\nIntegrated Service:")
    for data_type, result in service_results.items():
        if isinstance(result, (int, bool)):
            logger.info(f"  {data_type:20s} - {result}")
    
    logger.info("=" * 80)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test news crawlers and data service')
    parser.add_argument('--crawlers-only', action='store_true', help='Test crawlers only')
    parser.add_argument('--aggregator-only', action='store_true', help='Test aggregator only')
    parser.add_argument('--service-only', action='store_true', help='Test service only')
    
    args = parser.parse_args()
    
    try:
        crawler_results = {}
        aggregator_results = {}
        service_results = {}
        
        if not args.aggregator_only and not args.service_only:
            crawler_results = test_individual_crawlers()
        
        if not args.crawlers_only and not args.service_only:
            aggregator_results = test_news_aggregator()
        
        if not args.crawlers_only and not args.aggregator_only:
            service_results = test_integrated_service()
        
        # Print summary
        if crawler_results or aggregator_results or service_results:
            print_test_summary(crawler_results, aggregator_results, service_results)
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
