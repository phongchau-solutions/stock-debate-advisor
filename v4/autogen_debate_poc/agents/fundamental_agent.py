"""
Fundamental Analysis Agent
Evaluates firm metrics, valuation, and financial health.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from agents.base_agent import BaseAgent
from analysis_tools import FundamentalAnalysis

logger = logging.getLogger(__name__)


class FundamentalAgent(BaseAgent):
    """Fundamental Analysis specialist."""
    
    def __init__(self, llm_service: Any, system_prompt: Optional[str] = None):
        """Initialize fundamental analyst."""
        if system_prompt is None:
            # Load from prompt file
            try:
                with open("prompts/fundamental.txt", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = """You are a Fundamental Analysis Expert specializing in Vietnamese equities.
Evaluate financial health, valuation, growth prospects, and provide investment recommendations."""
        
        super().__init__(
            name="FundamentalAnalyst",
            role="Fundamental Analysis Expert",
            llm_service=llm_service,
            system_prompt=system_prompt,
        )
        self.analysis_tool = FundamentalAnalysis(
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
        Perform fundamental analysis.
        
        Args:
            stock_symbol: Stock ticker
            stock_data: Financial data dict
            period_days: Analysis period
            
        Returns:
            Analysis with signal, confidence, rationale
        """
        # Fetch financial data using the analysis tool
        financial_data = self.analysis_tool.fetch_financial_data()
        stock_data["financials"] = financial_data

        financials = stock_data.get("financials", {})
        price = stock_data.get("price", 0)
        
        # Extract key metrics
        pe_ratio = financials.get("pe_ratio", 0)
        roe = financials.get("roe", 0)
        debt_ratio = financials.get("debt_ratio", 0.5)
        dividend_yield = financials.get("dividend_yield", 0)
        
        # Determine signal
        signal, confidence = self._assess_valuation(
            pe_ratio, roe, debt_ratio, dividend_yield, price
        )
        
        rationale = self._generate_rationale(
            signal, pe_ratio, roe, debt_ratio, dividend_yield
        )
        
        return {
            "analysis_type": "fundamental",
            "stock_symbol": stock_symbol,
            "signal": signal,
            "confidence": confidence,
            "rationale": rationale,
            "metrics": {
                "pe_ratio": pe_ratio,
                "roe": roe,
                "debt_ratio": debt_ratio,
                "dividend_yield": dividend_yield,
                "current_price": price,
            },
        }
    
    def _assess_valuation(
        self,
        pe: float,
        roe: float,
        debt: float,
        div_yield: float,
        price: float,
    ) -> Tuple[str, float]:
        """Assess valuation: (signal, confidence)."""
        score = 0
        
        # P/E assessment
        if 0 < pe < 12:
            score += 1.5  # Undervalued
        elif 12 <= pe < 18:
            score += 0.5  # Fair
        elif pe >= 18:
            score -= 1.0  # Overvalued
        
        # ROE assessment
        if roe > 15:
            score += 1.5  # Strong profitability
        elif roe > 8:
            score += 0.5  # Adequate
        else:
            score -= 1.0  # Weak
        
        # Debt assessment
        if debt < 0.3:
            score += 1.0  # Conservative
        elif debt < 0.6:
            score += 0.3  # Moderate
        else:
            score -= 1.0  # High leverage
        
        # Dividend assessment
        if div_yield > 3:
            score += 0.5  # Good yield
        
        # Determine signal and confidence
        if score > 2.0:
            return "BUY", 0.75
        elif score > 0.5:
            return "BUY", 0.60
        elif score < -1.5:
            return "SELL", 0.75
        elif score < -0.5:
            return "SELL", 0.60
        else:
            return "HOLD", 0.65
    
    def _generate_rationale(
        self,
        signal: str,
        pe: float,
        roe: float,
        debt: float,
        div_yield: float,
    ) -> str:
        """Generate analysis rationale."""
        rationale = f"""
Fundamental Analysis for {signal} recommendation:

Key Metrics:
- P/E Ratio: {pe:.2f}x (market multiple ~15-18x)
- ROE: {roe:.1f}% (quality indicator, target >12%)
- Debt Ratio: {debt:.1%} (leverage, target <50%)
- Dividend Yield: {div_yield:.2f}%

Assessment:
"""
        if pe > 0:
            if pe < 12:
                rationale += f"• Stock trades at attractive valuation ({pe:.1f}x P/E)\n"
            elif pe > 20:
                rationale += f"• Stock appears expensive ({pe:.1f}x P/E)\n"
        
        if roe > 15:
            rationale += f"• Strong profitability (ROE {roe:.1f}% > 15%)\n"
        elif roe < 8:
            rationale += f"• Weak returns (ROE {roe:.1f}% < 8%)\n"
        
        if debt < 0.3:
            rationale += "• Conservative balance sheet with low leverage\n"
        elif debt > 0.6:
            rationale += "• High leverage warrants caution\n"
        
        if div_yield > 3:
            rationale += f"• Attractive dividend yield ({div_yield:.2f}%)\n"
        
        return rationale.strip()
