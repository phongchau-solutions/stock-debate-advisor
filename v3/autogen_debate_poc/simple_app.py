"""
SIMPLIFIED MULTI-AGENT STOCK ANALYSIS SYSTEM
============================================

Clean architecture without complex AutoGen dependencies.
Uses direct LLM calls with structured agent roles.
"""

import streamlit as st
import asyncio
from datetime import datetime
import json
from pathlib import Path

# Simple stock data service
from services.stock_data_service import StockDataService

# Technical analysis
import pandas as pd
import numpy as np

class SimpleAgent:
    """Base agent with LLM capabilities (optional)."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    def analyze(self, stock_symbol: str, data: dict) -> dict:
        """Override in subclasses."""
        raise NotImplementedError


class TechnicalAgent(SimpleAgent):
    """Technical analysis using indicators."""
    
    def __init__(self):
        super().__init__("Technical Analyst", "Technical Analysis")
    
    def analyze(self, stock_symbol: str, data: dict) -> dict:
        """Analyze technical indicators."""
        ohlcv = data.get('ohlcv', pd.DataFrame())
        
        if ohlcv.empty or len(ohlcv) < 20:
            return {
                'agent': self.name,
                'signal': 'hold',
                'confidence': 0.3,
                'rationale': f"Insufficient data for {stock_symbol} technical analysis"
            }
        
        # Calculate indicators
        close_prices = pd.to_numeric(ohlcv['close'], errors='coerce')
        
        # RSI
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Moving averages
        ma_5 = close_prices.rolling(5).mean().iloc[-1]
        ma_20 = close_prices.rolling(20).mean().iloc[-1]
        current_price = close_prices.iloc[-1]
        
        # Generate signal
        signal = 'hold'
        confidence = 0.5
        
        if current_rsi < 30 and current_price > ma_5:
            signal = 'buy'
            confidence = 0.75
        elif current_rsi > 70 and current_price < ma_5:
            signal = 'sell'
            confidence = 0.75
        elif ma_5 > ma_20 and current_rsi < 60:
            signal = 'buy'
            confidence = 0.65
        elif ma_5 < ma_20 and current_rsi > 40:
            signal = 'sell'
            confidence = 0.65
        
        return {
            'agent': self.name,
            'signal': signal,
            'confidence': confidence,
            'rationale': f"RSI: {current_rsi:.1f}, MA5: {ma_5:.0f}, MA20: {ma_20:.0f}, Price: {current_price:.0f}. "
                        f"{'Oversold conditions' if current_rsi < 30 else 'Overbought conditions' if current_rsi > 70 else 'Neutral momentum'}.",
            'indicators': {
                'RSI': float(current_rsi),
                'MA5': float(ma_5),
                'MA20': float(ma_20),
                'Price': float(current_price)
            }
        }


class FundamentalAgent(SimpleAgent):
    """Fundamental analysis using financial ratios."""
    
    def __init__(self):
        super().__init__("Fundamental Analyst", "Fundamental Analysis")
    
    def analyze(self, stock_symbol: str, data: dict) -> dict:
        """Analyze financial ratios."""
        financials = data.get('financials', {})
        
        if not financials:
            return {
                'agent': self.name,
                'signal': 'hold',
                'confidence': 0.3,
                'rationale': f"No financial data available for {stock_symbol}"
            }
        
        pe_ratio = financials.get('pe_ratio', 15)
        roe = financials.get('roe', 15)
        pb_ratio = financials.get('pb_ratio', 2.0)
        
        # Simple valuation logic
        signal = 'hold'
        confidence = 0.5
        
        if pe_ratio < 12 and roe > 18:
            signal = 'buy'
            confidence = 0.8
        elif pe_ratio > 20 and roe < 12:
            signal = 'sell'
            confidence = 0.8
        elif pe_ratio < 15 and roe > 15:
            signal = 'buy'
            confidence = 0.65
        elif pe_ratio > 18:
            signal = 'sell'
            confidence = 0.60
        
        return {
            'agent': self.name,
            'signal': signal,
            'confidence': confidence,
            'rationale': f"P/E: {pe_ratio:.1f}, ROE: {roe:.1f}%, P/B: {pb_ratio:.1f}. "
                        f"{'Undervalued with strong fundamentals' if pe_ratio < 12 and roe > 18 else 'Overvalued' if pe_ratio > 20 else 'Fair valuation'}.",
            'metrics': {
                'PE_Ratio': float(pe_ratio),
                'ROE': float(roe),
                'PB_Ratio': float(pb_ratio)
            }
        }


class SentimentAgent(SimpleAgent):
    """News sentiment analysis."""
    
    def __init__(self):
        super().__init__("Sentiment Analyst", "Sentiment Analysis")
    
    def analyze(self, stock_symbol: str, data: dict) -> dict:
        """Analyze news sentiment."""
        news = data.get('news', [])
        
        if not news:
            return {
                'agent': self.name,
                'signal': 'hold',
                'confidence': 0.3,
                'rationale': f"No news data available for {stock_symbol}"
            }
        
        # Simple keyword-based sentiment
        positive_words = ['growth', 'profit', 'increase', 'strong', 'upgrade', 'positive', 'gain', 'success']
        negative_words = ['loss', 'decline', 'decrease', 'weak', 'downgrade', 'negative', 'drop', 'risk']
        
        positive_count = 0
        negative_count = 0
        
        for article in news:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            text = title + ' ' + content
            
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
        
        sentiment_score = (positive_count - negative_count) / max(len(news), 1)
        
        if sentiment_score > 1:
            signal = 'buy'
            confidence = min(0.8, 0.5 + sentiment_score * 0.1)
        elif sentiment_score < -1:
            signal = 'sell'
            confidence = min(0.8, 0.5 + abs(sentiment_score) * 0.1)
        else:
            signal = 'hold'
            confidence = 0.5
        
        return {
            'agent': self.name,
            'signal': signal,
            'confidence': confidence,
            'rationale': f"Analyzed {len(news)} articles. Sentiment score: {sentiment_score:.2f}. "
                        f"{'Positive news sentiment' if sentiment_score > 1 else 'Negative news sentiment' if sentiment_score < -1 else 'Neutral sentiment'}.",
            'stats': {
                'article_count': len(news),
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'sentiment_score': float(sentiment_score)
            }
        }


class DebateOrchestrator:
    """Orchestrates multi-agent debate."""
    
    def __init__(self):
        self.agents = [
            TechnicalAgent(),
            FundamentalAgent(),
            SentimentAgent()
        ]
        self.data_service = StockDataService(use_cache=True)
    
    async def run_debate(self, stock_symbol: str, period_days: int = 30, min_rounds: int = 2):
        """Run multi-agent debate."""
        transcript = []
        
        # Fetch data once
        st.info(f"📊 Fetching data for {stock_symbol}...")
        data = await self.data_service.fetch_stock_data(stock_symbol, period_days)
        
        # Each agent analyzes
        all_analyses = []
        for round_num in range(1, min_rounds + 1):
            st.info(f"🔄 Round {round_num}/{min_rounds}")
            
            for agent in self.agents:
                analysis = agent.analyze(stock_symbol, data)
                analysis['round'] = round_num
                analysis['timestamp'] = datetime.now().isoformat()
                all_analyses.append(analysis)
                transcript.append(analysis)
                
                # Display in UI
                with st.expander(f"💬 {analysis['agent']} - Round {round_num}", expanded=True):
                    st.write(f"**Signal:** {analysis['signal'].upper()}")
                    st.write(f"**Confidence:** {analysis['confidence']:.0%}")
                    st.write(f"**Rationale:** {analysis['rationale']}")
                
                await asyncio.sleep(0.5)  # Dramatic effect
            
            # Check for consensus
            signals = [a['signal'] for a in all_analyses if a['round'] == round_num]
            if len(set(signals)) == 1 and round_num >= min_rounds:
                st.success(f"✅ Consensus reached after round {round_num}!")
                break
        
        # Synthesize consensus
        consensus = self._synthesize(all_analyses)
        transcript.append({
            'agent': 'Moderator',
            'timestamp': datetime.now().isoformat(),
            'consensus': consensus
        })
        
        return {
            'transcript': transcript,
            'consensus': consensus,
            'stock_symbol': stock_symbol
        }
    
    def _synthesize(self, analyses: list) -> dict:
        """Synthesize final recommendation."""
        signals = [a['signal'] for a in analyses]
        confidences = [a['confidence'] for a in analyses]
        
        # Count votes weighted by confidence
        votes = {}
        for signal, confidence in zip(signals, confidences):
            votes[signal] = votes.get(signal, 0) + confidence
        
        final_signal = max(votes, key=votes.get)
        avg_confidence = sum(c for s, c in zip(signals, confidences) if s == final_signal) / max(signals.count(final_signal), 1)
        
        return {
            'decision': final_signal,
            'confidence': avg_confidence,
            'summary': f"Final recommendation: {final_signal.upper()} with {avg_confidence:.0%} confidence. "
                      f"Based on {len(analyses)} agent analyses across {max(a['round'] for a in analyses)} rounds."
        }


# Streamlit UI
st.set_page_config(page_title="Multi-Agent Stock Analysis", page_icon="📈", layout="wide")

st.title("📈 Multi-Agent Stock Analysis System")
st.markdown("*Simplified architecture with Technical, Fundamental, and Sentiment agents*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    stock_symbol = st.text_input("Stock Symbol", value="VNM", help="Vietnamese stock symbol")
    period_days = st.number_input("Analysis Period (days)", min_value=7, max_value=365, value=30)
    min_rounds = st.number_input("Minimum Rounds", min_value=1, max_value=5, value=2)
    
    start_btn = st.button("🚀 Start Analysis", type="primary", use_container_width=True)

# Main area
if start_btn:
    orchestrator = DebateOrchestrator()
    
    with st.spinner("Running multi-agent analysis..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.run_debate(stock_symbol, period_days, min_rounds)
        )
    
    # Display final consensus
    st.markdown("---")
    st.header("🎯 Final Consensus")
    consensus = result['consensus']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Decision", consensus['decision'].upper())
    with col2:
        st.metric("Confidence", f"{consensus['confidence']:.0%}")
    with col3:
        st.metric("Rounds", len(set(a['round'] for a in result['transcript'] if 'round' in a)))
    
    st.info(consensus['summary'])
    
    # Download transcript
    st.download_button(
        "📥 Download Transcript",
        data=json.dumps(result, indent=2),
        file_name=f"{stock_symbol}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

st.markdown("---")
st.caption("Simplified Multi-Agent System | No complex dependencies | Pure Python")
