from __future__ import annotations

import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Provenance(BaseModel):
    session_id: str
    timestamp: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    # Standardized, validated JSON output each agent must return
    agent_name: str
    payload: Dict[str, Any]
    provenance: Provenance


class BaseAgent(ABC):
    """Minimal deterministic agent base class.

    Contract:
    - process(inputs) -> AgentOutput
    - All outputs must be Pydantic-validated JSON
    - Agents must accept a session_id to allow auditability/provenance
    """

    def __init__(self, name: str, deterministic: bool = True):
        self.name = name
        self.deterministic = deterministic

    def _make_provenance(self, session_id: Optional[str], source_ids: Optional[list[str]] = None) -> Provenance:
        return Provenance(session_id=session_id or str(uuid.uuid4()), source_ids=source_ids or [])

    @abstractmethod
    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        """Process inputs and return AgentOutput. Must be deterministic when deterministic=True."""

    def validate_and_serialize(self, output: AgentOutput) -> str:
        # Validate with pydantic and return canonical JSON for downstream deterministic channels
        validated = output.model_dump()
        # deterministic serialization
        return json.dumps(validated, sort_keys=True, separators=(",", ":"))
