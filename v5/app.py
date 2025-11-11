"""
Streamlit UI for the Gemini Multi-Agent Stock Debate PoC.
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
    layout=UIConstants.LAYOUT
)

# Custom CSS for chat-like interface with agent-specific backgrounds
def generate_css() -> str:
    """Generate CSS styles using constants from constants.py."""
    return f"""
<style>
    .chat-message {{
        padding: 1rem;
        border-radius: {UIConstants.BORDER_RADIUS};
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        width: {UIConstants.CHAT_MESSAGE_WIDTH};
        display: flex;
        flex-direction: column;
    }}
    .fundamental-analyst {{
        background-color: {AgentColor.FUNDAMENTAL.value};
        color: #0d47a1;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.FUNDAMENTAL.value};
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }}
    .technical-analyst {{
        background-color: {AgentColor.TECHNICAL.value};
        color: #4a148c;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.TECHNICAL.value};
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }}
    .sentiment-analyst {{
        background-color: {AgentColor.SENTIMENT.value};
        color: #1b5e20;
        border-left: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.SENTIMENT.value};
        margin-right: auto;
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
    }}
    .moderator {{
        background-color: {AgentColor.MODERATOR.value};
        color: #e65100;
        border-right: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.MODERATOR.value};
        border-left: none;
        margin-left: auto;
        margin-right: 0;
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
    }}
    .judge {{
        background-color: {AgentColor.JUDGE.value};
        color: #880e4f;
        border-right: {UIConstants.BORDER_WIDTH} solid {AgentBorderColor.JUDGE.value};
        border-left: none;
        margin-left: auto;
        margin-right: 0;
        border-top-left-radius: 20px;
        border-bottom-left-radius: 20px;
        font-weight: 500;
    }}
    .judge strong {{
        color: #ad1457;
        font-size: 1.05em;
    }}
    .judge ul {{
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }}
    .judge li {{
        margin: 0.3rem 0;
    }}
    .moderator strong {{
        color: #bf360c;
        font-size: 1.05em;
    }}
    .moderator ul {{
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }}
    .moderator li {{
        margin: 0.3rem 0;
    }}
    .chat-message .agent-name,
    .chat-message div {{
        text-align: left;
    }}
    .moderator .critique-arrow,
    .judge .critique-arrow {{
        display: inline-block;
        transform: scaleX(-1);
    }}
    .agent-name {{
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }}
    .round-badge {{
        display: inline-block;
        background-color: #666;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
    }}
    .critique-arrow {{
        display: inline-block;
        background-color: #ff5722;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
    }}
    .action-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
        font-weight: bold;
        color: white;
    }}
    .action-buy {{
        background-color: #4CAF50;
    }}
    .action-sell {{
        background-color: #f44336;
    }}
    .action-hold {{
        background-color: #ff9800;
    }}
    .action-change {{
        margin: 0 4px;
        color: #666;
        font-weight: normal;
    }}
    .critique-link {{
        display: inline-block;
        background-color: #e91e63;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-left: 8px;
        cursor: pointer;
    }}
</style>
"""

st.markdown(generate_css(), unsafe_allow_html=True)


def display_metrics_cards(symbol: str, orchestrator):
    """
    Display key metrics cards for fundamental, technical, and sentiment data.
    
    Args:
        symbol: Stock symbol
        orchestrator: Debate orchestrator instance with data loader
    """
    try:
        # Load all data
        financial = orchestrator.data_loader.load_financial_data(symbol)
        technical = orchestrator.data_loader.load_technical_data(symbol)
        sentiment = orchestrator.data_loader.load_sentiment_data(symbol)
        
        # Extract key metrics
        metrics = []
        chart_data = None
        
        # Technical: Current Price with color coding
        if technical and 'data' in technical:
            import pandas as pd
            df = pd.DataFrame(technical['data'])
            if 'close' in df.columns and len(df) >= 2:
                df = df.sort_values('date') if 'date' in df.columns else df
                latest_price = float(df['close'].iloc[-1])
                previous_price = float(df['close'].iloc[-2])
                
                # Determine color based on price change
                if latest_price > previous_price:
                    price_color = 'green'
                    price_change = '📈'
                elif latest_price < previous_price:
                    price_color = 'red'
                    price_change = '📉'
                else:
                    price_color = 'yellow'
                    price_change = '➡️'
                
                change_pct = ((latest_price - previous_price) / previous_price) * 100
                
                metrics.append({
                    'label': '💰 Current Price',
                    'value': f"{latest_price:,.0f} VND",
                    'subtext': f"{price_change} {change_pct:+.2f}%",
                    'category': 'technical',
                    'color': price_color
                })
        elif technical and 'summary' in technical and 'price_stats' in technical['summary']:
            # Fallback if no historical data
            price = technical['summary']['price_stats'].get('latest_close', 0)
            metrics.append({
                'label': '💰 Current Price',
                'value': f"{price:,.0f} VND" if price else "N/A",
                'category': 'technical',
                'color': 'yellow'  # Default to yellow when no comparison available
            })
        
        # Technical: 12-Month Price Chart Data
        if technical and 'data' in technical:
            import pandas as pd
            df = pd.DataFrame(technical['data'])
            if 'date' in df.columns and 'close' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                # Get last 12 months of data
                df = df.sort_values('date')
                df_12m = df.tail(252)  # Approx 252 trading days in a year
                chart_data = df_12m[['date', 'close']].copy()
                chart_data = chart_data.rename(columns={'date': 'Date', 'close': 'Price'})
        
        # Fundamental: P/E Ratio (if available in financial data)
        if financial:
            # Try to find P/E in various possible locations
            pe_ratio = None
            if isinstance(financial, dict):
                # Check common locations for P/E ratio
                pe_ratio = (financial.get('pe_ratio') or 
                           financial.get('PE') or 
                           financial.get('p_e_ratio'))
                
                # Check in records if it's a list
                if 'records' in financial and isinstance(financial['records'], list) and len(financial['records']) > 0:
                    latest = financial['records'][-1] if isinstance(financial['records'], list) else financial['records']
                    pe_ratio = pe_ratio or latest.get('pe_ratio') or latest.get('PE') or latest.get('p_e_ratio')
            
            if pe_ratio:
                metrics.append({
                    'label': '📈 P/E Ratio',
                    'value': f"{float(pe_ratio):.2f}",
                    'category': 'fundamental'
                })
        
        # Fundamental: P/B Ratio (if available)
        if financial:
            pb_ratio = None
            if isinstance(financial, dict):
                pb_ratio = (financial.get('pb_ratio') or 
                           financial.get('PB') or 
                           financial.get('p_b_ratio'))
                
                if 'records' in financial and isinstance(financial['records'], list) and len(financial['records']) > 0:
                    latest = financial['records'][-1] if isinstance(financial['records'], list) else financial['records']
                    pb_ratio = pb_ratio or latest.get('pb_ratio') or latest.get('PB') or latest.get('p_b_ratio')
            
            if pb_ratio:
                metrics.append({
                    'label': '📚 P/B Ratio',
                    'value': f"{float(pb_ratio):.2f}",
                    'category': 'fundamental'
                })
        
        # Technical: Average Volume
        if technical and 'summary' in technical and 'price_stats' in technical['summary']:
            avg_vol = technical['summary']['price_stats'].get('avg_volume')
            if avg_vol:
                formatted_vol = NumberFormatter.format_large_number(avg_vol)
                metrics.append({
                    'label': '📦 Avg Volume',
                    'value': formatted_vol,
                    'category': 'technical'
                })
        
        # Sentiment: Analyze sentiment from news articles with color coding
        if sentiment and 'articles' in sentiment:
            import pandas as pd
            df = pd.DataFrame(sentiment['articles'])
            
            sentiment_description = "Neutral coverage"
            sentiment_color = "yellow"  # Default to yellow/neutral
            
            if 'sentiment' in df.columns:
                # Count sentiment types
                sentiment_counts = df['sentiment'].value_counts()
                total = len(df)
                
                positive = sentiment_counts.get('positive', 0)
                negative = sentiment_counts.get('negative', 0)
                positive_pct = (positive / total) * 100
                negative_pct = (negative / total) * 100
                
                # Determine sentiment and color
                if positive_pct > 60:
                    sentiment_description = f"Strong positive ({int(positive_pct)}%)"
                    sentiment_color = "green"
                elif positive_pct > 40:
                    sentiment_description = f"Mostly positive ({int(positive_pct)}%)"
                    sentiment_color = "green"
                elif negative_pct > 60:
                    sentiment_description = f"Strong negative ({int(negative_pct)}%)"
                    sentiment_color = "red"
                elif negative_pct > 40:
                    sentiment_description = f"Mostly negative ({int(negative_pct)}%)"
                    sentiment_color = "red"
                elif positive > 0 and negative > 0 and abs(positive - negative) < total * 0.2:
                    sentiment_description = f"Mixed signals ({total} articles)"
                    sentiment_color = "yellow"
                else:
                    # Neutral or unclear
                    sentiment_description = "Neutral coverage"
                    sentiment_color = "yellow"
            else:
                # No sentiment column, just show count
                sentiment_description = f"{len(df)} recent articles"
                sentiment_color = "yellow"
            
            metrics.append({
                'label': '💭 Market Sentiment',
                'value': sentiment_description,
                'category': 'sentiment',
                'color': sentiment_color
            })
        
        # Display metrics in a grid (max 5 metrics + 1 chart)
        if metrics or chart_data is not None:
            metrics = metrics[:5]  # Limit to 5 metric cards
            
            # Category colors (default background colors)
            color_map = {
                'fundamental': '#e3f2fd',  # Light blue
                'technical': '#f3e5f5',    # Light purple
                'sentiment': '#e8f5e9'     # Light green
            }
            
            # Signal colors for dynamic cards (price, sentiment)
            signal_colors = {
                'green': {'bg': '#e8f5e9', 'border': '#4caf50', 'text': '#2e7d32'},
                'yellow': {'bg': '#fff9c4', 'border': '#ffc107', 'text': '#f57f17'},
                'red': {'bg': '#ffebee', 'border': '#f44336', 'text': '#c62828'}
            }
            
            # Create two rows if we have a chart
            if chart_data is not None:
                # First row: metrics
                cols = st.columns(len(metrics))
                for idx, metric in enumerate(metrics):
                    with cols[idx]:
                        # Use signal color if available, otherwise category color
                        if 'color' in metric:
                            colors = signal_colors[metric['color']]
                            bg_color = colors['bg']
                            border_color = colors['border']
                            text_color = colors['text']
                        else:
                            bg_color = color_map.get(metric['category'], '#f5f5f5')
                            border_color = '#1976d2' if metric['category'] == 'fundamental' else '#7b1fa2' if metric['category'] == 'technical' else '#388e3c'
                            text_color = '#333'
                        
                        # Add subtext if available
                        subtext_html = ""
                        if 'subtext' in metric:
                            subtext_html = f'<div style="font-size: 0.85rem; color: {text_color}; margin-top: 0.25rem;">{metric["subtext"]}</div>'
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {bg_color};
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid {border_color};
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                            min-height: 100px;
                            height: 100px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        ">
                            <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.25rem;">
                                {metric['label']}
                            </div>
                            <div style="font-size: 1.25rem; font-weight: bold; color: {text_color};">
                                {metric['value']}
                            </div>
                            {subtext_html}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Second row: chart
                st.markdown("##### 📊 12-Month Price Trend")
                st.line_chart(chart_data.set_index('Date'), height=200)
            else:
                # Single row with metrics only
                cols = st.columns(len(metrics))
                for idx, metric in enumerate(metrics):
                    with cols[idx]:
                        # Use signal color if available, otherwise category color
                        if 'color' in metric:
                            colors = signal_colors[metric['color']]
                            bg_color = colors['bg']
                            border_color = colors['border']
                            text_color = colors['text']
                        else:
                            bg_color = color_map.get(metric['category'], '#f5f5f5')
                            border_color = '#1976d2' if metric['category'] == 'fundamental' else '#7b1fa2' if metric['category'] == 'technical' else '#388e3c'
                            text_color = '#333'
                        
                        # Add subtext if available
                        subtext_html = ""
                        if 'subtext' in metric:
                            subtext_html = f'<div style="font-size: 0.85rem; color: {text_color}; margin-top: 0.25rem;">{metric["subtext"]}</div>'
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {bg_color};
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid {border_color};
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                            min-height: 100px;
                            height: 100px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        ">
                            <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.25rem;">
                                {metric['label']}
                            </div>
                            <div style="font-size: 1.25rem; font-weight: bold; color: {text_color};">
                                {metric['value']}
                            </div>
                            {subtext_html}
                        </div>
                        """, unsafe_allow_html=True)
        
    except Exception as e:
        # Silently fail - metrics are nice-to-have, not critical
        print(f"Warning: Could not display metrics cards: {e}")


def extract_action_with_llm(message: str, agent_name: str) -> str:
    """
    Use LLM to intelligently extract the investment action from analyst message.
    
    Args:
        message: The analyst's message
        agent_name: Name of the agent
        
    Returns:
        Detected action: "BUY", "HOLD", or "SELL"
    """
    try:
        import google.generativeai as genai
        from config import config
        
        # Configure Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prompt for action extraction
        extraction_prompt = f"""You are analyzing a stock analyst's message to determine their investment recommendation.

Analyst: {agent_name}
Message: "{message}"

What is the analyst's investment recommendation?

Rules:
- Respond with EXACTLY one word: BUY, HOLD, or SELL
- Base your answer on the analyst's actual recommendation, not incidental mentions of actions in their reasoning
- If the analyst says "I recommend HOLD" but mentions "buying pressure" in their explanation, the answer is HOLD
- If the analyst says "continues to be a BUY" or "maintain BUY", the answer is BUY
- Look for the analyst's concluding recommendation, not words used in their analysis

Your response (one word only):"""

        response = model.generate_content(extraction_prompt)
        detected_action = response.text.strip().upper()
        
        # Validate response
        valid_actions = [action.value for action in InvestmentAction]
        if detected_action in valid_actions:
            return detected_action
        else:
            # Fallback to HOLD if LLM returns invalid response
            return InvestmentAction.HOLD.value
            
    except Exception as e:
        print(f"LLM action extraction failed: {e}")
        # Fallback to HOLD on error
        return InvestmentAction.HOLD.value


def display_message(agent: str, message: str, round_num: int, target: str = ""):
    """
    Display a chat-style message with optional critique indicator, action, and action change.
    
    Args:
        agent: Agent role name
        message: Message content
        round_num: Current round number
        target: Target agent for critique (optional)
    """
    # Initialize action tracking in session state if not exists
    if 'agent_actions' not in st.session_state:
        st.session_state.agent_actions = {}
    
    # Normalize agent name for CSS class
    agent_class = agent.lower().replace(" ", "-")
    
    # Agent emoji mapping using enums
    emoji_map = {
        "fundamental-analyst": AgentEmoji.FUNDAMENTAL,
        "technical-analyst": AgentEmoji.TECHNICAL,
        "sentiment-analyst": AgentEmoji.SENTIMENT,
        "moderator": AgentEmoji.MODERATOR,
        "judge": AgentEmoji.JUDGE
    }
    
    emoji = emoji_map.get(agent_class, "🤖")
    
    # Extract or enforce action for debate agents
    current_action = ""
    is_analyst = any(role in agent_class for role in [
        "fundamental-analyst", 
        "technical-analyst", 
        "sentiment-analyst"
    ])
    
    if is_analyst:
        # Get previous action for this agent and round
        agent_key = f"{agent_class}-{round_num}"
        prev_round_key = f"{agent_class}-{round_num-1}" if round_num > 1 else None
        previous_action = st.session_state.agent_actions.get(prev_round_key, "")
        
        # Use LLM to extract action from message
        detected_action = extract_action_with_llm(message, agent)
        
        if detected_action:
            action_class = f"action-{detected_action.lower()}"
            current_action = f'<span class="action-badge {action_class}">{detected_action}</span>'
            
            # Store the current action
            st.session_state.agent_actions[agent_key] = detected_action
            
            # Show action change if different from previous round
            if previous_action and previous_action != detected_action:
                current_action = f'<span class="action-badge action-{previous_action.lower()}">{previous_action}</span> <span class="action-change">→</span> {current_action}'
    
    # Add critique indicator and link if targeting another agent
    critique_indicator = ""
    critique_link = ""
    if target:
        critique_indicator = f' <span class="critique-arrow">→ {target}</span>'
        critique_link = f' <span class="critique-link" onclick="document.getElementById(\'msg-{round_num}-{target.lower().replace(" ", "-")}\').scrollIntoView({{behavior: \'smooth\'}})">↩️ Linked</span>'
    
    # Highlight investment actions in message text
    highlighted_message = message
    for action_enum in InvestmentAction:
        action_keyword = action_enum.value
        highlighted_message = highlighted_message.replace(
            action_keyword, 
            f"<strong>{action_keyword}</strong>"
        )
    
    # Format Judge and Moderator messages with markdown-style formatting
    if agent_class in ["judge", "moderator"]:
        import re
        
        # Convert **text** to <strong>text</strong>
        highlighted_message = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', highlighted_message)
        
        # Convert bullet points (• or -) to proper HTML list
        lines = highlighted_message.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            # Check if line starts with bullet point
            if stripped.startswith('•') or (stripped.startswith('-') and len(stripped) > 1 and stripped[1] == ' '):
                if not in_list:
                    formatted_lines.append('<ul style="margin: 0.5rem 0; padding-left: 1.5rem;">')
                    in_list = True
                # Remove bullet and wrap in li
                content = stripped[1:].strip() if stripped.startswith('•') else stripped[2:].strip()
                formatted_lines.append(f'<li style="margin: 0.3rem 0;">{content}</li>')
            else:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                if stripped:  # Only add non-empty lines
                    formatted_lines.append(stripped)  # Use stripped to normalize spacing
                elif not in_list:  # Preserve paragraph breaks outside lists
                    formatted_lines.append('<br>')
        
        if in_list:
            formatted_lines.append('</ul>')
        
        highlighted_message = '<br>'.join(formatted_lines)
        # Clean up excessive breaks
        highlighted_message = re.sub(r'(<br>\s*){3,}', '<br><br>', highlighted_message)
    
    st.markdown(f"""
    <div class="chat-message {agent_class}" id="msg-{round_num}-{agent_class}">
        <div class="agent-name">
            {emoji} <strong>{agent}</strong>{critique_indicator} <span class="round-badge">Round <strong>{round_num}</strong></span>{current_action}{critique_link}
        </div>
        <div>{highlighted_message}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🎯 Stock Debate AI")
    st.markdown("**Multi-Agent Analysis System** • Powered by Google Gemini API")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize orchestrator with version check to ensure updated code is used
        ORCHESTRATOR_VERSION = "2.0"  # Increment when signature changes
        if ('orchestrator' not in st.session_state or 
            st.session_state.get('orchestrator_version') != ORCHESTRATOR_VERSION):
            try:
                st.session_state.orchestrator = DebateOrchestrator()
                st.session_state.orchestrator_version = ORCHESTRATOR_VERSION
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
        
        # Date picker for historical analysis
        st.markdown("**📅 Analysis Date**")
        
        # Get latest available date from technical data
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            technical_data = st.session_state.orchestrator.data_loader.load_technical_data(symbol)
            if technical_data and 'data' in technical_data:
                df = pd.DataFrame(technical_data['data'])
                if 'date' in df.columns and len(df) > 0:
                    df['date'] = pd.to_datetime(df['date'])
                    max_date = df['date'].max().date()
                    min_date = df['date'].min().date()
                else:
                    max_date = datetime.now().date()
                    min_date = max_date - timedelta(days=365)
            else:
                max_date = datetime.now().date()
                min_date = max_date - timedelta(days=365)
        except:
            max_date = datetime.now().date()
            min_date = max_date - timedelta(days=365)
        
        analysis_date = st.date_input(
            "Cutoff Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            help="Agents will analyze data only up to this date. Judge will verify with future data."
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
            st.session_state.force_conclude = False  # Reset force conclude flag
            st.session_state.current_symbol = symbol
            st.session_state.current_timeframe = timeframe
            st.session_state.current_min_rounds = min_rounds
            st.session_state.analysis_date = analysis_date  # Store selected date
        
        # Conclude debate button (only show when debate is running)
        if st.session_state.get('debate_running', False) and not st.session_state.get('debate_complete', False):
            if st.button("⚖️ Conclude Debate Now", type="secondary", use_container_width=True):
                st.session_state.force_conclude = True
                st.info("🔔 Judge will deliver final verdict after current round...")
                st.rerun()
        
        # Data availability
        st.divider()
        st.subheader("📊 Data Status")
        
        # Check data availability for current or selected symbol
        check_symbol = st.session_state.get('current_symbol', symbol)
        financial = st.session_state.orchestrator.data_loader.load_financial_data(check_symbol)
        technical = st.session_state.orchestrator.data_loader.load_technical_data(check_symbol)
        sentiment = st.session_state.orchestrator.data_loader.load_sentiment_data(check_symbol)
        
        st.write("💼 Fundamental:", "✅" if financial else "❌")
        st.write("📈 Technical:", "✅" if technical else "❌")
        st.write("💭 Sentiment:", "✅" if sentiment else "❌")
    
    # Display metrics cards if orchestrator is initialized and symbol is selected
    # Show metrics whenever a symbol is available (either selected or in session)
    display_symbol = st.session_state.get('current_symbol') or symbol if 'orchestrator' in st.session_state else None
    if display_symbol and 'orchestrator' in st.session_state:
        display_metrics_cards(display_symbol, st.session_state.orchestrator)
        st.markdown("---")
    
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
                
                # Define callback to check if user wants to force conclude
                def check_force_conclude():
                    return st.session_state.get('force_conclude', False)
                
                # Stream messages in real-time
                with message_container:
                    for entry in st.session_state.orchestrator.run_debate_streaming(
                        st.session_state.current_symbol,
                        rounds=min_rounds,
                        should_force_conclude=check_force_conclude,
                        cutoff_date=st.session_state.get('analysis_date'),
                        timeframe=st.session_state.get('current_timeframe', '3 months')
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
                import traceback
                error_details = traceback.format_exc()
                print(f"ERROR in debate: {error_details}")  # Log to terminal
                st.error(f"❌ Error during debate: {e}")
                st.error(f"Details: {error_details}")  # Show full traceback in UI
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
