#!/usr/bin/env python3
"""
Test script to verify the debate engine works locally with mock responses.
This allows testing without AWS Bedrock.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.core.engine import DebateEngine
import json

def test_mock_debate():
    """Test debate with mock responses"""
    print("=" * 60)
    print("Testing Stock Debate Advisor - Local Mock Mode")
    print("=" * 60)
    
    # Initialize engine with mock responses
    engine = DebateEngine()
    print("✓ Engine initialized (using mock LLM responses)")
    
    # Run a debate
    ticker = "MBB"
    timeframe = "3 months"
    min_rounds = 1
    max_rounds = 3
    
    print(f"\nRunning debate for {ticker} ({timeframe})...")
    print(f"Min rounds: {min_rounds}, Max rounds: {max_rounds}")
    
    try:
        result = engine.debate(ticker, timeframe, min_rounds, max_rounds)
        
        print("\n" + "=" * 60)
        print("DEBATE RESULTS")
        print("=" * 60)
        print(f"Ticker: {result['ticker']}")
        print(f"Timeframe: {result['timeframe']}")
        print(f"Actual Rounds: {result['actual_rounds']}")
        print(f"Final Recommendation: {result['final_recommendation']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Rationale: {result['rationale'][:200]}...")
        
        print("\n" + "=" * 60)
        print("FULL DEBATE JSON")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        print("\n✓ Debate test successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Debate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_request():
    """Test API request format"""
    print("\n" + "=" * 60)
    print("Testing API Request Format")
    print("=" * 60)
    
    import requests
    
    # Start server with: python -m uvicorn src.handlers.main:app --port 8000
    try:
        print("Testing POST /debate endpoint...")
        response = requests.post(
            "http://localhost:8000/debate",
            json={
                "ticker": "MBB",
                "timeframe": "3 months",
                "min_rounds": 1,
                "max_rounds": 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✓ API request successful")
            print(f"Response: {response.json()['final_recommendation']}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend at http://localhost:8000")
        print("Start the server with:")
        print("  cd v7/ai-service")
        print("  python -m uvicorn src.handlers.main:app --port 8000")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

if __name__ == "__main__":
    # Test mock engine directly
    mock_test_passed = test_mock_debate()
    
    # Try to test API if server is running
    print("\n")
    api_test_passed = test_api_request()
    
    sys.exit(0 if (mock_test_passed or api_test_passed) else 1)
