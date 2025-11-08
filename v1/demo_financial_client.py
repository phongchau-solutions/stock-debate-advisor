"""
Demo script using the enhanced FinancialDataClient adapted from zstock patterns.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.financial_data_client import FinancialDataClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_symbol():
    """Test zstock-style single symbol access."""
    print("=== Single Symbol Test (zstock-style) ===")
    
    # Create client for single symbol (like zstock)
    client = FinancialDataClient("VCB")
    
    # zstock-style property access
    print("\n1. Quote History (zstock-style):")
    try:
        history = client.quote.history(start="2024-10-01", end="2024-11-01")
        print(f"✅ Price history: {len(history)} records")
        if not history.empty:
            print(f"   Latest close: {history['close'].iloc[-1]}")
            print(f"   Columns: {list(history.columns)}")
    except Exception as e:
        print(f"❌ Quote error: {e}")
    
    print("\n2. Financial Ratios (zstock-style):")
    try:
        ratios = client.finance.ratios(period="quarterly")
        print(f"✅ Ratios: {len(ratios)} quarters")
        if not ratios.empty:
            print(f"   Available ratios: {list(ratios.columns)}")
            latest = ratios.iloc[-1]
            print(f"   Latest quarter: ROE={latest.get('roe')}, PE={latest.get('pe')}")
    except Exception as e:
        print(f"❌ Finance error: {e}")

def test_multi_symbol():
    """Test multi-symbol portfolio analysis."""
    print("\n\n=== Multi-Symbol Test (Portfolio Analysis) ===")
    
    # Create client for multiple symbols
    symbols = ["VCB", "VNM", "MSN"]
    client = FinancialDataClient(symbols)
    
    print("\n1. Multi-Asset Price Matrix:")
    try:
        close_prices = client.get_close_prices(start="2024-10-01", end="2024-11-01")
        print(f"✅ Price matrix: {close_prices.shape}")
        if not close_prices.empty:
            print(f"   Symbols: {list(close_prices.columns)}")
            print(f"   Latest prices:")
            for symbol in close_prices.columns:
                print(f"     {symbol}: {close_prices[symbol].iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ Multi-price error: {e}")
    
    print("\n2. Comparative Fundamentals:")
    try:
        key_ratios = client.get_key_ratios(period="quarterly")
        for symbol, ratios in key_ratios.items():
            print(f"✅ {symbol} ratios: {len(ratios)} quarters")
            if not ratios.empty:
                latest = ratios.iloc[-1]
                print(f"   ROE: {latest.get('roe')}, PE: {latest.get('pe')}, Revenue: {latest.get('revenue')}")
    except Exception as e:
        print(f"❌ Multi-ratios error: {e}")

def test_market_context():
    """Test market indices for beta calculation."""
    print("\n\n=== Market Context Test (Beta Analysis) ===")
    
    client = FinancialDataClient("VCB")
    
    print("\n1. Market Indices:")
    try:
        indices = client.get_market_indices()
        for idx_name, idx_data in indices.items():
            print(f"✅ {idx_name}: {len(idx_data)} data points")
            if not idx_data.empty:
                print(f"   Latest close: {idx_data['close'].iloc[-1]}")
    except Exception as e:
        print(f"❌ Market indices error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Financial Data Client")
    print("📊 Adapted from successful zstock reference implementation")
    
    test_single_symbol()
    test_multi_symbol() 
    test_market_context()
    
    print("\n✅ Demo completed!")
    print("\n🎯 Ready for:")
    print("   - Technical analysis (RSI, MACD, Bollinger Bands)")
    print("   - Fundamental analysis (P/E, ROE, growth rates)")
    print("   - Portfolio optimization and risk analysis")
    print("   - Multi-asset correlation and beta calculation")