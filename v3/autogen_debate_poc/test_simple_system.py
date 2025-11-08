#!/usr/bin/env python3
"""
Test the simplified multi-agent system.
Verifies all components work without running Streamlit.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.stock_data_service import StockDataService

# Import agent classes from simple_app
import importlib.util
spec = importlib.util.spec_from_file_location("simple_app", "simple_app.py")
simple_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simple_app)

TechnicalAgent = simple_app.TechnicalAgent
FundamentalAgent = simple_app.FundamentalAgent
SentimentAgent = simple_app.SentimentAgent
DebateOrchestrator = simple_app.DebateOrchestrator

async def test_system():
    """Test the complete system."""
    print("🧪 Testing Simplified Multi-Agent System")
    print("=" * 60)
    
    # Test 1: Agent initialization
    print("\n1️⃣ Testing Agent Initialization...")
    try:
        tech = TechnicalAgent()
        fund = FundamentalAgent()
        sent = SentimentAgent()
        print(f"   ✅ {tech.name}")
        print(f"   ✅ {fund.name}")
        print(f"   ✅ {sent.name}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Data service
    print("\n2️⃣ Testing Data Service...")
    try:
        service = StockDataService(use_cache=True)
        data = await service.fetch_stock_data('VNM', period_days=30)
        print(f"   ✅ Fetched data for VNM")
        print(f"   ✅ OHLCV days: {len(data.get('ohlcv', []))}")
        print(f"   ✅ News articles: {len(data.get('news', []))}")
        print(f"   ✅ Financials: {bool(data.get('financials'))}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Agent analysis
    print("\n3️⃣ Testing Agent Analysis...")
    try:
        tech_result = tech.analyze('VNM', data)
        print(f"   ✅ Technical: {tech_result['signal']} ({tech_result['confidence']:.0%})")
        
        fund_result = fund.analyze('VNM', data)
        print(f"   ✅ Fundamental: {fund_result['signal']} ({fund_result['confidence']:.0%})")
        
        sent_result = sent.analyze('VNM', data)
        print(f"   ✅ Sentiment: {sent_result['signal']} ({sent_result['confidence']:.0%})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Orchestrator
    print("\n4️⃣ Testing Debate Orchestrator...")
    try:
        orchestrator = DebateOrchestrator()
        print(f"   ✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
        print(f"   ✅ Ready for debate")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n🚀 System ready! Run: streamlit run simple_app.py")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_system())
    sys.exit(0 if result else 1)
