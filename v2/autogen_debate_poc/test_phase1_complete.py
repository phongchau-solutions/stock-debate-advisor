"""
Comprehensive test for Phase 1 - All three agents with standardized analyze() methods
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent


async def test_technical_agent():
    """Test technical agent with standardized analyze() method."""
    print("\n" + "="*80)
    print("Testing Technical Agent")
    print("="*80)
    
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY", "demo_key")
        
        # Initialize agent
        agent = TechnicalAgent(gemini_api_key=api_key)
        print(f"✓ Technical agent initialized: {agent.name}")
        
        # Test analyze method
        print("\nAnalyzing VNM (Vinamilk)...")
        result = await agent.analyze(stock_symbol="VNM", period="3mo")
        
        # Validate result structure
        assert "analysis_type" in result, "Missing analysis_type"
        assert result["analysis_type"] == "technical", "Wrong analysis_type"
        assert "stock_symbol" in result, "Missing stock_symbol"
        assert "timestamp" in result, "Missing timestamp"
        assert "signal" in result, "Missing signal"
        assert "confidence" in result, "Missing confidence"
        assert "indicators" in result, "Missing indicators"
        assert "rationale" in result, "Missing rationale"
        
        print(f"✓ Analysis completed successfully")
        print(f"  Signal: {result['signal']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Price: {result.get('current_price', 'N/A')}")
        
        # Check indicators
        indicators = result.get("indicators", {})
        print(f"\n  Technical Indicators:")
        print(f"    RSI: {indicators.get('rsi', 'N/A')}")
        print(f"    MACD Signal: {indicators.get('macd', {}).get('signal', 'N/A')}")
        print(f"    Bollinger Position: {indicators.get('bollinger_bands', {}).get('position', 'N/A')}")
        
        print(f"\n  Rationale (first 200 chars):")
        print(f"    {result['rationale'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Technical agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_fundamental_agent():
    """Test fundamental agent with standardized analyze() method."""
    print("\n" + "="*80)
    print("Testing Fundamental Agent")
    print("="*80)
    
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY", "demo_key")
        
        # Initialize agent
        agent = FundamentalAgent(gemini_api_key=api_key)
        print(f"✓ Fundamental agent initialized: {agent.name}")
        
        # Test analyze method
        print("\nAnalyzing VCB (Vietcombank)...")
        result = await agent.analyze(stock_symbol="VCB", period="3mo")
        
        # Validate result structure
        assert "analysis_type" in result, "Missing analysis_type"
        assert result["analysis_type"] == "fundamental", "Wrong analysis_type"
        assert "stock_symbol" in result, "Missing stock_symbol"
        assert "valuation" in result, "Missing valuation"
        assert "fair_value" in result, "Missing fair_value"
        assert "bias" in result, "Missing bias"
        assert "confidence" in result, "Missing confidence"
        assert "key_metrics" in result, "Missing key_metrics"
        assert "rationale" in result, "Missing rationale"
        assert "risk_factors" in result, "Missing risk_factors"
        
        print(f"✓ Analysis completed successfully")
        print(f"  Valuation: {result['valuation']}")
        print(f"  Fair Value: {result['fair_value']:,.0f} VND")
        print(f"  Bias: {result['bias']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        
        # Check metrics
        metrics = result.get("key_metrics", {})
        print(f"\n  Key Financial Metrics:")
        print(f"    P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
        print(f"    ROE: {metrics.get('roe', 'N/A')}%")
        print(f"    Debt/Equity: {metrics.get('debt_to_equity', 'N/A')}")
        
        # Check risk factors
        risks = result.get("risk_factors", [])
        print(f"\n  Risk Factors ({len(risks)} identified):")
        for i, risk in enumerate(risks[:3], 1):
            print(f"    {i}. {risk}")
        
        return True
        
    except Exception as e:
        print(f"✗ Fundamental agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_sentiment_agent():
    """Test sentiment agent with standardized analyze() method."""
    print("\n" + "="*80)
    print("Testing Sentiment Agent")
    print("="*80)
    
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY", "demo_key")
        
        # Initialize agent
        agent = SentimentAgent(gemini_api_key=api_key)
        print(f"✓ Sentiment agent initialized: {agent.name}")
        
        # Test analyze method
        print("\nAnalyzing VIC (Vingroup)...")
        result = await agent.analyze(stock_symbol="VIC", period="3mo")
        
        # Validate result structure
        assert "analysis_type" in result, "Missing analysis_type"
        assert result["analysis_type"] == "sentiment", "Wrong analysis_type"
        assert "stock_symbol" in result, "Missing stock_symbol"
        assert "sentiment_score" in result, "Missing sentiment_score"
        assert "sentiment_label" in result, "Missing sentiment_label"
        assert "bias" in result, "Missing bias"
        assert "confidence" in result, "Missing confidence"
        assert "news_analysis" in result, "Missing news_analysis"
        assert "key_themes" in result, "Missing key_themes"
        assert "rationale" in result, "Missing rationale"
        
        print(f"✓ Analysis completed successfully")
        print(f"  Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.2f})")
        print(f"  Bias: {result['bias']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        
        # Check news analysis
        news = result.get("news_analysis", {})
        print(f"\n  News Analysis:")
        print(f"    Total Articles: {news.get('total_articles', 0)}")
        print(f"    Positive: {news.get('positive_count', 0)}")
        print(f"    Neutral: {news.get('neutral_count', 0)}")
        print(f"    Negative: {news.get('negative_count', 0)}")
        
        # Check key themes
        themes = result.get("key_themes", [])
        print(f"\n  Key Themes ({len(themes)} identified):")
        for i, theme in enumerate(themes[:3], 1):
            print(f"    {i}. {theme}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sentiment agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_agents_parallel():
    """Test all three agents in parallel."""
    print("\n" + "="*80)
    print("Testing All Agents in Parallel")
    print("="*80)
    
    try:
        api_key = os.getenv("GEMINI_API_KEY", "demo_key")
        
        # Initialize all agents
        technical = TechnicalAgent(gemini_api_key=api_key)
        fundamental = FundamentalAgent(gemini_api_key=api_key)
        sentiment = SentimentAgent(gemini_api_key=api_key)
        
        print("✓ All agents initialized")
        
        # Run all analyses in parallel
        print("\nRunning parallel analysis for HPG (Hoa Phat Group)...")
        results = await asyncio.gather(
            technical.analyze("HPG", "3mo"),
            fundamental.analyze("HPG", "3mo"),
            sentiment.analyze("HPG", "3mo"),
            return_exceptions=True
        )
        
        # Check results
        success_count = 0
        for i, (agent_name, result) in enumerate(zip(
            ["Technical", "Fundamental", "Sentiment"], results
        )):
            if isinstance(result, Exception):
                print(f"✗ {agent_name} failed: {str(result)}")
            else:
                print(f"✓ {agent_name} completed: {result.get('analysis_type', 'unknown')}")
                success_count += 1
        
        print(f"\n✓ Parallel test completed: {success_count}/3 agents successful")
        return success_count == 3
        
    except Exception as e:
        print(f"✗ Parallel test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all Phase 1 tests."""
    print("\n" + "="*80)
    print("PHASE 1 AGENT TESTING - Comprehensive Validation")
    print("="*80)
    
    results = {
        "technical": False,
        "fundamental": False,
        "sentiment": False,
        "parallel": False
    }
    
    # Test each agent individually
    results["technical"] = await test_technical_agent()
    await asyncio.sleep(1)  # Brief pause between tests
    
    results["fundamental"] = await test_fundamental_agent()
    await asyncio.sleep(1)
    
    results["sentiment"] = await test_sentiment_agent()
    await asyncio.sleep(1)
    
    # Test all agents in parallel
    results["parallel"] = await test_all_agents_parallel()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name.capitalize()} Agent Test")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 Phase 1 Complete! All agents working correctly.")
        print("Ready to proceed to Phase 2: Debate Engine Stabilization")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
