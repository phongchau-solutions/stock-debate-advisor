"""
Streamlit UI for the CrewAI Stock Debate System.
Follows SOLID, DRY, and KISS principles.
"""
import streamlit as st
from orchestrator import DebateOrchestrator
from config import config
from constants import (
    UIConstants,
    AgentRole,
    AgentColor,
    AgentBorderColor,
    AgentEmoji,
    InvestmentAction
)
from data_loader import NumberFormatter


# Page configuration
st.set_page_config(
    page_title=UIConstants.PAGE_TITLE,
    page_icon=UIConstants.PAGE_ICON,
    layout=UIConstants.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(f"""
<style>
    .chat-message {{
        padding: 1rem;
        border-radius: {UIConstants.BORDER_RADIUS};
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: {UIConstants.CHAT_MESSAGE_WIDTH};
    }}
    
    .fundamental-analyst {{
        background-color: {AgentColor.FUNDAMENTAL.value};
        color: #0d47a1;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.FUNDAMENTAL.value};
    }}
    
    .technical-analyst {{
        background-color: {AgentColor.TECHNICAL.value};
        color: #4a148c;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.TECHNICAL.value};
    }}
    
    .sentiment-analyst {{
        background-color: {AgentColor.SENTIMENT.value};
        color: #1b5e20;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.SENTIMENT.value};
    }}
    
    .moderator {{
        background-color: {AgentColor.MODERATOR.value};
        color: #e65100;
        border-right: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.MODERATOR.value};
        border-left: none;
        margin-left: auto;
        margin-right: 0;
    }}
    
    .judge {{
        background-color: {AgentColor.JUDGE.value};
        color: #880e4f;
        border-right: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.JUDGE.value};
        border-left: none;
        margin-left: auto;
        margin-right: 0;
        font-weight: 500;
    }}
    
    .verdict-box {{
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }}
    
    .buy-verdict {{
        border-left-color: #27ae60;
        background-color: #f0fdf4;
    }}
    
    .sell-verdict {{
        border-left-color: #e74c3c;
        background-color: #fdf5f5;
    }}
    
    .hold-verdict {{
        border-left-color: #f39c12;
        background-color: #fefde8;
    }}
</style>
""", unsafe_allow_html=True)


class DebateUI:
    """Main UI controller for debate interface."""
    
    def __init__(self):
        """Initialize UI controller."""
        self.orchestrator = DebateOrchestrator()
        
    def render_header(self):
        """Render page header."""
        st.title(f"{UIConstants.PAGE_ICON} {UIConstants.PAGE_TITLE}")
        st.markdown("**Multi-Agent AI Debate System for Stock Analysis**")
        st.markdown("---")
    
    def render_sidebar(self):
        """Render sidebar controls."""
        st.sidebar.header("⚙️ Configuration")
        
        # Stock selection
        available_symbols = self.orchestrator.get_available_symbols()
        if not available_symbols:
            available_symbols = ["MBB", "VNM", "HPG", "FPT", "VIC"]
        
        selected_symbol = st.sidebar.selectbox(
            "📈 Select Stock Symbol",
            available_symbols,
            index=0 if "MBB" in available_symbols else 0
        )
        
        # Debate rounds
        num_rounds = st.sidebar.slider(
            "🔄 Number of Debate Rounds",
            min_value=1,
            max_value=5,
            value=3,
            help="More rounds = deeper analysis but longer execution"
        )
        
        # Run debate button
        run_button = st.sidebar.button(
            "🚀 Start Debate",
            use_container_width=True,
            type="primary"
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 About This System")
        st.sidebar.markdown("""
        This system uses CrewAI to orchestrate multiple AI agents:
        
        - **📊 Fundamental Analyst**: Financial metrics & valuation
        - **📈 Technical Analyst**: Price trends & indicators
        - **📰 Sentiment Analyst**: News & market psychology
        - **🎭 Moderator**: Debate facilitation
        - **⚖️ Judge**: Final recommendation
        """)
        
        return selected_symbol, num_rounds, run_button
    
    def render_message(self, agent: str, content: str, round_num: int = None):
        """Render a debate message."""
        emoji = self._get_agent_emoji(agent)
        
        if round_num:
            header = f"{emoji} **{agent}** (Round {round_num})"
        else:
            header = f"{emoji} **{agent}**"
        
        st.markdown(f"#### {header}")
        st.markdown(content)
        st.markdown("---")
    
    def render_verdict(self, verdict: dict):
        """Render final verdict."""
        recommendation = verdict.get('recommendation', 'HOLD')
        confidence = verdict.get('confidence', 'Medium')
        rationale = verdict.get('rationale', [])
        
        # Determine verdict color
        verdict_class = "hold-verdict"
        if recommendation == "BUY":
            verdict_class = "buy-verdict"
            emoji = "📈"
        elif recommendation == "SELL":
            verdict_class = "sell-verdict"
            emoji = "📉"
        else:
            emoji = "⏸️"
        
        # Render verdict box
        st.markdown(f"""
        <div class="verdict-box {verdict_class}">
            <h2 style="margin-top: 0;">{emoji} FINAL RECOMMENDATION</h2>
            <h1 style="color: #000; margin: 0.5rem 0;">{recommendation}</h1>
            <p><strong>Confidence Level:</strong> {confidence}</p>
            <h3>Key Rationale:</h3>
            <ul>
        """, unsafe_allow_html=True)
        
        for point in rationale[:3]:  # Limit to 3 points
            st.markdown(f"- {point}")
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    @staticmethod
    def _get_agent_emoji(agent: str) -> str:
        """Get emoji for agent."""
        agent_lower = agent.lower()
        if "fundamental" in agent_lower:
            return "📊"
        elif "technical" in agent_lower:
            return "📈"
        elif "sentiment" in agent_lower:
            return "📰"
        elif "moderator" in agent_lower:
            return "🎭"
        elif "judge" in agent_lower:
            return "⚖️"
        return "🤖"
    
    def run_debate_session(self, symbol: str, rounds: int):
        """Run a debate session."""
        with st.spinner(f"🔄 Starting debate for {symbol}..."):
            try:
                # Run debate
                result = self.orchestrator.run_debate(symbol, rounds)
                
                # Display results
                st.success(f"✅ Debate Complete for {symbol}!")
                st.markdown("---")
                
                # Display analysis
                if result.get('debate_transcript'):
                    st.subheader("📋 Debate Transcript")
                    for i, entry in enumerate(result['debate_transcript'], 1):
                        with st.expander(f"Round {entry.get('round', i)} - Analyses", expanded=(i==1)):
                            st.markdown(entry.get('analysis', 'No analysis available'))
                
                # Display moderation notes
                if result.get('debate_notes'):
                    st.subheader("🎭 Moderator's Synthesis")
                    st.markdown(result['debate_notes'])
                
                # Display final verdict
                st.subheader("⚖️ Final Judgment")
                self.render_verdict(result['verdict'])
                
                # Show raw output
                with st.expander("📝 Full Judge Output", expanded=False):
                    st.code(result['final_result'])
                
            except Exception as e:
                st.error(f"❌ Error during debate: {str(e)}")
                st.info("Please ensure you have the required data files and API keys configured.")


def main():
    """Main entry point."""
    ui = DebateUI()
    
    # Initialize session state
    if 'debate_running' not in st.session_state:
        st.session_state.debate_running = False
    
    # Render header
    ui.render_header()
    
    # Render sidebar and get controls
    symbol, rounds, run_button = ui.render_sidebar()
    
    # Main content area
    st.subheader(f"📊 Stock Analysis: {symbol}")
    
    # Display info about selected stock
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Analysis Rounds", rounds)
    with col2:
        st.metric("Agents", 5)
    with col3:
        st.metric("System", "CrewAI")
    
    st.markdown("---")
    
    # Run debate if button clicked
    if run_button:
        st.session_state.debate_running = True
    
    if st.session_state.debate_running:
        ui.run_debate_session(symbol, rounds)
        st.session_state.debate_running = False
    else:
        st.info("""
        👋 **Welcome to the Stock Debate AI System!**
        
        This system uses CrewAI to orchestrate 5 specialized agents that debate stock recommendations:
        
        1. **Fundamental Analyst** - Analyzes financial statements and valuation
        2. **Technical Analyst** - Analyzes price trends and technical indicators  
        3. **Sentiment Analyst** - Analyzes news and market sentiment
        4. **Moderator** - Facilitates the debate and synthesis
        5. **Judge** - Makes the final BUY/HOLD/SELL recommendation
        
        **How to use:**
        1. Select a stock symbol from the sidebar
        2. Choose the number of debate rounds (1-5)
        3. Click "Start Debate" to begin the analysis
        
        The system will run multiple rounds of analysis, with agents responding to each other and building on previous points until reaching a consensus recommendation.
        """)


if __name__ == "__main__":
    main()
