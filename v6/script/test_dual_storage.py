#!/usr/bin/env python3
"""
Test dual storage system (database + file store).
Fetches data and stores in both locations.
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dual_storage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_data_store():
    """Test the file-based data store."""
    from app.db.database import engine
    from app.db import models
    from app.storage.dual_storage_service import DualStorageService
    
    # Initialize database
    logger.info("Initializing database...")
    models.Base.metadata.create_all(bind=engine)
    
    # Initialize dual storage service
    logger.info("Initializing dual storage service...")
    service = DualStorageService(data_store_path="./data_store")
    
    # Test with a few stocks
    test_symbols = ['MBB.VN', 'VCB.VN', 'HPG.VN']
    
    logger.info("=" * 80)
    logger.info(f"Testing dual storage with {len(test_symbols)} symbols")
    logger.info("=" * 80)
    
    for symbol in test_symbols:
        logger.info(f"\nFetching data for {symbol}...")
        result = service.fetch_all_data_for_symbol(symbol, include_news=False)
        
        logger.info(f"Results for {symbol}:")
        logger.info(f"  Company Info: {result.get('company_info')}")
        logger.info(f"  Metrics: {result.get('metrics')}")
        logger.info(f"  Stock Prices: {result.get('stock_prices')}")
        logger.info(f"  Dividends: {result.get('dividends')}")
    
    # Show storage statistics
    logger.info("\n" + "=" * 80)
    logger.info("STORAGE STATISTICS")
    logger.info("=" * 80)
    
    storage_info = service.get_storage_info()
    
    logger.info(f"\nDatabase: {storage_info['database']['type']}")
    logger.info(f"  Purpose: {storage_info['database']['purpose']}")
    
    file_stats = storage_info['file_store']
    logger.info(f"\nFile Store: {file_stats['base_path']}")
    logger.info(f"  Total files: {file_stats['total_files']}")
    logger.info(f"  Total size: {file_stats['total_size_mb']} MB")
    
    if file_stats['years']:
        logger.info(f"\nOrganization by year:")
        for year, stocks in file_stats['years'].items():
            logger.info(f"  {year}/")
            for symbol, info in stocks.items():
                logger.info(f"    {symbol}/")
                logger.info(f"      Files: {info['files']}, Size: {info['size_mb']} MB")
    
    # Show file structure
    logger.info("\n" + "=" * 80)
    logger.info("FILE STRUCTURE")
    logger.info("=" * 80)
    
    data_store_path = Path("./data_store")
    if data_store_path.exists():
        for year_dir in sorted(data_store_path.iterdir()):
            if year_dir.is_dir():
                logger.info(f"\n{year_dir.name}/")
                for stock_dir in sorted(year_dir.iterdir()):
                    if stock_dir.is_dir():
                        logger.info(f"  {stock_dir.name}/")
                        for file in sorted(stock_dir.glob('*.json')):
                            size_kb = file.stat().st_size / 1024
                            lines = len(file.read_text().strip().split('\n'))
                            logger.info(f"    {file.name:25} ({lines:4} lines, {size_kb:7.2f} KB)")
    
    service.close()
    logger.info("\n✓ Test completed successfully!")


if __name__ == '__main__':
    try:
        test_data_store()
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
