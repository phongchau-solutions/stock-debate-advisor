"""
Human Proxy Agent with Streamlit Integration
Enables human-in-the-loop control of the debate via Streamlit UI callbacks.
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class HumanCommand(Enum):
    """Human commands from Streamlit UI."""
    START = "start"
    PAUSE = "pause"
    STOP = "stop"
    OVERRIDE = "override"
    VOTE = "vote"
    CONTINUE = "continue"


@dataclass
class HumanDecision:
    """Represents a human decision/input."""
    command: HumanCommand
    timestamp: datetime
    content: str
    round_num: Optional[int] = None
    agent_target: Optional[str] = None  # For override commands


class HumanProxyAgent:
    """
    Human proxy for interactive debate control.
    
    Integrates with Streamlit UI to:
    - Start/pause/stop debate
    - Override agent opinions
    - Cast tie-breaking votes
    - Inject custom prompts
    
    Uses asyncio event queue for non-blocking UI integration.
    """
    
    def __init__(
        self,
        name: str = "Human",
        enable_callbacks: bool = True,
    ):
        """
        Initialize human proxy agent.
        
        Args:
            name: Display name for human participant
            enable_callbacks: Whether to enable Streamlit callbacks
        """
        self.name = name
        self.enable_callbacks = enable_callbacks
        self.message_history: List[Dict[str, Any]] = []
        self.decision_queue: List[HumanDecision] = []
        self.current_state = "idle"  # idle, active, paused, stopped
        self.debate_id: Optional[str] = None
        self.override_threshold = 2  # Allow overrides per round
        self.override_count = 0
        
        logger.info(f"Initialized HumanProxyAgent: {name}")
    
    def register_streamlit_callback(
        self,
        callback: Callable[[HumanCommand, str], None]
    ) -> None:
        """
        Register Streamlit UI callback for human input.
        
        Args:
            callback: Async function(command, content) -> None
        """
        self.streamlit_callback = callback
        logger.info("Registered Streamlit callback")
    
    def submit_command(
        self,
        command: HumanCommand,
        content: str,
        round_num: Optional[int] = None,
        agent_target: Optional[str] = None,
    ) -> HumanDecision:
        """
        Submit a human command (from Streamlit UI).
        
        Args:
            command: Type of command (START, PAUSE, STOP, OVERRIDE, VOTE)
            content: Command content/text
            round_num: Current round number
            agent_target: For override: which agent to override
            
        Returns:
            HumanDecision object
        """
        decision = HumanDecision(
            command=command,
            timestamp=datetime.utcnow(),
            content=content,
            round_num=round_num,
            agent_target=agent_target,
        )
        
        self.decision_queue.append(decision)
        self._log_decision(decision)
        
        logger.info(
            f"Human command: {command.value} "
            f"(round {round_num}, target: {agent_target})"
        )
        
        return decision
    
    def get_next_command(self) -> Optional[HumanDecision]:
        """
        Get next human command from queue (non-blocking).
        
        Returns:
            HumanDecision if available, None otherwise
        """
        if self.decision_queue:
            return self.decision_queue.pop(0)
        return None
    
    def process_start_command(self) -> bool:
        """Process START command from human."""
        self.current_state = "active"
        logger.info(f"{self.name}: Debate started")
        return True
    
    def process_pause_command(self, round_num: int) -> bool:
        """Process PAUSE command from human."""
        self.current_state = "paused"
        logger.info(f"{self.name}: Debate paused at round {round_num}")
        return True
    
    def process_stop_command(self, round_num: int) -> bool:
        """Process STOP command from human."""
        self.current_state = "stopped"
        logger.info(f"{self.name}: Debate stopped at round {round_num}")
        return True
    
    def process_override_command(
        self,
        agent_target: str,
        override_opinion: str,
        round_num: int,
    ) -> bool:
        """
        Process OVERRIDE command to inject human opinion.
        
        Args:
            agent_target: Which agent to override (or 'all')
            override_opinion: Human's alternative stance
            round_num: Round number
            
        Returns:
            True if override accepted, False if threshold exceeded
        """
        if self.override_count >= self.override_threshold:
            logger.warning(f"{self.name}: Override threshold exceeded")
            return False
        
        self.override_count += 1
        
        message = {
            "agent": self.name,
            "type": "override",
            "target": agent_target,
            "opinion": override_opinion,
            "round": round_num,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.message_history.append(message)
        
        logger.info(
            f"{self.name}: Override #{self.override_count} - "
            f"Target: {agent_target}, Opinion: {override_opinion[:50]}..."
        )
        
        return True
    
    def process_vote_command(
        self,
        vote: str,  # BUY, HOLD, SELL
        reasoning: str = "",
    ) -> bool:
        """
        Process VOTE command for human's investment decision.
        
        Args:
            vote: Human's vote (BUY, HOLD, SELL)
            reasoning: Reasoning behind vote
            
        Returns:
            True if vote recorded
        """
        if vote not in ["BUY", "HOLD", "SELL"]:
            logger.error(f"Invalid vote: {vote}")
            return False
        
        message = {
            "agent": self.name,
            "type": "vote",
            "vote": vote,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.message_history.append(message)
        
        logger.info(f"{self.name}: Vote submitted - {vote}")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of human proxy."""
        return {
            "name": self.name,
            "state": self.current_state,
            "message_count": len(self.message_history),
            "override_count": self.override_count,
            "override_remaining": self.override_threshold - self.override_count,
            "last_message": (
                self.message_history[-1]["timestamp"]
                if self.message_history
                else None
            ),
        }
    
    def _log_decision(self, decision: HumanDecision) -> None:
        """Log human decision to message history."""
        message = {
            "agent": self.name,
            "type": "command",
            "command": decision.command.value,
            "content": decision.content,
            "round": decision.round_num,
            "timestamp": decision.timestamp.isoformat(),
        }
        self.message_history.append(message)
    
    def reset(self) -> None:
        """Reset for next debate."""
        self.decision_queue.clear()
        self.message_history.clear()
        self.current_state = "idle"
        self.override_count = 0
        logger.info(f"{self.name}: Reset for new debate")


class StreamlitHiLIntegration:
    """
    Integration layer between Streamlit UI and HumanProxyAgent.
    Handles async event queue and session state management.
    """
    
    def __init__(self, streamlit_session_state=None):
        """
        Initialize Streamlit HiL integration.
        
        Args:
            streamlit_session_state: st.session_state object
        """
        self.session_state = streamlit_session_state
        self.human_proxy = HumanProxyAgent()
        self.event_queue: asyncio.Queue = asyncio.Queue()
    
    async def handle_streamlit_event(
        self,
        command: HumanCommand,
        content: str,
        **kwargs
    ) -> bool:
        """
        Handle event from Streamlit UI (async).
        
        Args:
            command: Human command
            content: Command content
            **kwargs: Additional arguments (round_num, agent_target, etc.)
            
        Returns:
            True if processed successfully
        """
        try:
            decision = self.human_proxy.submit_command(
                command=command,
                content=content,
                **kwargs
            )
            
            # Queue for processing
            await self.event_queue.put(decision)
            
            # Update session state
            if self.session_state:
                self.session_state.human_decision = decision
            
            return True
        except Exception as e:
            logger.error(f"Error handling Streamlit event: {e}")
            return False
    
    def get_pending_decisions(self) -> List[HumanDecision]:
        """
        Get all pending human decisions (non-blocking).
        
        Returns:
            List of HumanDecision objects
        """
        decisions = []
        while True:
            decision = self.human_proxy.get_next_command()
            if decision is None:
                break
            decisions.append(decision)
        return decisions
    
    def update_ui_with_decision(self, decision: HumanDecision) -> None:
        """Update Streamlit UI with human decision result."""
        if self.session_state:
            self.session_state.last_human_decision = decision
            self.session_state.human_status = self.human_proxy.get_status()
