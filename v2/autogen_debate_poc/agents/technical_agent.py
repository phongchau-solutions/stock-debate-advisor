"""
Technical Analysis Agent for Vietnamese Stock Market
"""
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
import yfinance as yf
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from . import BaseFinancialAgent


class TechnicalAgent(BaseFinancialAgent):
    """Agent specialized in technical analysis."""
    
    def __init__(self, gemini_api_key: str, **kwargs):
        system_message = """
        You are a Technical Analysis Expert specializing in Vietnamese stock market.
        
        Your role:
        - Analyze price trends, volume patterns, and technical indicators
        - Provide bullish/bearish signals based on OHLCV data
        - Calculate support/resistance levels and price targets
        - Assess momentum using RSI, MACD, moving averages
        
        Output format should be structured JSON with:
        {
            "signal": "bullish|bearish|neutral",
            "target_price": float,
            "confidence": float (0-1),
            "key_indicators": {
                "rsi": float,
                "macd_signal": "bullish|bearish",
                "trend": "upward|downward|sideways",
                "volume_trend": "increasing|decreasing|stable"
            },
            "rationale": "Detailed technical reasoning",
            "timeframe": "30d"
        }
        
        Be specific about Vietnamese market conditions and provide actionable insights.
        """
        
        super().__init__(
            name="TechnicalAnalyst",
            role="Technical Analysis Expert",
            system_message=system_message,
            gemini_api_key=gemini_api_key,
            **kwargs
        )
        self.logger = logging.getLogger(__name__)
        self.vietcap_base_url = "https://mt.vietcap.com.vn/api"
        self.request_timeout = 10
    
    async def analyze(self, stock: str, period: str) -> Dict[str, Any]:
        """
        Main analysis method - standardized interface.
        
        Args:
            stock: Vietnamese stock symbol (e.g., 'VNM', 'VIC')
            period: Analysis period ('1mo', '3mo', '6mo', '1y')
            
        Returns:
            Dict with keys: signal, confidence, rationale, sources, indicators
        """
        try:
            self.logger.info(f"Technical analysis starting for {stock} over {period}")
            
            # Get OHLCV data with timeout handling
            ohlcv_data = await self._get_ohlcv_data_async(stock, period)
            
            if ohlcv_data is None or len(ohlcv_data) < 20:
                return await self._get_fallback_analysis(stock, period)
            
            # Calculate all technical indicators
            indicators = self._calculate_all_indicators(ohlcv_data)
            
            # Generate trading signal
            signal_analysis = self._generate_trading_signal(indicators, ohlcv_data)
            
            # Get AI-powered rationale
            rationale = await self._generate_ai_rationale(stock, indicators, signal_analysis)
            
            # Structure final output
            return {
                "signal": signal_analysis["signal"],  # "buy", "hold", "sell"
                "confidence": signal_analysis["confidence"],  # 0.0 - 1.0
                "rationale": rationale,
                "sources": ["vietcap_api", "yfinance", "technical_indicators"],
                "indicators": {
                    "rsi": indicators.get("rsi", 50.0),
                    "macd_signal": indicators.get("macd_signal", "neutral"),
                    "sma_20": indicators.get("sma_20", 0.0),
                    "sma_50": indicators.get("sma_50", 0.0),
                    "support_level": signal_analysis.get("support", 0.0),
                    "resistance_level": signal_analysis.get("resistance", 0.0)
                },
                "target_price": signal_analysis.get("target_price", 0.0),
                "timeframe": period,
                "timestamp": datetime.now().isoformat(),
                "agent": "TechnicalAnalyst"
            }
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed for {stock}: {e}")
            return await self._get_fallback_analysis(stock, period)

    async def analyze_data(self, stock_symbol: str, period: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return await self.analyze(stock_symbol, period)

    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators."""
        indicators = {}
        
        try:
            close_prices = data['Close']
            high_prices = data['High'] 
            low_prices = data['Low']
            volumes = data['Volume']
            
            # RSI (Relative Strength Index)
            indicators['rsi'] = self._calculate_rsi(close_prices)
            
            # Moving Averages
            indicators['sma_20'] = float(close_prices.rolling(20).mean().iloc[-1])
            indicators['sma_50'] = float(close_prices.rolling(50).mean().iloc[-1]) if len(data) >= 50 else None
            indicators['ema_12'] = float(close_prices.ewm(span=12).mean().iloc[-1])
            indicators['ema_26'] = float(close_prices.ewm(span=26).mean().iloc[-1])
            
            # MACD
            macd_data = self._calculate_macd(close_prices)
            indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self._calculate_bollinger_bands(close_prices)
            indicators.update(bb_data)
            
            # Volume indicators
            indicators['volume_sma'] = float(volumes.rolling(20).mean().iloc[-1])
            indicators['volume_trend'] = "increasing" if volumes.iloc[-1] > indicators['volume_sma'] else "decreasing"
            
            # Support and Resistance levels
            support_resistance = self._calculate_support_resistance(high_prices, low_prices, close_prices)
            indicators.update(support_resistance)
            
            # Price trend analysis
            indicators['price_trend'] = self._analyze_price_trend(close_prices, indicators)
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return self._get_default_indicators()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50.0  # Neutral RSI

    def _calculate_macd(self, prices: pd.Series) -> Dict[str, Any]:
        """Calculate MACD indicator."""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd_line': float(macd_line.iloc[-1]),
                'macd_signal_line': float(signal_line.iloc[-1]),
                'macd_histogram': float(histogram.iloc[-1]),
                'macd_signal': "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish"
            }
        except:
            return {
                'macd_line': 0.0,
                'macd_signal_line': 0.0, 
                'macd_histogram': 0.0,
                'macd_signal': "neutral"
            }

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        try:
            sma = prices.rolling(period).mean()
            std = prices.rolling(period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = prices.iloc[-1]
            upper = float(upper_band.iloc[-1])
            lower = float(lower_band.iloc[-1])
            middle = float(sma.iloc[-1])
            
            # Calculate position within bands
            band_position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
            
            return {
                'bb_upper': upper,
                'bb_middle': middle,
                'bb_lower': lower,
                'bb_position': float(band_position)
            }
        except:
            return {'bb_upper': 0.0, 'bb_middle': 0.0, 'bb_lower': 0.0, 'bb_position': 0.5}

    def _calculate_support_resistance(self, highs: pd.Series, lows: pd.Series, closes: pd.Series) -> Dict[str, float]:
        """Calculate support and resistance levels."""
        try:
            # Simple method: recent highs/lows
            recent_high = float(highs.tail(20).max())
            recent_low = float(lows.tail(20).min())
            current_price = float(closes.iloc[-1])
            
            # More sophisticated: pivot points
            pivot = (recent_high + recent_low + current_price) / 3
            resistance_1 = 2 * pivot - recent_low
            support_1 = 2 * pivot - recent_high
            
            return {
                'support_level': float(min(recent_low, support_1)),
                'resistance_level': float(max(recent_high, resistance_1)),
                'pivot_point': float(pivot)
            }
        except:
            return {'support_level': 0.0, 'resistance_level': 0.0, 'pivot_point': 0.0}

    def _analyze_price_trend(self, prices: pd.Series, indicators: Dict[str, Any]) -> str:
        """Analyze overall price trend."""
        try:
            current_price = prices.iloc[-1]
            sma_20 = indicators.get('sma_20', current_price)
            sma_50 = indicators.get('sma_50', current_price)
            
            if current_price > sma_20 and (sma_50 is None or sma_20 > sma_50):
                return "upward"
            elif current_price < sma_20 and (sma_50 is None or sma_20 < sma_50):
                return "downward"
            else:
                return "sideways"
        except:
            return "sideways"

    def _generate_trading_signal(self, indicators: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trading signal based on indicators."""
        try:
            signals = []
            confidence_factors = []
            
            current_price = float(data['Close'].iloc[-1])
            
            # RSI signal
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                signals.append('buy')
                confidence_factors.append(0.8)
            elif rsi > 70:
                signals.append('sell')
                confidence_factors.append(0.8)
            else:
                signals.append('hold')
                confidence_factors.append(0.3)
            
            # MACD signal
            macd_signal = indicators.get('macd_signal', 'neutral')
            if macd_signal == 'bullish':
                signals.append('buy')
                confidence_factors.append(0.7)
            elif macd_signal == 'bearish':
                signals.append('sell')
                confidence_factors.append(0.7)
            
            # Moving average signal
            sma_20 = indicators.get('sma_20', current_price)
            if current_price > sma_20 * 1.02:  # 2% above SMA
                signals.append('buy')
                confidence_factors.append(0.6)
            elif current_price < sma_20 * 0.98:  # 2% below SMA
                signals.append('sell')
                confidence_factors.append(0.6)
            
            # Bollinger Bands signal
            bb_position = indicators.get('bb_position', 0.5)
            if bb_position < 0.2:  # Near lower band
                signals.append('buy')
                confidence_factors.append(0.5)
            elif bb_position > 0.8:  # Near upper band
                signals.append('sell')
                confidence_factors.append(0.5)
            
            # Aggregate signals
            buy_signals = signals.count('buy')
            sell_signals = signals.count('sell')
            hold_signals = signals.count('hold')
            
            if buy_signals > sell_signals and buy_signals > hold_signals:
                final_signal = 'buy'
            elif sell_signals > buy_signals and sell_signals > hold_signals:
                final_signal = 'sell'
            else:
                final_signal = 'hold'
            
            # Calculate confidence
            total_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            signal_strength = max(buy_signals, sell_signals, hold_signals) / len(signals)
            final_confidence = min(total_confidence * signal_strength, 1.0)
            
            # Calculate target price
            support = indicators.get('support_level', current_price * 0.95)
            resistance = indicators.get('resistance_level', current_price * 1.05)
            
            if final_signal == 'buy':
                target_price = resistance
            elif final_signal == 'sell':
                target_price = support
            else:
                target_price = current_price
            
            return {
                'signal': final_signal,
                'confidence': float(final_confidence),
                'target_price': float(target_price),
                'support': float(support),
                'resistance': float(resistance),
                'signal_details': {
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'hold_signals': hold_signals
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")
            return {
                'signal': 'hold',
                'confidence': 0.5,
                'target_price': float(data['Close'].iloc[-1]),
                'support': 0.0,
                'resistance': 0.0,
                'signal_details': {}
            }

    async def _generate_ai_rationale(self, stock: str, indicators: Dict[str, Any], signal_analysis: Dict[str, Any]) -> str:
        """Generate AI-powered analysis rationale."""
        try:
            prompt = f"""
            Provide technical analysis rationale for Vietnamese stock {stock}:
            
            Technical Indicators:
            - RSI: {indicators.get('rsi', 50):.1f}
            - MACD Signal: {indicators.get('macd_signal', 'neutral')}
            - Price vs SMA20: {indicators.get('sma_20', 0):.0f}
            - Bollinger Band Position: {indicators.get('bb_position', 0.5):.2f}
            - Price Trend: {indicators.get('price_trend', 'sideways')}
            - Volume Trend: {indicators.get('volume_trend', 'stable')}
            
            Signal: {signal_analysis['signal'].upper()}
            Confidence: {signal_analysis['confidence']:.1%}
            Target: {signal_analysis['target_price']:.0f}
            
            Provide a concise technical rationale (100-150 words) explaining the signal based on these indicators.
            Focus on Vietnamese market context and actionable insights.
            """
            
            rationale = self.generate_llm_response(prompt)
            return rationale if rationale else self._get_default_rationale(signal_analysis['signal'])
            
        except Exception as e:
            self.logger.error(f"Error generating AI rationale: {e}")
            return self._get_default_rationale(signal_analysis['signal'])

    def _get_default_rationale(self, signal: str) -> str:
        """Get default rationale based on signal."""
        rationales = {
            'buy': "Technical indicators show oversold conditions with potential for upward momentum. RSI and MACD suggest accumulation opportunity.",
            'sell': "Technical indicators indicate overbought conditions with potential downward pressure. Consider profit-taking or position reduction.",
            'hold': "Mixed technical signals suggest sideways movement. Wait for clearer directional indicators before making trading decisions."
        }
        return rationales.get(signal, "Technical analysis inconclusive. Monitor for clearer signals.")

    def _get_default_indicators(self) -> Dict[str, Any]:
        """Get default indicators when calculation fails."""
        return {
            'rsi': 50.0,
            'sma_20': 0.0,
            'sma_50': 0.0,
            'macd_signal': 'neutral',
            'volume_trend': 'stable',
            'price_trend': 'sideways',
            'support_level': 0.0,
            'resistance_level': 0.0
        }

    async def _get_fallback_analysis(self, stock: str, period: str) -> Dict[str, Any]:
        """Fallback analysis when data fetching fails."""
        return {
            "signal": "hold",
            "confidence": 0.3,
            "rationale": f"Unable to fetch reliable data for {stock}. Analysis based on limited information suggests maintaining current position until better data becomes available.",
            "sources": ["fallback_analysis"],
            "indicators": self._get_default_indicators(),
            "target_price": 0.0,
            "timeframe": period,
            "timestamp": datetime.now().isoformat(),
            "agent": "TechnicalAnalyst",
            "error": "data_fetch_failed"
        }
    
    async def _fetch_stock_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch stock data from available sources."""
        try:
            # Try to use yfinance with .VN suffix for Vietnamese stocks
            vn_symbol = f"{symbol}.VN"
            stock = yf.Ticker(vn_symbol)
            
            # Convert period to yfinance format
            if "day" in period.lower():
                days = int(period.split()[0])
                yf_period = f"{days}d" if days <= 60 else "3mo"
            else:
                yf_period = "1mo"
            
            data = stock.history(period=yf_period)
            
            if data.empty:
                # Fallback: create dummy data for demo
                self.logger.warning(f"No data found for {symbol}, creating demo data")
                return self._create_demo_data()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return self._create_demo_data()
    
    def _create_demo_data(self) -> pd.DataFrame:
        """Create demo OHLCV data for testing."""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        # Generate realistic stock price movements
        base_price = 50000  # VND
        prices = []
        current_price = base_price
        
        for _ in dates:
            # Random walk with slight upward bias
            change = pd.np.random.normal(0.002, 0.03)  # 0.2% average gain, 3% volatility
            current_price *= (1 + change)
            prices.append(current_price)
        
        data = pd.DataFrame({
            'Open': [p * pd.np.random.normal(1, 0.01) for p in prices],
            'High': [p * pd.np.random.normal(1.02, 0.01) for p in prices],
            'Low': [p * pd.np.random.normal(0.98, 0.01) for p in prices],
            'Close': prices,
            'Volume': [pd.np.random.randint(100000, 1000000) for _ in prices]
        }, index=dates)
        
        return data
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        indicators = {}
        
        try:
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = float(100 - (100 / (1 + rs.iloc[-1])))
            
            # Moving averages
            indicators['sma_20'] = float(data['Close'].rolling(20).mean().iloc[-1])
            indicators['sma_50'] = float(data['Close'].rolling(50).mean().iloc[-1]) if len(data) >= 50 else None
            
            # MACD
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            indicators['macd'] = float(macd_line.iloc[-1])
            indicators['macd_signal'] = "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish"
            
            # Volume trend
            vol_avg = data['Volume'].rolling(10).mean()
            indicators['volume_trend'] = "increasing" if data['Volume'].iloc[-1] > vol_avg.iloc[-1] else "decreasing"
            
            # Price trend
            current_price = data['Close'].iloc[-1]
            if indicators['sma_20']:
                if current_price > indicators['sma_20']:
                    indicators['trend'] = "upward"
                elif current_price < indicators['sma_20'] * 0.98:
                    indicators['trend'] = "downward"
                else:
                    indicators['trend'] = "sideways"
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            indicators = {
                "rsi": 50.0,
                "macd_signal": "neutral",
                "trend": "sideways",
                "volume_trend": "stable"
            }
        
        return indicators
    
    def _extract_signal(self, response: str) -> str:
        """Extract trading signal from LLM response."""
        response_lower = response.lower()
        if any(word in response_lower for word in ['buy', 'bullish', 'positive', 'upward']):
            return "bullish"
        elif any(word in response_lower for word in ['sell', 'bearish', 'negative', 'downward']):
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_target_price(self, data: pd.DataFrame) -> float:
        """Calculate target price based on technical levels."""
        current_price = data['Close'].iloc[-1]
        
        # Simple target based on recent high/low and trend
        recent_high = data['High'].tail(20).max()
        recent_low = data['Low'].tail(20).min()
        
        # Target is 5% above current for bullish, 5% below for bearish
        if current_price > (recent_high + recent_low) / 2:
            return float(current_price * 1.05)
        else:
            return float(current_price * 0.95)
    
    def _calculate_confidence(self, indicators: Dict[str, Any]) -> float:
        """Calculate confidence score based on indicator alignment."""
        confidence = 0.5  # Base confidence
        
        # RSI confirmation
        rsi = indicators.get('rsi', 50)
        if 30 < rsi < 70:  # Not overbought/oversold
            confidence += 0.1
        
        # MACD confirmation
        if indicators.get('macd_signal') in ['bullish', 'bearish']:
            confidence += 0.2
        
        # Trend confirmation
        if indicators.get('trend') in ['upward', 'downward']:
            confidence += 0.2
        
        return min(confidence, 1.0)