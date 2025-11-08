"""
Judge Agent
Synthesizes debate and produces final decision.
"""
import logging
import json
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent, DebateMessage

logger = logging.getLogger(__name__)


class JudgeAgent(BaseAgent):
    """Judge - synthesizes debate and produces final verdict."""
    
    def __init__(self, llm_service, system_prompt: Optional[str] = None):
        """Initialize judge."""
        if system_prompt is None:
            try:
                with open("prompts/judge.txt", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = """You are the Judge responsible for synthesizing a multi-agent debate and producing a final investment decision.
Review all arguments, weigh evidence, and provide a clear, defensible recommendation."""
        
        super().__init__(
            name="Judge",
            role="Investment Decision Judge",
            llm_service=llm_service,
            system_prompt=system_prompt,
        )
    
    def analyze(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Judge doesn't perform independent analysis.
        This is a placeholder for interface compliance.
        """
        return {
            "analysis_type": "judgment",
            "role": "Judge - see final verdict",
        }
    
    def render_verdict(
        self,
        stock_symbol: str,
        moderator_brief: str,
        fundamental_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Render final investment decision.
        
        Args:
            stock_symbol: Stock symbol
            moderator_brief: Moderator's synthesis
            fundamental_analysis: Fundamental agent's analysis
            technical_analysis: Technical agent's analysis
            sentiment_analysis: Sentiment agent's analysis
            
        Returns:
            Final decision dict with BUY/HOLD/SELL recommendation
        """
        prompt = f"""
You are rendering a final investment verdict on {stock_symbol}.

MODERATOR BRIEF:
{moderator_brief}

FUNDAMENTAL ANALYSIS:
Signal: {fundamental_analysis['signal']}
Confidence: {fundamental_analysis['confidence']:.0%}
Key Points: {fundamental_analysis['rationale'][:200]}

TECHNICAL ANALYSIS:
Signal: {technical_analysis['signal']}
Confidence: {technical_analysis['confidence']:.0%}
Key Points: {technical_analysis['rationale'][:200]}

SENTIMENT ANALYSIS:
Signal: {sentiment_analysis['signal']}
Confidence: {sentiment_analysis['confidence']:.0%}
Key Points: {sentiment_analysis['rationale'][:200]}

Produce final verdict as JSON with following structure:
{{
  "stock": "{stock_symbol}",
  "decision": "BUY | HOLD | SELL",
  "confidence": 0.0-1.0,
  "summary": "One-paragraph executive summary",
  "rationale": {{
    "fundamental": "Key fundamental points",
    "technical": "Key technical points",
    "sentiment": "Key sentiment points"
  }},
  "key_catalysts": ["catalyst1", "catalyst2"],
  "risks": ["risk1", "risk2"],
  "time_horizon": "3-6 months | 6-12 months | 12+ months"
}}

Be decisive. Acknowledge uncertainty. Ground in data.
"""
        
        response = self.llm_service.generate_json_response(
            prompt,
            system_instruction=self.system_prompt,
        )
        
        # Ensure required fields
        if isinstance(response, dict):
            response.setdefault("stock", stock_symbol)
            response.setdefault("decision", "HOLD")
            response.setdefault("confidence", 0.5)
            response.setdefault("summary", "Balanced decision based on mixed signals.")
            response.setdefault("rationale", {
                "fundamental": fundamental_analysis.get('rationale', '')[:100],
                "technical": technical_analysis.get('rationale', '')[:100],
                "sentiment": sentiment_analysis.get('rationale', '')[:100],
            })
            response.setdefault("key_catalysts", [])
            response.setdefault("risks", [])
            response.setdefault("time_horizon", "3-6 months")
        else:
            response = {
                "stock": stock_symbol,
                "decision": "HOLD",
                "confidence": 0.5,
                "summary": "Unable to parse verdict. Default to HOLD.",
                "rationale": {
                    "fundamental": "See analysis",
                    "technical": "See analysis",
                    "sentiment": "See analysis",
                },
                "key_catalysts": [],
                "risks": [],
                "time_horizon": "3-6 months",
                "error": "JSON parsing failed",
            }
        
        # Record in message history
        message = DebateMessage(
            agent_name=self.name,
            round_num=99,  # Final round marker
            content=json.dumps(response, indent=2),
            is_final=True,
        )
        self.message_history.append(message)
        
        return response
    
    def consensus_check(
        self,
        fundamental_signal: str,
        technical_signal: str,
        sentiment_signal: str,
    ) -> Dict[str, Any]:
        """
        Check consensus level across three perspectives.
        
        Returns:
            Dict with convergence analysis
        """
        signals = [fundamental_signal, technical_signal, sentiment_signal]
        unique_signals = set(signals)
        
        consensus_level = 3 - len(unique_signals)  # 3=full consensus, 2=partial, 1=divergent
        
        return {
            "convergence_level": consensus_level,  # 1-3
            "convergence_pct": (3 - len(unique_signals)) / 3 * 100,
            "signals": {
                "fundamental": fundamental_signal,
                "technical": technical_signal,
                "sentiment": sentiment_signal,
            },
            "majority_signal": max(set(signals), key=signals.count),
            "full_consensus": consensus_level == 3,
        }
