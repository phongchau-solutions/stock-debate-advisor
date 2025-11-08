"""
Prompt Service for Dynamic LLM Prompt Management
Loads, fills, and manages agent-specific system prompts.
"""
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptService:
    """Service for loading and managing agent prompts with dynamic data injection."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_cache: Dict[str, str] = {}
        
    def load_prompt(self, agent_type: str) -> str:
        """
        Load prompt template for specified agent type.
        
        Args:
            agent_type: One of 'technical', 'fundamental', 'sentiment', 'moderator'
            
        Returns:
            Prompt template string
        """
        if agent_type in self.prompts_cache:
            return self.prompts_cache[agent_type]
        
        prompt_file = self.prompts_dir / f"{agent_type}_prompt.txt"
        
        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}, using default")
            return self._get_default_prompt(agent_type)
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
            self.prompts_cache[agent_type] = prompt
            logger.info(f"Loaded prompt for {agent_type} from {prompt_file}")
            return prompt
        except Exception as e:
            logger.error(f"Error loading prompt for {agent_type}: {e}")
            return self._get_default_prompt(agent_type)
    
    def inject_data(self, prompt_template: str, data_dict: Dict[str, Any]) -> str:
        """
        Inject data into prompt template using {variable} placeholders.
        
        Args:
            prompt_template: Template with {placeholders}
            data_dict: Dictionary of values to inject
            
        Returns:
            Filled prompt string
        """
        try:
            return prompt_template.format(**data_dict)
        except KeyError as e:
            logger.warning(f"Missing key in data injection: {e}")
            # Return template with available substitutions
            for key, value in data_dict.items():
                prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
            return prompt_template
    
    def _get_default_prompt(self, agent_type: str) -> str:
        """Fallback default prompts if files not found."""
        defaults = {
            "technical": """You are a Technical Analysis Expert for Vietnamese stock market.

Analyze price trends, volume, and technical indicators (RSI, MACD, Moving Averages, Bollinger Bands).
Provide clear BUY/HOLD/SELL signals with confidence levels and specific price targets.

Your analysis should be:
- Data-driven and objective
- Based on technical indicators
- Include specific entry/exit points
- Consider risk/reward ratios""",
            
            "fundamental": """You are a Fundamental Analysis Expert for Vietnamese stock market.

Analyze financial ratios, earnings, valuation metrics (P/E, P/B, ROE, Debt/Equity).
Evaluate company's financial health and competitive position.

Your analysis should be:
- Focus on long-term value
- Consider industry benchmarks
- Assess management quality
- Provide fair value estimates""",
            
            "sentiment": """You are a Market Sentiment Analyst for Vietnamese stock market.

Analyze news, social media, and market sentiment from VnEconomy, WSJ, and other sources.
Determine overall market mood and its impact on stock performance.

Your analysis should be:
- Consider both local and international sentiment
- Identify key themes and narratives
- Assess sentiment strength and reliability
- Flag potential market-moving events""",
            
            "moderator": """You are a Debate Moderator for multi-agent financial analysis.

Your responsibilities:
- Orchestrate fair and balanced debate rounds
- Ensure all agents contribute meaningfully
- Challenge weak arguments and probe assumptions
- Synthesize diverse viewpoints into consensus
- Make final investment recommendation

Be impartial but rigorous in your moderation."""
        }
        
        return defaults.get(agent_type, "You are a financial analysis agent. Provide expert insights.")
    
    def prepare_technical_context(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context dictionary for technical agent prompt."""
        ohlcv = stock_data.get("ohlcv")
        
        context = {
            "symbol": stock_data.get("symbol", "N/A"),
            "current_price": f"{stock_data.get('price', 0):.2f}",
            "volume": f"{stock_data.get('volume', 0):,}",
            "data_source": stock_data.get("data_source", "unknown"),
        }
        
        # Add technical indicators if OHLCV available
        if ohlcv is not None and not ohlcv.empty:
            close = ohlcv['Close'] if 'Close' in ohlcv.columns else None
            if close is not None and len(close) > 0:
                context["price_change_pct"] = f"{((close.iloc[-1] / close.iloc[0] - 1) * 100):.2f}%"
                context["price_trend"] = "upward" if close.iloc[-1] > close.iloc[0] else "downward"
        
        return context
    
    def prepare_fundamental_context(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context dictionary for fundamental agent prompt."""
        financials = stock_data.get("financials", {})
        
        return {
            "symbol": stock_data.get("symbol", "N/A"),
            "current_price": f"{stock_data.get('price', 0):.2f}",
            "pe_ratio": f"{stock_data.get('PE_ratio', 0):.2f}",
            "roe": f"{stock_data.get('ROE', 0):.2f}%",
            "dividend_yield": f"{stock_data.get('dividend_yield', 0):.2f}%",
            "revenue": f"{financials.get('revenue', 0):,.0f}",
            "net_income": f"{financials.get('net_income', 0):,.0f}",
            "data_source": stock_data.get("data_source", "unknown"),
        }
    
    def prepare_sentiment_context(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context dictionary for sentiment agent prompt."""
        news = stock_data.get("news", [])
        
        news_summary = "\n".join([
            f"- [{n.get('source', 'Unknown')}] {n.get('title', 'No title')}"
            for n in news[:5]
        ]) if news else "No recent news available"
        
        return {
            "symbol": stock_data.get("symbol", "N/A"),
            "news_count": len(news),
            "news_summary": news_summary,
            "data_source": stock_data.get("data_source", "unknown"),
        }
