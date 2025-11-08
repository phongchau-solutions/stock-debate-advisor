"""
Streamlit UI for the Gemini Multi-Agent Stock Debate PoC.
"""
import streamlit as st
from orchestrator import DebateOrchestrator
from config import config

# Page configuration
st.set_page_config(
    page_title="Stock Debate AI",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for chat-like interface with agent-specific backgrounds
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: 70%;
        display: flex;
        flex-direction: column;
    }
    .fundamental-analyst {
        background-color: #e3f2fd;
        color: #0d47a1;
        border-left: 4px solid #1976d2;
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }
    .technical-analyst {
        background-color: #f3e5f5;
        color: #4a148c;
        border-left: 4px solid #7b1fa2;
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }
    .sentiment-analyst {
        background-color: #e8f5e9;
        color: #1b5e20;
        border-left: 4px solid #388e3c;
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }
    .moderator {
        background-color: #fff3e0;
        color: #e65100;
        border-right: 4px solid #f57c00;
        border-left: none;
        margin-left: auto;
        margin-right: 0;
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
    }
    .judge {
        background-color: #fce4ec;
        color: #880e4f;
        border-right: 4px solid #c2185b;
        border-left: none;
        margin-left: auto;
        margin-right: 0;
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
        font-weight: 500;
    }
    /* Keep all text left-aligned regardless of message position */
    .chat-message .agent-name,
    .chat-message div {
        text-align: left;
    }
    .moderator .critique-arrow,
    .judge .critique-arrow {
        display: inline-block;
        transform: scaleX(-1);
    }
    .agent-name {
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .round-badge {
        display: inline-block;
        background-color: #666;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
    }
    .critique-arrow {
        display: inline-block;
        background-color: #ff5722;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
    }

    .action-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
        font-weight: bold;
        color: white;
    }
    .action-buy {
        background-color: #4CAF50;
    }
    .action-sell {
        background-color: #f44336;
    }
    .action-hold {
        background-color: #ff9800;
    }
    .action-change {
        margin: 0 4px;
        color: #666;
        font-weight: normal;
    }
    .critique-link {
        display: inline-block;
        background-color: #e91e63;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


def display_message(agent: str, message: str, round_num: int, target: str = ""):
    """Display a chat-style message with optional critique indicator, action, and action change."""
    # Initialize action tracking in session state if not exists
    if 'agent_actions' not in st.session_state:
        st.session_state.agent_actions = {}
    
    # Normalize agent name for CSS class
    agent_class = agent.lower().replace(" ", "-")
    
    # Agent emoji mapping
    emoji_map = {
        "fundamental-analyst": "💼",
        "technical-analyst": "📈",
        "sentiment-analyst": "💭",
        "moderator": "⚖️",
        "judge": "👨‍⚖️"
    }
    
    emoji = emoji_map.get(agent_class, "🤖")
    
    # Extract or enforce action for debate agents
    current_action = ""
    is_analyst = any(role in agent_class for role in ["fundamental-analyst", "technical-analyst", "sentiment-analyst"])
    
    if is_analyst:
        # Get previous action for this agent and round
        agent_key = f"{agent_class}-{round_num}"
        prev_round_key = f"{agent_class}-{round_num-1}" if round_num > 1 else None
        previous_action = st.session_state.agent_actions.get(prev_round_key, "")
        
        # Find action in message
        action_found = False
        for keyword in ["BUY", "SELL", "HOLD"]:
            if keyword in message.upper():
                action_class = f"action-{keyword.lower()}"
                current_action = f'<span class="action-badge {action_class}">{keyword}</span>'
                action_found = True
                
                # Store the current action
                st.session_state.agent_actions[agent_key] = keyword
                
                # Show action change if different from previous round
                if previous_action and previous_action != keyword:
                    current_action = f'<span class="action-badge action-{previous_action.lower()}">{previous_action}</span> <span class="action-change">→</span> {current_action}'
                break
        
        # If no action found, use previous action or default to HOLD
        if not action_found:
            if previous_action:
                action_class = f"action-{previous_action.lower()}"
                current_action = f'<span class="action-badge {action_class}">{previous_action}</span>'
                st.session_state.agent_actions[agent_key] = previous_action
            else:
                current_action = '<span class="action-badge action-hold">HOLD</span>'
                st.session_state.agent_actions[agent_key] = "HOLD"
    
    # Add critique indicator and link if targeting another agent
    critique_indicator = ""
    critique_link = ""
    if target:
        critique_indicator = f' <span class="critique-arrow">→ {target}</span>'
        critique_link = f' <span class="critique-link" onclick="document.getElementById(\'msg-{round_num}-{target.lower().replace(" ", "-")}\').scrollIntoView({{behavior: \'smooth\'}})">↩️ Linked</span>'
    
    st.markdown(f"""
    <div class="chat-message {agent_class}" id="msg-{round_num}-{agent_class}">
        <div class="agent-name">
            {emoji} <strong>{agent}</strong>{critique_indicator} <span class="round-badge">Round <strong>{round_num}</strong></span>{current_action}{critique_link}
        </div>
        <div>{message.replace("BUY", "<strong>BUY</strong>").replace("SELL", "<strong>SELL</strong>").replace("HOLD", "<strong>HOLD</strong>")}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🎯 Stock Debate AI")
    st.markdown("**Multi-Agent Analysis System** • Powered by Gemini & Autogen")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize orchestrator
        if 'orchestrator' not in st.session_state:
            try:
                st.session_state.orchestrator = DebateOrchestrator()
                st.success("✅ System initialized")
            except Exception as e:
                st.error(f"❌ Initialization failed: {e}")
                st.stop()
        
        # Get available symbols
        available_symbols = st.session_state.orchestrator.get_available_symbols()
        
        if not available_symbols:
            st.warning("⚠️ No stock data found in data directories")
            symbol = st.text_input("Enter Stock Symbol", value="VNM")
        else:
            symbol = st.selectbox("Select Stock Symbol", available_symbols)
        
        timeframe = st.selectbox(
            "Analysis Timeframe",
            ["1 month", "3 months", "6 months", "1 year"]
        )
        
        min_rounds = st.slider(
            "Minimum Debate Rounds",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            help="The debate will run for at least this many rounds. Each agent speaks once per round."
        )
        
        st.divider()
        
        # Start debate button
        if st.button("🚀 Start Debate", type="primary", use_container_width=True):
            st.session_state.debate_running = True
            st.session_state.debate_complete = False
            st.session_state.current_symbol = symbol
            st.session_state.current_timeframe = timeframe
            st.session_state.current_min_rounds = min_rounds
        
        # Data availability
        if hasattr(st.session_state, 'current_symbol'):
            st.divider()
            st.subheader("📊 Data Status")
            
            orch = st.session_state.orchestrator
            
            # Check data availability
            financial = orch.data_loader.load_financial_data(st.session_state.current_symbol)
            technical = orch.data_loader.load_technical_data(st.session_state.current_symbol)
            sentiment = orch.data_loader.load_sentiment_data(st.session_state.current_symbol)
            
            st.write("💼 Fundamental:", "✅" if financial else "❌")
            st.write("📈 Technical:", "✅" if technical else "❌")
            st.write("💭 Sentiment:", "✅" if sentiment else "❌")
    
    # Main content area
    if not hasattr(st.session_state, 'debate_running') or not st.session_state.debate_running:
        # Welcome screen
        st.info("👈 Select a stock symbol and click **Start Debate** to begin the analysis.")
        
        st.markdown("""
        ### How it works
        
        1. **Three Expert Agents** analyze the stock:
           - 💼 **Fundamental Analyst** - Financial metrics and ratios
           - 📈 **Technical Analyst** - Price trends and patterns
           - 💭 **Sentiment Analyst** - News and market psychology
        
        2. **Multi-Round Debate** (minimum 10 rounds):
           - Each agent provides brief 1-2 sentence arguments per round
           - Agents respond to each other's points across multiple rounds
           - Debate extends as long as needed for thorough analysis
        
        3. **Moderator** synthesizes all arguments
        
        4. **Judge** makes final BUY/HOLD/SELL verdict
        """)
        
    else:
        # Run the debate with real-time streaming
        if not st.session_state.debate_complete:
            st.markdown("---")
            st.subheader("💬 Debate Stream")
            
            # Create a container for messages
            message_container = st.container()
            
            try:
                # Get debate parameters
                min_rounds = st.session_state.get('current_min_rounds', 10)
                
                # Stream messages in real-time
                with message_container:
                    for entry in st.session_state.orchestrator.run_debate_streaming(
                        st.session_state.current_symbol,
                        rounds=min_rounds
                    ):
                        # Display each message as it arrives
                        display_message(
                            entry['agent'],
                            entry['statement'],
                            entry.get('round', '-'),
                            entry.get('target', '')
                        )
                
                # Mark debate as complete
                st.session_state.debate_complete = True
                st.success(f"✅ Debate completed for **{st.session_state.current_symbol}**")
                
            except Exception as e:
                st.error(f"❌ Error during debate: {e}")
                st.session_state.debate_running = False
        
        # Show reset button after completion
        if st.session_state.debate_complete:
            st.divider()
            if st.button("🔄 New Debate"):
                st.session_state.debate_running = False
                st.session_state.debate_complete = False
                st.rerun()


if __name__ == "__main__":
    # Validate configuration
    try:
        config.validate()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info("Please check your .env file and data directories.")
        st.stop()
    
    main()
