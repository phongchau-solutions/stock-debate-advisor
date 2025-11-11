"""
Streamlit Demo App for Agentic Service.
Demonstrates working debate orchestration with Microsoft Autogen.
"""
import streamlit as st
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orchestrators.debate_orchestrator import DebateOrchestrator
from app.config import config

# Page configuration
st.set_page_config(
    page_title="Stock Debate AI - v6",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .fundamental {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .technical {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    .sentiment {
        background-color: #e8f5e9;
        border-left: 4px solid #388e3c;
    }
    .moderator {
        background-color: #fff3e0;
        border-left: 4px solid #f57c00;
    }
    .judge {
        background-color: #fce4ec;
        border-left: 4px solid #c2185b;
        font-weight: bold;
    }
    .agent-name {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def display_message(agent: str, message: str, round_num: int):
    """Display a chat-style message."""
    agent_lower = agent.lower().replace(" ", "")
    
    if "fundamental" in agent_lower:
        css_class = "fundamental"
        emoji = "💼"
    elif "technical" in agent_lower:
        css_class = "technical"
        emoji = "📈"
    elif "sentiment" in agent_lower:
        css_class = "sentiment"
        emoji = "📰"
    elif "moderator" in agent_lower:
        css_class = "moderator"
        emoji = "⚖️"
    elif "judge" in agent_lower:
        css_class = "judge"
        emoji = "👨‍⚖️"
    else:
        css_class = ""
        emoji = "💬"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <div class="agent-name">{emoji} {agent} - Round {round_num}</div>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit app."""
    st.title("📊 Stock Debate AI - Multi-Agent Analysis")
    st.markdown("*Powered by Microsoft AutoGen & Microservices Architecture*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Stock symbol input
        symbol = st.text_input(
            "Stock Symbol",
            value="MBB",
            help="Enter Vietnamese stock symbol (e.g., MBB, VNM, VCB)"
        )
        
        # Debate rounds
        rounds = st.slider(
            "Debate Rounds",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of debate rounds"
        )
        
        # Model selection
        st.selectbox(
            "LLM Model",
            ["gemini-1.5-pro", "gpt-4"],
            disabled=True,
            help=f"Current: {config.LLM_MODEL}"
        )
        
        # Status indicators
        st.markdown("---")
        st.markdown("### 🔌 Service Status")
        st.success("✓ Agentic Service")
        st.info("ℹ️ Data Service")
        st.info("ℹ️ Analysis Service")
        
        st.markdown("---")
        st.markdown("### 📊 Agent Team")
        st.write("💼 Fundamental Analyst")
        st.write("📈 Technical Analyst")
        st.write("📰 Sentiment Analyst")
        st.write("⚖️ Moderator")
        st.write("👨‍⚖️ Judge")
    
    # Main content
    st.markdown("---")
    
    # Start debate button
    if st.button("🚀 Start Debate", type="primary", use_container_width=True):
        if not symbol:
            st.error("Please enter a stock symbol")
            return
        
        # Initialize orchestrator
        with st.spinner("Initializing debate orchestrator..."):
            orchestrator = DebateOrchestrator()
        
        # Run debate
        st.info(f"Starting multi-agent debate for **{symbol}** with {rounds} rounds...")
        
        # Progress container
        debate_container = st.container()
        
        with st.spinner("Running debate..."):
            try:
                # Run debate
                result = orchestrator.run_debate(symbol, rounds)
                
                # Display transcript
                with debate_container:
                    st.subheader("🎭 Debate Transcript")
                    
                    for msg in result["transcript"]:
                        display_message(
                            msg["agent"],
                            msg["message"],
                            msg["round"]
                        )
                    
                    # Display final decision
                    st.markdown("---")
                    st.subheader("⚖️ Final Judgment")
                    
                    final = result["final_decision"]
                    display_message(
                        "Judge",
                        final.get("decision", "No decision available"),
                        rounds
                    )
                
                st.success("✅ Debate completed successfully!")
                
                # Download button for results
                import json
                result_json = json.dumps(result, indent=2)
                st.download_button(
                    label="📥 Download Debate Results",
                    data=result_json,
                    file_name=f"debate_{symbol}_{result['timestamp']}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Error during debate: {str(e)}")
                st.exception(e)
    
    # Information section
    with st.expander("ℹ️ About This Demo"):
        st.markdown("""
        ### Multi-Agent Stock Debate System
        
        This demo showcases a microservices-based agentic system for stock analysis:
        
        **Architecture:**
        - **Data Service**: Fetches financial data, news, and prices
        - **Analysis Service**: Performs fundamental, technical, and sentiment analysis
        - **Agentic Service**: Orchestrates multi-agent debate using Google Gemini API
        
        **Agent Roles:**
        - **Fundamental Analyst**: Analyzes financial statements and ratios
        - **Technical Analyst**: Analyzes price trends and technical indicators
        - **Sentiment Analyst**: Analyzes news and market sentiment
        - **Moderator**: Guides debate and challenges arguments
        - **Judge**: Provides final investment decision
        
        **Features:**
        - Google Agent Development Kit (ADK) with LlmAgent orchestration
        - Clear service layer separation
        - MCP-ready architecture (native ADK support)
        - Scalable microservices design
        """)
    
    with st.expander("🔧 System Architecture"):
        st.markdown("""
        ```
        v6/
        ├── data-service/          # Data retrieval and storage
        │   ├── app/
        │   │   ├── api/           # FastAPI endpoints
        │   │   ├── clients/       # VietCap API client
        │   │   ├── crawlers/      # News crawlers
        │   │   └── db/            # Database models
        │   └── airflow/           # Data pipeline DAGs
        │
        ├── analysis-service/      # Analysis engines
        │   ├── app/
        │   │   ├── analyzers/     # Fundamental, Technical, Sentiment
        │   │   ├── etl/           # ETL processes
        │   │   └── api/           # FastAPI endpoints
        │
        └── agentic-service/       # Multi-agent orchestration
            ├── app/
            │   ├── agents/        # Agent implementations
            │   ├── orchestrators/ # Debate orchestration
            │   ├── tools/         # Agent tools
            │   ├── mcp/           # MCP integration
            │   └── prompts/       # Agent prompts
        ```
        """)


if __name__ == "__main__":
    main()
