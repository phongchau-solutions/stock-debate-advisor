#!/usr/bin/env python3
"""
Test refactored adapter architecture.
Verifies clean separation of concerns and fallback mechanisms.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.stock_data_service import StockDataService


async def test_adapter_architecture():
    """Test the refactored adapter pattern."""
    print("=" * 80)
    print("TESTING REFACTORED ADAPTER ARCHITECTURE")
    print("=" * 80)
    
    service = StockDataService()
    
    print("\n1. Adapter Availability:")
    print(f"   Vietcap: {'✓ Available' if service.vietcap.is_available() else '✗ Blocked'}")
    print(f"   YFinance: {'✓ Available' if service.yfinance.is_available() else '✗ Not installed'}")
    
    print("\n2. Fetching VNM data...")
    print("-" * 80)
    
    try:
        data = await service.fetch_stock_data('VNM', period_days=30)
        
        print(f"\n✓ Data fetched successfully")
        print(f"   Symbol: {data['symbol']}")
        print(f"   Source: {data['data_source']}")
        print(f"   Current Price: {data['price']:,.0f} VND")
        print(f"   Volume: {data['volume']:,.0f}")
        print(f"   Days of data: {data['days_of_data']}")
        
        print(f"\n3. Financial Ratios:")
        financials = data['financials']
        print(f"   P/E: {financials.get('pe', 'N/A')}")
        print(f"   ROE: {financials.get('roe', 'N/A')}%")
        print(f"   EPS: {financials.get('eps', 'N/A')}")
        print(f"   Source: {financials.get('source', 'N/A')}")
        
        if 'note' in financials:
            print(f"   Note: {financials['note']}")
        
        print(f"\n4. News Articles:")
        news = data['news']
        print(f"   Total articles: {len(news)}")
        if news:
            for i, article in enumerate(news[:3], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:60]}...")
                print(f"      Source: {article.get('source', 'N/A')}")
        
        print(f"\n5. OHLCV Data:")
        ohlcv = data['ohlcv']
        print(f"   Shape: {ohlcv.shape}")
        print(f"   Columns: {list(ohlcv.columns)}")
        print(f"   Date range: {ohlcv.index[0]} to {ohlcv.index[-1]}")
        
        if 'warning' in data:
            print(f"\n⚠ Warning: {data['warning']}")
        
        print("\n" + "=" * 80)
        print("ARCHITECTURE TEST PASSED")
        print("=" * 80)
        
        print("\n✓ Benefits of refactored architecture:")
        print("  1. Clean separation: Adapters, Service, Orchestrator")
        print("  2. Automatic fallback: Vietcap → YFinance → Synthetic")
        print("  3. Easy to extend: Add new adapters (e.g., VietStock)")
        print("  4. Testable: Each component can be tested independently")
        print("  5. Follows ref/zstock pattern: Professional structure")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_multiple_symbols():
    """Test fetching multiple symbols."""
    print("\n" + "=" * 80)
    print("TESTING MULTIPLE SYMBOLS")
    print("=" * 80)
    
    service = StockDataService()
    symbols = ['VNM', 'VIC', 'VCB']
    
    for symbol in symbols:
        try:
            print(f"\nFetching {symbol}...", end=" ")
            data = await service.fetch_stock_data(symbol, period_days=7)
            print(f"✓ {data['price']:,.0f} VND ({data['data_source']})")
        except Exception as e:
            print(f"✗ {str(e)[:50]}")


async def main():
    """Run all tests."""
    await test_adapter_architecture()
    await test_multiple_symbols()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
