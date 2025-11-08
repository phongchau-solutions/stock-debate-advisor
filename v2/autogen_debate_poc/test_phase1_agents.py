#!/usr/bin/env python3
"""
Test script for Phase 1 agent functionality validation
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent


async def test_agent_analyze_method(agent, agent_name: str, stock_symbol: str = "VNM"):
    """Test an agent's analyze method."""
    print(f"\n{'='*60}")
    print(f"Testing {agent_name} for {stock_symbol}")
    print(f"{'='*60}")
    
    try:
        # Test the standardized analyze method
        start_time = datetime.now()
        result = await agent.analyze(stock_symbol, period="3mo", timeout=20)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        print(f"✅ {agent_name} completed in {duration:.2f} seconds")
        
        # Validate response structure
        required_fields = ["analysis_type", "stock_symbol", "timestamp"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"📊 Analysis Type: {result.get('analysis_type')}")
        print(f"🎯 Stock Symbol: {result.get('stock_symbol')}")
        print(f"⏰ Timestamp: {result.get('timestamp')}")
        
        # Agent-specific validation
        if agent_name == "TechnicalAgent":
            print(f"📈 Signal: {result.get('signal', 'N/A')}")
            print(f"🎯 Target Price: {result.get('target_price', 'N/A')}")
            indicators = result.get('technical_indicators', {})
            print(f"📊 RSI: {indicators.get('rsi', 'N/A')}")
            print(f"📊 MACD Signal: {indicators.get('macd_signal', 'N/A')}")
            
        elif agent_name == "FundamentalAgent":
            print(f"💰 Valuation: {result.get('valuation', 'N/A')}")
            print(f"🎯 Fair Value: {result.get('fair_value', 'N/A')}")
            metrics = result.get('key_metrics', {})
            print(f"📊 P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
            print(f"📊 ROE: {metrics.get('roe', 'N/A')}")
            
        elif agent_name == "SentimentAgent":
            print(f"😊 Sentiment: {result.get('sentiment', 'N/A')}")
            print(f"📊 Sentiment Score: {result.get('sentiment_score', 'N/A')}")
            print(f"📰 Articles Analyzed: {result.get('articles_analyzed', 'N/A')}")
            themes = result.get('key_themes', [])
            print(f"🏷️ Key Themes: {', '.join(themes[:3]) if themes else 'None'}")
        
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
        
        # Show error if present
        if 'error' in result:
            print(f"⚠️ Error: {result['error']}")
        
        # Show rationale snippet
        rationale = result.get('rationale', '')
        if rationale:
            snippet = rationale[:200] + "..." if len(rationale) > 200 else rationale
            print(f"💭 Rationale: {snippet}")
        
        return True
        
    except Exception as e:
        print(f"❌ {agent_name} failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Phase 1 Agent Functionality Tests")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    # Mock API key for testing (agents should handle demo data)
    test_api_key = "test_gemini_api_key_for_demo"
    
    # Initialize agents
    try:
        technical_agent = TechnicalAgent(gemini_api_key=test_api_key)
        fundamental_agent = FundamentalAgent(gemini_api_key=test_api_key)
        sentiment_agent = SentimentAgent(gemini_api_key=test_api_key)
        print("✅ All agents initialized successfully")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Test stocks
    test_stocks = ["VNM", "VIC", "VCB"]
    agents_to_test = [
        (technical_agent, "TechnicalAgent"),
        (fundamental_agent, "FundamentalAgent"),
        (sentiment_agent, "SentimentAgent")
    ]
    
    results = []
    
    # Test each agent with each stock
    for stock in test_stocks:
        print(f"\n🏢 Testing with stock: {stock}")
        stock_results = {}
        
        for agent, agent_name in agents_to_test:
            success = await test_agent_analyze_method(agent, agent_name, stock)
            stock_results[agent_name] = success
            
            # Add delay between tests
            await asyncio.sleep(1)
        
        results.append((stock, stock_results))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(test_stocks) * len(agents_to_test)
    passed_tests = 0
    
    for stock, stock_results in results:
        print(f"\n🏢 {stock}:")
        for agent_name, success in stock_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {agent_name}: {status}")
            if success:
                passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    success_rate = (passed_tests / total_tests) * 100
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Phase 1 validation: SUCCESS! Agents are working correctly.")
    else:
        print("⚠️ Phase 1 validation: NEEDS WORK. Some agents need fixes.")
    
    print(f"\n⏰ Test completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())