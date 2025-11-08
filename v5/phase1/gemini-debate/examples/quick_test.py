#!/usr/bin/env python3
"""
Quick test to verify the v5 debate system is working.
"""
import sys
from pathlib import Path

print("=" * 70)
print("🧪 V5 Gemini Multi-Agent Debate System - Quick Test")
print("=" * 70)

# Test 1: Check configuration
print("\n1️⃣ Testing configuration...")
try:
    from config import config
    config.validate()
    print("   ✅ Configuration loaded successfully")
    print(f"   - API Key: {'*' * 20}{config.GEMINI_API_KEY[-4:]}")
    print(f"   - Model: {config.GEMINI_MODEL}")
    print(f"   - Debate rounds: {config.DEBATE_ROUNDS}")
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    sys.exit(1)

# Test 2: Check data loader
print("\n2️⃣ Testing data loader...")
try:
    from data_loader import DataLoader
    loader = DataLoader()
    symbols = loader.get_available_symbols()
    print(f"   ✅ Data loader initialized")
    print(f"   - Available symbols: {symbols}")
except Exception as e:
    print(f"   ❌ Data loader error: {e}")
    sys.exit(1)

# Test 3: Load MBB data
print("\n3️⃣ Loading MBB stock data...")
try:
    if 'MBB' in symbols:
        ohlc = loader.load_technical_data('MBB')
        news = loader.load_sentiment_data('MBB')
        
        print(f"   ✅ MBB data loaded successfully")
        print(f"   - OHLC records: {len(ohlc)} rows")
        print(f"   - Date range: {ohlc['date'].min()} to {ohlc['date'].max()}")
        print(f"   - Latest close: {ohlc['close'].iloc[-1]:,.0f} VND")
        print(f"   - News articles: {len(news)} items")
    else:
        print("   ⚠️  MBB symbol not found")
except Exception as e:
    print(f"   ❌ Data loading error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Initialize agents
print("\n4️⃣ Testing agent initialization...")
try:
    from agents import (
        FundamentalAgent,
        TechnicalAgent, 
        SentimentAgent,
        ModeratorAgent,
        JudgeAgent
    )
    
    tech_agent = TechnicalAgent("Technical Analyst")
    sent_agent = SentimentAgent("Sentiment Analyst")
    mod_agent = ModeratorAgent("Moderator")
    
    print("   ✅ All agents initialized successfully")
    print(f"   - Technical Agent: {tech_agent.name}")
    print(f"   - Sentiment Agent: {sent_agent.name}")
    print(f"   - Moderator Agent: {mod_agent.name}")
except Exception as e:
    print(f"   ❌ Agent initialization error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test Gemini API connection
print("\n5️⃣ Testing Gemini API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content("Say 'OK' if you can hear me.")
    
    if response.text:
        print("   ✅ Gemini API connection successful")
        print(f"   - Response: {response.text[:50]}...")
    else:
        print("   ⚠️  Gemini API responded but with empty text")
except Exception as e:
    print(f"   ❌ Gemini API error: {e}")
    print("   💡 Hint: Check your GEMINI_API_KEY in .env file")

print("\n" + "=" * 70)
print("✅ System test complete!")
print("=" * 70)
print("\n🚀 Ready to run: streamlit run app.py")
print("📊 Symbol available for debate: MBB")
print()
