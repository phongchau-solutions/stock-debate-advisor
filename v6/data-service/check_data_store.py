#!/usr/bin/env python3
"""
Quick checker script to verify data_store integrity.
Run this anytime to verify all data is present and complete.
"""

import json
from pathlib import Path
from datetime import datetime


def check_data_store():
    """Check data_store integrity."""
    data_store = Path(__file__).parent / "data_store" / "2026"
    
    if not data_store.exists():
        print("❌ data_store/2026 not found")
        return False
    
    stock_dirs = sorted([d for d in data_store.iterdir() if d.is_dir()])
    
    print("\n" + "=" * 80)
    print(f"DATA STORE INTEGRITY CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    results = {
        'total_stocks': len(stock_dirs),
        'complete': 0,
        'missing_reports': [],
        'missing_prices': [],
        'corrupted': []
    }
    
    for stock_dir in stock_dirs:
        symbol = stock_dir.name
        issues = []
        
        # Check financial_reports.json
        reports_file = stock_dir / "financial_reports.json"
        if not reports_file.exists():
            issues.append("no financial_reports.json")
            results['missing_reports'].append(symbol)
        else:
            try:
                with open(reports_file) as f:
                    lines = f.readlines()
                    if len(lines) != 2:
                        issues.append(f"reports has {len(lines)} lines (expected 2)")
            except Exception as e:
                issues.append(f"corrupted reports: {e}")
                results['corrupted'].append(symbol)
        
        # Check ohlc_prices.json
        prices_file = stock_dir / "ohlc_prices.json"
        if not prices_file.exists():
            issues.append("no ohlc_prices.json")
            results['missing_prices'].append(symbol)
        else:
            try:
                with open(prices_file) as f:
                    data = json.load(f)
                    count = len(data.get('prices', []))
                    if count != 249:
                        issues.append(f"prices has {count} records (expected 249)")
            except Exception as e:
                issues.append(f"corrupted prices: {e}")
                results['corrupted'].append(symbol)
        
        if not issues:
            results['complete'] += 1
            print(f"✓ {symbol}")
        else:
            print(f"✗ {symbol}: {', '.join(issues)}")
    
    # Summary
    print(f"\n{'-' * 80}")
    print(f"Total Stocks:      {results['total_stocks']}")
    print(f"Complete:          {results['complete']}/{results['total_stocks']}")
    
    if results['missing_reports']:
        print(f"Missing Reports:   {', '.join(results['missing_reports'])}")
    
    if results['missing_prices']:
        print(f"Missing Prices:    {', '.join(results['missing_prices'])}")
    
    if results['corrupted']:
        print(f"Corrupted Files:   {', '.join(results['corrupted'])}")
    
    success = (results['complete'] == results['total_stocks'] and
               not results['missing_reports'] and
               not results['missing_prices'] and
               not results['corrupted'])
    
    if success:
        print(f"\n✓ ALL CHECKS PASSED!")
    else:
        print(f"\n❌ ISSUES DETECTED - Please run migrate_data.py again")
    
    print("=" * 80 + "\n")
    return success


if __name__ == "__main__":
    exit(0 if check_data_store() else 1)
