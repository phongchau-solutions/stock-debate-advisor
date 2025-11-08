"""
Moderator Agent for orchestrating multi-agent debate.
Dynamically determines speaking order and synthesizes consensus.
"""
import logging
from typing import Dict, Any, List, Optional
import random

logger = logging.getLogger(__name__)


class ModeratorAgent:
    """Moderator Agent to orchestrate debate flow and synthesize decisions."""
    
    name = "Moderator"
    role = "Debate Moderator"
    
    def __init__(
        self,
        system_prompt: str,
        llm_config: Optional[Dict[str, Any]] = None
    ):
        self.system_prompt = system_prompt
        self.llm_config = llm_config or {}
        self.debate_history: List[Dict[str, Any]] = []
        self.speaking_order: List[str] = []
        
        logger.info(f"Initialized {self.name} in PoC mode (rule-based synthesis)")
    
    def determine_next_speaker(
        self,
        available_agents: List[str],
        current_round: int,
        total_rounds: int,
        previous_speaker: Optional[str] = None
    ) -> str:
        """
        Dynamically determine which agent should speak next.
        
        Logic:
        - Round 1: Standard order (Technical → Fundamental → Sentiment)
        - Later rounds: Let criticized agents respond, rotate order
        - Final round: Ensure all agents have spoken
        """
        if current_round == 1:
            # First round: standard presentation order
            order = ["TechnicalAnalyst", "FundamentalAnalyst", "SentimentAnalyst"]
            for agent in order:
                if agent in available_agents and agent not in self.speaking_order:
                    self.speaking_order.append(agent)
                    return agent
        
        # Middle rounds: dynamic selection
        if current_round < total_rounds:
            # Check for agents who haven't spoken recently
            recent_speakers = self.speaking_order[-3:] if len(self.speaking_order) >= 3 else self.speaking_order
            candidates = [a for a in available_agents if a not in recent_speakers]
            
            if candidates:
                # Prefer agents not heard from recently
                selected = random.choice(candidates)
            else:
                # All spoke recently, rotate fairly
                selected = random.choice(available_agents)
            
            self.speaking_order.append(selected)
            return selected
        
        # Final round: ensure consensus input from all
        for agent in available_agents:
            if agent not in self.speaking_order[-len(available_agents):]:
                self.speaking_order.append(agent)
                return agent
        
        # Default fallback
        selected = random.choice(available_agents)
        self.speaking_order.append(selected)
        return selected
    
    def record_message(self, agent_name: str, message: Dict[str, Any], round_num: int):
        """Record agent message in debate history."""
        self.debate_history.append({
            "round": round_num,
            "agent": agent_name,
            "message": message,
            "timestamp": message.get("timestamp", "")
        })
    
    def synthesize_consensus(self, all_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize final investment recommendation from all agent analyses.
        
        Uses voting weighted by confidence levels.
        """
        if not all_analyses:
            return self._create_default_consensus()
        
        # Extract recommendations and confidence
        votes = {"buy": 0.0, "hold": 0.0, "sell": 0.0}
        agent_positions = []
        
        for analysis in all_analyses:
            agent_name = analysis.get("analysis_type", "unknown")
            confidence = float(analysis.get("confidence", 0.5))
            
            # Map different analysis types to buy/hold/sell
            if analysis.get("signal"):  # Technical
                vote = analysis["signal"]
            elif analysis.get("bias"):  # Fundamental or Sentiment
                vote = analysis["bias"]
            else:
                vote = "hold"
            
            if vote in votes:
                votes[vote] += confidence
                agent_positions.append({
                    "agent": agent_name,
                    "position": vote,
                    "confidence": confidence,
                    "rationale": analysis.get("rationale", "")
                })
        
        # Determine final decision
        if not votes or sum(votes.values()) == 0:
            return self._create_default_consensus()
        
        best_vote = max(votes.items(), key=lambda x: x[1])
        decision = best_vote[0].upper()
        total_weight = sum(votes.values())
        confidence = best_vote[1] / total_weight if total_weight > 0 else 0.5
        
        # Determine consensus level
        second_best = sorted(votes.values(), reverse=True)[1] if len(votes) > 1 else 0
        if best_vote[1] > second_best * 2:
            consensus = "full"
        elif best_vote[1] > second_best * 1.2:
            consensus = "partial"
        else:
            consensus = "divided"
        
        # Generate summary
        summary = self._generate_summary(decision, confidence, agent_positions, votes)
        
        return {
            "decision": decision,
            "confidence": float(confidence),
            "consensus": consensus,
            "votes": {k: float(v) for k, v in votes.items()},
            "summary": summary,
            "agent_positions": agent_positions,
            "rationale": self._generate_rationale(decision, agent_positions)
        }
    
    def _generate_summary(
        self,
        decision: str,
        confidence: float,
        positions: List[Dict],
        votes: Dict[str, float]
    ) -> str:
        """Generate executive summary of debate conclusion."""
        parts = []
        parts.append(f"After comprehensive multi-agent analysis, recommendation is {decision}.")
        parts.append(f"Confidence level: {confidence:.0%}.")
        
        supporting = [p for p in positions if p["position"] == decision.lower()]
        if supporting:
            agent_names = ", ".join([p["agent"] for p in supporting])
            parts.append(f"Supporting agents: {agent_names}.")
        
        return " ".join(parts)
    
    def _generate_rationale(self, decision: str, positions: List[Dict]) -> str:
        """Generate detailed rationale for final decision."""
        rationales = []
        for pos in positions:
            if pos["position"] == decision.lower():
                agent_type = pos["agent"].replace("Analyst", "").replace("analysis", "")
                rationales.append(f"{agent_type}: {pos['rationale'][:100]}")
        
        return " | ".join(rationales) if rationales else "Mixed signals from debate."
    
    def _create_default_consensus(self) -> Dict[str, Any]:
        """Create default consensus when no clear decision."""
        return {
            "decision": "HOLD",
            "confidence": 0.5,
            "consensus": "none",
            "votes": {"buy": 0.0, "hold": 1.0, "sell": 0.0},
            "summary": "Insufficient data for clear recommendation.",
            "agent_positions": [],
            "rationale": "Unable to reach consensus with available information."
        }
