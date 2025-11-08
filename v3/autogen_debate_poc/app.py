"""
Streamlit UI for Autogen Multi-Agent Financial Debate POC.
Enhanced with live debate feed, color-coded agents, and transcript download.

Run: streamlit run app.py
"""
import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path

# Add services to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from services.debate_orchestrator import DebateOrchestrator

# Page config
st.set_page_config(
    page_title="Autogen Multi-Agent Debate POC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agent colors for UI
AGENT_COLORS = {
    "TechnicalAnalyst": "#1f77b4",  # Blue
    "FundamentalAnalyst": "#2ca02c",  # Green
    "SentimentAnalyst": "#ff7f0e",  # Orange
    "Moderator": "#d62728"  # Red
}

def format_agent_message(msg: dict) -> str:
    """Format agent message for display."""
    agent = msg.get("agent", "Unknown")
    round_num = msg.get("round", 0)
    color = AGENT_COLORS.get(agent, "#666666")
    
    if "analysis" in msg:
        analysis = msg["analysis"]
        signal = analysis.get("signal", analysis.get("bias", "N/A"))
        confidence = analysis.get("confidence", 0)
        rationale = analysis.get("rationale", "No rationale provided")
        
        return f"""
<div style="border-left: 4px solid {color}; padding: 10px; margin: 10px 0; background: #f9f9f9;">
    <strong style="color: {color};">Round {round_num} | {agent}</strong><br/>
    <span style="font-size: 0.9em;">Signal: <strong>{signal.upper()}</strong> | Confidence: {confidence:.0%}</span><br/>
    <span style="font-size: 0.85em; color: #555;">{rationale}</span>
</div>
"""
    elif "consensus" in msg:
        consensus = msg["consensus"]
        decision = consensus.get("decision", "N/A")
        conf = consensus.get("confidence", 0)
        summary = consensus.get("summary", "")
        
        return f"""
<div style="border: 3px solid {color}; padding: 15px; margin: 15px 0; background: #fff3cd;">
    <strong style="color: {color}; font-size: 1.2em;">🎯 FINAL DECISION</strong><br/>
    <span style="font-size: 1.1em;"><strong>Recommendation: {decision}</strong></span><br/>
    <span>Confidence: {conf:.0%}</span><br/>
    <span style="font-size: 0.9em; color: #555;">{summary}</span>
</div>
"""
    
    return f"<div>{msg}</div>"

# UI Header
st.title("🤖 Autogen Multi-Agent Financial Debate POC")
st.markdown("**Vietnamese Stock Market Investment Decision System**")
st.markdown("---")

# Sidebar inputs
with st.sidebar:
    st.header("⚙️ Debate Configuration")
    
    stock_symbol = st.text_input(
        "Stock Symbol",
        value="VNM",
        help="Vietnamese stock symbol (e.g., VNM, VIC, VCB)"
    )
    
    period_days = st.slider(
        "Analysis Period (days)",
        min_value=7,
        max_value=90,
        value=30,
        help="Historical data period for analysis"
    )
    
    rounds = st.number_input(
        "Minimum Debate Rounds",
        min_value=1,
        max_value=10,
        value=3,
        help="Minimum number of debate rounds (can end early if consensus reached)"
    )
    
    st.markdown("---")
    
    # LLM Configuration (optional)
    st.subheader("🔧 LLM Settings (Optional)")
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Optional: Provide Gemini API key for real LLM integration"
    )
    
    st.markdown("---")
    start_debate_btn = st.button("🚀 Start Debate", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.caption("Powered by Microsoft Autogen + Google Gemini")

# Main content area
debate_container = st.container()
status_container = st.container()

# Run debate
if start_debate_btn:
    with status_container:
        status_placeholder = st.empty()
        status_placeholder.info(f"🔄 Initializing debate for **{stock_symbol}**...")
    
    # Configure LLM if API key provided
    llm_config = None
    if gemini_api_key:
        llm_config = {
            "config_list": [{
                "model": "gemini-1.5-flash",
                "api_type": "gemini",
                "api_key": gemini_api_key
            }],
            "timeout": 120
        }
    
    # Initialize orchestrator
    orchestrator = DebateOrchestrator(
        rounds=rounds,
        llm_config=llm_config,
        use_cache=True,  # Enable caching for PoC
        cache_max_age_hours=24  # 24-hour cache TTL
    )
    
    # Data summary display (will be updated as debate progresses)
    with debate_container:
        st.subheader("📊 Current Analysis Summary")
        summary_placeholder = st.empty()
        
        # Initialize agent summaries
        agent_summaries = {
            "TechnicalAnalyst": {"signal": "...", "confidence": 0, "key_data": "Analyzing..."},
            "FundamentalAnalyst": {"signal": "...", "confidence": 0, "key_data": "Analyzing..."},
            "SentimentAnalyst": {"signal": "...", "confidence": 0, "key_data": "Analyzing..."}
        }
        
        def update_summary_display():
            """Update the summary cards above debate feed."""
            col1, col2, col3 = summary_placeholder.columns(3)
            
            with col1:
                tech = agent_summaries["TechnicalAnalyst"]
                st.markdown(f"""
<div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #1f77b4;">
    <h4 style="margin: 0; color: #1f77b4;">📈 Technical</h4>
    <p style="margin: 5px 0;"><strong>Signal:</strong> {tech['signal'].upper()}</p>
    <p style="margin: 5px 0;"><strong>Confidence:</strong> {tech['confidence']:.0%}</p>
    <p style="margin: 5px 0; font-size: 0.85em; color: #555;">{tech['key_data']}</p>
</div>
""", unsafe_allow_html=True)
            
            with col2:
                fund = agent_summaries["FundamentalAnalyst"]
                st.markdown(f"""
<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 4px solid #2ca02c;">
    <h4 style="margin: 0; color: #2ca02c;">💼 Fundamental</h4>
    <p style="margin: 5px 0;"><strong>Signal:</strong> {fund['signal'].upper()}</p>
    <p style="margin: 5px 0;"><strong>Confidence:</strong> {fund['confidence']:.0%}</p>
    <p style="margin: 5px 0; font-size: 0.85em; color: #555;">{fund['key_data']}</p>
</div>
""", unsafe_allow_html=True)
            
            with col3:
                sent = agent_summaries["SentimentAnalyst"]
                st.markdown(f"""
<div style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff7f0e;">
    <h4 style="margin: 0; color: #ff7f0e;">📰 Sentiment</h4>
    <p style="margin: 5px 0;"><strong>Signal:</strong> {sent['signal'].upper()}</p>
    <p style="margin: 5px 0;"><strong>Confidence:</strong> {sent['confidence']:.0%}</p>
    <p style="margin: 5px 0; font-size: 0.85em; color: #555;">{sent['key_data']}</p>
</div>
""", unsafe_allow_html=True)
        
        # Initial display
        update_summary_display()
        
        st.markdown("---")
        st.subheader("💬 Live Debate Feed")
        messages_placeholder = st.empty()
        messages_html = []
        
        def on_message(msg: dict):
            """Callback for streaming messages to UI."""
            # Update agent summaries
            agent = msg.get("agent", "Unknown")
            if agent in agent_summaries and "analysis" in msg:
                analysis = msg["analysis"]
                signal = analysis.get("signal", analysis.get("bias", analysis.get("sentiment_label", "N/A")))
                confidence = analysis.get("confidence", 0)
                
                # Extract key data based on agent type
                if agent == "TechnicalAnalyst":
                    indicators = analysis.get("indicators", {})
                    rsi = indicators.get("rsi", "N/A")
                    macd = indicators.get("macd", "N/A")
                    key_data = f"RSI: {rsi}, MACD: {macd}"
                elif agent == "FundamentalAnalyst":
                    ratios = analysis.get("ratios", {})
                    pe = ratios.get("pe", "N/A")
                    roe = ratios.get("roe", "N/A")
                    key_data = f"P/E: {pe}, ROE: {roe}"
                elif agent == "SentimentAnalyst":
                    news_count = len(analysis.get("news_articles", []))
                    sentiment_score = analysis.get("sentiment_score", "N/A")
                    key_data = f"{news_count} articles, Score: {sentiment_score}"
                else:
                    key_data = "N/A"
                
                agent_summaries[agent] = {
                    "signal": signal,
                    "confidence": confidence,
                    "key_data": key_data
                }
                
                # Update summary display
                update_summary_display()
            
            # Add message to debate feed
            messages_html.append(format_agent_message(msg))
            messages_placeholder.markdown("\n".join(messages_html), unsafe_allow_html=True)
        
        # Run debate (async)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                orchestrator.run_debate(
                    stock_symbol=stock_symbol,
                    period_days=period_days,
                    on_message=on_message
                )
            )
            loop.close()
            
            status_placeholder.success(f"✅ Debate completed in {result.get('total_rounds', '?')} rounds!")
            
            # Display final consensus
            st.markdown("---")
            consensus = result.get("consensus", {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Decision", consensus.get("decision", "N/A"))
            with col2:
                st.metric("Confidence", f"{consensus.get('confidence', 0):.0%}")
            with col3:
                st.metric("Rounds", f"{result.get('total_rounds', '?')}/{result.get('max_rounds', '?')}")
            with col4:
                st.metric("Consensus", consensus.get("consensus", "N/A").capitalize())
            
            # Detailed results
            with st.expander("📊 Detailed Analysis"):
                st.json(consensus.get("votes", {}))
                st.write("**Agent Positions:**")
                for pos in consensus.get("agent_positions", []):
                    st.write(f"- {pos.get('agent')}: **{pos.get('position').upper()}** ({pos.get('confidence'):.0%})")
            
            # Transcript download
            transcript_text = "\n\n".join([
                f"[Round {m.get('round')}] {m.get('agent')}\n{m.get('analysis', m.get('consensus', {})).get('rationale', str(m))}"
                for m in result.get("transcript", [])
            ])
            
            st.download_button(
                label="📥 Download Transcript",
                data=transcript_text,
                file_name=f"debate_{stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            status_placeholder.error(f"❌ Error: {str(e)}")
            st.exception(e)

else:
    with debate_container:
        st.info("👈 Configure debate settings in the sidebar and click **Start Debate** to begin.")
        
        # Show example
        st.subheader("📖 How it works")
        st.markdown("""
        1. **Data Fetching**: Retrieves real-time Vietnamese stock data from Vietcap API (with yfinance fallback)
        2. **Agent Initialization**: Technical, Fundamental, and Sentiment analysts receive stock data and prompts
        3. **Debate Rounds**: Moderator orchestrates dynamic multi-round debate between agents
        4. **Consensus**: Moderator synthesizes final investment recommendation weighted by agent confidence
        5. **Transcript**: Complete debate log saved to `/logs` directory
        
        **Agents:**
        - 🔵 **Technical Analyst**: RSI, MACD, Bollinger Bands, Moving Averages
        - 🟢 **Fundamental Analyst**: P/E, ROE, Valuation, Financial Health
        - 🟠 **Sentiment Analyst**: News analysis from VnEconomy + WSJ
        - 🔴 **Moderator**: Orchestrates debate, synthesizes consensus
        """)
