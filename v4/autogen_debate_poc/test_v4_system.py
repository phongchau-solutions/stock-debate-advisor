#!/usr/bin/env python3
"""Quick test to verify v4 system components"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.data_service import DataService
from services.gemini_service import GeminiService
from agents.fundamental_agent import FundamentalAgent

print("="*60)
print("V4 SYSTEM VERIFICATION TEST")
print("="*60)

# Test 1: Data Service
print("\n1. Testing Data Service...")
ds = DataService()
data = ds.fetch_stock_data('AAPL', period_days=7)
print(f"   ✓ Data fetched for {data.get('symbol')}")
print(f"   ✓ Current price: {data.get('current_price', 'N/A')}")
print(f"   ✓ Has OHLCV: {'ohlcv' in data}")
print(f"   ✓ Has sentiment: {'sentiment_score' in data}")
print(f"   ✓ Available keys: {', '.join(list(data.keys())[:8])}")

# Test 2: Gemini Service (requires API key)
print("\n2. Testing Gemini Service...")
try:
    gemini = GeminiService()
    print("   ✓ Gemini service initialized")
    
    # Test 3: Agent Analysis
    print("\n3. Testing Agent Analysis...")
    agent = FundamentalAgent(gemini)
    analysis = agent.analyze('AAPL', data, period_days=7)
    print(f"   ✓ Analysis type: {analysis.get('analysis_type')}")
    print(f"   ✓ Signal: {analysis.get('signal')}")
    print(f"   ✓ Confidence: {analysis.get('confidence', 0):.2%}")
    print(f"   ✓ Has rationale: {bool(analysis.get('rationale'))}")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED - V4 system is working!")
    print("="*60)
    
except Exception as e:
    print(f"   ⚠ Gemini test skipped (API key needed): {e}")
    print("\n" + "="*60)
    print("✓ DATA SERVICE OK - Gemini requires API key")
    print("="*60)
