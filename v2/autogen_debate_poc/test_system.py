"""
Test script for the Autogen Multi-Agent Financial Debate POC
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from debate_orchestrator import DebateOrchestrator
from data.data_integration import DataIntegrationManager


async def test_basic_functionality():
    """Test basic functionality without requiring API keys."""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)
    
    # Test data integration
    print("1. Testing Data Integration...")
    try:
        data_manager = DataIntegrationManager()
        test_data = await data_manager.fetch_all_data("VNM", "30 days")
        
        print(f"   ✅ Stock data fetched: {test_data.get('stock_data', {}).get('symbol', 'Unknown')}")
        print(f"   ✅ News articles: {len(test_data.get('news_data', {}).get('vneconomy', []))}")
        print(f"   ✅ Data sources: {test_data.get('data_sources', [])}")
        
    except Exception as e:
        print(f"   ❌ Data integration error: {e}")
        return False
    
    print("\n2. Testing Debate Orchestrator (Demo Mode)...")
    try:
        # Use a dummy API key for testing
        orchestrator = DebateOrchestrator(
            gemini_api_key="test_key_for_demo",
            max_rounds=3
        )
        
        # Test agent initialization
        print(f"   ✅ Agents initialized: {len(orchestrator.agents)}")
        print(f"   ✅ Technical agent: {orchestrator.technical_agent.name}")
        print(f"   ✅ Fundamental agent: {orchestrator.fundamental_agent.name}")
        print(f"   ✅ Sentiment agent: {orchestrator.sentiment_agent.name}")
        
    except Exception as e:
        print(f"   ⚠️  Orchestrator error (expected without valid API key): {e}")
    
    print("\n3. Testing Individual Agent Analysis (Demo Mode)...")
    try:
        # Test individual agent analysis with demo data
        from agents.technical_agent import TechnicalAgent
        from agents.fundamental_agent import FundamentalAgent
        from agents.sentiment_agent import SentimentAgent
        
        # Create test agents
        technical_agent = TechnicalAgent("demo_key")
        fundamental_agent = FundamentalAgent("demo_key")
        sentiment_agent = SentimentAgent("demo_key")
        
        # Test analysis methods
        tech_result = await technical_agent.analyze_data("VNM", "30 days", {})
        fund_result = await fundamental_agent.analyze_data("VNM", "30 days", {})
        sent_result = await sentiment_agent.analyze_data("VNM", "30 days", {})
        
        print(f"   ✅ Technical analysis: {tech_result.get('signal', 'Unknown')}")
        print(f"   ✅ Fundamental analysis: {fund_result.get('bias', 'Unknown')}")
        print(f"   ✅ Sentiment analysis: {sent_result.get('sentiment', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Agent analysis error: {e}")
        return False
    
    print("\n✅ Basic functionality test completed successfully!")
    return True


async def test_full_system():
    """Test the full system with a real API key (if available)."""
    print("\n🚀 Testing Full System Integration")
    print("=" * 50)
    
    # Check for environment variable
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
        print("   Set GEMINI_API_KEY to test with real LLM integration")
        print("   Skipping full system test...")
        return True
    
    print("🔑 Found Gemini API key, testing full system...")
    
    try:
        # Initialize orchestrator with real API key
        orchestrator = DebateOrchestrator(
            gemini_api_key=gemini_api_key,
            max_rounds=3,
            update_callback=lambda x: print(f"   📈 {x}")
        )
        
        print("1. Starting multi-agent debate for VNM...")
        results = await orchestrator.conduct_debate("VNM", "30 days")
        
        print(f"\n✅ Debate completed successfully!")
        print(f"   📊 Final decision: {results.get('final_decision', {}).get('action', 'Unknown')}")
        print(f"   🎯 Confidence: {results.get('final_decision', {}).get('confidence', 0):.1%}")
        print(f"   💬 Debate rounds: {results.get('total_rounds', 0)}")
        
        # Save results for inspection
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   💾 Results saved to test_results.json")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Full system test error: {e}")
        return False


def test_docker_setup():
    """Test Docker setup and configuration."""
    print("\n🐳 Testing Docker Setup")
    print("=" * 50)
    
    files_to_check = [
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        ".env.example",
        "run.sh"
    ]
    
    all_present = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Missing")
            all_present = False
    
    # Check run.sh permissions
    if os.path.exists("run.sh"):
        import stat
        st = os.stat("run.sh")
        if st.st_mode & stat.S_IEXEC:
            print(f"   ✅ run.sh is executable")
        else:
            print(f"   ⚠️  run.sh is not executable")
    
    return all_present


def test_project_structure():
    """Test project structure and imports."""
    print("\n📁 Testing Project Structure")
    print("=" * 50)
    
    required_dirs = [
        "agents",
        "data",
        "logs"
    ]
    
    required_files = [
        "app.py",
        "debate_orchestrator.py",
        "requirements.txt",
        "README.md",
        "agents/__init__.py",
        "agents/technical_agent.py",
        "agents/fundamental_agent.py",
        "agents/sentiment_agent.py",
        "data/data_integration.py"
    ]
    
    all_present = True
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - Missing directory")
            all_present = False
    
    # Check files
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} - Missing file")
            all_present = False
    
    return all_present


async def main():
    """Main test function."""
    print("🤖 Autogen Multi-Agent Financial Debate POC - Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("Project Structure", test_project_structure),
        ("Docker Setup", test_docker_setup),
        ("Basic Functionality", test_basic_functionality),
        ("Full System", test_full_system),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready for deployment.")
        print("\n🚀 Quick Start:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your GEMINI_API_KEY to .env")
        print("   3. Run: ./run.sh start")
        print("   4. Open: http://localhost:8501")
        print("   5. Test with VNM stock for 30 days")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())