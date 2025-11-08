from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base_agent import AgentOutput, BaseAgent


class DebateAgent(BaseAgent):
    """A debate agent that wraps a reasoning LLM (Gemini) to produce structured arguments.

    Each DebateAgent should receive the same evidence (top-K) and apply a bias/role-specific few-shot template.
    Output must include citations and a numeric confidence score.
    """

    def __init__(self, role: str):
        super().__init__(name=f"debate_agent_{role}", deterministic=True)
        self.role = role

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        evidence: List[Dict[str, Any]] = inputs.get("evidence", [])
        # Minimal deterministic verdict: simple scoring based on role
        base_score = {"fundamental": 0.7, "technical": 0.5, "sentiment": 0.4}.get(self.role, 0.5)
        # Prefer 'id' but fall back to 'doc_id' for compatibility with ParserAgent
        citations: List[str] = []
        for e in evidence[:3]:
            cid = e.get("id") or e.get("doc_id")
            if cid is not None:
                citations.append(str(cid))

        payload: Dict[str, Any] = {
            "role": self.role,
            "verdict": "BUY" if base_score > 0.5 else "HOLD",
            "confidence": base_score,
            "rationale": f"{self.role} agent considered {len(evidence)} pieces of evidence.",
            "citations": citations,
        }
        return AgentOutput(agent_name=self.name, payload=payload, provenance=self._make_provenance(session_id))
