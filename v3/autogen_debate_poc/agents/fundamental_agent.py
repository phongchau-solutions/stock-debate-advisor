"""
Fundamental Analysis Agent for stock market analysis.
Evaluates financial ratios, valuation metrics, and company health.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FundamentalAgent:
    """Fundamental Analysis Agent for PoC."""
    
    name = "FundamentalAnalyst"
    role = "Fundamental Analysis Expert"

    def __init__(
        self,
        system_prompt: str,
        llm_config: Optional[Dict[str, Any]] = None,
        stock_data: Optional[Dict[str, Any]] = None
    ):
        self.system_prompt = system_prompt
        self.llm_config = llm_config or {}
        self.stock_data = stock_data or {}
        
        logger.info(f"Initialized {self.name} in PoC mode (rule-based analysis)")
    
    def analyze(self, stock_symbol: str, period_days: int = 30) -> Dict[str, Any]:
        """Perform fundamental analysis using stock data."""
        financials = self.stock_data.get("financials", {})
        price = self.stock_data.get("price", 0)
        pe_ratio = self.stock_data.get("PE_ratio", 0)
        roe = self.stock_data.get("ROE", 0)
        
        if not financials and price == 0:
            return self._create_error_response(stock_symbol)
        
        # Valuation assessment
        valuation, bias, confidence = self._assess_valuation(pe_ratio, roe, price)
        
        # Calculate fair value (simple DCF-like)
        fair_value = self._calculate_fair_value(financials, price, roe)
        
        return {
            "analysis_type": "fundamental",
            "stock_symbol": stock_symbol,
            "valuation": valuation,
            "fair_value": float(fair_value),
            "bias": bias,
            "confidence": float(confidence),
            "key_metrics": {
                "pe_ratio": float(pe_ratio),
                "roe": float(roe),
                "dividend_yield": float(self.stock_data.get("dividend_yield", 0))
            },
            "rationale": self._generate_rationale(valuation, pe_ratio, roe, fair_value, price)
        }
    
    def _assess_valuation(self, pe: float, roe: float, price: float) -> tuple:
        """Assess if stock is undervalued, fairly valued, or overvalued."""
        if pe == 0 or roe == 0:
            return "fairly_valued", "hold", 0.5
        
        # Simple valuation logic
        undervalued_score = 0
        overvalued_score = 0
        
        if pe < 12:
            undervalued_score += 1
        elif pe > 25:
            overvalued_score += 1
        
        if roe > 15:
            undervalued_score += 1
        elif roe < 8:
            overvalued_score += 1
        
        if undervalued_score > overvalued_score:
            return "undervalued", "buy", 0.7
        elif overvalued_score > undervalued_score:
            return "overvalued", "sell", 0.7
        else:
            return "fairly_valued", "hold", 0.5
    
    def _calculate_fair_value(self, financials: Dict, price: float, roe: float) -> float:
        """Calculate fair value estimate."""
        if price == 0:
            return 0.0
        
        # Simple approach: adjust price based on ROE vs market average
        avg_roe = 12.0
        adjustment = 1.0 + ((roe - avg_roe) / 100)
        return price * adjustment
    
    def _generate_rationale(self, valuation: str, pe: float, roe: float, fair_value: float, current_price: float) -> str:
        """Generate rationale for fundamental analysis."""
        parts = []
        parts.append(f"Stock appears {valuation} based on fundamental metrics.")
        parts.append(f"P/E ratio of {pe:.1f} {'below' if pe < 15 else 'above'} market average.")
        parts.append(f"ROE of {roe:.1f}% indicates {'strong' if roe > 15 else 'moderate' if roe > 10 else 'weak'} profitability.")
        
        if fair_value > 0 and current_price > 0:
            upside = ((fair_value / current_price) - 1) * 100
            parts.append(f"Fair value estimate suggests {abs(upside):.1f}% {'upside' if upside > 0 else 'downside'}.")
        
        return " ".join(parts)
    
    def _create_error_response(self, stock_symbol: str) -> Dict[str, Any]:
        """Create error response when data unavailable."""
        return {
            "analysis_type": "fundamental",
            "stock_symbol": stock_symbol,
            "valuation": "fairly_valued",
            "fair_value": 0.0,
            "bias": "hold",
            "confidence": 0.1,
            "key_metrics": {},
            "rationale": "Insufficient fundamental data",
            "error": "no_data"
        }

