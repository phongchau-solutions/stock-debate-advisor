from __future__ import annotations

from typing import Any, Dict, Optional

from .base_agent import AgentOutput, BaseAgent


class ParserAgent(BaseAgent):
    """Parser agent stub: extract structured data from raw documents.

    Real implementation should use pdfplumber, camelot, and OCR for scanned documents.
    """

    def __init__(self):
        super().__init__(name="parser_agent", deterministic=True)

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        # Minimal deterministic parse output
        payload = {
            "documents": [
                {"doc_id": "sample_1", "tables": [{"rows": 3}], "narrative": "Sample parsed narrative."}
            ]
        }
        return AgentOutput(agent_name=self.name, payload=payload, provenance=self._make_provenance(session_id))
