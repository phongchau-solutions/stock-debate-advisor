"""
Technical Analysis Agent
Analyzes price action, indicators, and momentum.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from agents.base_agent import BaseAgent
from analysis_tools import TechnicalAnalysis

logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    """Technical Analysis specialist."""
    
    def __init__(self, llm_service: Any, system_prompt: Optional[str] = None):
        """Initialize technical analyst."""
        if system_prompt is None:
            try:
                with open("prompts/technical.txt", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = """You are a Technical Analysis Expert specializing in Vietnamese stock market patterns.
Analyze charts, indicators (MA, RSI, MACD), trends, and momentum."""
        
        super().__init__(
            name="TechnicalAnalyst",
            role="Technical Analysis Expert",
            llm_service=llm_service,
            system_prompt=system_prompt,
        )
        self.analysis_tool = TechnicalAnalysis(
            base_url="https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/VCI",
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
        )
    
    def analyze(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Perform technical analysis.
        
        Args:
            stock_symbol: Stock ticker
            stock_data: OHLCV and indicators data
            period_days: Analysis period
            
        Returns:
            Analysis with signal, confidence, rationale
        """
        # Fetch technical data using the analysis tool
        technical_data = self.analysis_tool.fetch_technical_one_day()
        stock_data.update(technical_data)
        
        price = stock_data.get("price", 0)
        ma_50 = stock_data.get("ma_50", 0)
        ma_200 = stock_data.get("ma_200", 0)
        rsi = stock_data.get("rsi", 50)
        macd = stock_data.get("macd", 0)
        volume_trend = stock_data.get("volume_trend", "neutral")
        
        # Determine trend
        trend = self._assess_trend(price, ma_50, ma_200)
        
        # Determine signal
        signal, confidence = self._assess_signal(
            trend, rsi, macd, volume_trend, price, ma_50, ma_200
        )
        
        rationale = self._generate_rationale(
            signal, trend, price, ma_50, ma_200, rsi, macd, volume_trend
        )
        
        return {
            "analysis_type": "technical",
            "stock_symbol": stock_symbol,
            "signal": signal,
            "confidence": confidence,
            "rationale": rationale,
            "indicators": {
                "current_price": price,
                "ma_50": ma_50,
                "ma_200": ma_200,
                "rsi": rsi,
                "macd": macd,
                "trend": trend,
            },
        }
    
    def _assess_trend(self, price: float, ma_50: float, ma_200: float) -> str:
        """Assess trend based on moving averages."""
        if price > ma_50 > ma_200:
            return "UPTREND"
        elif price < ma_50 < ma_200:
            return "DOWNTREND"
        else:
            return "CONSOLIDATION"
    
    def _assess_signal(
        self,
        trend: str,
        rsi: float,
        macd: float,
        volume: str,
        price: float,
        ma_50: float,
        ma_200: float,
    ) -> Tuple[str, float]:
        """Assess signal: (signal, confidence)."""
        score = 0
        
        # Trend scoring
        if trend == "UPTREND":
            score += 1.5
        elif trend == "DOWNTREND":
            score -= 1.5
        else:
            score += 0.0
        
        # RSI scoring (30-70 is normal range)
        if rsi < 30:
            score += 1.0  # Oversold, potential bounce
        elif rsi > 70:
            score -= 1.0  # Overbought, potential pullback
        elif 40 < rsi < 60:
            score += 0.3  # Neutral, slight bullish bias
        
        # MACD scoring
        if macd > 0:
            score += 0.8
        elif macd < 0:
            score -= 0.8
        
        # Volume scoring
        if volume == "increasing":
            score += 0.5
        elif volume == "decreasing":
            score -= 0.3
        
        # Price vs MA scoring
        if price > ma_50 > ma_200:
            score += 0.3
        
        # Determine signal and confidence
        if score > 2.0:
            return "BUY", 0.70
        elif score > 0.5:
            return "BUY", 0.55
        elif score < -2.0:
            return "SELL", 0.70
        elif score < -0.5:
            return "SELL", 0.55
        else:
            return "HOLD", 0.65
    
    def _generate_rationale(
        self,
        signal: str,
        trend: str,
        price: float,
        ma_50: float,
        ma_200: float,
        rsi: float,
        macd: float,
        volume: str,
    ) -> str:
        """Generate technical rationale."""
        rationale = f"""
Technical Analysis for {signal} recommendation:

Chart Structure:
- Current Trend: {trend}
- Price Level: {price:.0f}
- MA(50): {ma_50:.0f} | MA(200): {ma_200:.0f}

Indicators:
- RSI: {rsi:.1f} (30=oversold, 70=overbought, neutral=50)
- MACD: {macd:+.3f}
- Volume Trend: {volume}

Analysis:
"""
        if trend == "UPTREND":
            rationale += "• Strong uptrend structure (price > MA50 > MA200)\n"
        elif trend == "DOWNTREND":
            rationale += "• Strong downtrend structure (price < MA50 < MA200)\n"
        else:
            rationale += "• Consolidation pattern - awaiting breakout\n"
        
        if rsi < 30:
            rationale += f"• RSI {rsi:.0f} indicates oversold condition - potential rebound\n"
        elif rsi > 70:
            rationale += f"• RSI {rsi:.0f} indicates overbought condition - watch for pullback\n"
        
        if macd > 0:
            rationale += "• MACD positive - bullish momentum\n"
        else:
            rationale += "• MACD negative - bearish momentum\n"
        
        if volume == "increasing":
            rationale += "• Rising volume supports trend\n"
        elif volume == "decreasing":
            rationale += "• Declining volume suggests weakening momentum\n"
        
        return rationale.strip()
