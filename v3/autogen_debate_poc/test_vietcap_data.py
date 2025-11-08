"""
Test Vietcap Financial Data Integration
Validates OHLCV, balance sheet, and financial metrics from real Vietcap API via zstock.
"""
import asyncio
import sys
from pathlib import Path
from pprint import pprint

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from services.vietcap_service import VietcapService


async def test_vietcap_integration():
    """Test comprehensive Vietcap data fetching for VNM"""
    print("=" * 80)
    print("VIETCAP FINANCIAL DATA INTEGRATION TEST")
    print("=" * 80)
    
    service = VietcapService()
    
    # Test symbol
    symbol = "VNM"
    period_days = 90
    
    print(f"\n📊 Fetching data for {symbol} (last {period_days} days)...")
    print("-" * 80)
    
    try:
        stock_data = await service.fetch_stock_data(symbol, period_days)
        
        if not stock_data:
            print("❌ No data returned from VietcapService")
            return
        
        print(f"\n✅ Data successfully fetched!")
        print(f"   Data source: {stock_data.get('data_source', 'unknown')}")
        print()
        
        # 1. Basic Price Data
        print("=" * 80)
        print("1. PRICE DATA")
        print("=" * 80)
        print(f"Symbol:          {stock_data['symbol']}")
        print(f"Current Price:   {stock_data['price']:,.0f} VND")
        print(f"Volume:          {stock_data['volume']:,}")
        print()
        
        # 2. Financial Ratios
        print("=" * 80)
        print("2. FINANCIAL RATIOS")
        print("=" * 80)
        print(f"P/E Ratio:       {stock_data['PE_ratio']:.2f}")
        print(f"ROE:             {stock_data['ROE']:.2f}%")
        print(f"Dividend Yield:  {stock_data['dividend_yield']:.2f}%")
        print()
        
        # 3. OHLCV Historical Data
        print("=" * 80)
        print("3. OHLCV HISTORICAL DATA")
        print("=" * 80)
        ohlcv = stock_data.get('ohlcv')
        if ohlcv is not None and not ohlcv.empty:
            print(f"Data points:     {len(ohlcv)} days")
            print(f"Date range:      {ohlcv.index[0]} to {ohlcv.index[-1]}")
            print(f"\nFirst 3 rows:")
            print(ohlcv.head(3).to_string())
            print(f"\nLast 3 rows:")
            print(ohlcv.tail(3).to_string())
            print(f"\nColumns: {list(ohlcv.columns)}")
        else:
            print("⚠️  No OHLCV data available")
        print()
        
        # 4. Detailed Financials
        print("=" * 80)
        print("4. DETAILED FINANCIAL METRICS")
        print("=" * 80)
        financials = stock_data.get('financials', {})
        if financials:
            print(f"EPS:             {financials.get('eps', 0):,.2f}")
            print(f"P/B Ratio:       {financials.get('pb', 0):.2f}")
            print(f"Revenue:         {financials.get('revenue', 0):,.0f}")
            print(f"Net Income:      {financials.get('net_income', 0):,.0f}")
            print(f"Total Assets:    {financials.get('total_assets', 0):,.0f}")
            print(f"Total Debt:      {financials.get('total_debt', 0):,.0f}")
            print(f"Book Value:      {financials.get('book_value', 0):,.0f}")
            print(f"Market Cap:      {financials.get('market_cap', 0):,.0f}")
            
            # Check if this looks like real data or synthetic
            if financials.get('revenue', 0) > 1_000_000_000:
                print("\n✅ Financial data appears to be REAL (large revenue values)")
            else:
                print("\n⚠️  Financial data may be SYNTHETIC/DEMO")
        else:
            print("❌ No detailed financials available")
        print()
        
        # 5. News Data
        print("=" * 80)
        print("5. NEWS ARTICLES")
        print("=" * 80)
        news = stock_data.get('news', [])
        if news:
            print(f"Articles found:  {len(news)}")
            for i, article in enumerate(news[:3], 1):
                print(f"\n  Article {i}:")
                print(f"    Source:    {article.get('source', 'Unknown')}")
                print(f"    Title:     {article.get('title', 'N/A')[:80]}")
                print(f"    Published: {article.get('published', 'N/A')[:19]}")
                if 'note' in article:
                    print(f"    Note:      {article['note']}")
                if 'method' in article:
                    print(f"    Method:    {article['method']}")
        else:
            print("❌ No news articles fetched")
        print()
        
        # Summary
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        validations = []
        validations.append(("Price data", stock_data.get('price', 0) > 0))
        validations.append(("OHLCV data", ohlcv is not None and not ohlcv.empty if ohlcv is not None else False))
        validations.append(("Financial ratios", stock_data.get('PE_ratio', 0) > 0))
        validations.append(("Detailed financials", bool(financials)))
        validations.append(("News articles", len(news) > 0))
        validations.append(("Real Vietcap source", stock_data.get('data_source') == 'zstock_vietcap'))
        
        for check, passed in validations:
            status = "✅" if passed else "⚠️ "
            print(f"{status} {check}")
        
        passed_count = sum(1 for _, p in validations if p)
        print(f"\nPassed: {passed_count}/{len(validations)} checks")
        
        if stock_data.get('data_source') == 'zstock_vietcap':
            print("\n🎉 SUCCESS: Using REAL Vietcap data via ref/zstock!")
        elif stock_data.get('data_source') == 'fallback':
            print("\n⚠️  WARNING: Using yfinance fallback (zstock not available)")
        else:
            print(f"\n❓ UNKNOWN data source: {stock_data.get('data_source')}")
        
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.close()


async def test_multiple_symbols():
    """Test fetching data for multiple Vietnamese stocks"""
    print("\n\n")
    print("=" * 80)
    print("MULTI-SYMBOL TEST")
    print("=" * 80)
    
    symbols = ["VNM", "VCB", "HPG", "FPT"]
    service = VietcapService()
    
    results = []
    for symbol in symbols:
        print(f"\nFetching {symbol}...", end=" ")
        try:
            data = await service.fetch_stock_data(symbol, period_days=30)
            if data:
                results.append({
                    "symbol": symbol,
                    "price": data.get('price', 0),
                    "pe": data.get('PE_ratio', 0),
                    "source": data.get('data_source', 'unknown'),
                    "news_count": len(data.get('news', []))
                })
                print(f"✅ {data.get('price'):,.0f} VND")
            else:
                print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if results:
        print("\n" + "=" * 80)
        print("SUMMARY TABLE")
        print("=" * 80)
        print(f"{'Symbol':<10} {'Price (VND)':>15} {'P/E':>8} {'News':>6} {'Source':<20}")
        print("-" * 80)
        for r in results:
            print(f"{r['symbol']:<10} {r['price']:>15,.0f} {r['pe']:>8.2f} {r['news_count']:>6} {r['source']:<20}")
    
    await service.close()


if __name__ == "__main__":
    print("\n🧪 Starting Vietcap Financial Data Tests...\n")
    
    # Run comprehensive test for VNM
    asyncio.run(test_vietcap_integration())
    
    # Test multiple symbols
    asyncio.run(test_multiple_symbols())
    
    print("\n\n✅ All tests completed!\n")
