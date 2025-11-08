"""
Streamlit Frontend for Autogen Multi-Agent Financial Debate POC
"""
import streamlit as st
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import orchestrators and streaming components
from simple_orchestrator import SimpleDebateOrchestrator as DebateOrchestrator
from streaming_orchestrator import StreamingDebateOrchestrator
from streaming_conversation import create_streaming_debate_ui


# Page configuration
st.set_page_config(
    page_title="Autogen Financial Debate POC",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    .technical-agent {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .fundamental-agent {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .sentiment-agent {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    
    .coordinator {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    
    .decision-card {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .buy-decision {
        background-color: #e8f5e8;
        border: 2px solid #4caf50;
    }
    
    .sell-decision {
        background-color: #ffebee;
        border: 2px solid #f44336;
    }
    
    .hold-decision {
        background-color: #fff3e0;
        border: 2px solid #ff9800;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Autogen Multi-Agent Financial Debate POC</h1>
        <p>Vietnamese Stock Market Investment Decisioning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key"
        )
        
        # Stock symbol input
        stock_symbol = st.text_input(
            "Stock Symbol",
            value="VNM",
            help="Enter Vietnamese stock symbol (e.g., VNM, VIC, VCB)"
        ).upper()
        
        # Analysis period
        period_options = ["7 days", "15 days", "30 days", "60 days", "90 days"]
        period = st.selectbox("Analysis Period", period_options, index=2)
        
        # Debate configuration
        st.subheader("Debate Settings")
        
        # Debate mode selection
        debate_mode = st.radio(
            "Select Debate Mode:",
            ["🎬 Streaming Live Debate", "📊 Traditional Analysis"],
            index=0,
            help="Streaming mode shows real-time conversation with moderator and judges"
        )
        
        max_rounds = st.slider("Maximum Rounds", 3, 10, 5)
        
        # Start debate button
        if debate_mode == "🎬 Streaming Live Debate":
            start_debate = st.button(
                "🎬 Start Live Streaming Debate",
                type="primary",
                disabled=not gemini_api_key,
                use_container_width=True
            )
        else:
            start_debate = st.button(
                "🚀 Start Traditional Debate",
                type="primary",
                disabled=not gemini_api_key,
                use_container_width=True
            )
    
    # Main content area
    if not gemini_api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to begin.")
        
        # Show demo information
        st.info("""
        **About this POC:**
        
        This demonstration showcases Microsoft Autogen orchestrating a multi-agent debate for Vietnamese stock analysis:
        
        - 🔧 **Technical Agent**: Analyzes price trends, volume, and technical indicators
        - 📊 **Fundamental Agent**: Evaluates financial ratios, earnings, and valuation
        - 📰 **Sentiment Agent**: Analyzes news sentiment from VnEconomy and WSJ
        
        The agents debate for multiple rounds and reach a consensus on BUY/HOLD/SELL recommendations.
        """)
        return
    
    # Initialize session state
    if 'debate_results' not in st.session_state:
        st.session_state.debate_results = None
    if 'debate_in_progress' not in st.session_state:
        st.session_state.debate_in_progress = False
    
    # Initialize streaming mode state
    if 'streaming_mode' not in st.session_state:
        st.session_state.streaming_mode = False
    
    # Start debate
    if start_debate and not st.session_state.debate_in_progress:
        st.session_state.debate_in_progress = True
        st.session_state.debate_results = None
        st.session_state.streaming_mode = (debate_mode == "🎬 Streaming Live Debate")
        
        if st.session_state.streaming_mode:
            # Streaming debate mode
            st.header("🎬 Live Streaming Debate")
            
            # Create streaming container
            streaming_container = st.empty()
            
            try:
                with st.spinner("🚀 Initializing streaming debate system..."):
                    debate_results = run_streaming_debate(
                        gemini_api_key, stock_symbol, period, streaming_container
                    )
                    st.session_state.debate_results = debate_results
                    st.session_state.debate_in_progress = False
                    st.rerun()
            except Exception as e:
                st.error(f"Error during streaming debate: {str(e)}")
                st.session_state.debate_in_progress = False
        else:
            # Traditional debate mode
            with st.spinner("Initializing agents and starting debate..."):
                try:
                    debate_results = run_debate(
                        gemini_api_key, stock_symbol, period, max_rounds
                    )
                    st.session_state.debate_results = debate_results
                    st.session_state.debate_in_progress = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during debate: {str(e)}")
                    st.session_state.debate_in_progress = False
    
    # Display debate results
    if st.session_state.debate_results:
        display_debate_results(st.session_state.debate_results)
    
    # Show current status
    if st.session_state.debate_in_progress:
        st.info("🔄 Debate in progress... Please wait for completion.")


def run_debate(gemini_api_key: str, stock_symbol: str, period: str, max_rounds: int) -> Dict[str, Any]:
    """Run the multi-agent debate."""
    
    # Progress tracking
    progress_container = st.container()
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()
    
    def update_progress(message: str):
        status_text.text(message)
    
    try:
        # Initialize orchestrator
        orchestrator = DebateOrchestrator(
            gemini_api_key=gemini_api_key,
            max_rounds=max_rounds,
            update_callback=update_progress
        )
        
        # Run the debate (we need to handle async in Streamlit)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                orchestrator.conduct_debate(stock_symbol, period)
            )
        finally:
            loop.close()
        
        progress_bar.progress(100)
        status_text.text("✅ Debate completed successfully!")
        
        return results
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text(f"❌ Error: {str(e)}")
        raise


def display_debate_results(results: Dict[str, Any]):
    """Display the debate results in a structured format."""
    
    stock_symbol = results.get('stock_symbol', 'Unknown')
    period = results.get('analysis_period', 'Unknown')
    
    st.header(f"📊 Debate Results for {stock_symbol}")
    st.caption(f"Analysis Period: {period} | Completed: {results.get('timestamp', 'Unknown')}")
    
    # Final Decision Section
    final_decision = results.get('final_decision', {})
    display_final_decision(final_decision)
    
    # Individual Analyses
    st.header("🔍 Individual Agent Analyses")
    individual_analyses = results.get('individual_analyses', {})
    display_individual_analyses(individual_analyses)
    
    # Debate Transcript
    st.header("💬 Debate Transcript")
    debate_transcript = results.get('debate_transcript', [])
    display_debate_transcript(debate_transcript)
    
    # Summary Metrics
    st.header("📈 Analysis Summary")
    display_summary_metrics(results)
    
    # Download option
    st.header("💾 Export Results")
    display_download_options(results, stock_symbol)


def display_final_decision(final_decision: Dict[str, Any]):
    """Display the final investment decision."""
    
    action = final_decision.get('action', 'HOLD')
    confidence = final_decision.get('confidence', 0.5)
    target_price = final_decision.get('target_price', 0)
    
    # Decision card styling based on action
    card_class = {
        'BUY': 'buy-decision',
        'SELL': 'sell-decision',
        'HOLD': 'hold-decision'
    }.get(action, 'hold-decision')
    
    st.markdown(f"""
    <div class="decision-card {card_class}">
        <h2>🎯 Final Recommendation: {action}</h2>
        <h3>Confidence: {confidence:.1%}</h3>
        {f'<h4>Target Price: {target_price:,.0f} VND</h4>' if target_price > 0 else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Rationale
    rationale = final_decision.get('rationale', 'No rationale provided')
    st.subheader("📝 Decision Rationale")
    st.write(rationale)
    
    # Key factors and risks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Key Factors")
        key_factors = final_decision.get('key_factors', [])
        for factor in key_factors:
            st.write(f"• {factor}")
    
    with col2:
        st.subheader("⚠️ Risk Assessment")
        risk_level = final_decision.get('risk_assessment', 'MEDIUM')
        risk_color = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red'
        }.get(risk_level, 'orange')
        st.markdown(f"**Risk Level: <span style='color: {risk_color}'>{risk_level}</span>**", unsafe_allow_html=True)


def display_individual_analyses(individual_analyses: Dict[str, Any]):
    """Display individual agent analyses."""
    
    # Create tabs for each agent
    tech_analysis = individual_analyses.get('technical', {})
    fund_analysis = individual_analyses.get('fundamental', {})
    sent_analysis = individual_analyses.get('sentiment', {})
    
    tab1, tab2, tab3 = st.tabs(["🔧 Technical", "📊 Fundamental", "📰 Sentiment"])
    
    with tab1:
        display_technical_analysis(tech_analysis)
    
    with tab2:
        display_fundamental_analysis(fund_analysis)
    
    with tab3:
        display_sentiment_analysis(sent_analysis)


def display_technical_analysis(analysis: Dict[str, Any]):
    """Display technical analysis results."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        signal = analysis.get('signal', 'neutral')
        confidence = analysis.get('confidence', 0.5)
        st.metric("Signal", signal.upper(), f"Confidence: {confidence:.1%}")
    
    with col2:
        current_price = analysis.get('current_price', 0)
        target_price = analysis.get('target_price', 0)
        if current_price > 0:
            st.metric("Current Price", f"{current_price:,.0f} VND")
            if target_price > 0:
                change = ((target_price / current_price) - 1) * 100
                st.metric("Target Price", f"{target_price:,.0f} VND", f"{change:+.1f}%")
    
    with col3:
        price_change = analysis.get('price_change_pct', 0)
        st.metric("Price Change", f"{price_change:+.1f}%")
    
    # Technical indicators
    indicators = analysis.get('key_indicators', {})
    if indicators:
        st.subheader("Technical Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = indicators.get('rsi', 50)
            st.metric("RSI", f"{rsi:.1f}")
        
        with col2:
            trend = indicators.get('trend', 'sideways')
            st.metric("Trend", trend.title())
        
        with col3:
            macd = indicators.get('macd_signal', 'neutral')
            st.metric("MACD", macd.title())
        
        with col4:
            volume = indicators.get('volume_trend', 'stable')
            st.metric("Volume", volume.title())


def display_fundamental_analysis(analysis: Dict[str, Any]):
    """Display fundamental analysis results."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        valuation = analysis.get('valuation', 'fairly_valued')
        bias = analysis.get('bias', 'hold')
        st.metric("Valuation", valuation.replace('_', ' ').title())
        st.metric("Recommendation", bias.upper())
    
    with col2:
        confidence = analysis.get('confidence', 0.5)
        fair_value = analysis.get('fair_value', 0)
        st.metric("Confidence", f"{confidence:.1%}")
        if fair_value > 0:
            st.metric("Fair Value", f"{fair_value:,.0f} VND")
    
    with col3:
        company_profile = analysis.get('company_profile', {})
        company_name = company_profile.get('name', 'Unknown')
        sector = company_profile.get('sector', 'Unknown')
        st.metric("Company", company_name[:20] + "..." if len(company_name) > 20 else company_name)
        st.metric("Sector", sector)
    
    # Financial metrics
    metrics = analysis.get('key_metrics', {})
    if metrics:
        st.subheader("Key Financial Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pe_ratio = metrics.get('pe_ratio')
            if pe_ratio:
                st.metric("P/E Ratio", f"{pe_ratio:.1f}")
        
        with col2:
            pb_ratio = metrics.get('pb_ratio')
            if pb_ratio:
                st.metric("P/B Ratio", f"{pb_ratio:.1f}")
        
        with col3:
            roe = metrics.get('roe')
            if roe:
                st.metric("ROE", f"{roe:.1f}%")
        
        with col4:
            debt_equity = metrics.get('debt_to_equity')
            if debt_equity:
                st.metric("D/E Ratio", f"{debt_equity:.2f}")
    
    # Risk factors
    risk_factors = analysis.get('risk_factors', [])
    if risk_factors:
        st.subheader("Risk Factors")
        for risk in risk_factors[:3]:  # Show top 3 risks
            st.write(f"⚠️ {risk}")


def display_sentiment_analysis(analysis: Dict[str, Any]):
    """Display sentiment analysis results."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment = analysis.get('sentiment', 'neutral')
        sentiment_score = analysis.get('sentiment_score', 0)
        st.metric("Sentiment", sentiment.title())
        st.metric("Score", f"{sentiment_score:+.2f}")
    
    with col2:
        confidence = analysis.get('confidence', 0.5)
        news_impact = analysis.get('news_impact', 'low')
        st.metric("Confidence", f"{confidence:.1%}")
        st.metric("News Impact", news_impact.upper())
    
    with col3:
        articles_analyzed = analysis.get('articles_analyzed', 0)
        st.metric("Articles Analyzed", articles_analyzed)
    
    # Key themes
    key_themes = analysis.get('key_themes', [])
    if key_themes:
        st.subheader("Key Themes")
        theme_cols = st.columns(len(key_themes))
        for i, theme in enumerate(key_themes):
            with theme_cols[i]:
                st.write(f"🏷️ {theme.replace('_', ' ').title()}")
    
    # News sources
    sources = analysis.get('sources', [])
    if sources:
        st.subheader("Recent News")
        for source in sources[:3]:  # Show top 3 sources
            title = source.get('title', 'Unknown')
            source_name = source.get('source', 'Unknown')
            sentiment = source.get('sentiment', 'neutral')
            
            sentiment_emoji = {
                'positive': '📈',
                'negative': '📉',
                'neutral': '➡️'
            }.get(sentiment, '➡️')
            
            st.write(f"{sentiment_emoji} **{title}** ({source_name})")


def display_debate_transcript(transcript: List[Dict[str, Any]]):
    """Display the debate transcript in a conversational format."""
    
    if not transcript:
        st.write("No debate transcript available.")
        return
    
    # Display as a continuous conversation flow
    st.markdown("""
    <style>
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #fafafa;
        margin-bottom: 20px;
    }
    
    .chat-message {
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 15px;
        position: relative;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .technical-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .fundamental-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: auto;
        text-align: left;
    }
    
    .sentiment-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        margin-right: auto;
        text-align: left;
    }
    
    .moderator-message {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #333;
        margin: 0 auto;
        text-align: center;
        max-width: 90%;
    }
    
    .speaker-name {
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    
    .message-content {
        font-size: 1em;
        line-height: 1.5;
        margin-bottom: 8px;
    }
    
    .message-time {
        font-size: 0.75em;
        opacity: 0.7;
        font-style: italic;
    }
    
    .round-header {
        text-align: center;
        color: #666;
        font-weight: bold;
        margin: 25px 0 15px 0;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 20px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    current_round = 0
    for i, message in enumerate(transcript):
        speaker = message.get('speaker', 'Unknown')
        role = message.get('role', 'Unknown')
        content = message.get('message', '')
        round_num = message.get('round', 1)
        timestamp = message.get('timestamp', '')
        
        # Add round headers
        if round_num != current_round:
            current_round = round_num
            round_names = {
                1: "🎯 Opening Statements",
                2: "💬 Cross-Analysis Discussion", 
                3: "🤝 Building Consensus",
                4: "✅ Final Thoughts"
            }
            round_name = round_names.get(round_num, f"Round {round_num}")
            st.markdown(f'<div class="round-header">{round_name}</div>', unsafe_allow_html=True)
        
        # Determine message styling based on speaker
        if 'technical' in speaker.lower():
            message_class = 'technical-message'
            emoji = '📈'
        elif 'fundamental' in speaker.lower():
            message_class = 'fundamental-message'
            emoji = '📊'
        elif 'sentiment' in speaker.lower():
            message_class = 'sentiment-message'
            emoji = '📰'
        else:  # moderator
            message_class = 'moderator-message'
            emoji = '⚖️'
        
        # Format timestamp
        try:
            from datetime import datetime
            time_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = time_obj.strftime('%H:%M')
        except:
            time_str = timestamp[-8:-3] if len(timestamp) > 8 else ''
        
        # Display message in chat format
        st.markdown(f"""
        <div class="chat-message {message_class}">
            <div class="speaker-name">{emoji} {speaker}</div>
            <div class="message-content">{content}</div>
            <div class="message-time">{time_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add small delay effect between messages for better readability
        if i < len(transcript) - 1:
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add summary stats
    total_messages = len(transcript)
    participants = len(set(msg.get('speaker', '') for msg in transcript))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💬 Total Messages", total_messages)
    with col2:
        st.metric("👥 Participants", participants) 
    with col3:
        rounds = len(set(msg.get('round', 1) for msg in transcript))
        st.metric("🔄 Rounds", rounds)


def display_summary_metrics(results: Dict[str, Any]):
    """Display summary metrics of the analysis."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rounds = results.get('total_rounds', 0)
        st.metric("Debate Rounds", total_rounds)
    
    with col2:
        agents_count = results.get('agents_participated', 0)
        st.metric("Agents Participated", agents_count)
    
    with col3:
        final_decision = results.get('final_decision', {})
        confidence = final_decision.get('confidence', 0)
        st.metric("Overall Confidence", f"{confidence:.1%}")
    
    with col4:
        timestamp = results.get('timestamp', '')
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            st.metric("Completed", dt.strftime("%H:%M:%S"))
    
    # Individual agent signals chart
    individual_analyses = results.get('individual_analyses', {})
    if individual_analyses:
        st.subheader("Agent Signal Comparison")
        
        # Prepare data for visualization
        agents = []
        signals = []
        confidences = []
        
        tech_analysis = individual_analyses.get('technical', {})
        if tech_analysis:
            agents.append('Technical')
            signals.append(tech_analysis.get('signal', 'neutral'))
            confidences.append(tech_analysis.get('confidence', 0.5))
        
        fund_analysis = individual_analyses.get('fundamental', {})
        if fund_analysis:
            agents.append('Fundamental')
            signals.append(fund_analysis.get('bias', 'hold'))
            confidences.append(fund_analysis.get('confidence', 0.5))
        
        sent_analysis = individual_analyses.get('sentiment', {})
        if sent_analysis:
            agents.append('Sentiment')
            signals.append(sent_analysis.get('sentiment', 'neutral'))
            confidences.append(sent_analysis.get('confidence', 0.5))
        
        if agents:
            # Create visualization
            fig = go.Figure()
            
            # Map signals to numeric values for visualization
            signal_map = {
                'bullish': 1, 'buy': 1, 'positive': 1,
                'bearish': -1, 'sell': -1, 'negative': -1,
                'neutral': 0, 'hold': 0
            }
            
            signal_values = [signal_map.get(signal, 0) for signal in signals]
            
            fig.add_trace(go.Bar(
                x=agents,
                y=signal_values,
                text=[f"{signal}<br>{conf:.1%}" for signal, conf in zip(signals, confidences)],
                textposition='auto',
                marker_color=['green' if v > 0 else 'red' if v < 0 else 'orange' for v in signal_values]
            ))
            
            fig.update_layout(
                title="Agent Signal Comparison",
                xaxis_title="Agents",
                yaxis_title="Signal Strength",
                yaxis=dict(range=[-1.2, 1.2]),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)


def display_download_options(results: Dict[str, Any], stock_symbol: str):
    """Display download options for the results."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        json_data = json.dumps(results, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download JSON Results",
            data=json_data,
            file_name=f"{stock_symbol}_debate_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Text transcript export
        transcript_text = generate_text_transcript(results)
        st.download_button(
            label="📝 Download Text Transcript",
            data=transcript_text,
            file_name=f"{stock_symbol}_debate_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def generate_text_transcript(results: Dict[str, Any]) -> str:
    """Generate a text version of the debate transcript."""
    
    stock_symbol = results.get('stock_symbol', 'Unknown')
    period = results.get('analysis_period', 'Unknown')
    timestamp = results.get('timestamp', 'Unknown')
    
    transcript = f"""
AUTOGEN MULTI-AGENT FINANCIAL DEBATE TRANSCRIPT
==============================================

Stock Symbol: {stock_symbol}
Analysis Period: {period}
Completed: {timestamp}

FINAL DECISION
==============
"""
    
    final_decision = results.get('final_decision', {})
    transcript += f"""
Action: {final_decision.get('action', 'HOLD')}
Confidence: {final_decision.get('confidence', 0.5):.1%}
Target Price: {final_decision.get('target_price', 0):,.0f} VND
Risk Assessment: {final_decision.get('risk_assessment', 'MEDIUM')}

Rationale:
{final_decision.get('rationale', 'No rationale provided')}

DEBATE TRANSCRIPT
================
"""
    
    debate_transcript = results.get('debate_transcript', [])
    current_round = 0
    
    for message in debate_transcript:
        round_num = message.get('round', 1)
        if round_num != current_round:
            transcript += f"\n--- ROUND {round_num} ---\n"
            current_round = round_num
        
        speaker = message.get('speaker', 'Unknown')
        role = message.get('role', 'Unknown')
        content = message.get('message', '')
        timestamp = message.get('timestamp', '')
        
        transcript += f"\n{speaker} ({role}) - {timestamp}:\n{content}\n"
    
    transcript += f"""

INDIVIDUAL ANALYSES SUMMARY
===========================

Technical Analysis:
- Signal: {results.get('individual_analyses', {}).get('technical', {}).get('signal', 'N/A')}
- Confidence: {results.get('individual_analyses', {}).get('technical', {}).get('confidence', 0):.1%}

Fundamental Analysis:
- Bias: {results.get('individual_analyses', {}).get('fundamental', {}).get('bias', 'N/A')}
- Valuation: {results.get('individual_analyses', {}).get('fundamental', {}).get('valuation', 'N/A')}
- Confidence: {results.get('individual_analyses', {}).get('fundamental', {}).get('confidence', 0):.1%}

Sentiment Analysis:
- Sentiment: {results.get('individual_analyses', {}).get('sentiment', {}).get('sentiment', 'N/A')}
- Score: {results.get('individual_analyses', {}).get('sentiment', {}).get('sentiment_score', 0):+.2f}
- Confidence: {results.get('individual_analyses', {}).get('sentiment', {}).get('confidence', 0):.1%}

=== END OF TRANSCRIPT ===
"""
    
    return transcript


def run_streaming_debate(
    gemini_api_key: str,
    stock_symbol: str, 
    period: str,
    container
) -> Dict[str, Any]:
    """Run streaming debate with moderator and judges."""
    
    async def async_streaming_debate():
        """Async wrapper for streaming debate."""
        try:
            # Initialize streaming orchestrator
            streaming_orchestrator = StreamingDebateOrchestrator(
                gemini_api_key=gemini_api_key
            )
            
            # Conduct streaming debate
            results = await streaming_orchestrator.conduct_streaming_debate(
                stock_symbol=stock_symbol,
                period=period,
                stock_data={},
                container=container
            )
            
            return results
            
        except Exception as e:
            st.error(f"Error in streaming debate: {e}")
            return {
                "error": str(e),
                "stock_symbol": stock_symbol,
                "period": period,
                "timestamp": datetime.now().isoformat()
            }
    
    # Run the async debate
    return asyncio.run(async_streaming_debate())


if __name__ == "__main__":
    main()