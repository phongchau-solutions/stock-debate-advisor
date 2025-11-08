"""
Base Agent class for debate system.
All specialist agents inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class DebateMessage:
    """Message structure for debate communication."""
    
    def __init__(
        self,
        agent_name: str,
        round_num: int,
        content: str,
        analysis: Optional[Dict[str, Any]] = None,
        is_final: bool = False,
    ):
        self.timestamp = datetime.utcnow().isoformat()
        self.agent_name = agent_name
        self.round_num = round_num
        self.content = content
        self.analysis = analysis or {}
        self.is_final = is_final
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "round_num": self.round_num,
            "content": self.content,
            "analysis": self.analysis,
            "is_final": self.is_final,
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class BaseAgent(ABC):
    """
    Base class for all debate agents.
    
    Attributes:
        name: Agent identifier
        role: Agent's role in the debate
        llm_service: Gemini service instance
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        llm_service,
        system_prompt: str = None,
    ):
        self.name = name
        self.role = role
        self.llm_service = llm_service
        self.system_prompt = system_prompt or f"You are {role}."
        self.message_history: list[DebateMessage] = []
        
        logger.info(f"Initialized {self.__class__.__name__}: {name} ({role})")
    
    @abstractmethod
    def analyze(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Perform specialized analysis.
        
        Args:
            stock_symbol: Stock ticker symbol.
            stock_data: Financial/market data dict.
            period_days: Analysis lookback period.
            
        Returns:
            Analysis result dict with signal (BUY/HOLD/SELL), confidence, rationale.
        """
        pass
    
    def present_argument(
        self,
        round_num: int,
        previous_arguments: list[DebateMessage] = None,
    ) -> DebateMessage:
        """
        Generate argument for the current debate round.
        
        Args:
            round_num: Current round number.
            previous_arguments: Messages from previous rounds.
            
        Returns:
            DebateMessage with agent's argument.
        """
        context = self._build_context(previous_arguments)
        
        prompt = f"""
Current Debate Round: {round_num}

Your Role: {self.role}

Previous Arguments:
{context}

Provide your analysis and perspective on the stock investment decision.
Be concise, data-driven, and respectful of other viewpoints.
"""
        
        response = self.llm_service.generate_response(
            prompt,
            system_instruction=self.system_prompt,
        )
        
        message = DebateMessage(
            agent_name=self.name,
            round_num=round_num,
            content=response,
        )
        
        self.message_history.append(message)
        return message
    
    def rebut(
        self,
        round_num: int,
        opposing_argument: str,
        previous_arguments: list[DebateMessage] = None,
    ) -> DebateMessage:
        """
        Generate rebuttal to opposing argument.
        
        Args:
            round_num: Current round number.
            opposing_argument: Argument to rebut.
            previous_arguments: Message history.
            
        Returns:
            DebateMessage with rebuttal.
        """
        context = self._build_context(previous_arguments)
        
        prompt = f"""
Current Debate Round: {round_num}

Your Role: {self.role}

Previous Arguments:
{context}

Opposing Argument to Address:
{opposing_argument}

Provide a respectful rebuttal with data-driven counter-points.
Acknowledge valid points from the opposing view while maintaining your perspective.
"""
        
        response = self.llm_service.generate_response(
            prompt,
            system_instruction=self.system_prompt,
        )
        
        message = DebateMessage(
            agent_name=self.name,
            round_num=round_num,
            content=response,
        )
        
        self.message_history.append(message)
        return message
    
    def _build_context(self, messages: list[DebateMessage] = None) -> str:
        """Build context from message history."""
        if not messages:
            return "No previous arguments."
        
        context_lines = []
        for msg in messages[-3:]:  # Last 3 messages for context
            context_lines.append(f"{msg.agent_name} (Round {msg.round_num}): {msg.content}")
        
        return "\n".join(context_lines)
    
    def get_history(self) -> list[Dict[str, Any]]:
        """Get agent's message history."""
        return [msg.to_dict() for msg in self.message_history]
    
    def clear_history(self):
        """Clear message history."""
        self.message_history = []
