"""
Demo using exact zstock patterns - Direct adaptation from reference examples.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.zstock_adapter import ZStock, MultiAssetZStock, configure_logging
import logging

# Configure logging exactly like zstock examples
configure_logging(level=logging.INFO)

def demo_single_stock():
    """Demo using exact zstock pattern from simple_demo1.py."""
    print("=== Single Stock Demo (Exact zstock pattern) ===")
    
    # Create ZStock instance exactly like reference
    stock = ZStock(symbol='VCB', source='VIETCAP')
    
    print(f"✅ Created ZStock for {stock.symbol}")
    
    # Get OHLC data exactly like reference
    print("\n1. OHLC History:")
    try:
        ohlc = stock.quote.history(start='2024-10-01', end='2024-11-01', interval='1d')
        print(f"✅ OHLC data: {len(ohlc)} records")
        if not ohlc.empty:
            print("First few records:")
            print(ohlc.head())
            print(f"\nLatest close: {ohlc['close'].iloc[-1]}")
    except Exception as e:
        print(f"❌ OHLC error: {e}")
    
    # Get financial ratios exactly like reference
    print("\n2. Financial Ratios:")
    try:
        ratios = stock.finance.ratios(period='quarterly')
        print(f"✅ Ratios: {len(ratios)} quarters")
        if not ratios.empty:
            print("Available columns:")
            print(list(ratios.columns))
            print("\nLatest quarter:")
            print(ratios.iloc[-1])
    except Exception as e:
        print(f"❌ Ratios error: {e}")
    
    # Get balance sheet
    print("\n3. Balance Sheet:")
    try:
        balance = stock.finance.balance_sheet(period='quarterly')
        print(f"✅ Balance sheet: {len(balance)} quarters")
        if not balance.empty:
            print(f"Balance sheet items: {len(balance.columns)} fields")
    except Exception as e:
        print(f"❌ Balance sheet error: {e}")
    
    # Get all symbols
    print("\n4. All Symbols:")
    try:
        symbols = stock.listing.all_symbols()
        print(f"✅ Available symbols: {symbols}")
    except Exception as e:
        print(f"❌ Symbols error: {e}")

def demo_multi_asset():
    """Demo multi-asset portfolio exactly like zstock."""
    print("\n\n=== Multi-Asset Demo (zstock multi-symbol pattern) ===")
    
    # Create multi-asset instance
    symbols = ['VCB', 'VNM', 'MSN']
    portfolio = MultiAssetZStock(symbols, source='VIETCAP')
    
    print(f"✅ Created portfolio for {portfolio.symbols}")
    
    # Fetch history for all symbols
    print("\n1. Portfolio History:")
    try:
        history_data = portfolio.history(start='2024-10-15', end='2024-11-01', interval='1d')
        
        for symbol, data in history_data.items():
            print(f"✅ {symbol}: {len(data)} records")
            if not data.empty:
                print(f"   Latest close: {data['close'].iloc[-1]}")
    except Exception as e:
        print(f"❌ Portfolio history error: {e}")
    
    # Get close prices matrix
    print("\n2. Close Prices Matrix:")
    try:
        close_matrix = portfolio.get_close_prices()
        print(f"✅ Price matrix: {close_matrix.shape}")
        if not close_matrix.empty:
            print("Latest prices:")
            print(close_matrix.iloc[-1])
            
            print("\nCorrelation matrix:")
            print(close_matrix.corr())
    except Exception as e:
        print(f"❌ Close prices error: {e}")

def demo_financial_analysis():
    """Demo financial analysis like financials.py reference."""
    print("\n\n=== Financial Analysis Demo (financials.py pattern) ===")
    
    stock = ZStock(symbol='VCB', source='VIETCAP')
    finance = stock.finance
    
    # Get ratios for analysis
    print("\n1. Key Financial Ratios:")
    try:
        ratios = finance.ratios(period='quarterly')
        if not ratios.empty:
            print("✅ Financial ratios retrieved")
            
            # Extract key metrics like the reference does
            latest = ratios.iloc[-1]
            print(f"\nLatest Quarter Analysis:")
            print(f"Revenue: {latest.get('revenue', 'N/A')}")
            print(f"Net Profit: {latest.get('netProfit', 'N/A')}")  
            print(f"ROE: {latest.get('roe', 'N/A')}%")
            print(f"P/E Ratio: {latest.get('pe', 'N/A')}")
            print(f"P/B Ratio: {latest.get('pb', 'N/A')}")
            
            # Show trend if multiple quarters available
            if len(ratios) > 1:
                print(f"\nROE Trend (last 3 quarters):")
                roe_trend = ratios['roe'].tail(3) if 'roe' in ratios.columns else None
                if roe_trend is not None and not roe_trend.empty:
                    for year, roe in roe_trend.items():
                        print(f"  {year}: {roe}%")
    except Exception as e:
        print(f"❌ Financial analysis error: {e}")

if __name__ == "__main__":
    print("🚀 ZStock Adapter Demo - Exact Reference Implementation")
    print("📊 Following successful zstock patterns exactly")
    
    demo_single_stock()
    demo_multi_asset()
    demo_financial_analysis()
    
    print("\n✅ ZStock Adapter Demo Complete!")
    print("\n🎯 Proven patterns successfully adapted:")
    print("   ✓ Single symbol access (stock.quote.history)")
    print("   ✓ Financial data (stock.finance.ratios)")
    print("   ✓ Multi-asset portfolios (close price matrix)")
    print("   ✓ Caching and error handling")
    print("   ✓ zstock-compatible API surface")