"""
Fundamental Analysis Module
Analyzes financial statements and company fundamentals.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """Performs fundamental analysis on financial data."""

    def __init__(self):
        """Initialize fundamental analyzer."""
        pass

    def analyze(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis.
        
        Args:
            financial_data: Dict containing balance_sheet, income_statement, 
                          cash_flow, metrics, ratios
        
        Returns:
            Dict with analysis results, scores, and recommendations
        """
        try:
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": "fundamental",
            }

            # Analyze profitability
            result["profitability"] = self._analyze_profitability(financial_data)
            
            # Analyze liquidity
            result["liquidity"] = self._analyze_liquidity(financial_data)
            
            # Analyze solvency
            result["solvency"] = self._analyze_solvency(financial_data)
            
            # Analyze efficiency
            result["efficiency"] = self._analyze_efficiency(financial_data)
            
            # Analyze valuation
            result["valuation"] = self._analyze_valuation(financial_data)
            
            # Calculate overall fundamental score
            result["overall_score"] = self._calculate_overall_score(result)
            
            # Generate recommendation
            result["recommendation"] = self._generate_recommendation(result)
            
            # Key insights
            result["insights"] = self._generate_insights(result)
            
            return result

        except Exception as e:
            logger.error(f"Error in fundamental analysis: {e}")
            raise

    def _analyze_profitability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profitability metrics."""
        metrics = data.get("metrics", {})
        income = data.get("income_statement", {})
        
        return {
            "roe": metrics.get("roe", 0),  # Return on Equity
            "roa": metrics.get("roa", 0),  # Return on Assets
            "profit_margin": metrics.get("netProfitMargin", 0),
            "gross_margin": metrics.get("grossMargin", 0),
            "operating_margin": metrics.get("operatingMargin", 0),
            "score": self._score_profitability(metrics),
            "trend": "improving",  # Calculate trend from historical data
        }

    def _analyze_liquidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze liquidity metrics."""
        ratios = data.get("ratios", {})
        balance_sheet = data.get("balance_sheet", {})
        
        current_ratio = ratios.get("currentRatio", 1.5)
        quick_ratio = ratios.get("quickRatio", 1.0)
        
        return {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_ratio": ratios.get("cashRatio", 0.5),
            "working_capital": balance_sheet.get("workingCapital", 0),
            "score": self._score_liquidity(current_ratio, quick_ratio),
            "assessment": self._assess_liquidity(current_ratio, quick_ratio),
        }

    def _analyze_solvency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze solvency and leverage metrics."""
        ratios = data.get("ratios", {})
        
        debt_to_equity = ratios.get("debtToEquity", 0.5)
        debt_to_assets = ratios.get("debtToAssets", 0.3)
        
        return {
            "debt_to_equity": debt_to_equity,
            "debt_to_assets": debt_to_assets,
            "interest_coverage": ratios.get("interestCoverage", 5.0),
            "equity_ratio": ratios.get("equityRatio", 0.5),
            "score": self._score_solvency(debt_to_equity, debt_to_assets),
            "assessment": self._assess_solvency(debt_to_equity),
        }

    def _analyze_efficiency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze operational efficiency metrics."""
        ratios = data.get("ratios", {})
        
        return {
            "asset_turnover": ratios.get("assetTurnover", 1.0),
            "inventory_turnover": ratios.get("inventoryTurnover", 5.0),
            "receivables_turnover": ratios.get("receivablesTurnover", 6.0),
            "days_sales_outstanding": ratios.get("dso", 60),
            "score": self._score_efficiency(ratios),
        }

    def _analyze_valuation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze valuation metrics."""
        ratios = data.get("ratios", {})
        metrics = data.get("metrics", {})
        
        pe_ratio = ratios.get("pe", 15.0)
        pb_ratio = ratios.get("pb", 2.0)
        
        return {
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "ps_ratio": ratios.get("ps", 1.5),
            "pcf_ratio": ratios.get("pcf", 10.0),
            "ev_ebitda": ratios.get("evToEbitda", 12.0),
            "dividend_yield": metrics.get("dividendYield", 0.03),
            "score": self._score_valuation(pe_ratio, pb_ratio),
            "assessment": self._assess_valuation(pe_ratio, pb_ratio),
        }

    def _score_profitability(self, metrics: Dict[str, Any]) -> float:
        """Score profitability (0-100)."""
        roe = metrics.get("roe", 0)
        roa = metrics.get("roa", 0)
        margin = metrics.get("netProfitMargin", 0)
        
        score = 0
        # ROE scoring
        if roe > 20:
            score += 40
        elif roe > 15:
            score += 30
        elif roe > 10:
            score += 20
        elif roe > 5:
            score += 10
        
        # ROA scoring
        if roa > 10:
            score += 30
        elif roa > 5:
            score += 20
        elif roa > 2:
            score += 10
        
        # Margin scoring
        if margin > 15:
            score += 30
        elif margin > 10:
            score += 20
        elif margin > 5:
            score += 10
        
        return min(score, 100)

    def _score_liquidity(self, current_ratio: float, quick_ratio: float) -> float:
        """Score liquidity (0-100)."""
        score = 0
        
        # Current ratio scoring
        if 1.5 <= current_ratio <= 3.0:
            score += 50
        elif 1.0 <= current_ratio < 1.5:
            score += 30
        elif current_ratio > 3.0:
            score += 35
        
        # Quick ratio scoring
        if quick_ratio >= 1.0:
            score += 50
        elif quick_ratio >= 0.7:
            score += 30
        elif quick_ratio >= 0.5:
            score += 15
        
        return min(score, 100)

    def _score_solvency(self, debt_to_equity: float, debt_to_assets: float) -> float:
        """Score solvency (0-100)."""
        score = 0
        
        # Debt to equity scoring (lower is better)
        if debt_to_equity < 0.5:
            score += 50
        elif debt_to_equity < 1.0:
            score += 35
        elif debt_to_equity < 2.0:
            score += 20
        
        # Debt to assets scoring
        if debt_to_assets < 0.3:
            score += 50
        elif debt_to_assets < 0.5:
            score += 35
        elif debt_to_assets < 0.7:
            score += 20
        
        return min(score, 100)

    def _score_efficiency(self, ratios: Dict[str, Any]) -> float:
        """Score operational efficiency (0-100)."""
        asset_turnover = ratios.get("assetTurnover", 1.0)
        
        score = 0
        if asset_turnover > 2.0:
            score = 100
        elif asset_turnover > 1.5:
            score = 80
        elif asset_turnover > 1.0:
            score = 60
        elif asset_turnover > 0.5:
            score = 40
        else:
            score = 20
        
        return score

    def _score_valuation(self, pe_ratio: float, pb_ratio: float) -> float:
        """Score valuation (0-100, higher means more attractive)."""
        score = 0
        
        # PE ratio scoring (lower is better for value)
        if pe_ratio < 10:
            score += 50
        elif pe_ratio < 15:
            score += 40
        elif pe_ratio < 20:
            score += 25
        elif pe_ratio < 30:
            score += 10
        
        # PB ratio scoring
        if pb_ratio < 1.0:
            score += 50
        elif pb_ratio < 2.0:
            score += 35
        elif pb_ratio < 3.0:
            score += 20
        elif pb_ratio < 5.0:
            score += 10
        
        return min(score, 100)

    def _assess_liquidity(self, current_ratio: float, quick_ratio: float) -> str:
        """Assess liquidity health."""
        if current_ratio >= 2.0 and quick_ratio >= 1.0:
            return "Excellent"
        elif current_ratio >= 1.5 and quick_ratio >= 0.7:
            return "Good"
        elif current_ratio >= 1.0:
            return "Adequate"
        else:
            return "Concerning"

    def _assess_solvency(self, debt_to_equity: float) -> str:
        """Assess solvency health."""
        if debt_to_equity < 0.5:
            return "Strong"
        elif debt_to_equity < 1.0:
            return "Healthy"
        elif debt_to_equity < 2.0:
            return "Moderate"
        else:
            return "High Risk"

    def _assess_valuation(self, pe_ratio: float, pb_ratio: float) -> str:
        """Assess valuation attractiveness."""
        if pe_ratio < 15 and pb_ratio < 2.0:
            return "Undervalued"
        elif pe_ratio < 20 and pb_ratio < 3.0:
            return "Fair Value"
        else:
            return "Expensive"

    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted overall fundamental score."""
        weights = {
            "profitability": 0.30,
            "liquidity": 0.20,
            "solvency": 0.20,
            "efficiency": 0.15,
            "valuation": 0.15,
        }
        
        total_score = 0
        for category, weight in weights.items():
            if category in analysis and "score" in analysis[category]:
                total_score += analysis[category]["score"] * weight
        
        # Determine rating
        if total_score >= 80:
            rating = "Strong Buy"
        elif total_score >= 65:
            rating = "Buy"
        elif total_score >= 50:
            rating = "Hold"
        elif total_score >= 35:
            rating = "Sell"
        else:
            rating = "Strong Sell"
        
        return {
            "score": round(total_score, 2),
            "rating": rating,
            "confidence": "High" if total_score > 60 or total_score < 40 else "Medium",
        }

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate investment recommendation."""
        score = analysis["overall_score"]["score"]
        rating = analysis["overall_score"]["rating"]
        
        if score >= 75:
            return f"{rating}: Strong fundamentals with excellent profitability and financial health."
        elif score >= 60:
            return f"{rating}: Good fundamentals with solid financial metrics."
        elif score >= 45:
            return f"{rating}: Average fundamentals, monitor key metrics closely."
        else:
            return f"{rating}: Weak fundamentals, significant concerns identified."

    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate key insights from analysis."""
        insights = []
        
        # Profitability insights
        prof_score = analysis["profitability"]["score"]
        if prof_score >= 70:
            insights.append("Strong profitability metrics indicate efficient operations")
        elif prof_score < 40:
            insights.append("Profitability concerns require attention")
        
        # Liquidity insights
        liquidity = analysis["liquidity"]["assessment"]
        if liquidity in ["Excellent", "Good"]:
            insights.append(f"{liquidity} liquidity position supports short-term obligations")
        elif liquidity == "Concerning":
            insights.append("Liquidity position may pose short-term risks")
        
        # Solvency insights
        solvency = analysis["solvency"]["assessment"]
        if solvency in ["Strong", "Healthy"]:
            insights.append(f"{solvency} balance sheet with manageable debt levels")
        elif solvency == "High Risk":
            insights.append("High leverage poses financial risk")
        
        # Valuation insights
        valuation = analysis["valuation"]["assessment"]
        insights.append(f"Stock appears {valuation.lower()} based on valuation metrics")
        
        return insights
