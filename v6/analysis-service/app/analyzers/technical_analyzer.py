"""
Technical Analysis Module
Analyzes price action and technical indicators.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Performs technical analysis on price data."""

    def __init__(self):
        """Initialize technical analyzer."""
        pass

    def analyze(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis.
        
        Args:
            price_data: DataFrame with columns: date, open, high, low, close, volume
        
        Returns:
            Dict with analysis results, signals, and recommendations
        """
        try:
            if price_data.empty:
                raise ValueError("Price data is empty")

            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": "technical",
            }

            # Calculate indicators
            result["indicators"] = self._calculate_indicators(price_data)
            
            # Analyze trend
            result["trend"] = self._analyze_trend(price_data, result["indicators"])
            
            # Analyze momentum
            result["momentum"] = self._analyze_momentum(result["indicators"])
            
            # Analyze volume
            result["volume"] = self._analyze_volume(price_data)
            
            # Identify support/resistance
            result["levels"] = self._identify_support_resistance(price_data)
            
            # Generate signals
            result["signals"] = self._generate_signals(result)
            
            # Calculate overall technical score
            result["overall_score"] = self._calculate_overall_score(result)
            
            # Generate recommendation
            result["recommendation"] = self._generate_recommendation(result)
            
            return result

        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            raise

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        indicators = {}
        
        # Moving Averages
        indicators["sma_20"] = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
        indicators["sma_50"] = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
        indicators["sma_200"] = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
        
        indicators["ema_12"] = close.ewm(span=12).mean().iloc[-1]
        indicators["ema_26"] = close.ewm(span=26).mean().iloc[-1]
        
        # RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        indicators["rsi"] = rsi.iloc[-1] if len(rsi) > 0 else 50
        
        # MACD
        macd_line = indicators["ema_12"] - indicators["ema_26"]
        signal_line = pd.Series([macd_line] * len(close)).ewm(span=9).mean().iloc[-1]
        indicators["macd"] = macd_line
        indicators["macd_signal"] = signal_line
        indicators["macd_histogram"] = macd_line - signal_line
        
        # Bollinger Bands
        sma_20_series = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        indicators["bb_upper"] = (sma_20_series + 2 * std_20).iloc[-1] if len(sma_20_series) >= 20 else None
        indicators["bb_middle"] = sma_20_series.iloc[-1] if len(sma_20_series) >= 20 else None
        indicators["bb_lower"] = (sma_20_series - 2 * std_20).iloc[-1] if len(sma_20_series) >= 20 else None
        
        # Stochastic Oscillator
        low_14 = low.rolling(window=14).min()
        high_14 = high.rolling(window=14).max()
        k_percent = 100 * ((close - low_14) / (high_14 - low_14))
        indicators["stoch_k"] = k_percent.iloc[-1] if len(k_percent) > 0 else 50
        indicators["stoch_d"] = k_percent.rolling(window=3).mean().iloc[-1] if len(k_percent) >= 3 else 50
        
        # ATR (Average True Range)
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        indicators["atr"] = tr.rolling(window=14).mean().iloc[-1] if len(tr) >= 14 else 0
        
        # Current price
        indicators["current_price"] = close.iloc[-1]
        
        return indicators

    def _analyze_trend(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price trend."""
        current_price = indicators["current_price"]
        sma_20 = indicators.get("sma_20")
        sma_50 = indicators.get("sma_50")
        sma_200 = indicators.get("sma_200")
        
        trend = {
            "direction": "neutral",
            "strength": "weak",
            "score": 50,
        }
        
        # Determine trend direction
        if sma_20 and sma_50:
            if current_price > sma_20 > sma_50:
                trend["direction"] = "bullish"
                trend["strength"] = "strong"
                trend["score"] = 80
            elif current_price > sma_20:
                trend["direction"] = "bullish"
                trend["strength"] = "moderate"
                trend["score"] = 65
            elif current_price < sma_20 < sma_50:
                trend["direction"] = "bearish"
                trend["strength"] = "strong"
                trend["score"] = 20
            elif current_price < sma_20:
                trend["direction"] = "bearish"
                trend["strength"] = "moderate"
                trend["score"] = 35
        
        # Check for golden/death cross
        if sma_50 and sma_200:
            if sma_50 > sma_200:
                trend["pattern"] = "Golden Cross"
            elif sma_50 < sma_200:
                trend["pattern"] = "Death Cross"
        
        return trend

    def _analyze_momentum(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze momentum indicators."""
        rsi = indicators["rsi"]
        macd_histogram = indicators["macd_histogram"]
        stoch_k = indicators["stoch_k"]
        
        momentum = {
            "rsi_value": rsi,
            "macd_histogram": macd_histogram,
            "stochastic": stoch_k,
        }
        
        # RSI assessment
        if rsi > 70:
            momentum["rsi_signal"] = "overbought"
            momentum["rsi_score"] = 30
        elif rsi > 60:
            momentum["rsi_signal"] = "strong"
            momentum["rsi_score"] = 70
        elif rsi > 50:
            momentum["rsi_signal"] = "bullish"
            momentum["rsi_score"] = 60
        elif rsi > 40:
            momentum["rsi_signal"] = "bearish"
            momentum["rsi_score"] = 40
        elif rsi > 30:
            momentum["rsi_signal"] = "weak"
            momentum["rsi_score"] = 30
        else:
            momentum["rsi_signal"] = "oversold"
            momentum["rsi_score"] = 70  # Oversold can be a buy signal
        
        # MACD assessment
        if macd_histogram > 0:
            momentum["macd_signal"] = "bullish"
        else:
            momentum["macd_signal"] = "bearish"
        
        # Stochastic assessment
        if stoch_k > 80:
            momentum["stoch_signal"] = "overbought"
        elif stoch_k < 20:
            momentum["stoch_signal"] = "oversold"
        else:
            momentum["stoch_signal"] = "neutral"
        
        # Overall momentum score
        momentum["score"] = momentum["rsi_score"]
        
        return momentum

    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns."""
        volume = df['volume']
        close = df['close']
        
        avg_volume = volume.mean()
        recent_volume = volume.iloc[-5:].mean()
        latest_volume = volume.iloc[-1]
        
        # Price change
        price_change = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
        
        volume_analysis = {
            "average_volume": avg_volume,
            "recent_volume": recent_volume,
            "latest_volume": latest_volume,
            "volume_trend": "increasing" if recent_volume > avg_volume else "decreasing",
        }
        
        # Volume confirmation
        if latest_volume > avg_volume * 1.5 and price_change > 2:
            volume_analysis["signal"] = "strong_buy_volume"
            volume_analysis["score"] = 80
        elif latest_volume > avg_volume * 1.5 and price_change < -2:
            volume_analysis["signal"] = "strong_sell_volume"
            volume_analysis["score"] = 20
        elif latest_volume > avg_volume:
            volume_analysis["signal"] = "above_average"
            volume_analysis["score"] = 60
        else:
            volume_analysis["signal"] = "below_average"
            volume_analysis["score"] = 40
        
        return volume_analysis

    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify support and resistance levels."""
        close = df['close']
        high = df['high']
        low = df['low']
        
        current_price = close.iloc[-1]
        
        # Simple support/resistance based on recent highs/lows
        recent_high = high.iloc[-20:].max() if len(high) >= 20 else high.max()
        recent_low = low.iloc[-20:].min() if len(low) >= 20 else low.min()
        
        return {
            "current_price": current_price,
            "resistance": recent_high,
            "support": recent_low,
            "distance_to_resistance": ((recent_high - current_price) / current_price) * 100,
            "distance_to_support": ((current_price - recent_low) / current_price) * 100,
        }

    def _generate_signals(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate trading signals."""
        signals = []
        
        indicators = analysis["indicators"]
        trend = analysis["trend"]
        momentum = analysis["momentum"]
        
        # RSI signals
        rsi = indicators["rsi"]
        if rsi < 30:
            signals.append({"type": "buy", "indicator": "RSI", "reason": "Oversold condition"})
        elif rsi > 70:
            signals.append({"type": "sell", "indicator": "RSI", "reason": "Overbought condition"})
        
        # MACD signals
        if indicators["macd_histogram"] > 0 and momentum["macd_signal"] == "bullish":
            signals.append({"type": "buy", "indicator": "MACD", "reason": "Bullish crossover"})
        elif indicators["macd_histogram"] < 0 and momentum["macd_signal"] == "bearish":
            signals.append({"type": "sell", "indicator": "MACD", "reason": "Bearish crossover"})
        
        # Trend signals
        if trend["direction"] == "bullish" and trend["strength"] == "strong":
            signals.append({"type": "buy", "indicator": "Trend", "reason": "Strong uptrend"})
        elif trend["direction"] == "bearish" and trend["strength"] == "strong":
            signals.append({"type": "sell", "indicator": "Trend", "reason": "Strong downtrend"})
        
        return signals

    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted overall technical score."""
        weights = {
            "trend": 0.35,
            "momentum": 0.30,
            "volume": 0.20,
            "signals": 0.15,
        }
        
        total_score = 0
        total_score += analysis["trend"]["score"] * weights["trend"]
        total_score += analysis["momentum"]["score"] * weights["momentum"]
        total_score += analysis["volume"]["score"] * weights["volume"]
        
        # Signals weight
        buy_signals = len([s for s in analysis["signals"] if s["type"] == "buy"])
        sell_signals = len([s for s in analysis["signals"] if s["type"] == "sell"])
        if buy_signals > sell_signals:
            total_score += 70 * weights["signals"]
        elif sell_signals > buy_signals:
            total_score += 30 * weights["signals"]
        else:
            total_score += 50 * weights["signals"]
        
        # Determine rating
        if total_score >= 75:
            rating = "Strong Buy"
        elif total_score >= 60:
            rating = "Buy"
        elif total_score >= 45:
            rating = "Hold"
        elif total_score >= 30:
            rating = "Sell"
        else:
            rating = "Strong Sell"
        
        return {
            "score": round(total_score, 2),
            "rating": rating,
            "confidence": "High" if len(analysis["signals"]) >= 3 else "Medium",
        }

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate trading recommendation."""
        score = analysis["overall_score"]["score"]
        rating = analysis["overall_score"]["rating"]
        trend = analysis["trend"]["direction"]
        
        buy_signals = len([s for s in analysis["signals"] if s["type"] == "buy"])
        sell_signals = len([s for s in analysis["signals"] if s["type"] == "sell"])
        
        if score >= 70:
            return f"{rating}: Strong technical setup with {buy_signals} buy signals. {trend.capitalize()} trend confirmed."
        elif score >= 55:
            return f"{rating}: Positive technical indicators with {trend} bias."
        elif score >= 45:
            return f"{rating}: Mixed technical signals, wait for clearer direction."
        else:
            return f"{rating}: Weak technical setup with {sell_signals} sell signals. Consider caution."
