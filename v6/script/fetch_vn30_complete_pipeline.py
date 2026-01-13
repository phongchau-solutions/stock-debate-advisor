#!/usr/bin/env python3
"""
Complete VN30 Data Pipeline Script
Fetches financial reports, stock prices, company info, and news for all VN30 stocks
Saves results to JSON and database
"""
import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vn30_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# VN30 Stocks
VN30_SYMBOLS = [
    'ACB.VN', 'BCM.VN', 'BID.VN', 'BVH.VN', 'CTG.VN',
    'FPT.VN', 'GAS.VN', 'GVR.VN', 'HDB.VN', 'HPG.VN',
    'KDH.VN', 'MBB.VN', 'MSN.VN', 'MWG.VN', 'NVL.VN',
    'PDR.VN', 'PLX.VN', 'POW.VN', 'SAB.VN', 'SHB.VN',
    'SSB.VN', 'SSI.VN', 'STB.VN', 'TCB.VN', 'TPB.VN',
    'VCB.VN', 'VHM.VN', 'VIB.VN', 'VIC.VN', 'VJC.VN'
]


def init_database():
    """Initialize database tables."""
    try:
        from app.db.database import engine
        from app.db import models
        
        logger.info("Initializing database tables...")
        # Create all tables (ignores if they already exist)
        models.Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        return True
    except Exception as e:
        # Ignore "already exists" errors - they're harmless
        if "already exists" in str(e):
            logger.info("✓ Database tables already exist")
            return True
        logger.error(f"Error initializing database: {e}")
        return False


def get_db_session():
    """Get database session."""
    from app.db.database import SessionLocal
    return SessionLocal()


def fetch_vn30_data(include_news: bool = True, max_workers: int = 3) -> Dict[str, Any]:
    """
    Fetch all data for VN30 stocks (dual storage: database + file store).
    
    Args:
        include_news: Whether to fetch news articles
        max_workers: Number of concurrent workers
    
    Returns:
        Summary of fetch operation
    """
    from app.storage.dual_storage_service import DualStorageService
    
    logger.info("=" * 80)
    logger.info(f"Starting VN30 Data Pipeline (Dual Storage: DB + File Store)")
    logger.info(f"Symbols: {len(VN30_SYMBOLS)}")
    logger.info(f"Include News: {include_news}")
    logger.info(f"Max Workers: {max_workers}")
    logger.info("=" * 80)
    
    db = get_db_session()
    service = DualStorageService(db_session=db, data_store_path="./data_store")
    
    try:
        # Fetch all data (stores in both database and file store)
        batch_results = service.fetch_all_data_batch(
            VN30_SYMBOLS,
            max_workers=max_workers,
            include_news=include_news
        )
        
        return batch_results
    
    finally:
        db.close()


def print_summary(results: Dict[str, Any]) -> None:
    """Print summary of fetch operation."""
    logger.info("\n" + "=" * 80)
    logger.info("VN30 DATA PIPELINE SUMMARY")
    logger.info("=" * 80)
    
    total = results.get('total_symbols', 0)
    successful = results.get('successful', 0)
    failed = results.get('failed', 0)
    
    logger.info(f"Total Symbols: {total}")
    logger.info(f"Successful: {successful} ({successful/total*100:.1f}%)" if total > 0 else "Successful: 0")
    logger.info(f"Failed: {failed}")
    
    # Aggregate statistics
    total_company_info = 0
    total_quarterly = 0
    total_annual = 0
    total_metrics = 0
    total_prices = 0
    total_dividends = 0
    total_news = 0
    
    for symbol, result in results.get('results', {}).items():
        if isinstance(result, dict) and 'error' not in result:
            total_company_info += 1 if result.get('company_info') else 0
            total_quarterly += result.get('quarterly_reports', 0)
            total_annual += result.get('annual_reports', 0)
            total_metrics += 1 if result.get('metrics') else 0
            total_prices += result.get('stock_prices', 0)
            total_dividends += result.get('dividends', 0)
            total_news += result.get('news', 0)
    
    logger.info("\nData Stored:")
    logger.info(f"  Company Info: {total_company_info}")
    logger.info(f"  Quarterly Reports: {total_quarterly}")
    logger.info(f"  Annual Reports: {total_annual}")
    logger.info(f"  Metrics: {total_metrics}")
    logger.info(f"  Stock Prices: {total_prices:,}")
    logger.info(f"  Dividends: {total_dividends}")
    logger.info(f"  News Articles: {total_news}")
    
    # Per-symbol details
    logger.info("\nPer-Symbol Results:")
    for symbol in sorted(results.get('results', {}).keys()):
        result = results['results'][symbol]
        
        if isinstance(result, dict) and 'error' not in result:
            errors = len(result.get('errors', []))
            status = "✓" if not errors else "⚠"
            logger.info(f"  {status} {symbol:8s} | Q:{result.get('quarterly_reports', 0):2d} "
                       f"A:{result.get('annual_reports', 0):2d} "
                       f"P:{result.get('stock_prices', 0):4d} "
                       f"N:{result.get('news', 0):3d}")
            if errors:
                for error in result.get('errors', []):
                    logger.warning(f"      └─ {error}")
        else:
            logger.error(f"  ✗ {symbol:8s} | Error: {result.get('error', 'Unknown error')}")
    
    logger.info("=" * 80)
    logger.info(f"Pipeline completed at {results.get('end_time', datetime.now().isoformat())}")


def save_results_to_json(results: Dict[str, Any], output_dir: str = 'pipeline_results') -> str:
    """Save results to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = output_path / f'vn30_pipeline_{timestamp}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"Results saved to {filepath}")
    return str(filepath)


def test_news_crawler() -> None:
    """Test news crawler on a sample stock."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING NEWS CRAWLER")
    logger.info("=" * 80)
    
    from app.crawlers.news_crawler_v2 import NewsAggregator
    
    aggregator = NewsAggregator()
    
    # Test on a couple of stocks
    test_symbols = ['MBB.VN', 'VCB.VN']
    
    for symbol in test_symbols:
        logger.info(f"\nCrawling news for {symbol}...")
        
        articles_by_source = aggregator.crawl_for_symbol(symbol, days=7)
        
        for source, articles in articles_by_source.items():
            logger.info(f"  {source}: {len(articles)} articles")
            
            # Show top 3 articles
            for i, article in enumerate(articles[:3], 1):
                logger.info(f"    {i}. {article.get('title', 'N/A')[:60]}...")
    
    logger.info("=" * 80)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='VN30 Data Pipeline - Fetch financial and news data'
    )
    parser.add_argument(
        '--no-news',
        action='store_true',
        help='Skip news fetching'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='Number of concurrent workers (default: 3)'
    )
    parser.add_argument(
        '--test-crawler',
        action='store_true',
        help='Test news crawler only'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='pipeline_results',
        help='Output directory for results (default: pipeline_results)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize database
        if not init_database():
            logger.error("Failed to initialize database")
            return 1
        
        # Test crawler if requested
        if args.test_crawler:
            test_news_crawler()
            return 0
        
        # Fetch VN30 data
        results = fetch_vn30_data(
            include_news=not args.no_news,
            max_workers=args.workers
        )
        
        # Print summary
        print_summary(results)
        
        # Save results
        save_results_to_json(results, args.output_dir)
        
        return 0 if results.get('failed', 0) == 0 else 1
    
    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
