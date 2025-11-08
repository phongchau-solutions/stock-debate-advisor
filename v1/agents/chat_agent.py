from __future__ import annotations

from typing import Any, Dict, Optional

from .base_agent import AgentOutput, BaseAgent


class ChatAgent(BaseAgent):
    """Chat agent: RAG-backed interface using Gemini for reasoning. Returns function-callable structured outputs.

    This is a stub that demonstrates the expected method signature for integrating a FastAPI websocket or HTTP chat.
    """

    def __init__(self):
        super().__init__(name="chat_agent", deterministic=True)

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        # inputs expected: {'query': str, 'user_id': str, 'evidence': [...]}
        q = inputs.get("query", "")
        payload = {"response": f"Stubbed RAG response for: {q}", "source_refs": ["source_1"]}
        return AgentOutput(agent_name=self.name, payload=payload, provenance=self._make_provenance(session_id))
