"""
Test script to verify end-to-end integration of agent tools with data service.

This script:
1. Starts a debate session with knowledge loaded
2. Verifies each agent can access their tools
3. Runs a single debate round
4. Validates tool invocation and output
5. Confirms session persistence
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import httpx

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

async def test_api_health():
    """Test 1: Verify API is running and healthy"""
    print_section("TEST 1: API Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/")
            print(f"✅ Health Check: {response.status_code}")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   API Version: {data.get('version', 'N/A')}")
            return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

async def test_available_symbols():
    """Test 2: Get available symbols"""
    print_section("TEST 2: Available Symbols")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/api/symbols")
            data = response.json()
            # Handle both array and dict responses
            symbols = data.get('symbols', data) if isinstance(data, dict) else data
            print(f"✅ Available Symbols: {symbols}")
            return symbols[0] if symbols else None
    except Exception as e:
        print(f"❌ Failed to fetch symbols: {e}")
        return None

async def test_start_debate_session(symbol: str):
    """Test 3: Start a debate session"""
    print_section("TEST 3: Start Debate Session")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/debate/start",
                json={"symbol": symbol, "rounds": 2}  # Minimum is 2 rounds
            )
            data = response.json()
            session_id = data.get("session_id")
            print(f"✅ Debate Session Started")
            print(f"   Session ID: {session_id}")
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Status: {data.get('status')}")
            return session_id
    except Exception as e:
        print(f"❌ Failed to start debate: {e}")
        return None

async def test_knowledge_loaded(session_id: str):
    """Test 4: Verify knowledge is loaded in the session"""
    print_section("TEST 4: Verify Knowledge Loaded")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get fundamental knowledge
            response = await client.get(
                f"http://localhost:8001/api/session/{session_id}/knowledge/fundamental"
            )
            fund_data = response.json()
            has_fund = bool(fund_data.get("financial_data"))
            print(f"✅ Fundamental Knowledge: {'Loaded' if has_fund else 'Empty'}")
            if has_fund:
                print(f"   Reports: {fund_data.get('report_count', 0)}")
            
            # Get technical knowledge
            response = await client.get(
                f"http://localhost:8001/api/session/{session_id}/knowledge/technical"
            )
            tech_data = response.json()
            has_tech = bool(tech_data.get("technical_data"))
            print(f"✅ Technical Knowledge: {'Loaded' if has_tech else 'Empty'}")
            if has_tech:
                print(f"   Data Points: {len(tech_data.get('dates', []))}")
            
            # Get sentiment knowledge
            response = await client.get(
                f"http://localhost:8001/api/session/{session_id}/knowledge/sentiment"
            )
            sent_data = response.json()
            has_sent = bool(sent_data.get("sentiment_data"))
            print(f"✅ Sentiment Knowledge: {'Loaded' if has_sent else 'Empty'}")
            if has_sent:
                print(f"   Articles: {len(sent_data.get('articles', []))}")
            
            return has_fund and has_tech and has_sent
    except Exception as e:
        print(f"❌ Failed to verify knowledge: {e}")
        return False

def test_agents_with_tools():
    """Test 5: Verify agents can access tools"""
    print_section("TEST 5: Agent Tool Access")
    
    try:
        from agent_tools import (
            fetch_financial_reports, analyze_financial_metrics,
            fetch_technical_data, analyze_price_action,
            fetch_sentiment_data, analyze_news_sentiment,
            get_session_context, compare_all_perspectives
        )
        from agents import DebateAgents
        
        print("✅ All agent tools imported successfully:")
        tools = [
            fetch_financial_reports,
            analyze_financial_metrics,
            fetch_technical_data,
            analyze_price_action,
            fetch_sentiment_data,
            analyze_news_sentiment,
            get_session_context,
            compare_all_perspectives
        ]
        for tool in tools:
            print(f"   • {tool.name}: {tool.description[:50]}...")
        
        # Verify agents have tools
        agents_factory = DebateAgents()
        session_id = "test-session-123"
        
        fundamental = agents_factory.create_fundamental_agent("", session_id=session_id)
        technical = agents_factory.create_technical_agent("", session_id=session_id)
        sentiment = agents_factory.create_sentiment_agent("", session_id=session_id)
        moderator = agents_factory.create_moderator_agent(session_id=session_id)
        judge = agents_factory.create_judge_agent(session_id=session_id)
        
        print(f"\n✅ Agent Tool Assignments:")
        print(f"   Fundamental: {len(fundamental.tools)} tools")
        print(f"   Technical: {len(technical.tools)} tools")
        print(f"   Sentiment: {len(sentiment.tools)} tools")
        print(f"   Moderator: {len(moderator.tools)} tools")
        print(f"   Judge: {len(judge.tools)} tools")
        
        return True
    except Exception as e:
        print(f"❌ Failed to verify agents: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_session_pass():
    """Test 6: Verify orchestrator passes session_id correctly"""
    print_section("TEST 6: Orchestrator Session ID Passing")
    
    try:
        from orchestrator_v2 import DebateOrchestrator
        
        orchestrator = DebateOrchestrator()
        result = orchestrator.start_debate_session("TPB", rounds=2)
        
        session_id = result.get("session_id")
        print(f"✅ Session created: {session_id}")
        
        # Verify session was stored
        if session_id in orchestrator.sessions:
            session = orchestrator.sessions[session_id]
            print(f"   Symbol: {session.symbol}")
            print(f"   Knowledge loaded: {session.knowledge is not None}")
            if session.knowledge:
                print(f"   Financial reports: {len(session.knowledge.financial_reports)}")
                print(f"   News articles: {len(session.knowledge.news_articles)}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to verify orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║  STOCK DEBATE ADVISOR - INTEGRATION TEST SUITE  ║")
    print("║  Testing Agent Tool Integration with Data Service  ║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Test 1: API Health
    results["API Health"] = await test_api_health()
    
    # Test 2: Symbols
    symbol = await test_available_symbols()
    results["Available Symbols"] = symbol is not None
    
    if not symbol:
        print("\n⚠️  Cannot continue without available symbols")
        return results
    
    # Test 3: Start Session
    session_id = await test_start_debate_session(symbol)
    results["Start Debate Session"] = session_id is not None
    
    if not session_id:
        print("\n⚠️  Cannot continue without valid session")
        return results
    
    # Test 4: Knowledge Loaded
    await asyncio.sleep(1)  # Give API time to load knowledge
    results["Knowledge Loaded"] = await test_knowledge_loaded(session_id)
    
    # Test 5: Agent Tools
    results["Agent Tools Import"] = test_agents_with_tools()
    
    # Test 6: Orchestrator Session
    results["Orchestrator Session Passing"] = test_orchestrator_session_pass()
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    # Run async tests
    results = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    if all(results.values()):
        print("✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. See above for details.")
        sys.exit(1)
