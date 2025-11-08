"""
Test script for the Gemini Multi-Agent Stock Debate system.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from data_loader import DataLoader
from agents import FundamentalAgent, TechnicalAgent, SentimentAgent, JudgeAgent
from orchestrator import DebateOrchestrator


def test_configuration():
    """Test configuration loading."""
    print("🧪 Testing Configuration...")
    try:
        print(f"  ✓ GEMINI_API_KEY: {'Set' if config.GEMINI_API_KEY else 'Not set'}")
        print(f"  ✓ GEMINI_MODEL: {config.GEMINI_MODEL}")
        print(f"  ✓ FINANCE_DATA_PATH: {config.FINANCE_DATA_PATH}")
        print(f"  ✓ NEWS_DATA_PATH: {config.NEWS_DATA_PATH}")
        print(f"  ✓ DEBATE_ROUNDS: {config.DEBATE_ROUNDS}")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def test_data_loader():
    """Test data loader functionality."""
    print("\n🧪 Testing Data Loader...")
    try:
        loader = DataLoader(config.FINANCE_DATA_PATH, config.NEWS_DATA_PATH)
        
        # Check for available symbols
        symbols = loader.get_available_symbols()
        print(f"  ✓ Found {len(symbols)} available symbols: {', '.join(symbols[:5])}")
        
        if symbols:
            # Test loading data for first symbol
            test_symbol = symbols[0]
            print(f"\n  Testing data loading for {test_symbol}:")
            
            financial = loader.load_financial_data(test_symbol)
            print(f"    {'✓' if financial else '✗'} Financial data")
            
            technical = loader.load_technical_data(test_symbol)
            print(f"    {'✓' if technical else '✗'} Technical data")
            
            sentiment = loader.load_sentiment_data(test_symbol)
            print(f"    {'✓' if sentiment else '✗'} Sentiment data")
        
        return True
    except Exception as e:
        print(f"  ✗ Data loader error: {e}")
        return False


def test_agents():
    """Test agent initialization."""
    print("\n🧪 Testing Agents...")
    try:
        fundamental = FundamentalAgent()
        print(f"  ✓ Fundamental Agent initialized")
        
        technical = TechnicalAgent()
        print(f"  ✓ Technical Agent initialized")
        
        sentiment = SentimentAgent()
        print(f"  ✓ Sentiment Agent initialized")
        
        judge = JudgeAgent()
        print(f"  ✓ Judge Agent initialized")
        
        return True
    except Exception as e:
        print(f"  ✗ Agent initialization error: {e}")
        return False


def test_orchestrator():
    """Test orchestrator initialization."""
    print("\n🧪 Testing Orchestrator...")
    try:
        orch = DebateOrchestrator()
        print(f"  ✓ Orchestrator initialized")
        
        symbols = orch.get_available_symbols()
        print(f"  ✓ Can retrieve available symbols: {len(symbols)} found")
        
        return True
    except Exception as e:
        print(f"  ✗ Orchestrator error: {e}")
        return False


def test_full_debate():
    """Test running a full debate (requires API key)."""
    print("\n🧪 Testing Full Debate...")
    
    if not config.GEMINI_API_KEY:
        print("  ⚠ Skipping (no API key)")
        return True
    
    try:
        orch = DebateOrchestrator()
        symbols = orch.get_available_symbols()
        
        if not symbols:
            print("  ⚠ No symbols available for testing")
            return True
        
        test_symbol = symbols[0]
        print(f"  Running debate for {test_symbol}...")
        
        result = orch.run_full_debate(test_symbol, "3 months")
        
        print(f"  ✓ Debate completed")
        print(f"    - Symbol: {result['symbol']}")
        print(f"    - Transcript entries: {len(result['transcript'])}")
        print(f"    - Verdict available: {'verdict' in result}")
        
        # Show verdict
        if 'verdict' in result:
            print(f"\n  📊 Final Verdict:")
            print(f"    {result['verdict'][:200]}...")
        
        return True
    except Exception as e:
        print(f"  ✗ Full debate error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Gemini Multi-Agent Stock Debate - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Data Loader", test_data_loader),
        ("Agents", test_agents),
        ("Orchestrator", test_orchestrator),
        ("Full Debate", test_full_debate),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
