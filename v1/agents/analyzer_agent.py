from __future__ import annotations

from typing import Any, Dict, Optional

from .base_agent import AgentOutput, BaseAgent


class AnalyzerAgent(BaseAgent):
    """Analyzer agent stub: compute financial ratios, technical metrics, sentiment.

    Real implementation should read parsed data from Postgres and produce metrics stored back to Postgres.
    """

    def __init__(self):
        super().__init__(name="analyzer_agent", deterministic=True)

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        payload = {
            "fundamentals": {"pe_ratio": 12.3, "eps": 1.45},
            "technical": {"rsi": 42.1, "sma_50": 101.2},
            "sentiment": {"score": 0.12, "sources": ["twitter", "news"]},
        }
        return AgentOutput(agent_name=self.name, payload=payload, provenance=self._make_provenance(session_id))
