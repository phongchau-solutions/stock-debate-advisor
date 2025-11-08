"""
Streamlit Demo Application for Multi-Agent Stock Debate PoC
Provides interactive UI for running stock investment debates with Gemini + Autogen
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict
from io import StringIO

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.debate_orchestrator import DebateOrchestrator
from services.gemini_service import GeminiService
from services.data_service import DataService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ============================================================================
# Streamlit Configuration
# ============================================================================

st.set_page_config(
    page_title="Stock Debate PoC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .agent-message {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    .agent-fundamental {
        background-color: #f0f7ff;
        border-left-color: #1f77b4;
    }
    .agent-technical {
        background-color: #fff0f5;
        border-left-color: #ff7f0e;
    }
    .agent-sentiment {
        background-color: #f0fff0;
        border-left-color: #2ca02c;
    }
    .agent-moderator {
        background-color: #fff8e1;
        border-left-color: #d62728;
    }
    .agent-judge {
        background-color: #f5f5f5;
        border-left-color: #9467bd;
    }
    .verdict-buy {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .verdict-hold {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .verdict-sell {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Management
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "debate_in_progress" not in st.session_state:
        st.session_state.debate_in_progress = False
    if "debate_result" not in st.session_state:
        st.session_state.debate_result = None
    if "debate_messages" not in st.session_state:
        st.session_state.debate_messages = []
    if "stock_data" not in st.session_state:
        st.session_state.stock_data = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

initialize_session_state()

# Define a custom type for session state variables
class SessionState:
    chat_history: list[Dict[str, Any]]
    user_input: str

# Initialize session state with default values
if not hasattr(st.session_state, "chat_history"):
    st.session_state.chat_history = []  # type: ignore
if not hasattr(st.session_state, "user_input"):
    st.session_state.user_input = ""  # type: ignore

# ============================================================================
# Utility Functions
# ============================================================================

def get_agent_color(agent_name: str) -> str:
    """Return CSS class for agent styling"""
    color_map = {
        "fundamental": "#1f77b4",
        "technical": "#ff7f0e",
        "sentiment": "#2ca02c",
        "moderator": "#d62728",
        "judge": "#9467bd"
    }
    for key in color_map:
        if key in agent_name.lower():
            return key
    return "moderator"

def format_agent_message(agent: str, message: str, round_num: int = None) -> str:
    """Format agent message for display"""
    prefix = f"Round {round_num} | {agent}" if round_num else agent
    return f"**{prefix}:**\n{message}"

def get_verdict_emoji(verdict: str) -> str:
    """Return emoji for verdict"""
    verdict_lower = verdict.lower()
    if "buy" in verdict_lower:
        return "📈"
    elif "sell" in verdict_lower:
        return "📉"
    else:
        return "⏸️"

def validate_stock_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    return len(symbol) > 0 and len(symbol) <= 10 and symbol.isalnum()

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return len(api_key) > 20  # Basic check

def get_safe_value(data: Dict[str, Any], key: str, default: Any) -> Any:
    """Retrieve a value from a dictionary and ensure it's safe for formatting."""
    value = data.get(key, default)
    if isinstance(value, (int, float)):
        return value
    return default

# ============================================================================
# Main Layout - Header
# ============================================================================

st.title("📊 Multi-Agent Stock Debate PoC")
st.markdown("_Powered by Google Gemini 2.0 Flash + Microsoft Autogen_")

# Display header info
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("System", "v4 Debate Engine")
with col2:
    st.metric("LLM", "Gemini 2.0 Flash")
with col3:
    st.metric("Orchestration", "Autogen 0.10.0")

st.divider()

# ============================================================================
# Sidebar Configuration
# ============================================================================

st.sidebar.header("⚙️ Configuration")

# API Key input (masked)
api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Get your API key from https://ai.google.dev/"
)

if not api_key and not os.getenv("GEMINI_API_KEY"):
    st.sidebar.warning("⚠️ API key not configured. Please enter your Gemini API key.")

st.sidebar.divider()

# Stock symbol
stock_symbol = st.sidebar.text_input(
    "Stock Symbol",
    value="VCB",  # Vietnamese bank stock as example
    placeholder="e.g., VCB, TCB, BID",
    help="Vietnamese stock symbol (e.g., VCB, TCB, BID)"
).upper()

if not validate_stock_symbol(stock_symbol):
    st.sidebar.error("Invalid stock symbol")

# Number of debate rounds
num_rounds = st.sidebar.slider(
    "Debate Rounds",
    min_value=1,
    max_value=4,
    value=2,
    help="Number of rounds each agent will speak in the debate"
)

# Period for analysis
period = st.sidebar.selectbox(
    "Analysis Period",
    options=["1mo", "3mo", "6mo", "1y"],
    index=2,
    help="Time period for technical analysis"
)

st.sidebar.divider()

# Advanced options
with st.sidebar.expander("🔧 Advanced Options"):
    use_cache = st.checkbox("Use cached data (if available)", value=True)
    use_db = st.checkbox("Save results to database", value=False)
    db_url = st.text_input(
        "Database URL (optional)",
        placeholder="postgresql://user:pass@localhost/db",
        help="Only used if 'Save results to database' is enabled"
    ) if use_db else None
    max_tokens = st.slider(
        "Max tokens per response",
        min_value=256,
        max_value=2048,
        value=512
    )

st.sidebar.divider()

# Run button
run_debate = st.sidebar.button(
    "🚀 Start Debate",
    type="primary",
    disabled=not api_key or not validate_stock_symbol(stock_symbol)
)

# ============================================================================
# Main Content Area
# ============================================================================

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎯 Debate Live", "📈 Stock Data", "📊 Results", "💾 Export"]
)

# ============================================================================
# Tab 1: Live Debate
# ============================================================================

with tab1:
    if run_debate:
        st.session_state.debate_in_progress = True
        st.session_state.debate_messages = []
        st.session_state.error_message = None
        
        # Initialize services
        gemini_service = GeminiService(api_key=api_key)
        data_service = DataService()
        
        # Create placeholder for streaming updates
        debate_container = st.container()
        status_container = st.container()
        
        try:
            with status_container:
                with st.spinner(f"🔄 Fetching stock data for {stock_symbol}..."):
                    # Fetch stock data
                    try:
                        # Convert period string to days
                        period_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
                        period_days = period_map.get(period, 180)
                        
                        stock_data = data_service.fetch_stock_data(
                            stock_symbol,
                            period_days=period_days
                        )
                        st.session_state.stock_data = stock_data
                    except Exception as e:
                        st.error(f"❌ Failed to fetch stock data: {str(e)}")
                        st.info("💡 Ensure stock symbol is valid (e.g., VCB, TCB, BID for Vietnamese stocks)")
                        st.stop()
                
                # Initialize orchestrator
                with st.spinner(f"🚀 Initializing debate orchestrator..."):
                    orchestrator = DebateOrchestrator(
                        llm_service=gemini_service,
                        db_manager=None  # No database persistence in demo
                    )
                
                # Run debate with progress updates
                with st.spinner(f"🎬 Running {num_rounds}-round debate..."):
                    progress_bar = st.progress(0)
                    
                    # Run the actual debate
                    result = orchestrator.run_debate(
                        stock_symbol=stock_symbol,
                        stock_data=stock_data,
                        num_rounds=num_rounds,
                        period_days=period_days
                    )
                    
                    st.session_state.debate_result = result
                    progress_bar.progress(100)
                
                # Display completion message
                st.success(f"✅ Debate completed successfully!")
        
        except Exception as e:
            st.session_state.error_message = str(e)
            st.error(f"❌ Error during debate: {str(e)}")
            logger.exception(f"Debate error: {e}")
        
        finally:
            st.session_state.debate_in_progress = False
    
    # Display debate results if available
    if st.session_state.debate_result:
        result = st.session_state.debate_result
        
        st.subheader(f"📋 Debate Summary - {result.stock_symbol}")
        
        # Debate metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rounds", result.num_rounds)
        with col2:
            duration_seconds = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
            st.metric("Duration", f"{duration_seconds:.1f}s")
        with col3:
            st.metric("Timestamp", result.start_time.strftime("%H:%M:%S"))
        with col4:
            st.metric("Messages", len(result.transcript))
        
        st.divider()
        
        # Display messages by round
        st.subheader("💬 Debate Messages")
        
        for i, msg in enumerate(result.transcript):
            agent_color = get_agent_color(msg.agent_name)
            agent_class = f"agent-message agent-{agent_color}"

            # Parse timestamp locally
            try:
                timestamp = datetime.fromisoformat(msg.timestamp)
                formatted_timestamp = timestamp.strftime('%H:%M:%S')
            except ValueError:
                formatted_timestamp = "Invalid timestamp"

            # Create expandable message
            with st.expander(f"**{msg.agent_name}** (Round {msg.round_num}): {msg.content[:80]}..."):
                st.write(msg.content)
                st.caption(f"Timestamp: {formatted_timestamp}")
        
        st.divider()
        
        # Display final verdict
        st.subheader(f"{get_verdict_emoji(result.final_decision)} Final Verdict")
        
        verdict = result.final_decision
        verdict_class = {
            'BUY': 'verdict-buy',
            'HOLD': 'verdict-hold',
            'SELL': 'verdict-sell'
        }.get(verdict, 'verdict-hold')
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f"""
                <div class='{verdict_class}' style='padding: 20px; border-radius: 10px; text-align: center;'>
                    <h2>{verdict}</h2>
                    <p><strong>Confidence:</strong> {result.confidence}%</p>
                    <p><strong>Rationale:</strong> {result.summary}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.divider()
        
        # Move Agent Analysis to the top
        st.subheader("🎯 Agent Analysis")
        if st.session_state.debate_result:
            result = st.session_state.debate_result
            st.write(f"**Final Decision:** {result.final_decision}")
            st.write(f"**Confidence:** {result.confidence}%")
            st.write(f"**Debate Rounds:** {result.num_rounds}")
            st.divider()

            for agent, rationale in result.rationale.items():
                with st.expander(f"**{agent.title()}** Analysis"):
                    st.write(rationale)
    
    elif not st.session_state.debate_in_progress:
        st.info("👉 Configure debate parameters and click 'Start Debate' to begin")

# ============================================================================
# Tab 2: Stock Data
# ============================================================================

with tab2:
    if st.session_state.stock_data or (run_debate and st.session_state.stock_data):
        st.subheader(f"📊 {stock_symbol} Technical Data")
        
        data = st.session_state.stock_data
        
        # Display current stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            current_price = get_safe_value(data, 'current_price', 'N/A')
            if isinstance(current_price, (int, float)):
                st.metric("Current Price", f"${current_price:.2f}")
            else:
                st.metric("Current Price", f"{current_price}")
        with col2:
            change_pct = get_safe_value(data, 'change_pct', 0)
            color = "green" if change_pct > 0 else "red"
            if isinstance(change_pct, (int, float)):
                st.metric("Change %", f"{change_pct:.2f}%")
            else:
                st.metric("Change %", f"{change_pct}")
        with col3:
            fifty_two_week_high = get_safe_value(data, 'fifty_two_week_high', 'N/A')
            if isinstance(fifty_two_week_high, (int, float)):
                st.metric("52w High", f"${fifty_two_week_high:.2f}")
            else:
                st.metric("52w High", f"{fifty_two_week_high}")
        with col4:
            fifty_two_week_low = get_safe_value(data, 'fifty_two_week_low', 'N/A')
            if isinstance(fifty_two_week_low, (int, float)):
                st.metric("52w Low", f"${fifty_two_week_low:.2f}")
            else:
                st.metric("52w Low", f"{fifty_two_week_low}")
        
        st.divider()
        
        # Fundamental metrics
        st.subheader("💰 Fundamental Metrics")
        if "fundamentals" in data:
            fund = data["fundamentals"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("P/E Ratio", f"{fund.get('pe_ratio', 'N/A'):.2f}")
            with col2:
                st.metric("Market Cap", f"${fund.get('market_cap', 0) / 1e9:.2f}B")
            with col3:
                st.metric("Dividend Yield", f"{fund.get('dividend_yield', 0):.2f}%")
        
        # Technical indicators
        st.subheader("📈 Technical Indicators")
        if "technical" in data:
            tech = data["technical"]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("RSI (14)", f"{tech.get('rsi', 'N/A'):.2f}")
            with col2:
                st.metric("MA50", f"${tech.get('sma_50', 'N/A'):.2f}")
            with col3:
                st.metric("MA200", f"${tech.get('sma_200', 'N/A'):.2f}")
            with col4:
                st.metric("MACD", f"{tech.get('macd', 'N/A'):.4f}")
        
        # Display raw data table
        if "historical_data" in data and not data["historical_data"].empty:
            st.subheader("📋 Historical Data (Last 30 days)")
            st.dataframe(
                data["historical_data"].tail(30),
                use_container_width=True
            )
    else:
        st.info("📊 Run a debate to load stock data")

# ============================================================================
# Tab 3: Results
# ============================================================================

with tab3:
    if st.session_state.debate_result:
        result = st.session_state.debate_result
        
        st.subheader("📊 Debate Analysis Results")
        
        # Create summary dataframe
        duration_seconds = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
        # Ensure all values in the Value column are strings
        summary_data = {
            "Metric": [
                "Stock Symbol",
                "Debate Rounds",
                "Total Duration",
                "Messages Count",
                "Final Decision",
                "Decision Confidence",
                "Timestamp"
            ],
            "Value": [
                str(result.stock_symbol),
                str(result.num_rounds),
                f"{duration_seconds:.2f}s",
                str(len(result.transcript)),
                str(result.final_decision),
                f"{result.confidence}%",
                result.start_time.strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        
        st.dataframe(
            pd.DataFrame(summary_data),
            use_container_width=True,
            hide_index=True
        )
        
        # Detailed results
        st.subheader("📝 Detailed Results")
        
        # Create columns for structured display
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Decision**")
            st.write(f"### {result.final_decision}")
            
            st.write("**Summary**")
            st.write(result.summary)
        
        with col2:
            st.write("**Confidence Level**")
            confidence = result.confidence
            st.progress(confidence / 100.0)
            st.write(f"{confidence}%")
            
            st.write("**Key Analysis**")
            for agent, rationale in result.rationale.items():
                st.write(f"• **{agent.title()}**: {rationale[:100]}...")
    else:
        st.info("📊 Run a debate to see results")

# ============================================================================
# Tab 4: Export
# ============================================================================

with tab4:
    if st.session_state.debate_result:
        result = st.session_state.debate_result
        
        st.subheader("💾 Export Debate Results")
        
        # Export formats
        col1, col2, col3 = st.columns(3)
        
        duration_seconds = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
        
        with col1:
            st.write("**JSON Export**")
            json_data = {
                "stock_symbol": result.stock_symbol,
                "num_rounds": result.num_rounds,
                "duration_seconds": duration_seconds,
                "timestamp": result.start_time.isoformat(),
                "final_decision": result.final_decision,
                "confidence": result.confidence,
                "messages_count": len(result.transcript),
                "debate_id": result.debate_id
            }
            
            json_str = json.dumps(json_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"debate_{result.stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            st.write("**CSV Export**")
            # Convert messages to CSV
            messages_data = []
            for msg in result.transcript:
                messages_data.append({
                    "agent": msg.agent_name,
                    "round": msg.round_num,
                    "timestamp": msg.timestamp if isinstance(msg.timestamp, str) else msg.timestamp.isoformat(),
                    "content": msg.content[:500]  # Truncate for CSV
                })
            
            messages_df = pd.DataFrame(messages_data)
            csv_str = messages_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name=f"debate_messages_{result.stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col3:
            st.write("**Full Report**")
            # Create comprehensive report
            report = f"""
# Stock Debate Analysis Report

## Metadata
- **Stock:** {result.stock_symbol}
- **Date:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Rounds:** {result.num_rounds}
- **Duration:** {duration_seconds:.2f}s

## Final Verdict
- **Decision:** {result.final_decision}
- **Confidence:** {result.confidence}%
- **Summary:** {result.summary}

## Agent Rationale
{json.dumps(result.rationale, indent=2)}

## Messages ({len(result.transcript)} total)
"""
            for msg in result.transcript:
                report += f"\n### {msg.agent_name} - Round {msg.round_num}\n{msg.content}\n"
            
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"debate_report_{result.stock_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        st.divider()
        
        # Display raw JSON
        st.subheader("📄 Raw JSON Data")
        st.json(json_data)
    else:
        st.info("💾 Run a debate to export results")

# ============================================================================
# Chat UI - Experimental
# ============================================================================

st.divider()
st.header("💬 Debate Chat (Experimental)")

def render_chat_ui():
    """Render a chat-style UI for conversation."""
    st.title("💬 Multi-Agent Debate Chat")  # type: ignore

    # Scrollable chat box
    with st.container():  # type: ignore
        st.markdown(
            """
            <style>
            .chat-box {
                max-height: 70vh;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .agent-message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                display: inline-block;
            }
            .agent-fundamental {
                background-color: #e0f7fa;
                color: #006064;
            }
            .agent-technical {
                background-color: #e8f5e9;
                color: #1b5e20;
            }
            .agent-sentiment {
                background-color: #fce4ec;
                color: #880e4f;
            }
            .moderator-message {
                background-color: #ede7f6;
                color: #311b92;
            }
            .judge-message {
                background-color: #fff3e0;
                color: #bf360c;
            }
            </style>
            """,
            unsafe_allow_html=True  # type: ignore
        )

        st.markdown('<div class="chat-box">', unsafe_allow_html=True)  # type: ignore
        for message in st.session_state.chat_history:  # type: ignore
            agent_class = f"agent-{message.get('agent_type', 'moderator')}"
            content = message.get("content", "")
            st.markdown(
                f'<div class="agent-message {agent_class}">{content}</div>',
                unsafe_allow_html=True  # type: ignore
            )
        st.markdown('</div>', unsafe_allow_html=True)  # type: ignore

    # Input box for user message
    user_input = st.text_input("Type your response here and hit enter:", key="user_input")  # type: ignore

    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"agent_type": None, "content": user_input})  # type: ignore

        # Simulate system response
        system_response = f"You said: {user_input}"  # Replace with actual system logic
        st.session_state.chat_history.append({"agent_type": "moderator", "content": system_response})  # type: ignore

        # Clear input box
        st.session_state.user_input = ""  # type: ignore

# Render the chat UI
render_chat_ui()

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.markdown("""
---
**Multi-Agent Stock Debate PoC v4** | Built with Streamlit + Gemini + Autogen

📚 [Documentation](README.md) | 🐛 [Issues](#) | 📧 Support
""")
