"""
Technical Analysis Agent for stock market analysis.
Analyzes price trends, technical indicators, and provides trading signals.
"""
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalAgent:
    """Technical Analysis Agent for PoC."""
    
    name = "TechnicalAnalyst"
    role = "Technical Analysis Expert"

    def __init__(
        self,
        system_prompt: str,
        llm_config: Optional[Dict[str, Any]] = None,
        stock_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Technical Agent.
        
        Args:
            system_prompt: System prompt defining agent behavior
            llm_config: LLM configuration (not used in PoC mode)
            stock_data: Preloaded stock data from service
        """
        self.system_prompt = system_prompt
        self.llm_config = llm_config or {}
        self.stock_data = stock_data or {}
        
        logger.info(f"Initialized {self.name} in PoC mode (rule-based analysis)")
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate MACD indicator."""
        if len(prices) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line.iloc[-1]),
            "signal": float(signal_line.iloc[-1]),
            "histogram": float(histogram.iloc[-1])
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            current = float(prices.iloc[-1]) if len(prices) > 0 else 0.0
            return {"upper": current, "middle": current, "lower": current, "position": 0.5}
        
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (2 * std)
        lower = middle - (2 * std)
        
        current_price = float(prices.iloc[-1])
        upper_val = float(upper.iloc[-1])
        lower_val = float(lower.iloc[-1])
        middle_val = float(middle.iloc[-1])
        
        # Calculate position within bands (0 = lower, 0.5 = middle, 1 = upper)
        band_width = upper_val - lower_val
        position = (current_price - lower_val) / band_width if band_width > 0 else 0.5
        
        return {
            "upper": upper_val,
            "middle": middle_val,
            "lower": lower_val,
            "position": float(position)
        }
    
    def analyze(self, stock_symbol: str, period_days: int = 30, debate_history: List[Dict[str, Any]] = None, current_round: int = 1) -> Dict[str, Any]:
        """
        Perform technical analysis with debate context awareness.
        
        Args:
            stock_symbol: Stock symbol to analyze
            period_days: Number of days for historical data
            debate_history: List of previous messages from all agents
            current_round: Current debate round number
            
        Returns structured analysis with signal, indicators, and rationale.
        """
        ohlcv = self.stock_data.get("ohlcv", pd.DataFrame())
        
        if ohlcv.empty or "Close" not in ohlcv.columns:
            logger.warning(f"No OHLCV data available for {stock_symbol}")
            return self._create_error_response(stock_symbol)
        
        close = ohlcv["Close"].dropna()
        
        # Format debate history for context
        debate_context = self._format_debate_history(debate_history or [], current_round)
        
        # Calculate indicators
        rsi = self._calculate_rsi(close)
        macd = self._calculate_macd(close)
        bb = self._calculate_bollinger_bands(close)
        
        # Moving averages
        ma_5 = float(close.rolling(window=5).mean().iloc[-1]) if len(close) >= 5 else float(close.iloc[-1])
        ma_20 = float(close.rolling(window=20).mean().iloc[-1]) if len(close) >= 20 else float(close.iloc[-1])
        
        current_price = float(close.iloc[-1])
        
        # Generate signal
        signal, confidence = self._generate_signal(rsi, macd, bb, ma_5, ma_20)
        
        # Calculate target price
        target_multiplier = 1.05 if signal == "buy" else 0.95 if signal == "sell" else 1.0
        target_price = current_price * target_multiplier
        stop_loss = current_price * 0.95 if signal == "buy" else current_price * 1.05 if signal == "sell" else current_price
        
        return {
            "analysis_type": "technical",
            "stock_symbol": stock_symbol,
            "signal": signal,
            "target_price": float(target_price),
            "stop_loss": float(stop_loss),
            "current_price": float(current_price),
            "confidence": float(confidence),
            "indicators": {
                "rsi": float(rsi),
                "macd": macd,
                "bollinger_bands": bb,
                "ma_5": float(ma_5),
                "ma_20": float(ma_20)
            },
            "rationale": self._generate_rationale(signal, rsi, macd, bb, ma_5, ma_20, debate_context)
        }
    
    def _format_debate_history(self, debate_history: List[Dict[str, Any]], current_round: int) -> str:
        """Format debate history into readable context for LLM."""
        if not debate_history:
            return "Round 1: No previous debate history."
        
        context_lines = [f"\n=== Debate History (Round {current_round}) ==="]
        for msg in debate_history:
            agent_name = msg.get("agent", "Unknown")
            round_num = msg.get("round", 0)
            payload = msg.get("payload", {})
            
            # Extract key points from each agent's previous statement
            if payload.get("analysis_type") == "technical":
                signal = payload.get("signal", "N/A")
                context_lines.append(f"[R{round_num}] {agent_name}: Signal={signal}, Confidence={payload.get('confidence', 0):.2f}")
            elif payload.get("analysis_type") == "fundamental":
                bias = payload.get("bias", "N/A")
                valuation = payload.get("valuation", "N/A")
                context_lines.append(f"[R{round_num}] {agent_name}: Bias={bias}, Valuation={valuation}")
            elif payload.get("analysis_type") == "sentiment":
                sentiment = payload.get("sentiment_label", "N/A")
                context_lines.append(f"[R{round_num}] {agent_name}: Sentiment={sentiment}")
            
            # Include rationale if available
            rationale = payload.get("rationale", "")
            if rationale:
                context_lines.append(f"  Rationale: {rationale[:150]}...")  # Truncate for brevity
        
        return "\n".join(context_lines)
    
    def _generate_signal(self, rsi: float, macd: Dict, bb: Dict, ma_5: float, ma_20: float) -> tuple:
        """Generate trading signal based on indicators."""
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if rsi < 30:
            buy_signals += 2
        elif rsi > 70:
            sell_signals += 2
        
        # MACD signals
        if macd["histogram"] > 0 and macd["macd"] > macd["signal"]:
            buy_signals += 1
        elif macd["histogram"] < 0 and macd["macd"] < macd["signal"]:
            sell_signals += 1
        
        # Bollinger Band signals
        if bb["position"] < 0.2:
            buy_signals += 1
        elif bb["position"] > 0.8:
            sell_signals += 1
        
        # Moving average crossover
        if ma_5 > ma_20:
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Determine signal and confidence
        total_signals = buy_signals + sell_signals
        if buy_signals > sell_signals:
            signal = "buy"
            confidence = min(0.9, 0.5 + (buy_signals / total_signals) * 0.4)
        elif sell_signals > buy_signals:
            signal = "sell"
            confidence = min(0.9, 0.5 + (sell_signals / total_signals) * 0.4)
        else:
            signal = "hold"
            confidence = 0.5
        
        return signal, confidence
    
    def _generate_rationale(self, signal: str, rsi: float, macd: Dict, bb: Dict, ma_5: float, ma_20: float, debate_context: str = "") -> str:
        """Generate human-readable rationale for the signal, considering debate context."""
        parts = []
        
        # Reference debate context if available
        if debate_context and "Round" not in debate_context.split("\n")[0]:
            parts.append(f"Considering previous debate points...")
        
        if signal == "buy":
            parts.append(f"Technical indicators suggest BUY opportunity.")
        elif signal == "sell":
            parts.append(f"Technical indicators suggest SELL signal.")
        else:
            parts.append(f"Technical indicators are mixed, recommending HOLD.")
        
        parts.append(f"RSI at {rsi:.1f} {'(oversold)' if rsi < 30 else '(overbought)' if rsi > 70 else '(neutral)'}.")
        parts.append(f"MACD {'bullish' if macd['histogram'] > 0 else 'bearish'} with histogram at {macd['histogram']:.2f}.")
        parts.append(f"Price at {bb['position']*100:.0f}% of Bollinger Band range.")
        
        return " ".join(parts)
    
    def _create_error_response(self, stock_symbol: str) -> Dict[str, Any]:
        """Create error response when data unavailable."""
        return {
            "analysis_type": "technical",
            "stock_symbol": stock_symbol,
            "signal": "hold",
            "target_price": 0.0,
            "stop_loss": 0.0,
            "current_price": 0.0,
            "confidence": 0.1,
            "indicators": {},
            "rationale": "Insufficient data for technical analysis",
            "error": "no_data"
        }
