"""
Debate Orchestrator
Manages multi-round debate flow and coordination.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from agents.fundamental_agent import FundamentalAgent
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.moderator_agent import ModeratorAgent
from agents.judge_agent import JudgeAgent
from agents.base_agent import DebateMessage

import streamlit as st

logger = logging.getLogger(__name__)


@dataclass
class DebateResult:
    """Final debate result."""
    debate_id: str
    stock_symbol: str
    start_time: datetime
    end_time: Optional[datetime]
    num_rounds: int
    final_decision: str
    confidence: float
    summary: str
    transcript: List[DebateMessage]
    rationale: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "debate_id": self.debate_id,
            "stock_symbol": self.stock_symbol,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "num_rounds": self.num_rounds,
            "final_decision": self.final_decision,
            "confidence": self.confidence,
            "summary": self.summary,
            "rationale": self.rationale,
            "transcript": [msg.to_dict() for msg in self.transcript],
        }


class DebateOrchestrator:
    """
    Orchestrates multi-agent investment debate.
    
    Flow:
    1. Initialize all agents
    2. Run debate rounds (initial + rebuttals)
    3. Moderator synthesizes
    4. Judge renders verdict
    5. Store results
    """
    
    def __init__(self, llm_service, db_manager=None):
        """
        Initialize orchestrator.
        
        Args:
            llm_service: Gemini LLM service
            db_manager: Optional database manager for persistence
        """
        self.llm_service = llm_service
        self.db_manager = db_manager
        self.debate_id = str(uuid.uuid4())
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        # Initialize agents
        self.fundamental_agent = FundamentalAgent(
            llm_service,
            system_prompt=self.prompts.get("fundamental"),
        )
        self.technical_agent = TechnicalAgent(
            llm_service,
            system_prompt=self.prompts.get("technical"),
        )
        self.sentiment_agent = SentimentAgent(
            llm_service,
            system_prompt=self.prompts.get("sentiment"),
        )
        self.moderator_agent = ModeratorAgent(
            llm_service,
            system_prompt=self.prompts.get("moderator"),
        )
        self.judge_agent = JudgeAgent(
            llm_service,
            system_prompt=self.prompts.get("judge"),
        )
        
        self.agents = [
            self.fundamental_agent,
            self.technical_agent,
            self.sentiment_agent,
        ]
        
        self.debate_transcript: List[DebateMessage] = []
        logger.info(f"Initialized DebateOrchestrator (debate_id: {self.debate_id})")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load system prompts from files."""
        prompts = {}
        for agent_type in ["fundamental", "technical", "sentiment", "moderator", "judge"]:
            try:
                with open(f"prompts/{agent_type}.txt", "r") as f:
                    prompts[agent_type] = f.read()
            except FileNotFoundError:
                logger.warning(f"Prompt file not found: prompts/{agent_type}.txt")
                prompts[agent_type] = f"You are a {agent_type} agent."
        
        return prompts
    
    def run_debate(
        self,
        stock_symbol: str,
        stock_data: Dict[str, Any],
        num_rounds: int = 3,
        period_days: int = 30,
    ) -> DebateResult:
        """
        Run complete multi-round debate.
        
        Args:
            stock_symbol: Stock to debate
            stock_data: Financial/market data
            num_rounds: Number of debate rounds
            period_days: Analysis period
            
        Returns:
            DebateResult with final decision
        """
        start_time = datetime.utcnow()
        logger.info(
            f"Starting debate on {stock_symbol} "
            f"({num_rounds} rounds, debate_id={self.debate_id})"
        )
        
        # Round 0: Initial analysis by all agents
        logger.info(f"Round 0: Initial analysis")
        analyses = {
            "fundamental": self.fundamental_agent.analyze(stock_symbol, stock_data, period_days),
            "technical": self.technical_agent.analyze(stock_symbol, stock_data, period_days),
            "sentiment": self.sentiment_agent.analyze(stock_symbol, stock_data, period_days),
        }

        # Record initial positions and stream to UI/logs
        for agent_name, analysis in analyses.items():
            msg = DebateMessage(
                agent_name=agent_name.replace("_", " ").title(),
                round_num=0,
                content=f"Signal: {analysis['signal']}\n{analysis['rationale']}",
                analysis=analysis,
            )
            self.debate_transcript.append(msg)

            # Stream to Streamlit UI
            st.write(f"**{msg.agent_name}** (Round {msg.round_num}): {msg.content}")

            # Log to terminal
            print(f"{msg.agent_name} (Round {msg.round_num}): {msg.content}")

        # Rounds 1-N: Debate and rebuttals
        for round_num in range(1, num_rounds + 1):
            logger.info(f"Round {round_num}: Debate and rebuttals")

            # Moderator synthesis
            mod_msg = self.moderator_agent.manage_round(
                round_num,
                self.debate_transcript[-3].content if len(self.debate_transcript) >= 3 else "",
                self.debate_transcript[-2].content if len(self.debate_transcript) >= 2 else "",
                self.debate_transcript[-1].content if len(self.debate_transcript) >= 1 else "",
            )
            self.debate_transcript.append(mod_msg)
            logger.debug(f"Moderator: {mod_msg.content[:100]}...")

            # Stream moderator message
            st.write(f"**Moderator** (Round {round_num}): {mod_msg.content}")
            print(f"Moderator (Round {round_num}): {mod_msg.content}")

            # Agents present rebuttals (in rotation)
            for i, agent in enumerate(self.agents):
                if i == 0:
                    other_agents = self.agents[1:3]
                else:
                    other_agents = [self.agents[j] for j in range(3) if j != i]

                opposing = "\n".join([
                    f"{a.name}: {a.message_history[-1].content[:100] if a.message_history else 'No argument'}"
                    for a in other_agents
                ])

                rebuttal = agent.rebut(
                    round_num,
                    opposing,
                    self.debate_transcript[-5:],  # Last 5 messages for context
                )
                self.debate_transcript.append(rebuttal)
                logger.debug(f"{agent.name}: {rebuttal.content[:100]}...")

                # Stream rebuttal
                st.write(f"**{agent.name}** (Round {round_num}): {rebuttal.content}")
                print(f"{agent.name} (Round {round_num}): {rebuttal.content}")

        # Judge phase: Moderator prepares brief
        logger.info("Final phase: Judge rendering verdict")
        judge_brief = self.moderator_agent.prepare_judge_brief(
            stock_symbol,
            analyses["fundamental"],
            analyses["technical"],
            analyses["sentiment"],
            self.debate_transcript,
        )
        
        # Judge renders verdict
        verdict = self.judge_agent.render_verdict(
            stock_symbol,
            judge_brief,
            analyses["fundamental"],
            analyses["technical"],
            analyses["sentiment"],
        )
        
        # Record judge decision
        judge_msg = DebateMessage(
            agent_name="Judge",
            round_num=99,
            content=f"Decision: {verdict.get('decision')}",
            analysis=verdict,
            is_final=True,
        )
        self.debate_transcript.append(judge_msg)
        
        # Create result
        end_time = datetime.utcnow()
        result = DebateResult(
            debate_id=self.debate_id,
            stock_symbol=stock_symbol,
            start_time=start_time,
            end_time=end_time,
            num_rounds=num_rounds,
            final_decision=verdict.get("decision", "HOLD"),
            confidence=verdict.get("confidence", 0.5),
            summary=verdict.get("summary", ""),
            transcript=self.debate_transcript,
            rationale=verdict.get("rationale", {}),
        )
        
        # Persist to database if available
        if self.db_manager:
            self._persist_result(result, verdict)
        
        logger.info(
            f"Debate complete: {stock_symbol} → {result.final_decision} "
            f"(confidence {result.confidence:.0%})"
        )
        
        return result
    
    def _persist_result(self, result: DebateResult, verdict: Dict[str, Any]):
        """Persist debate result to database."""
        try:
            from db.models import DebateLog
            import json
            
            session = self.db_manager.get_session()
            
            log = DebateLog(
                debate_id=result.debate_id,
                stock_symbol=result.stock_symbol,
                start_time=result.start_time,
                end_time=result.end_time,
                num_rounds=result.num_rounds,
                final_decision=result.final_decision,
                confidence_score=result.confidence,
                transcript="\n".join([f"{m.agent_name}: {m.content}" for m in result.transcript]),
                summary=result.summary,
                debate_json=result.to_dict(),
            )
            
            session.add(log)
            session.commit()
            session.close()
            
            logger.info(f"Persisted debate {result.debate_id} to database")
        
        except Exception as e:
            logger.error(f"Failed to persist result: {e}")
    
    def reset(self):
        """Reset orchestrator for new debate."""
        self.debate_id = str(uuid.uuid4())
        self.debate_transcript = []
        for agent in self.agents + [self.moderator_agent, self.judge_agent]:
            agent.clear_history()
        logger.info(f"Reset orchestrator (new debate_id: {self.debate_id})")
