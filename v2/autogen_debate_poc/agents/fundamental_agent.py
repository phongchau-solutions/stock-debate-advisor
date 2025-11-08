"""
Fundamental Analysis Agent for Vietnamese Stock Market
"""
import json
import requests
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import concurrent.futures

from . import BaseFinancialAgent


class FundamentalAgent(BaseFinancialAgent):
    """Agent specialized in fundamental analysis."""
    
    def __init__(self, gemini_api_key: str, **kwargs):
        system_message = """
        You are a Fundamental Analysis Expert specializing in Vietnamese stock market.
        
        Your role:
        - Analyze financial ratios, earnings, and company valuation
        - Evaluate P/E, P/B, ROE, debt ratios, and growth metrics
        - Assess company's financial health and competitive position
        - Provide fair value estimates and investment recommendations
        
        Output format should be structured JSON with:
        {
            "valuation": "undervalued|overvalued|fairly_valued",
            "fair_value": float,
            "bias": "buy|hold|sell",
            "confidence": float (0-1),
            "key_metrics": {
                "pe_ratio": float,
                "pb_ratio": float,
                "roe": float,
                "debt_to_equity": float,
                "revenue_growth": float
            },
            "rationale": "Detailed fundamental reasoning",
            "risk_factors": ["list", "of", "risks"]
        }
        
        Consider Vietnamese market conditions, economic factors, and sector-specific dynamics.
        """
        
        super().__init__(
            name="FundamentalAnalyst",
            role="Fundamental Analysis Expert",
            system_message=system_message,
            gemini_api_key=gemini_api_key,
            **kwargs
        )
        self.logger = logging.getLogger(__name__)

    async def analyze(self, stock_symbol: str, period: str = "3mo", timeout: int = 30) -> Dict[str, Any]:
        """
        Standardized analyze method for fundamental analysis.
        
        Args:
            stock_symbol: Stock symbol to analyze (e.g., 'VNM', 'VIC')
            period: Analysis period (not used for fundamental but kept for interface compatibility)
            timeout: Timeout in seconds for data fetching
            
        Returns:
            Dict containing structured fundamental analysis results
        """
        try:
            self.logger.info(f"Starting fundamental analysis for {stock_symbol}")
            
            # Use asyncio timeout for the entire analysis
            return await asyncio.wait_for(
                self._perform_fundamental_analysis(stock_symbol, period),
                timeout=timeout
            )
            
        except asyncio.TimeoutError:
            self.logger.error(f"Fundamental analysis timeout for {stock_symbol}")
            return self._create_error_response("Analysis timeout", stock_symbol)
        except Exception as e:
            self.logger.error(f"Fundamental analysis failed for {stock_symbol}: {str(e)}")
            return self._create_error_response(str(e), stock_symbol)

    async def _perform_fundamental_analysis(self, stock_symbol: str, period: str) -> Dict[str, Any]:
        """Perform the actual fundamental analysis."""
        # Fetch fundamental data with timeout
        financial_data = await self._fetch_financial_data_async(stock_symbol)
        
        if not financial_data:
            return self._create_error_response("No fundamental data available", stock_symbol)
        
        # Calculate key financial metrics
        metrics = self._calculate_fundamental_metrics(financial_data)
        
        # Generate AI-powered analysis
        ai_rationale = await self._generate_ai_fundamental_analysis(stock_symbol, financial_data, metrics)
        
        # Determine investment recommendation
        valuation = self._determine_valuation(metrics)
        fair_value = self._calculate_fair_value(financial_data, metrics)
        bias = self._extract_bias(ai_rationale)
        confidence = self._calculate_confidence(metrics, financial_data)
        risk_factors = self._identify_risk_factors(financial_data, metrics)
        
        # Structure the response
        return {
            "analysis_type": "fundamental",
            "stock_symbol": stock_symbol,
            "timestamp": datetime.now().isoformat(),
            "valuation": valuation,
            "fair_value": fair_value,
            "current_price": self._estimate_current_price(financial_data),
            "bias": bias,
            "confidence": confidence,
            "key_metrics": metrics,
            "rationale": ai_rationale,
            "risk_factors": risk_factors,
            "company_profile": {
                "name": financial_data.get('company_name', stock_symbol),
                "sector": financial_data.get('sector', 'Unknown'),
                "market_cap": financial_data.get('market_cap', 'N/A')
            },
            "data_quality": self._assess_data_quality(financial_data, metrics)
        }

    def _create_error_response(self, error_message: str, stock_symbol: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "analysis_type": "fundamental",
            "stock_symbol": stock_symbol,
            "timestamp": datetime.now().isoformat(),
            "valuation": "fairly_valued",
            "fair_value": 0.0,
            "current_price": 0.0,
            "bias": "hold",
            "confidence": 0.1,
            "key_metrics": {},
            "rationale": f"Analysis failed: {error_message}",
            "risk_factors": ["Data unavailable", "Analysis incomplete"],
            "company_profile": {"name": stock_symbol, "sector": "Unknown", "market_cap": "N/A"},
            "data_quality": "poor",
            "error": error_message
        }
    
    async def analyze_data(self, stock_symbol: str, period: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fundamental analysis on company data."""
        try:
            # Fetch fundamental data
            financial_data = await self._fetch_financial_data(stock_symbol)
            
            if not financial_data:
                return {
                    "valuation": "fairly_valued",
                    "fair_value": 0,
                    "bias": "hold",
                    "confidence": 0.1,
                    "error": "No fundamental data available"
                }
            
            # Calculate key metrics
            metrics = self._calculate_fundamental_metrics(financial_data)
            
            # Generate analysis using Gemini
            analysis_prompt = f"""
            Analyze the following fundamental data for {stock_symbol}:
            
            Company: {financial_data.get('company_name', stock_symbol)}
            Sector: {financial_data.get('sector', 'Unknown')}
            Market Cap: {financial_data.get('market_cap', 'N/A')}
            
            Key Financial Metrics:
            {json.dumps(metrics, indent=2)}
            
            Financial Highlights:
            - Revenue: {financial_data.get('revenue', 'N/A')}
            - Net Income: {financial_data.get('net_income', 'N/A')}
            - Total Assets: {financial_data.get('total_assets', 'N/A')}
            - Total Debt: {financial_data.get('total_debt', 'N/A')}
            - Book Value: {financial_data.get('book_value', 'N/A')}
            
            Recent developments and news:
            {financial_data.get('recent_news', 'No recent news available')}
            
            Provide a comprehensive fundamental analysis with investment recommendation.
            Consider the Vietnamese market context and economic environment.
            """
            
            response = self.generate_llm_response(analysis_prompt)
            
            # Structure the analysis
            structured_analysis = {
                "valuation": self._determine_valuation(metrics),
                "fair_value": self._calculate_fair_value(financial_data, metrics),
                "bias": self._extract_bias(response),
                "confidence": self._calculate_confidence(metrics),
                "key_metrics": metrics,
                "rationale": response,
                "risk_factors": self._identify_risk_factors(financial_data, metrics),
                "company_profile": {
                    "name": financial_data.get('company_name', stock_symbol),
                    "sector": financial_data.get('sector', 'Unknown'),
                    "market_cap": financial_data.get('market_cap', 'N/A')
                }
            }
            
            return structured_analysis
            
        except Exception as e:
            self.logger.error(f"Fundamental analysis error: {e}")
            return {
                "valuation": "fairly_valued",
                "fair_value": 0,
                "bias": "hold",
                "confidence": 0.1,
                "error": str(e)
            }
    
    async def _fetch_financial_data_async(self, symbol: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
        """Async wrapper for fetching financial data with timeout."""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(executor, self._fetch_financial_data_sync, symbol)
                return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching financial data for {symbol}")
            return None
        except Exception as e:
            self.logger.error(f"Error in async financial data fetch for {symbol}: {e}")
            return None

    def _fetch_financial_data_sync(self, symbol: str) -> Dict[str, Any]:
        """Synchronous financial data fetching for threading."""
        try:
            # For demo purposes, create realistic financial data
            # In production, this would connect to Vietcap API or other data sources
            return self._create_demo_financial_data(symbol)
        except Exception as e:
            self.logger.error(f"Error fetching financial data for {symbol}: {e}")
            return {}

    async def _generate_ai_fundamental_analysis(self, stock_symbol: str, financial_data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate AI-powered fundamental analysis rationale."""
        try:
            analysis_prompt = f"""
            Provide comprehensive fundamental analysis for {stock_symbol}:
            
            Company: {financial_data.get('company_name', stock_symbol)}
            Sector: {financial_data.get('sector', 'Unknown')}
            Market Cap: {financial_data.get('market_cap', 'N/A')}
            
            Key Financial Metrics:
            {json.dumps(metrics, indent=2)}
            
            Financial Highlights:
            - Revenue: {financial_data.get('revenue', 'N/A')}
            - Net Income: {financial_data.get('net_income', 'N/A')}
            - Total Assets: {financial_data.get('total_assets', 'N/A')}
            - Total Debt: {financial_data.get('total_debt', 'N/A')}
            - Book Value: {financial_data.get('book_value', 'N/A')}
            
            Recent developments:
            {financial_data.get('recent_news', 'No recent news available')}
            
            Consider Vietnamese market conditions and provide investment recommendation.
            Focus on financial health, valuation attractiveness, and growth prospects.
            """
            
            return self.generate_llm_response(analysis_prompt)
            
        except Exception as e:
            self.logger.error(f"Error generating AI analysis: {e}")
            return f"Fundamental analysis for {stock_symbol}: Unable to generate detailed analysis due to system error."

    def _estimate_current_price(self, financial_data: Dict[str, Any]) -> float:
        """Estimate current stock price from market cap and shares."""
        try:
            def extract_numeric(value_str):
                if isinstance(value_str, (int, float)):
                    return float(value_str)
                if isinstance(value_str, str):
                    return float(value_str.split()[0].replace(',', ''))
                return 0.0
            
            market_cap = extract_numeric(financial_data.get('market_cap', 0))
            shares_outstanding = extract_numeric(financial_data.get('shares_outstanding', 1))
            
            if market_cap > 0 and shares_outstanding > 0:
                return market_cap / shares_outstanding
            else:
                return 50000.0  # Default estimate in VND
                
        except Exception as e:
            self.logger.error(f"Error estimating current price: {e}")
            return 50000.0

    def _assess_data_quality(self, financial_data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Assess the quality of financial data available."""
        if not financial_data:
            return "poor"
        
        # Check completeness of financial data
        required_fields = ['revenue', 'net_income', 'total_assets', 'book_value', 'company_name']
        available_fields = sum(1 for field in required_fields if financial_data.get(field) and financial_data[field] != 'N/A')
        
        # Check metrics completeness
        complete_metrics = sum(1 for v in metrics.values() if v is not None and v != 'N/A')
        total_metrics = len(metrics)
        
        completeness_score = (available_fields / len(required_fields) + complete_metrics / max(total_metrics, 1)) / 2
        
        if completeness_score >= 0.8:
            return "excellent"
        elif completeness_score >= 0.6:
            return "good"
        elif completeness_score >= 0.4:
            return "fair"
        else:
            return "poor"

    async def _fetch_financial_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial data from available sources."""
        try:
            # For demo purposes, create realistic financial data
            # In production, this would connect to Vietcap API or other data sources
            
            demo_data = self._create_demo_financial_data(symbol)
            return demo_data
            
        except Exception as e:
            self.logger.error(f"Error fetching financial data for {symbol}: {e}")
            return {}
    
    def _create_demo_financial_data(self, symbol: str) -> Dict[str, Any]:
        """Create demo financial data for testing."""
        
        # Vietnamese stock examples
        company_profiles = {
            'VNM': {
                'company_name': 'Vietnam Dairy Products Joint Stock Company (Vinamilk)',
                'sector': 'Consumer Staples',
                'market_cap': '365,000 billion VND',
                'revenue': '62,000 billion VND',
                'net_income': '12,500 billion VND',
                'total_assets': '45,000 billion VND',
                'total_debt': '8,500 billion VND',
                'book_value': '28,000 billion VND',
                'shares_outstanding': '2.17 billion',
                'recent_news': 'Vinamilk reports strong Q3 2024 results, expanding regional presence'
            },
            'VIC': {
                'company_name': 'Vingroup Joint Stock Company',
                'sector': 'Real Estate',
                'market_cap': '280,000 billion VND',
                'revenue': '145,000 billion VND',
                'net_income': '8,200 billion VND',
                'total_assets': '385,000 billion VND',
                'total_debt': '180,000 billion VND',
                'book_value': '125,000 billion VND',
                'shares_outstanding': '5.2 billion',
                'recent_news': 'Vingroup focuses on electric vehicles and technology investments'
            },
            'VCB': {
                'company_name': 'Joint Stock Commercial Bank for Foreign Trade of Vietnam',
                'sector': 'Banking',
                'market_cap': '820,000 billion VND',
                'revenue': '85,000 billion VND',
                'net_income': '28,500 billion VND',
                'total_assets': '1,450,000 billion VND',
                'total_debt': '1,200,000 billion VND',
                'book_value': '185,000 billion VND',
                'shares_outstanding': '4.65 billion',
                'recent_news': 'Vietcombank maintains strong credit growth and asset quality'
            }
        }
        
        return company_profiles.get(symbol, {
            'company_name': f'{symbol} Corporation',
            'sector': 'Unknown',
            'market_cap': '50,000 billion VND',
            'revenue': '25,000 billion VND',
            'net_income': '3,500 billion VND',
            'total_assets': '45,000 billion VND',
            'total_debt': '15,000 billion VND',
            'book_value': '22,000 billion VND',
            'shares_outstanding': '1 billion',
            'recent_news': 'No recent news available'
        })
    
    def _calculate_fundamental_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key fundamental metrics."""
        metrics = {}
        
        try:
            # Extract numeric values (removing "billion VND" etc.)
            def extract_numeric(value_str):
                if isinstance(value_str, str):
                    return float(value_str.split()[0].replace(',', ''))
                return float(value_str) if value_str else 0
            
            revenue = extract_numeric(financial_data.get('revenue', 0))
            net_income = extract_numeric(financial_data.get('net_income', 0))
            total_assets = extract_numeric(financial_data.get('total_assets', 0))
            total_debt = extract_numeric(financial_data.get('total_debt', 0))
            book_value = extract_numeric(financial_data.get('book_value', 0))
            market_cap = extract_numeric(financial_data.get('market_cap', 0))
            shares_outstanding = extract_numeric(financial_data.get('shares_outstanding', 1))
            
            # Calculate ratios
            if net_income > 0 and shares_outstanding > 0:
                eps = net_income / shares_outstanding
                current_price = market_cap / shares_outstanding if market_cap > 0 else 50  # Estimated
                metrics['pe_ratio'] = current_price / eps if eps > 0 else None
            else:
                metrics['pe_ratio'] = None
            
            # P/B ratio
            book_value_per_share = book_value / shares_outstanding if shares_outstanding > 0 else 0
            if book_value_per_share > 0:
                current_price = market_cap / shares_outstanding if market_cap > 0 else 50
                metrics['pb_ratio'] = current_price / book_value_per_share
            else:
                metrics['pb_ratio'] = None
            
            # ROE
            if book_value > 0:
                metrics['roe'] = (net_income / book_value) * 100
            else:
                metrics['roe'] = None
            
            # Debt to Equity
            equity = total_assets - total_debt if total_assets > total_debt else book_value
            if equity > 0:
                metrics['debt_to_equity'] = total_debt / equity
            else:
                metrics['debt_to_equity'] = None
            
            # Revenue growth (simulated)
            metrics['revenue_growth'] = 8.5  # Assuming 8.5% growth
            
            # Profit margin
            if revenue > 0:
                metrics['profit_margin'] = (net_income / revenue) * 100
            else:
                metrics['profit_margin'] = None
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            metrics = {
                "pe_ratio": 15.0,
                "pb_ratio": 2.0,
                "roe": 12.0,
                "debt_to_equity": 0.4,
                "revenue_growth": 5.0,
                "profit_margin": 8.0
            }
        
        return metrics
    
    def _determine_valuation(self, metrics: Dict[str, Any]) -> str:
        """Determine if stock is undervalued, overvalued, or fairly valued."""
        pe_ratio = metrics.get('pe_ratio')
        pb_ratio = metrics.get('pb_ratio')
        roe = metrics.get('roe')
        
        undervalued_signals = 0
        overvalued_signals = 0
        
        # P/E analysis
        if pe_ratio:
            if pe_ratio < 12:
                undervalued_signals += 1
            elif pe_ratio > 25:
                overvalued_signals += 1
        
        # P/B analysis
        if pb_ratio:
            if pb_ratio < 1.5:
                undervalued_signals += 1
            elif pb_ratio > 3:
                overvalued_signals += 1
        
        # ROE analysis
        if roe:
            if roe > 15:
                undervalued_signals += 1
            elif roe < 8:
                overvalued_signals += 1
        
        if undervalued_signals > overvalued_signals:
            return "undervalued"
        elif overvalued_signals > undervalued_signals:
            return "overvalued"
        else:
            return "fairly_valued"
    
    def _calculate_fair_value(self, financial_data: Dict[str, Any], metrics: Dict[str, Any]) -> float:
        """Calculate estimated fair value."""
        try:
            def extract_numeric(value_str):
                if isinstance(value_str, str):
                    return float(value_str.split()[0].replace(',', ''))
                return float(value_str) if value_str else 0
            
            market_cap = extract_numeric(financial_data.get('market_cap', 0))
            shares_outstanding = extract_numeric(financial_data.get('shares_outstanding', 1))
            
            current_price = market_cap / shares_outstanding if market_cap > 0 else 50000
            
            # Simple DCF-like approach
            growth_rate = metrics.get('revenue_growth', 5) / 100
            fair_value = current_price * (1 + growth_rate * 2)  # 2-year forward
            
            return float(fair_value)
            
        except Exception as e:
            self.logger.error(f"Error calculating fair value: {e}")
            return 50000.0  # Default value
    
    def _extract_bias(self, response: str) -> str:
        """Extract investment bias from LLM response."""
        response_lower = response.lower()
        if any(word in response_lower for word in ['buy', 'purchase', 'invest', 'bullish', 'positive']):
            return "buy"
        elif any(word in response_lower for word in ['sell', 'avoid', 'bearish', 'negative']):
            return "sell"
        else:
            return "hold"
    
    def _calculate_confidence(self, metrics: Dict[str, Any], financial_data: Optional[Dict[str, Any]] = None) -> float:
        """Calculate confidence based on data quality and metric consistency."""
        confidence = 0.6  # Base confidence
        
        # Check data completeness
        complete_metrics = sum(1 for v in metrics.values() if v is not None and v != 'N/A')
        total_metrics = len(metrics)
        
        if total_metrics > 0:
            completeness = complete_metrics / total_metrics
            confidence += completeness * 0.3
        
        # Check metric reasonableness
        pe_ratio = metrics.get('pe_ratio')
        if pe_ratio and 5 < pe_ratio < 50:  # Reasonable P/E range
            confidence += 0.1
        
        # Factor in financial data quality
        if financial_data:
            required_fields = ['revenue', 'net_income', 'total_assets']
            available_fields = sum(1 for field in required_fields if financial_data.get(field))
            if available_fields == len(required_fields):
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _identify_risk_factors(self, financial_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        # High debt
        debt_to_equity = metrics.get('debt_to_equity')
        if debt_to_equity and debt_to_equity > 1.0:
            risks.append("High debt-to-equity ratio indicating financial leverage risk")
        
        # Low profitability
        roe = metrics.get('roe')
        if roe and roe < 8:
            risks.append("Low return on equity suggesting inefficient use of shareholder capital")
        
        # High valuation
        pe_ratio = metrics.get('pe_ratio')
        if pe_ratio and pe_ratio > 30:
            risks.append("High P/E ratio indicating potential overvaluation")
        
        # Market-specific risks
        risks.append("Vietnamese market volatility and regulatory changes")
        risks.append("Currency exchange rate fluctuations (VND/USD)")
        
        sector = financial_data.get('sector', '')
        if 'real estate' in sector.lower():
            risks.append("Real estate market cyclicality and government policy changes")
        elif 'banking' in sector.lower():
            risks.append("Interest rate sensitivity and credit risk exposure")
        
        return risks[:5]  # Limit to top 5 risks