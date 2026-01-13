"""
Debate Orchestrator v2 with Knowledge Management
Coordinates multi-agent debates with persistent knowledge loading
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import google.generativeai as genai
from crewai import Crew
from agents import DebateAgents, AnalysisTasks
from knowledge_manager import get_knowledge_manager, DebateSessionKnowledge
from config import config
from constants import (
    AgentRole, InvestmentAction, DebateDecision,
    DebateConstants, PromptConstants, SuccessMessages, ErrorMessages
)


class DebateSession:
    """Represents a single debate session with persistent knowledge"""
    
    def __init__(self, session_id: str, symbol: str, knowledge: DebateSessionKnowledge):
        self.session_id = session_id
        self.symbol = symbol
        self.knowledge = knowledge
        self.created_at = datetime.now()
        self.debate_transcript: List[Dict[str, str]] = []
        self.current_round = 0
        self.verdict = None
        self.crew = None


class DebateOrchestrator:
    """
    Orchestrates multi-agent stock debates with knowledge persistence.
    
    Key Features:
    - Loads financial reports for fundamental analysis
    - Loads technical data for technical analysis
    - Loads news/sentiment data for sentiment analysis
    - Data persists throughout debate session
    - Session-based knowledge management
    """
    
    def __init__(self):
        """Initialize orchestrator and knowledge system"""
        config.validate()
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        self.agent_factory = DebateAgents()
        self.task_factory = AnalysisTasks()
        self.knowledge_manager = get_knowledge_manager()
        
        # Active sessions
        self.sessions: Dict[str, DebateSession] = {}
    
    def get_available_symbols(self) -> List[str]:
        """Get available stock symbols from data directory"""
        return self.knowledge_manager.get_available_symbols()
    
    def start_debate_session(self, symbol: str, rounds: int = 3) -> Dict[str, Any]:
        """
        Start a new debate session with knowledge loading.
        
        Args:
            symbol: Stock symbol
            rounds: Number of debate rounds
            
        Returns:
            Session info with session_id
        """
        # Create session
        session_id = str(uuid.uuid4())
        
        try:
            # Load knowledge for this session
            knowledge = self.knowledge_manager.load_session_knowledge(session_id, symbol)
            
            # Create session
            session = DebateSession(session_id, symbol, knowledge)
            self.sessions[session_id] = session
            
            # Log what was loaded
            info = {
                "session_id": session_id,
                "symbol": symbol,
                "status": "initialized",
                "data_loaded": {
                    "financial_reports": len(knowledge.financial_reports),
                    "technical_datapoints": len(knowledge.technical_data.closes) if knowledge.technical_data else 0,
                    "news_articles": len(knowledge.news_articles)
                },
                "rounds": rounds
            }
            
            print(f"✅ Debate session {session_id} started for {symbol}")
            print(f"   Financial reports: {len(knowledge.financial_reports)}")
            print(f"   Technical data points: {len(knowledge.technical_data.closes) if knowledge.technical_data else 0}")
            print(f"   News articles: {len(knowledge.news_articles)}")
            
            return info
            
        except Exception as e:
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_session_knowledge(self, session_id: str) -> Optional[DebateSessionKnowledge]:
        """Get knowledge for a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].knowledge
        return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get info about a debate session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        knowledge = session.knowledge
        
        return {
            "session_id": session_id,
            "symbol": session.symbol,
            "created_at": session.created_at.isoformat(),
            "current_round": session.current_round,
            "data": {
                "financial_reports": len(knowledge.financial_reports),
                "technical_datapoints": len(knowledge.technical_data.closes) if knowledge.technical_data else 0,
                "news_articles": len(knowledge.news_articles),
                "current_price": knowledge.technical_data.current_price if knowledge.technical_data else None
            },
            "verdict": session.verdict,
            "transcript_length": len(session.debate_transcript)
        }
    
    def run_debate_round(
        self, 
        session_id: str, 
        round_num: int = 1
    ) -> Dict[str, Any]:
        """
        Run a single debate round.
        
        Args:
            session_id: Session ID
            round_num: Round number
            
        Returns:
            Debate results
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        knowledge = session.knowledge
        symbol = session.symbol
        
        try:
            # Get knowledge context for each agent
            fundamental_context = self.knowledge_manager.get_fundamental_knowledge(session_id)
            technical_context = self.knowledge_manager.get_technical_knowledge(session_id)
            sentiment_context = self.knowledge_manager.get_sentiment_knowledge(session_id)
            moderator_context = self.knowledge_manager.get_context_for_moderator(session_id)
            
            # Create agents with session_id for data service integration
            fundamental_agent = self.agent_factory.create_fundamental_agent(
                fundamental_context, 
                session_id=session_id
            )
            technical_agent = self.agent_factory.create_technical_agent(
                technical_context, 
                session_id=session_id
            )
            sentiment_agent = self.agent_factory.create_sentiment_agent(
                sentiment_context, 
                session_id=session_id
            )
            moderator_agent = self.agent_factory.create_moderator_agent(session_id=session_id)
            judge_agent = self.agent_factory.create_judge_agent(session_id=session_id)
            
            # Create tasks with session_id for data service calls
            fundamental_task = self.task_factory.create_fundamental_analysis_task(
                fundamental_agent, 
                symbol,
                fundamental_context,
                debate_round=round_num,
                session_id=session_id
            )
            technical_task = self.task_factory.create_technical_analysis_task(
                technical_agent, 
                symbol,
                technical_context,
                debate_round=round_num,
                session_id=session_id
            )
            sentiment_task = self.task_factory.create_sentiment_analysis_task(
                sentiment_agent, 
                symbol,
                sentiment_context,
                debate_round=round_num,
                session_id=session_id
            )
            moderation_task = self.task_factory.create_moderation_task(
                moderator_agent,
                symbol,
                moderator_context
            )
            judge_task = self.task_factory.create_final_judgment_task(
                judge_agent,
                symbol,
                f"Based on all analysis for round {round_num}"
            )
            
            # Create and run crew
            crew = Crew(
                agents=[
                    fundamental_agent,
                    technical_agent,
                    sentiment_agent,
                    moderator_agent,
                    judge_agent
                ],
                tasks=[
                    fundamental_task,
                    technical_task,
                    sentiment_task,
                    moderation_task,
                    judge_task
                ],
                verbose=config.VERBOSE,
                memory=True,
                max_rpm=30
            )
            
            # Run crew
            result = crew.kickoff()
            
            # Store in session
            session.current_round = round_num
            session.debate_transcript.append({
                "round": round_num,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            })
            session.crew = crew
            
            return {
                "session_id": session_id,
                "round": round_num,
                "result": str(result),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "session_id": session_id,
                "round": round_num,
                "status": "error",
                "error": str(e)
            }
    
    def get_debate_results(self, session_id: str) -> Dict[str, Any]:
        """Get complete debate results for a session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "symbol": session.symbol,
            "rounds_completed": session.current_round,
            "transcript": session.debate_transcript,
            "verdict": session.verdict,
            "knowledge_summary": {
                "financial_reports_used": len(session.knowledge.financial_reports),
                "technical_datapoints": len(session.knowledge.technical_data.closes) if session.knowledge.technical_data else 0,
                "news_articles_analyzed": len(session.knowledge.news_articles)
            }
        }
    
    def end_debate_session(self, session_id: str):
        """End a debate session and clean up"""
        if session_id in self.sessions:
            # Clear knowledge cache
            self.knowledge_manager.clear_session(session_id)
            # Remove session
            del self.sessions[session_id]
            return {"status": "session_ended", "session_id": session_id}
        
        return {"error": "Session not found"}


# Global orchestrator instance
_orchestrator = None


def get_orchestrator() -> DebateOrchestrator:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DebateOrchestrator()
    return _orchestrator
