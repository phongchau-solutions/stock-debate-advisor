#!/usr/bin/env python3
"""Validate and fix the migrated data."""

import json
import os
import shutil
from pathlib import Path
from collections import defaultdict

def fix_news_path():
    """Fix the MBB news data path."""
    source = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026/MBB")
    target = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026/MBB.VN")
    
    if source.exists():
        news_file = source / "news_data.json"
        if news_file.exists():
            shutil.copy2(news_file, target / "news_data.json")
            shutil.rmtree(source)
            print("✓ Fixed MBB news data path")
            return True
    return False

def validate_migration():
    """Validate the entire migration."""
    data_store_dir = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026")
    
    if not data_store_dir.exists():
        print("✗ data_store directory not found")
        return False
    
    stock_dirs = sorted([d for d in data_store_dir.iterdir() if d.is_dir()])
    print(f"\n📊 MIGRATION VALIDATION REPORT")
    print("=" * 70)
    print(f"Total stocks: {len(stock_dirs)}\n")
    
    stats = {
        'stocks_with_financial_reports': 0,
        'stocks_with_prices': 0,
        'stocks_with_news': 0,
        'total_financial_records': 0,
        'total_price_records': 0,
        'errors': []
    }
    
    for stock_dir in stock_dirs:
        symbol = stock_dir.name
        
        # Check financial_reports.json
        financial_file = stock_dir / "financial_reports.json"
        if financial_file.exists():
            try:
                with open(financial_file, 'r') as f:
                    lines = f.readlines()
                    stats['stocks_with_financial_reports'] += 1
                    stats['total_financial_records'] += len(lines)
            except Exception as e:
                stats['errors'].append(f"{symbol}: Error reading financial_reports.json - {e}")
        else:
            stats['errors'].append(f"{symbol}: Missing financial_reports.json")
        
        # Check ohlc_prices.json
        prices_file = stock_dir / "ohlc_prices.json"
        if prices_file.exists():
            try:
                with open(prices_file, 'r') as f:
                    data = json.load(f)
                    prices = data.get('prices', [])
                    stats['stocks_with_prices'] += 1
                    stats['total_price_records'] += len(prices)
            except Exception as e:
                stats['errors'].append(f"{symbol}: Error reading ohlc_prices.json - {e}")
        else:
            stats['errors'].append(f"{symbol}: Missing ohlc_prices.json")
        
        # Check news_data.json
        news_file = stock_dir / "news_data.json"
        if news_file.exists():
            stats['stocks_with_news'] += 1
    
    # Print statistics
    print(f"Stocks with financial reports:  {stats['stocks_with_financial_reports']}/{len(stock_dirs)}")
    print(f"Stocks with OHLC prices:        {stats['stocks_with_prices']}/{len(stock_dirs)}")
    print(f"Stocks with news data:          {stats['stocks_with_news']}/{len(stock_dirs)}")
    print(f"\nTotal financial records:        {stats['total_financial_records']}")
    print(f"Total price records:            {stats['total_price_records']}")
    
    if stats['errors']:
        print(f"\n⚠️  Issues found ({len(stats['errors'])}):")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n✓ All validations passed!")
    
    # Directory structure summary
    print(f"\n📁 Directory Structure:")
    print(f"   data_store/")
    print(f"   └── 2026/")
    print(f"       ├── ACB.VN/")
    print(f"       │   ├── financial_reports.json")
    print(f"       │   ├── ohlc_prices.json")
    print(f"       │   └── [news_data.json - if available]")
    print(f"       ├── BCM.VN/")
    print(f"       │   └── ...")
    print(f"       └── ... ({len(stock_dirs)} stocks total)")
    
    return len(stats['errors']) == 0

if __name__ == "__main__":
    fix_news_path()
    success = validate_migration()
    exit(0 if success else 1)
