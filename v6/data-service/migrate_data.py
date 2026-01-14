#!/usr/bin/env python3
"""
One-time data migration script for Stock Debate Advisor.

Migrates data from /data (flat structure) to /data_store (year → stock → reports/prices).

Structure:
  /data/financial/{symbol}.json → /data_store/{year}/{symbol}/financial_reports.json
  /data/news/{symbol}.json → /data_store/{year}/{symbol}/news_data.json
  Price data is extracted from financial data → /data_store/{year}/{symbol}/ohlc_prices.json

The script ensures:
1. All financial data is properly migrated
2. Price data is extracted and organized separately
3. News data is organized by symbol and year
4. Data completeness and correctness is verified
5. Directory structure is created as needed
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """Handles data migration from /data to /data_store."""
    
    def __init__(self, source_dir: str, target_dir: str):
        """Initialize migrator with source and target directories."""
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.stats = {
            'financial_files_processed': 0,
            'news_files_processed': 0,
            'stocks_migrated': 0,
            'errors': 0,
            'warnings': 0,
        }
        
    def migrate(self) -> bool:
        """Execute full migration process."""
        logger.info(f"Starting migration from {self.source_dir} to {self.target_dir}")
        
        try:
            # Create target directory
            self.target_dir.mkdir(parents=True, exist_ok=True)
            
            # Get current year
            year = datetime.now().year
            
            # Migrate financial data
            self._migrate_financial_data(year)
            
            # Migrate news data
            self._migrate_news_data(year)
            
            # Validate and report
            self._validate_migration(year)
            self._print_stats()
            
            return True
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _migrate_financial_data(self, year: int) -> None:
        """Migrate financial data from /data/financial to /data_store/{year}/{symbol}."""
        financial_dir = self.source_dir / "financial"
        
        if not financial_dir.exists():
            logger.warning(f"Financial directory not found: {financial_dir}")
            return
        
        logger.info(f"Migrating financial data from {financial_dir}")
        
        for json_file in financial_dir.glob("*.json"):
            try:
                symbol = json_file.stem
                logger.info(f"Processing financial data for {symbol}")
                
                # Read financial data
                with open(json_file, 'r', encoding='utf-8') as f:
                    financial_data = json.load(f)
                
                # Extract prices from financial data
                prices_data = self._extract_prices(financial_data)
                
                # Prepare company info (separate file)
                company_info_data = self._prepare_company_info(financial_data)
                
                # Prepare financial reports (without company_info)
                financial_reports = self._prepare_financial_reports(financial_data)
                
                # Create stock directory
                stock_dir = self.target_dir / str(year) / symbol
                stock_dir.mkdir(parents=True, exist_ok=True)
                
                # Save company info as separate file
                company_info_file = stock_dir / "company_info.json"
                with open(company_info_file, 'w', encoding='utf-8') as f:
                    json.dump(company_info_data, f, indent=2)
                logger.info(f"  → Saved company info to {company_info_file}")
                
                # Save financial reports (quarterly, annual, metrics, dividends, splits)
                reports_file = stock_dir / "financial_reports.json"
                with open(reports_file, 'w', encoding='utf-8') as f:
                    json.dump(financial_reports, f, indent=2)
                logger.info(f"  → Saved financial reports to {reports_file}")
                
                # Save price data
                prices_file = stock_dir / "ohlc_prices.json"
                with open(prices_file, 'w', encoding='utf-8') as f:
                    json.dump(prices_data, f, indent=2)
                logger.info(f"  → Saved OHLC prices to {prices_file}")
                
                self.stats['financial_files_processed'] += 1
                self.stats['stocks_migrated'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                self.stats['errors'] += 1
    
    def _migrate_news_data(self, year: int) -> None:
        """Migrate news data from /data/news to /data_store/{year}/{symbol}."""
        news_dir = self.source_dir / "news"
        
        if not news_dir.exists():
            logger.warning(f"News directory not found: {news_dir}")
            return
        
        logger.info(f"Migrating news data from {news_dir}")
        
        for json_file in news_dir.glob("*.json"):
            try:
                symbol = json_file.stem
                logger.info(f"Processing news data for {symbol}")
                
                # Read news data
                with open(json_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                
                # Create stock directory
                stock_dir = self.target_dir / str(year) / symbol
                stock_dir.mkdir(parents=True, exist_ok=True)
                
                # Save news data
                news_file = stock_dir / "news_data.json"
                with open(news_file, 'w', encoding='utf-8') as f:
                    json.dump(news_data, f, indent=2)
                logger.info(f"  → Saved news data to {news_file}")
                
                self.stats['news_files_processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                self.stats['errors'] += 1
    
    def _extract_prices(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract OHLC prices from financial data."""
        prices_info = {
            'symbol': financial_data.get('symbol', 'UNKNOWN'),
            'timestamp': financial_data.get('timestamp', datetime.now().isoformat()),
            'prices': []
        }
        
        # Extract from prices section
        if 'prices' in financial_data and 'prices' in financial_data['prices']:
            prices_info['prices'] = financial_data['prices']['prices']
            prices_info['period'] = financial_data['prices'].get('period', '1y')
            prices_info['interval'] = financial_data['prices'].get('interval', '1d')
            prices_info['total_records'] = len(prices_info['prices'])
        
        return prices_info
    
    def _prepare_company_info(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and prepare company information as separate JSON object."""
        company_info = {
            'symbol': financial_data.get('symbol', 'UNKNOWN'),
            'timestamp': financial_data.get('timestamp', datetime.now().isoformat()),
        }
        
        # Add company information from 'info' section
        if 'info' in financial_data:
            company_info['info'] = financial_data['info']
        else:
            company_info['info'] = None
        
        return company_info
    
    def _prepare_financial_reports(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare financial reports as a single JSON object (without company_info).
        
        Schema:
        {
            "symbol": "MBB.VN",
            "timestamp": "2026-01-09T18:25:25.904066",
            "quarterly": { ... },          # Quarterly financial data
            "annual": { ... },             # Annual financial data  
            "metrics": { ... },            # Calculated financial metrics
            "dividends": { ... },          # Dividend history
            "splits": { ... }              # Stock split history
        }
        """
        report = {
            'symbol': financial_data.get('symbol', 'UNKNOWN'),
            'timestamp': financial_data.get('timestamp', datetime.now().isoformat()),
        }
        
        # Add quarterly financial data
        if 'quarterly' in financial_data:
            report['quarterly'] = financial_data['quarterly']
        else:
            report['quarterly'] = None
        
        # Add annual financial data
        if 'annual' in financial_data:
            report['annual'] = financial_data['annual']
        else:
            report['annual'] = None
        
        # Add financial metrics
        if 'metrics' in financial_data:
            report['metrics'] = financial_data['metrics']
        else:
            report['metrics'] = None
        
        # Add dividends
        if 'dividends' in financial_data:
            report['dividends'] = financial_data['dividends']
        else:
            report['dividends'] = None
        
        # Add stock splits
        if 'splits' in financial_data:
            report['splits'] = financial_data['splits']
        else:
            report['splits'] = None
        
        return report
    
    def _validate_migration(self, year: int) -> None:
        """Validate the migration was successful."""
        logger.info("Validating migration...")
        
        year_dir = self.target_dir / str(year)
        
        if not year_dir.exists():
            logger.warning(f"Year directory {year_dir} does not exist")
            return
        
        # Check for stock directories
        stock_dirs = [d for d in year_dir.iterdir() if d.is_dir()]
        logger.info(f"Found {len(stock_dirs)} stock directories")
        
        # Validate each stock directory
        for stock_dir in stock_dirs:
            symbol = stock_dir.name
            
            # Check company_info.json
            if not (stock_dir / "company_info.json").exists():
                logger.warning(f"{symbol}: Missing company_info.json")
                self.stats['warnings'] += 1
            else:
                try:
                    with open(stock_dir / "company_info.json", 'r') as f:
                        company_info = json.load(f)
                        if 'info' in company_info and company_info['info']:
                            logger.info(f"{symbol}: company_info.json complete")
                        else:
                            logger.warning(f"{symbol}: company_info.json missing 'info' section")
                            self.stats['warnings'] += 1
                except Exception as e:
                    logger.error(f"{symbol}: Error reading company_info.json: {e}")
                    self.stats['errors'] += 1
            
            # Check financial_reports.json
            if not (stock_dir / "financial_reports.json").exists():
                logger.warning(f"{symbol}: Missing financial_reports.json")
                self.stats['warnings'] += 1
            else:
                try:
                    with open(stock_dir / "financial_reports.json", 'r') as f:
                        reports = json.load(f)
                        # Check that it's a proper JSON object with required keys
                        required_keys = ['symbol', 'timestamp', 'quarterly', 
                                        'annual', 'metrics', 'dividends', 'splits']
                        missing_keys = [k for k in required_keys if k not in reports]
                        if missing_keys:
                            logger.warning(f"{symbol}: financial_reports.json missing keys: {missing_keys}")
                            self.stats['warnings'] += 1
                        else:
                            logger.info(f"{symbol}: financial_reports.json has all required sections")
                except Exception as e:
                    logger.error(f"{symbol}: Error reading financial_reports.json: {e}")
                    self.stats['errors'] += 1
            
            # Check ohlc_prices.json
            if not (stock_dir / "ohlc_prices.json").exists():
                logger.warning(f"{symbol}: Missing ohlc_prices.json")
                self.stats['warnings'] += 1
            else:
                try:
                    with open(stock_dir / "ohlc_prices.json", 'r') as f:
                        prices = json.load(f)
                        count = len(prices.get('prices', []))
                        logger.info(f"{symbol}: ohlc_prices.json has {count} price records")
                except Exception as e:
                    logger.error(f"{symbol}: Error reading ohlc_prices.json: {e}")
                    self.stats['errors'] += 1
            
            # Check news_data.json (optional)
            if (stock_dir / "news_data.json").exists():
                logger.info(f"{symbol}: news_data.json present")
    
    def _print_stats(self) -> None:
        """Print migration statistics."""
        logger.info("=" * 60)
        logger.info("MIGRATION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Financial files processed: {self.stats['financial_files_processed']}")
        logger.info(f"News files processed:      {self.stats['news_files_processed']}")
        logger.info(f"Stocks migrated:           {self.stats['stocks_migrated']}")
        logger.info(f"Errors:                    {self.stats['errors']}")
        logger.info(f"Warnings:                  {self.stats['warnings']}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent
    source_dir = base_dir / "data"
    target_dir = base_dir / "data_store"
    
    migrator = DataMigrator(str(source_dir), str(target_dir))
    success = migrator.migrate()
    
    if success:
        logger.info("Migration completed successfully!")
        return 0
    else:
        logger.error("Migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
