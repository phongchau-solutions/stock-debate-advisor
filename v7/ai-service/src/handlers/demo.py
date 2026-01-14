from typing import Optional
import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Debate Advisor", layout="wide")

st.title("📊 Stock Debate Advisor")
st.markdown("Multi-agent AI analysis of stocks through iterative debate")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    ticker = st.text_input("Stock Ticker", placeholder="MBB", value="MBB").upper()

with col2:
    timeframe = st.selectbox("Timeframe", ["1 month", "3 months", "6 months", "1 year"])

with col3:
    rounds = st.slider("Max Rounds", 1, 5, 3)

col1, col2 = st.columns(2)
with col1:
    min_rounds = st.slider("Min Rounds", 1, 3, 1)

def load_ohlc_chart(ticker: str) -> go.Figure:
    """Load and plot OHLC data from data store"""
    try:
        from engine import DataLoader
        loader = DataLoader()
        stock_data = loader.load_stock_data(ticker)
        
        if "ohlc_prices" not in stock_data:
            return None
        
        prices = stock_data["ohlc_prices"].get("prices", [])
        if not prices:
            return None
        
        df = pd.DataFrame(prices)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').tail(60)  # Last 60 days
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )])
        
        fig.update_layout(
            title=f"{ticker} - Last 60 Days OHLC",
            yaxis_title="Price (VND)",
            xaxis_title="Date",
            template="plotly_white",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Could not load OHLC data: {e}")
        return None

# Show OHLC chart for selected ticker
st.subheader("📈 Stock Price (Last 60 Days)")
with st.spinner("Loading OHLC chart..."):
    fig = load_ohlc_chart(ticker)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No OHLC data available for {ticker}")

st.divider()

st.subheader("🤖 Multi-Agent Debate Analysis")

if st.button("Start Debate", type="primary"):
    if not ticker:
        st.error("Please enter a ticker")
    else:
        with st.spinner("Agents debating..."):
            try:
                response = requests.post(
                    "http://localhost:8000/debate",
                    json={
                        "ticker": ticker,
                        "timeframe": timeframe,
                        "min_rounds": min_rounds,
                        "max_rounds": rounds
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"Debate complete for {ticker}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Recommendation", data["final_recommendation"])
                    with col2:
                        st.metric("Confidence", data["confidence"])
                    with col3:
                        st.metric("Timeframe", data["timeframe"])
                    with col4:
                        st.metric("Rounds", data["actual_rounds"])
                    
                    st.divider()
                    
                    st.subheader("Debate Rounds")
                    for round_data in data["rounds"]:
                        with st.expander(f"Round {round_data['round_num']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Fundamental**")
                                st.write(round_data["fundamental"][:300])
                            with col2:
                                st.write("**Technical**")
                                st.write(round_data["technical"][:300])
                            with col3:
                                st.write("**Sentiment**")
                                st.write(round_data["sentiment"][:300])
                            st.divider()
                            st.write("**Judge Decision**")
                            st.info(round_data["judge_decision"][:500])
                    
                    st.divider()
                    st.subheader("Final Verdict")
                    st.success(f"**For {data['timeframe']}: {data['final_recommendation']}**")
                    st.write(f"**Confidence:** {data['confidence']}")
                    st.write(f"**Rationale:** {data['rationale']}")
                    st.warning(f"**Risks:** {data['risks']}")
                    st.info(f"**Monitor:** {data['monitor']}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
