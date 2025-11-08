#!/usr/bin/env python3
"""
Direct test of Vietcap API via zstock library.
Tests the exact usage pattern from /ref/zstock examples.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add ref/zstock to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'ref' / 'zstock'))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("DIRECT VIETCAP API TEST via zstock")
print("=" * 80)

try:
    from zstock.core import ZStock
    print("\n✓ zstock library imported successfully")
except ImportError as e:
    print(f"\n✗ Failed to import zstock: {e}")
    print("Installing zstock from ref/zstock...")
    import subprocess
    zstock_path = Path(__file__).parent.parent.parent / 'ref' / 'zstock'
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(zstock_path)], check=True)
    from zstock.core import ZStock
    print("✓ zstock installed and imported")

# Test symbol
symbol = 'VNM'

print(f"\n{'='*80}")
print(f"TEST 1: Initialize ZStock for {symbol}")
print(f"{'='*80}")

try:
    # Use CORRECT API: symbols (plural), not symbol (singular)
    # Even for single symbol, use symbols parameter
    stock = ZStock(symbols=symbol, source='VIETCAP')
    print(f"✓ ZStock initialized: {stock}")
    print(f"  - Symbols: {stock.symbols}")
    print(f"  - Source: {stock.source}")
    
    # For single symbol, access via dictionaries
    print(f"\nAccessing single symbol data via dictionaries:")
    print(f"  - quotes: {list(stock.quotes.keys())}")
    print(f"  - companies: {list(stock.companies.keys())}")
    print(f"  - finances: {list(stock.finances.keys())}")
except Exception as e:
    print(f"✗ Failed to initialize ZStock: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'='*80}")
print(f"TEST 2: Fetch Company Overview")
print(f"{'='*80}")

try:
    # Access company data for specific symbol via dictionary
    company_overview = stock.companies[symbol].overview()
    print(f"✓ Company overview fetched for {symbol}")
    print(f"\nCompany Overview Data:")
    for key, value in company_overview.items():
        print(f"  - {key}: {value}")
except Exception as e:
    print(f"✗ Failed to fetch company overview: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print(f"TEST 3: Fetch Historical OHLCV Data")
print(f"{'='*80}")

try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Use quotes dictionary for specific symbol
    ohlc = stock.quotes[symbol].history(
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval='ONE_DAY'
    )
    
    print(f"✓ OHLCV data fetched")
    print(f"\nData shape: {ohlc.shape}")
    print(f"Columns: {list(ohlc.columns)}")
    print(f"\nFirst 5 rows:")
    print(ohlc.head())
    print(f"\nLast 5 rows:")
    print(ohlc.tail())
    
    # Get current price
    if not ohlc.empty:
        current_price = ohlc['close'].iloc[-1]
        current_volume = ohlc['volume'].iloc[-1]
        print(f"\nCurrent metrics:")
        print(f"  - Price: {current_price:,.0f} VND")
        print(f"  - Volume: {current_volume:,.0f} shares")
        
except Exception as e:
    print(f"✗ Failed to fetch OHLCV data: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print(f"TEST 4: Fetch Financial Ratios")
print(f"{'='*80}")

try:
    # Get ratio definitions - use finances dictionary
    ratio_defs = stock.finances[symbol].get_ratio_definitions(lang='en')
    print(f"✓ Available ratios: {len(ratio_defs)} ratios")
    print(f"\nSample ratios:")
    for i, (code, name) in enumerate(list(ratio_defs.items())[:10]):
        print(f"  - {code}: {name}")
    
    # Get specific ratios
    print(f"\nFetching key financial ratios...")
    key_ratios = ['pe', 'pb', 'roe', 'eps', 'dividend_yield', 'revenue', 'netProfit']
    
    for ratio in key_ratios:
        try:
            ratio_data = stock.finances[symbol].get_specific_fields([ratio], period='annual', lang='en')
            print(f"  - {ratio}: {ratio_data}")
        except Exception as e:
            print(f"  - {ratio}: Failed - {e}")
            
except Exception as e:
    print(f"✗ Failed to fetch financial ratios: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print(f"TEST 5: Balance Sheet")
print(f"{'='*80}")

try:
    balance_sheet = stock.finances[symbol].balance_sheet(period='annual', lang='en')
    print(f"✓ Balance sheet fetched")
    print(f"\nBalance sheet shape: {balance_sheet.shape}")
    print(f"\nBalance sheet columns: {list(balance_sheet.columns)[:20]}")
    print(f"\nBalance sheet sample:")
    print(balance_sheet.head())
except Exception as e:
    print(f"✗ Failed to fetch balance sheet: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print(f"TEST 6: List All Symbols")
print(f"{'='*80}")

try:
    all_symbols = stock.listing.all_symbols()
    print(f"✓ All symbols fetched: {len(all_symbols)} symbols")
    print(f"\nSample symbols (first 20):")
    print(all_symbols[:20])
except Exception as e:
    print(f"✗ Failed to fetch all symbols: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print(f"SUMMARY")
print(f"{'='*80}")
print(f"""
Key Findings:
1. ZStock initialization: Check if successful
2. Company overview: Check if returns data or 403
3. Historical OHLCV: Check if returns price data
4. Financial ratios: Check available metrics
5. Balance sheet: Check detailed financials
6. Symbols listing: Check API accessibility

Next Steps Based on Results:
- If 403 errors: Vietcap API is blocking requests (need VPN/auth)
- If successful: Update vietcap_service.py to match working pattern
- If partial success: Use working endpoints, fallback for blocked ones
""")
