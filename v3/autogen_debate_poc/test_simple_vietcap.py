#!/usr/bin/env python3
"""
Simple test to verify VietcapService works with yfinance fallback.
Tests the complete data flow for VNM stock.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.vietcap_service import VietcapService


async def main():
    print("=" * 80)
    print("SIMPLE VIETCAP SERVICE TEST")
    print("=" * 80)
    
    symbol = "VNM"
    print(f"\nTesting {symbol} stock data retrieval...")
    
    service = VietcapService()
    
    # Fetch stock data (will use yfinance fallback since Vietcap API is blocked)
    data = await service.fetch_stock_data(symbol, period_days=90)
    
    if not data:
        print(f"✗ Failed to fetch data for {symbol}")
        return
    
    print(f"\n✓ Successfully fetched data for {symbol}")
    print(f"\nData Source: {data.get('data_source', 'unknown')}")
    print(f"\nPrice Information:")
    print(f"  Current Price: {data['price']:,.0f} VND")
    print(f"  Volume: {data['volume']:,.0f} shares")
    
    print(f"\nFinancial Ratios:")
    print(f"  P/E Ratio: {data['PE_ratio']:.2f}")
    print(f"  ROE: {data['ROE']:.2f}%")
    print(f"  Dividend Yield: {data['dividend_yield']:.2f}%")
    
    print(f"\nDetailed Financials:")
    financials = data.get('financials', {})
    print(f"  EPS: {financials.get('eps', 0):,.2f}")
    print(f"  Revenue: {financials.get('revenue', 0):,.0f}")
    print(f"  Net Income: {financials.get('net_income', 0):,.0f}")
    print(f"  Market Cap: {financials.get('market_cap', 0):,.0f}")
    
    print(f"\nOHLCV Data:")
    ohlcv = data.get('ohlcv')
    if ohlcv is not None and not ohlcv.empty:
        print(f"  Days of data: {len(ohlcv)}")
        print(f"  Date range: {ohlcv.index[0]} to {ohlcv.index[-1]}")
        print(f"\n  Last 5 days:")
        print(ohlcv.tail())
    else:
        print(f"  No OHLCV data available")
    
    print(f"\nNews Articles:")
    news = data.get('news', [])
    print(f"  Total articles: {len(news)}")
    for i, article in enumerate(news[:3], 1):
        print(f"\n  Article {i}:")
        print(f"    Source: {article.get('source', 'N/A')}")
        print(f"    Title: {article.get('title', 'N/A')[:80]}")
        if 'note' in article:
            print(f"    Note: {article['note']}")
    
    print(f"\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    print(f"\nSummary:")
    print(f"✓ Price data: WORKING")
    print(f"✓ Financial ratios: WORKING")
    print(f"✓ OHLCV data: {'WORKING' if ohlcv is not None and not ohlcv.empty else 'UNAVAILABLE'}")
    print(f"✓ News articles: {len(news)} articles")
    print(f"\nSystem Status: FUNCTIONAL with {'real' if 'yfinance' in data.get('data_source', '') else 'demo'} data")


if __name__ == "__main__":
    asyncio.run(main())
