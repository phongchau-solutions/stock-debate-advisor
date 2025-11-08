from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .base_agent import AgentOutput, BaseAgent


class AggregationResult(BaseModel):
    action: str
    confidence: float
    rationale: str
    citations: List[str]


class AggregatorAgent(BaseAgent):
    """Aggregator: merges analyzer + debate outputs to produce final BUY/HOLD/SELL with enforced citations.

    Enforcement: if final output lacks citations, it will be rejected (compliance requirement).
    """

    def __init__(self):
        super().__init__(name="aggregator_agent", deterministic=True)

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        # inputs expected: {'debates': [...], 'analyzers': [...]}
        debates = inputs.get("debates", [])
        # Simple deterministic merge: average confidences
        confidences = [d.get("confidence", 0.5) for d in debates]
        avg_conf = sum(confidences) / (len(confidences) or 1)
        votes = [d.get("verdict") for d in debates]
        # deterministic tie-break: sorted votes, pick first most common
        from collections import Counter

        cnt = Counter(votes)
        action = cnt.most_common(1)[0][0] if votes else "HOLD"
        citations = []
        for d in debates:
            citations.extend(d.get("citations", []))
            # filter out None and dedupe while keeping order
            citations = [c for c in citations if c is not None]
        seen = set()
        citations = [c for c in citations if not (c in seen or seen.add(c))]

        result = AggregationResult(action=action, confidence=avg_conf, rationale="Merged debates", citations=citations)
        payload = result.model_dump()
        # Enforce that citations are present
        if not payload.get("citations"):
            payload["compliance_reject"] = True
        return AgentOutput(agent_name=self.name, payload=payload, provenance=self._make_provenance(session_id))
