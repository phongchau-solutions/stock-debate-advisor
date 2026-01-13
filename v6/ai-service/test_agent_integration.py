#!/usr/bin/env python3
"""
Test script for agent data service integration
Tests that agents can fetch and use data from the data service
"""

import asyncio
import requests
import time
import json
from typing import Dict, Any
import subprocess
import sys

# Colors for output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

API_BASE_URL = "http://localhost:8001"
TIMEOUT = 30


def print_header(msg: str):
    """Print colored header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{msg}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg: str):
    """Print error message"""
    print(f"{RED}❌ {msg}{RESET}")


def print_info(msg: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {msg}{RESET}")


def check_api_running() -> bool:
    """Check if FastAPI server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        print_success("FastAPI server is running")
        return True
    except requests.exceptions.ConnectionError:
        print_error("FastAPI server is not running at http://localhost:8001")
        print_info("Start the server with: python api_server.py")
        return False


def get_available_symbols() -> list:
    """Get available stock symbols"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/symbols", timeout=TIMEOUT)
        response.raise_for_status()
        symbols = response.json()
        print_success(f"Available symbols: {symbols}")
        return symbols
    except Exception as e:
        print_error(f"Failed to get symbols: {str(e)}")
        return []


def start_debate_session(symbol: str) -> str:
    """Start a debate session"""
    try:
        payload = {"symbol": symbol, "rounds": 2}
        response = requests.post(
            f"{API_BASE_URL}/api/debate/start",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        session_id = data.get("session_id")
        print_success(f"Debate session started: {session_id}")
        print(f"  Symbol: {symbol}")
        print(f"  Data loaded: {data.get('data_loaded', {})}")
        return session_id
    except Exception as e:
        print_error(f"Failed to start debate session: {str(e)}")
        return None


def test_fundamental_knowledge(session_id: str) -> bool:
    """Test fetching fundamental knowledge"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/session/{session_id}/knowledge/fundamental",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        knowledge = data.get("knowledge", "")
        
        if knowledge and len(knowledge) > 0:
            print_success("Fundamental knowledge fetched")
            print(f"  Knowledge length: {len(knowledge)} characters")
            print(f"  Preview: {knowledge[:200]}...")
            return True
        else:
            print_error("Fundamental knowledge is empty")
            return False
    except Exception as e:
        print_error(f"Failed to fetch fundamental knowledge: {str(e)}")
        return False


def test_technical_knowledge(session_id: str) -> bool:
    """Test fetching technical knowledge"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/session/{session_id}/knowledge/technical",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        knowledge = data.get("knowledge", "")
        
        if knowledge and len(knowledge) > 0:
            print_success("Technical knowledge fetched")
            print(f"  Knowledge length: {len(knowledge)} characters")
            print(f"  Preview: {knowledge[:200]}...")
            return True
        else:
            print_error("Technical knowledge is empty")
            return False
    except Exception as e:
        print_error(f"Failed to fetch technical knowledge: {str(e)}")
        return False


def test_sentiment_knowledge(session_id: str) -> bool:
    """Test fetching sentiment knowledge"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/session/{session_id}/knowledge/sentiment",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        knowledge = data.get("knowledge", "")
        
        if knowledge and len(knowledge) > 0:
            print_success("Sentiment knowledge fetched")
            print(f"  Knowledge length: {len(knowledge)} characters")
            print(f"  Preview: {knowledge[:200]}...")
            return True
        else:
            print_error("Sentiment knowledge is empty")
            return False
    except Exception as e:
        print_error(f"Failed to fetch sentiment knowledge: {str(e)}")
        return False


def test_agent_tools():
    """Test that agent tools are properly imported"""
    try:
        from agent_tools import (
            fetch_financial_reports, analyze_financial_metrics,
            fetch_technical_data, analyze_price_action,
            fetch_sentiment_data, analyze_news_sentiment,
            get_session_context, compare_all_perspectives,
            AGENT_TOOLS
        )
        
        print_success("Agent tools imported successfully")
        print(f"  Available tools: {len(AGENT_TOOLS)}")
        for tool in AGENT_TOOLS:
            print(f"    - {tool.name}")
        return True
    except Exception as e:
        print_error(f"Failed to import agent tools: {str(e)}")
        return False


def test_agent_creation():
    """Test that agents can be created with tools"""
    try:
        from agents import DebateAgents
        from config import config
        
        agent_factory = DebateAgents()
        
        # Create agents with session_id
        session_id = "test-session-123"
        
        fundamental = agent_factory.create_fundamental_agent(session_id=session_id)
        print_success(f"Fundamental agent created with {len(fundamental.tools)} tools")
        
        technical = agent_factory.create_technical_agent(session_id=session_id)
        print_success(f"Technical agent created with {len(technical.tools)} tools")
        
        sentiment = agent_factory.create_sentiment_agent(session_id=session_id)
        print_success(f"Sentiment agent created with {len(sentiment.tools)} tools")
        
        moderator = agent_factory.create_moderator_agent(session_id=session_id)
        print_success(f"Moderator agent created with {len(moderator.tools)} tools")
        
        judge = agent_factory.create_judge_agent(session_id=session_id)
        print_success(f"Judge agent created with {len(judge.tools)} tools")
        
        return True
    except Exception as e:
        print_error(f"Failed to create agents: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_data_client():
    """Test agent data client"""
    try:
        from agent_data_client import get_agent_data_client
        
        client = get_agent_data_client()
        print_success("Agent data client created")
        
        # Test session info fetch (without needing actual session)
        print_info("Agent data client has methods:")
        methods = [m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m))]
        for method in methods[:8]:
            print(f"    - {method}")
        
        return True
    except Exception as e:
        print_error(f"Failed to create data client: {str(e)}")
        return False


def test_full_integration(symbol: str = "MBB") -> bool:
    """Test full integration: start debate and fetch all knowledge"""
    print_header("FULL INTEGRATION TEST")
    
    # Start debate session
    session_id = start_debate_session(symbol)
    if not session_id:
        return False
    
    print_info("Session created, testing knowledge endpoints...")
    time.sleep(1)
    
    # Test all knowledge endpoints
    results = {
        "fundamental": test_fundamental_knowledge(session_id),
        "technical": test_technical_knowledge(session_id),
        "sentiment": test_sentiment_knowledge(session_id)
    }
    
    # Clean up
    try:
        requests.delete(f"{API_BASE_URL}/api/session/{session_id}", timeout=TIMEOUT)
        print_success("Session cleaned up")
    except:
        pass
    
    return all(results.values())


def main():
    """Run all tests"""
    print_header("AGENT DATA SERVICE INTEGRATION TEST")
    
    results = {}
    
    # Test 1: API running
    print_header("TEST 1: API Server")
    if not check_api_running():
        print_error("Cannot continue without API server")
        return 1
    
    # Test 2: Agent tools
    print_header("TEST 2: Agent Tools")
    results["tools"] = test_agent_tools()
    
    # Test 3: Agent creation
    print_header("TEST 3: Agent Creation")
    results["agents"] = test_agent_creation()
    
    # Test 4: Data client
    print_header("TEST 4: Data Client")
    results["client"] = test_data_client()
    
    # Test 5: Symbols
    print_header("TEST 5: Available Symbols")
    symbols = get_available_symbols()
    results["symbols"] = len(symbols) > 0
    
    if not symbols:
        print_error("No symbols available to test")
        return 1
    
    # Test 6: Full integration
    symbol = symbols[0]
    results["integration"] = test_full_integration(symbol)
    
    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}PASS{RESET}" if passed_test else f"{RED}FAIL{RESET}"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! Agent integration is ready.")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
