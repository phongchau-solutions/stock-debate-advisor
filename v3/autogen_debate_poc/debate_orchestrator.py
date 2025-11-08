"""
DebateOrchestrator for Multi-Agent Stock Debate System.
Uses Microsoft Autogen (autogen-agentchat) for agent coordination.
Runs N rounds with debate history tracking for context-aware analysis.
"""
from typing import List, Dict, Any, Callable
import time
import datetime
import logging

# Import autogen-agentchat (must be installed in environment)
from autogen_agentchat.agents import GroupChat, GroupChatManager

logger = logging.getLogger(__name__)


class DebateOrchestrator:
    def __init__(self, agents: List[Any], rounds: int = 5, autogen_config: Dict[str, Any] = None):
        self.agents = agents
        self.rounds = rounds
        self.autogen_config = autogen_config or {}
        self.transcript: List[Dict[str, Any]] = []

    def run(self, symbol: str, period_days: int = 30, on_message: Callable[[Dict[str, Any]], None] = None) -> Dict[str, Any]:
        """Run the debate synchronously and call on_message for each message (for streaming UI)."""
        logger.info(f"Starting debate for {symbol} for {self.rounds} rounds using autogen-agentchat")

        # Round-based orchestrator: each agent provides a message per round
        for r in range(1, self.rounds + 1):
            for agent in self.agents:
                try:
                    # Pass accumulated debate history to agent for context-aware responses
                    result = agent.analyze(
                        stock_symbol=symbol, 
                        period_days=period_days,
                        debate_history=self.transcript,
                        current_round=r
                    )
                except Exception as e:
                    result = {"analysis_type": getattr(agent, 'name', 'agent'), "stock_symbol": symbol, "error": str(e), "signal": "hold", "confidence": 0.1}

                message = {
                    "round": r,
                    "agent": getattr(agent, 'name', agent.__class__.__name__),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "payload": result
                }
                self.transcript.append(message)
                if on_message:
                    on_message(message)
                # small pause to simulate streaming
                time.sleep(0.2)

        # Aggregate final decision: simple voting weighted by confidence
        votes = {"buy": 0.0, "hold": 0.0, "sell": 0.0}
        reasons = []
        for m in self.transcript:
            p = m.get("payload", {})
            # map different agent outputs to buy/hold/sell
            label = None
            conf = float(p.get("confidence", 0.0) or 0.0)
            if p.get("analysis_type") == "technical":
                sig = p.get("signal", "hold")
                label = sig
            elif p.get("analysis_type") == "fundamental":
                bias = p.get("bias", "hold")
                label = bias
            elif p.get("analysis_type") == "sentiment":
                lab = p.get("sentiment_label", "neutral")
                if lab == "positive":
                    label = "buy"
                elif lab == "negative":
                    label = "sell"
                else:
                    label = "hold"
            if label in votes:
                votes[label] += conf
            reasons.append({"agent": m["agent"], "label": label, "confidence": conf, "rationale": p.get("rationale")})

        best = max(votes.items(), key=lambda x: x[1])
        final_action = best[0]
        total_conf = sum(votes.values())
        final_confidence = float(best[1] / (total_conf + 1e-9)) if total_conf > 0 else 0.0

        summary = {
            "action": final_action,
            "confidence": final_confidence,
            "votes": votes,
            "reasons": reasons
        }

        return {"transcript": self.transcript, "summary": summary}
