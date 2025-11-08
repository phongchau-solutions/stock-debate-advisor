"""
Moderator Agent
Manages debate flow, turn order, and synthesis.
Enhanced with Human-in-the-Loop support and dynamic round control.
"""
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from agents.base_agent import BaseAgent, DebateMessage

logger = logging.getLogger(__name__)


class RoundControl(Enum):
    """Moderation commands for round control."""
    CONTINUE = "continue"
    PAUSE = "pause"
    STOP = "stop"
    EXTEND = "extend"
    SKIP = "skip"


class ModeratorAgent(BaseAgent):
    """
    Debate Moderator - manages flow, turn order, and synthesis.
    
    Enhanced capabilities:
    - Dynamic round control (pause/resume/stop)
    - Turn order management with fairness tracking
    - Human override support
    - Round time limits
    """
    
    def __init__(self, llm_service, system_prompt: Optional[str] = None, max_rounds: int = 5):
        """
        Initialize moderator.
        
        Args:
            llm_service: LLM service for synthesis
            system_prompt: Custom system prompt
            max_rounds: Maximum debate rounds (supports >=5)
        """
        if system_prompt is None:
            try:
                with open("prompts/moderator.txt", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                system_prompt = """You are the Debate Moderator responsible for managing a structured investment debate.
Maintain fair discourse, encourage evidence-based reasoning, and prepare synthesis for the Judge."""
        
        super().__init__(
            name="Moderator",
            role="Debate Moderator",
            llm_service=llm_service,
            system_prompt=system_prompt,
        )
        self.debate_summary = None
        self.max_rounds = max_rounds
        
        # HiL support
        self.is_paused = False
        self.current_round = 0
        self.round_control = RoundControl.CONTINUE
        
        # Turn fairness tracking
        self.agent_turn_counts: Dict[str, int] = {}
        self.agent_last_spoke: Dict[str, int] = {}
    
    def analyze(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Moderator doesn't perform technical analysis.
        This is a placeholder for interface compliance.
        """
        return {
            "analysis_type": "moderation",
            "role": "Moderator - see debate flow",
        }
    
    def manage_round(
        self,
        round_num: int,
        fundamental_arg: str,
        technical_arg: str,
        sentiment_arg: str,
    ) -> DebateMessage:
        """
        Synthesize round arguments and provide moderation summary.
        
        Args:
            round_num: Current round number
            fundamental_arg: Fundamental agent's argument
            technical_arg: Technical agent's argument
            sentiment_arg: Sentiment agent's argument
            
        Returns:
            Moderator's synthesis and guidance
        """
        prompt = f"""
Round {round_num} Synthesis and Moderation:

Fundamental Analysis:
{fundamental_arg}

Technical Analysis:
{technical_arg}

Sentiment Analysis:
{sentiment_arg}

As moderator, provide:
1. Key agreements across perspectives
2. Key disagreements to explore
3. Guidance for next round of discussion
4. Any red flags or follow-up questions

Keep response concise and structured.
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
        
        # Track turns for fairness
        self._track_agent_turn("Fundamental")
        self._track_agent_turn("Technical")
        self._track_agent_turn("Sentiment")
        
        self.current_round = round_num
        return message
    
    def get_next_speaker(self, agents: List[str]) -> str:
        """
        Determine fair next speaker based on turn tracking.
        
        Args:
            agents: List of available agents
            
        Returns:
            Name of next agent to speak
        """
        # Initialize counts if needed
        for agent in agents:
            if agent not in self.agent_turn_counts:
                self.agent_turn_counts[agent] = 0
                self.agent_last_spoke[agent] = -999
        
        # Find agent with fewest turns (or who spoke longest ago)
        next_speaker = min(
            agents,
            key=lambda a: (self.agent_turn_counts[a], self.agent_last_spoke[a])
        )
        
        return next_speaker
    
    def _track_agent_turn(self, agent_name: str) -> None:
        """Track turn for fairness analysis."""
        if agent_name not in self.agent_turn_counts:
            self.agent_turn_counts[agent_name] = 0
        
        self.agent_turn_counts[agent_name] += 1
        self.agent_last_spoke[agent_name] = self.current_round
    
    def pause_debate(self, reason: str = "") -> Dict[str, Any]:
        """
        Pause debate (HiL support).
        
        Args:
            reason: Reason for pause
            
        Returns:
            Pause state
        """
        self.is_paused = True
        self.round_control = RoundControl.PAUSE
        
        logger.info(f"Debate paused. Reason: {reason}")
        
        return {
            "status": "paused",
            "current_round": self.current_round,
            "reason": reason,
            "turn_summary": self.agent_turn_counts.copy(),
        }
    
    def resume_debate(self) -> Dict[str, Any]:
        """
        Resume paused debate (HiL support).
        
        Returns:
            Resume state
        """
        self.is_paused = False
        self.round_control = RoundControl.CONTINUE
        
        logger.info("Debate resumed")
        
        return {
            "status": "resumed",
            "current_round": self.current_round,
        }
    
    def stop_debate(self, reason: str = "") -> Dict[str, Any]:
        """
        Stop debate early (HiL support).
        
        Args:
            reason: Reason for stopping
            
        Returns:
            Stop state
        """
        self.round_control = RoundControl.STOP
        
        logger.info(f"Debate stopped. Reason: {reason}")
        
        return {
            "status": "stopped",
            "current_round": self.current_round,
            "reason": reason,
            "total_rounds_completed": self.current_round,
        }
    
    def can_continue_debate(self) -> bool:
        """Check if debate can continue to next round."""
        if self.round_control == RoundControl.STOP:
            return False
        
        if self.round_control == RoundControl.PAUSE:
            return False
        
        if self.current_round >= self.max_rounds:
            logger.info(f"Max rounds ({self.max_rounds}) reached")
            return False
        
        return True
    
    def extend_round(self, additional_points: str) -> DebateMessage:
        """
        Extend current round with additional discussion (HiL support).
        
        Args:
            additional_points: Additional discussion points
            
        Returns:
            Moderator message about extension
        """
        prompt = f"""
Round {self.current_round} - Extended Discussion:

Additional points raised:
{additional_points}

Provide brief moderation on these additional points and determine if they:
1. Strengthen existing positions
2. Introduce new considerations
3. Resolve previous disagreements
4. Require further analysis

Keep response concise.
"""
        
        response = self.llm_service.generate_response(
            prompt,
            system_instruction=self.system_prompt,
        )
        
        message = DebateMessage(
            agent_name=self.name,
            round_num=self.current_round,
            content=response,
        )
        
        self.message_history.append(message)
        return message
    
    def get_debate_status(self) -> Dict[str, Any]:
        """Get current debate status for HiL dashboard."""
        return {
            "is_paused": self.is_paused,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "can_continue": self.can_continue_debate(),
            "control_state": self.round_control.value,
            "agent_turns": self.agent_turn_counts.copy(),
            "total_messages": len(self.message_history),
        }
    
    def prepare_judge_brief(
        self,
        stock_symbol: str,
        fundamental_analysis: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        debate_messages: List[DebateMessage],
    ) -> str:
        """
        Prepare comprehensive brief for Judge's final decision.
        
        Args:
            stock_symbol: Stock symbol
            fundamental_analysis: Final fundamental analysis
            technical_analysis: Final technical analysis
            sentiment_analysis: Final sentiment analysis
            debate_messages: All debate messages for context
            
        Returns:
            Structured brief for Judge
        """
        prompt = f"""
Prepare comprehensive judge brief for final investment decision on {stock_symbol}:

=== FUNDAMENTAL PERSPECTIVE ===
Signal: {fundamental_analysis['signal']}
Confidence: {fundamental_analysis['confidence']:.0%}
Rationale: {fundamental_analysis['rationale']}

Metrics:
- P/E Ratio: {fundamental_analysis['metrics'].get('pe_ratio', 'N/A')}
- ROE: {fundamental_analysis['metrics'].get('roe', 'N/A')}
- Debt Ratio: {fundamental_analysis['metrics'].get('debt_ratio', 'N/A')}

=== TECHNICAL PERSPECTIVE ===
Signal: {technical_analysis['signal']}
Confidence: {technical_analysis['confidence']:.0%}
Rationale: {technical_analysis['rationale']}

Indicators:
- Trend: {technical_analysis['indicators'].get('trend', 'N/A')}
- RSI: {technical_analysis['indicators'].get('rsi', 'N/A')}
- MACD: {technical_analysis['indicators'].get('macd', 'N/A')}

=== SENTIMENT PERSPECTIVE ===
Signal: {sentiment_analysis['signal']}
Confidence: {sentiment_analysis['confidence']:.0%}
Rationale: {sentiment_analysis['rationale']}

Score: {sentiment_analysis['metrics'].get('sentiment_score', 'N/A')}

=== DEBATE SUMMARY ===
Debate Rounds: {len(debate_messages)}
Key Points: [Insert debate highlights]

Provide structured output for Judge with:
1. Convergence: Where do analysts agree?
2. Divergence: Where do they disagree?
3. Key Risks: What could go wrong?
4. Key Catalysts: What could drive decision?
5. Recommendation Strength: How strong is each signal?
"""
        
        response = self.llm_service.generate_response(
            prompt,
            system_instruction=self.system_prompt,
        )
        
        self.debate_summary = response
        return response
