"""
Debate Orchestrator using Google Agent Development Kit (ADK).
Coordinates multi-agent debate for stock analysis.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from google.adk.agents import LlmAgent

from app.config import config, AGENT_PROMPTS
from app.tools.analysis_tools import analysis_tools

logger = logging.getLogger(__name__)


class DebateOrchestrator:
    """Orchestrates multi-agent debate using Google ADK."""
    
    def __init__(self):
        """Initialize debate orchestrator."""
        self.agents = {}
        self.debate_history = []
        
    def setup_agents(self, symbol: str):
        """
        Set up Google ADK agents for debate.
        
        Args:
            symbol: Stock symbol to analyze
        """
        # Fundamental Analyst Agent
        self.fundamental_agent = LlmAgent(
            name="FundamentalAnalyst",
            model=config.LLM_MODEL,
            instruction=AGENT_PROMPTS["fundamental"],
            description="Analyzes financial statements, ratios, and fundamental metrics"
        )
        
        # Technical Analyst Agent
        self.technical_agent = LlmAgent(
            name="TechnicalAnalyst",
            model=config.LLM_MODEL,
            instruction=AGENT_PROMPTS["technical"],
            description="Analyzes price trends, technical indicators, and chart patterns"
        )
        
        # Sentiment Analyst Agent
        self.sentiment_agent = LlmAgent(
            name="SentimentAnalyst",
            model=config.LLM_MODEL,
            instruction=AGENT_PROMPTS["sentiment"],
            description="Analyzes news sentiment, market psychology, and narratives"
        )
        
        # Moderator Agent
        self.moderator_agent = LlmAgent(
            name="Moderator",
            model=config.LLM_MODEL,
            instruction=AGENT_PROMPTS["moderator"],
            description="Moderates debate, challenges arguments, ensures balanced analysis"
        )
        
        # Judge Agent
        self.judge_agent = LlmAgent(
            name="Judge",
            model=config.LLM_MODEL,
            instruction=AGENT_PROMPTS["judge"],
            description="Evaluates arguments and makes final investment decision"
        )
        
        # Coordinator Agent (parent) that manages the debate flow
        self.coordinator_agent = LlmAgent(
            name="DebateCoordinator",
            model=config.LLM_MODEL,
            instruction=f"""You are the Debate Coordinator for stock {symbol} analysis.
            
Your role is to orchestrate a structured multi-round debate between:
- Fundamental Analyst
- Technical Analyst  
- Sentiment Analyst
- Moderator (who challenges and guides)
- Judge (who makes final decision)

Ensure each agent speaks in turn, builds on previous points, and provides actionable insights.""",
            description=f"Coordinates multi-agent debate for {symbol} stock analysis",
            sub_agents=[
                self.fundamental_agent,
                self.technical_agent,
                self.sentiment_agent,
                self.moderator_agent,
                self.judge_agent
            ]
        )
        
        self.agents = {
            "coordinator": self.coordinator_agent,
            "fundamental": self.fundamental_agent,
            "technical": self.technical_agent,
            "sentiment": self.sentiment_agent,
            "moderator": self.moderator_agent,
            "judge": self.judge_agent,
        }
        
        logger.info(f"Set up {len(self.agents)} Google ADK agents for debate on {symbol}")
    
    def run_debate(self, symbol: str, rounds: int = 3) -> Dict[str, Any]:
        """
        Run multi-round debate on a stock using Google ADK.
        
        Args:
            symbol: Stock symbol
            rounds: Number of debate rounds
        
        Returns:
            Dict with debate transcript and final decision
        """
        logger.info(f"Starting ADK-based debate for {symbol} with {rounds} rounds")
        
        # Setup agents
        self.setup_agents(symbol)
        
        # Fetch comprehensive analysis
        logger.info("Fetching comprehensive analysis data...")
        analysis_data = analysis_tools.get_comprehensive_analysis(symbol)
        
        # Prepare context for agents
        context = self._prepare_context(symbol, analysis_data)
        
        # Initialize debate results
        debate_result = {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "rounds": rounds,
            "transcript": [],
            "final_decision": None,
        }
        
        # Run debate rounds using ADK's coordinator pattern
        for round_num in range(1, rounds + 1):
            logger.info(f"Running debate round {round_num}/{rounds}")
            
            # Build prompt for this round
            round_prompt = f"""
DEBATE ROUND {round_num} for {symbol}

{context}

Previous discussion:
{self._format_transcript(debate_result["transcript"])}

Each analyst should now provide their analysis and recommendation (BUY/SELL/HOLD) in 2-3 sentences.
Fundamental Analyst, please start.
"""
            
            try:
                # Invoke coordinator agent which will orchestrate sub-agents
                from google.adk.sessions import Session
                
                session = Session()
                response = session.run(
                    agent=self.coordinator_agent,
                    prompt=round_prompt
                )
                
                # Extract messages from response
                if hasattr(response, 'messages'):
                    for msg in response.messages:
                        if hasattr(msg, 'author') and hasattr(msg, 'content'):
                            debate_result["transcript"].append({
                                "round": round_num,
                                "agent": msg.author,
                                "message": msg.content
                            })
                elif hasattr(response, 'content'):
                    # Fallback: treat as single response
                    debate_result["transcript"].append({
                        "round": round_num,
                        "agent": "Coordinator",
                        "message": str(response.content)
                    })
                
            except Exception as e:
                logger.error(f"Error in round {round_num}: {e}")
                debate_result["transcript"].append({
                    "round": round_num,
                    "agent": "System",
                    "message": f"Error in round: {e}"
                })
        
        # Get final judgment
        logger.info("Getting final judgment...")
        final_judgment = self._get_final_judgment_adk(symbol, debate_result["transcript"])
        debate_result["final_decision"] = final_judgment
        
        return debate_result
    
    def _prepare_context(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Prepare context string for agents."""
        context = f"""
STOCK ANALYSIS DEBATE: {symbol}
================================

You are participating in a multi-agent debate to determine the investment merit of {symbol}.

Available Analysis Data:
- Fundamental Analysis: {analysis_data.get('fundamental', {}).get('overall_score', {})}
- Technical Analysis: {analysis_data.get('technical', {}).get('overall_score', {})}
- Sentiment Analysis: {analysis_data.get('sentiment', {}).get('overall_score', {})}

Your task is to present your analysis perspective and debate with other analysts to reach the best investment decision.
"""
        return context
    
    def _format_analysis_for_agent(self, agent_type: str, analysis: Dict[str, Any]) -> str:
        """Format analysis data for specific agent type."""
        if agent_type == "fundamental":
            overall = analysis.get("overall_score", {})
            return f"""
Overall Score: {overall.get('score', 'N/A')} - {overall.get('rating', 'N/A')}
Profitability: {analysis.get('profitability', {}).get('score', 'N/A')}
Liquidity: {analysis.get('liquidity', {}).get('assessment', 'N/A')}
Solvency: {analysis.get('solvency', {}).get('assessment', 'N/A')}
Valuation: {analysis.get('valuation', {}).get('assessment', 'N/A')}
Recommendation: {analysis.get('recommendation', 'N/A')}
"""
        elif agent_type == "technical":
            overall = analysis.get("overall_score", {})
            trend = analysis.get("trend", {})
            return f"""
Overall Score: {overall.get('score', 'N/A')} - {overall.get('rating', 'N/A')}
Trend: {trend.get('direction', 'N/A')} ({trend.get('strength', 'N/A')})
RSI: {analysis.get('momentum', {}).get('rsi_value', 'N/A')}
Signals: {len(analysis.get('signals', []))} detected
Recommendation: {analysis.get('recommendation', 'N/A')}
"""
        elif agent_type == "sentiment":
            overall = analysis.get("overall_score", {})
            aggregate = analysis.get("aggregate", {})
            return f"""
Overall Score: {overall.get('score', 'N/A')} - {overall.get('rating', 'N/A')}
Average Sentiment: {aggregate.get('average_score', 'N/A')}
Positive Articles: {aggregate.get('positive_articles', 0)}
Negative Articles: {aggregate.get('negative_articles', 0)}
Recommendation: {analysis.get('recommendation', 'N/A')}
"""
        return str(analysis)
    
    def _format_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """Format transcript for context."""
        if not transcript:
            return "No previous discussion."
        
        formatted = []
        for entry in transcript[-10:]:  # Last 10 entries
            formatted.append(f"{entry['agent']}: {entry['message'][:200]}...")
        return "\n".join(formatted)
    
    def _get_final_judgment_adk(self, symbol: str, transcript: List[Dict[str, str]]) -> Dict[str, Any]:
        """Get final judgment from judge agent using ADK."""
        # Summarize full debate
        debate_summary = "\n\n".join([
            f"Round {msg['round']} - {msg['agent']}:\n{msg['message']}"
            for msg in transcript
        ])
        
        prompt = f"""
FINAL JUDGMENT FOR {symbol}

Complete Debate Transcript:
{debate_summary}

Based on all arguments presented, provide your final investment decision:

1. **Decision**: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
2. **Confidence**: High / Medium / Low
3. **Key Reasoning**: 2-3 main points
4. **Risk Factors**: Key risks to consider

Be decisive and clear.
"""
        
        try:
            from google.adk.sessions import Session
            
            session = Session()
            response = session.run(
                agent=self.judge_agent,
                prompt=prompt
            )
            
            decision_text = str(response.content) if hasattr(response, 'content') else str(response)
            
            return {
                "decision": decision_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting final judgment: {e}")
            return {
                "decision": "Error in final judgment",
                "error": str(e),
            }
