"""
Streaming Debate Orchestrator with Moderator, Judges, and Turn-Based Conversation
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import time

from system_prompts import SystemPrompts
from moderator_judges import ModeratorAgent, JudgePanel
from streaming_conversation import StreamingDebateManager
from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent  
from agents.sentiment_agent import SentimentAgent

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class StreamingDebateOrchestrator:
    """Advanced orchestrator for streaming, moderated debates with judging."""
    
    def __init__(
        self,
        gemini_api_key: str,
        update_callback: Optional[Callable] = None,
        streaming_manager: Optional[StreamingDebateManager] = None
    ):
        """Initialize the streaming debate orchestrator."""
        self.logger = logging.getLogger(__name__)
        self.gemini_api_key = gemini_api_key
        self.update_callback = update_callback
        
        # Initialize streaming manager
        self.streaming_manager = streaming_manager or StreamingDebateManager(update_callback)
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize moderator and judges
        self.moderator = ModeratorAgent(gemini_api_key, update_callback)
        self.judge_panel = JudgePanel(gemini_api_key)
        
        # Debate state
        self.debate_active = False
        self.current_round = 0
        self.conversation_history = []
        
        self.logger.info("Streaming Debate Orchestrator initialized")
    
    def _initialize_agents(self):
        """Initialize all debate agents."""
        try:
            # Initialize analyst agents with enhanced system prompts
            self.technical_agent = TechnicalAgent(
                gemini_api_key=self.gemini_api_key
            )
            self.fundamental_agent = FundamentalAgent(
                gemini_api_key=self.gemini_api_key
            )
            self.sentiment_agent = SentimentAgent(
                gemini_api_key=self.gemini_api_key
            )
            
            self.agents = {
                'TechnicalAnalyst': self.technical_agent,
                'FundamentalAnalyst': self.fundamental_agent,
                'SentimentAnalyst': self.sentiment_agent
            }
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            raise
    
    async def conduct_streaming_debate(
        self,
        stock_symbol: str,
        period: str,
        stock_data: Optional[Dict[str, Any]] = None,
        container = None
    ) -> Dict[str, Any]:
        """Conduct a full streaming debate with moderation and judging."""
        
        try:
            self.debate_active = True
            self.stock_symbol = stock_symbol
            self.period = period
            self.stock_data = stock_data or {}
            
            # Initialize streaming UI
            if container:
                self.streaming_manager.start_streaming_debate(container)
            
            # Show initial status
            self.streaming_manager.show_status_update(
                f"🎬 Starting live debate on {stock_symbol} ({period})"
            )
            
            # Step 1: Gather individual analyses first
            self.streaming_manager.show_status_update("📊 Analysts preparing their research...")
            individual_analyses = await self._gather_individual_analyses_silent()
            
            # Step 2: Start moderated streaming debate
            await self._conduct_moderated_streaming_debate(individual_analyses)
            
            # Step 3: Judge evaluation
            await self._conduct_judging_phase()
            
            # Step 4: Compile final results
            results = self._compile_final_results(individual_analyses)
            
            self.debate_active = False
            self.streaming_manager.stop_streaming()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in streaming debate: {e}")
            self.debate_active = False
            raise
    
    async def _gather_individual_analyses_silent(self) -> Dict[str, Any]:
        """Gather individual analyses without streaming (preparation phase)."""
        analyses = {}
        
        try:
            # Get analyses from each agent
            analyses["technical"] = await self.technical_agent.analyze_data(
                self.stock_symbol, self.period, self.stock_data
            )
            analyses["fundamental"] = await self.fundamental_agent.analyze_data(
                self.stock_symbol, self.period, self.stock_data
            )
            analyses["sentiment"] = await self.sentiment_agent.analyze_data(
                self.stock_symbol, self.period, self.stock_data
            )
            
            self.logger.info("Individual analyses completed")
            return analyses
            
        except Exception as e:
            self.logger.error(f"Error in individual analyses: {e}")
            # Return default analyses
            return {
                "technical": {"signal": "neutral", "confidence": 0.5},
                "fundamental": {"bias": "hold", "confidence": 0.5},
                "sentiment": {"sentiment": "neutral", "confidence": 0.5}
            }
    
    async def _conduct_moderated_streaming_debate(self, individual_analyses: Dict[str, Any]):
        """Conduct the main streaming debate with moderator control."""
        
        # Show debate start
        self.streaming_manager.show_round_transition("🎯 Round 1: Opening Statements")
        
        # Moderator opens the debate
        opening_message = await self.moderator.start_debate(
            self.stock_symbol, self.period, self.stock_data
        )
        
        # Stream moderator opening
        await self._stream_message_with_delay(opening_message, typing_delay=2.0)
        
        # Main debate loop
        while not self.moderator.is_debate_finished():
            
            # Get next speaker from moderator
            next_speaker = self._get_next_speaker_from_last_message()
            
            if not next_speaker:
                break
            
            # Generate agent response
            agent_message = await self._generate_agent_response(
                next_speaker, individual_analyses
            )
            
            if agent_message:
                # Stream agent message
                await self._stream_message_with_delay(agent_message, typing_delay=1.5)
                
                # Get moderator's next instruction
                moderator_response = await self.moderator.get_next_instruction(agent_message)
                
                if moderator_response:
                    # Check for round transition
                    current_round = moderator_response.get('round', 1)
                    if current_round > self.current_round:
                        self.current_round = current_round
                        round_names = {
                            2: "💬 Round 2: Cross-Examination",
                            3: "🔄 Round 3: Rebuttal Round", 
                            4: "🎯 Round 4: Final Arguments"
                        }
                        if current_round in round_names:
                            self.streaming_manager.show_round_transition(round_names[current_round])
                    
                    # Stream moderator response
                    await self._stream_message_with_delay(moderator_response, typing_delay=1.0)
                
                # Brief pause between turns
                await asyncio.sleep(0.5)
        
        # End of debate
        self.streaming_manager.show_status_update("🏁 Debate complete! Judges are now evaluating...")
    
    async def _generate_agent_response(
        self, 
        agent_name: str, 
        individual_analyses: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate response from specified agent based on conversation history."""
        
        if agent_name not in self.agents:
            return None
        
        agent = self.agents[agent_name]
        
        try:
            # Build context-aware prompt
            context_prompt = SystemPrompts.get_conversation_context_prompt(
                self.conversation_history, agent_name.lower().replace('analyst', '')
            )
            
            # Get analysis data for this agent
            agent_data = {}
            if 'Technical' in agent_name:
                agent_data = individual_analyses.get('technical', {})
            elif 'Fundamental' in agent_name:
                agent_data = individual_analyses.get('fundamental', {})
            elif 'Sentiment' in agent_name:
                agent_data = individual_analyses.get('sentiment', {})
            
            # Generate contextual response
            response_text = await self._generate_contextual_response(
                agent, context_prompt, agent_data
            )
            
            # Create message
            message = {
                "round": self.current_round or 1,
                "speaker": agent_name,
                "role": self._get_agent_role(agent_name),
                "message": response_text,
                "timestamp": datetime.now().isoformat()
            }
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating response for {agent_name}: {e}")
            return None
    
    async def _generate_contextual_response(
        self,
        agent,
        context_prompt: str,
        agent_data: Dict[str, Any]
    ) -> str:
        """Generate contextual response using agent's analysis capabilities."""
        
        try:
            # Use agent's existing analysis method but with enhanced context
            if hasattr(agent, 'generate_llm_response'):
                response = await agent.generate_llm_response(
                    f"{context_prompt}\n\nYour analysis data: {agent_data}"
                )
                return response
            else:
                # Fallback generic response
                return f"Based on my analysis, I see several key factors to consider for {self.stock_symbol}."
                
        except Exception as e:
            self.logger.error(f"Error generating contextual response: {e}")
            return "I'll need to review my analysis further before making specific recommendations."
    
    def _get_next_speaker_from_last_message(self) -> Optional[str]:
        """Extract next speaker from last moderator message."""
        if not self.conversation_history:
            return "TechnicalAnalyst"
        
        last_message = self.conversation_history[-1]
        return last_message.get('next_speaker')
    
    def _get_agent_role(self, agent_name: str) -> str:
        """Get role title for agent."""
        roles = {
            'TechnicalAnalyst': 'Technical Analysis Expert',
            'FundamentalAnalyst': 'Fundamental Analysis Expert',
            'SentimentAnalyst': 'Sentiment Analysis Expert'
        }
        return roles.get(agent_name, 'Financial Expert')
    
    async def _stream_message_with_delay(
        self, 
        message: Dict[str, Any], 
        typing_delay: float = 1.5
    ):
        """Stream a message with appropriate delay."""
        # Add to conversation history
        self.conversation_history.append(message)
        
        # Stream to UI
        self.streaming_manager.stream_message_to_ui(
            message, 
            typing_delay=typing_delay,
            chunk_delay=0.04
        )
        
        # Wait for streaming to complete
        estimated_words = len(message.get('message', '').split())
        streaming_time = typing_delay + (estimated_words * 0.04)
        await asyncio.sleep(streaming_time)
    
    async def _conduct_judging_phase(self):
        """Conduct judge evaluation phase."""
        
        self.streaming_manager.show_status_update("👨‍⚖️ Judges are evaluating the debate...")
        
        # Round-by-round evaluation (brief)
        for round_num in range(1, 5):
            round_evaluations = await self.judge_panel.evaluate_round(
                round_num, self.conversation_history
            )
            
            # Stream brief judge comments
            for evaluation in round_evaluations:
                judge_message = {
                    "round": 5,  # Judging phase
                    "speaker": f"Judge{evaluation['judge'][-1]}",
                    "role": "Judge",
                    "message": f"Round {round_num} feedback: {evaluation['evaluation'][:100]}...",
                    "timestamp": datetime.now().isoformat()
                }
                await self._stream_message_with_delay(judge_message, typing_delay=0.8)
        
        # Final judging
        self.streaming_manager.show_status_update("🏆 Final judging in progress...")
        
        final_results = await self.judge_panel.final_judging(self.conversation_history)
        
        # Announce winner
        winner_message = {
            "round": 5,
            "speaker": "JudgePanel",
            "role": "Chief Judge",
            "message": f"🏆 After careful deliberation, the judges declare {final_results['winner']} as the winner of this debate! Final scores: " + 
                      ", ".join([f"{agent}: {score:.1f}/10" for agent, score in final_results['average_scores'].items()]),
            "timestamp": datetime.now().isoformat()
        }
        
        await self._stream_message_with_delay(winner_message, typing_delay=2.5)
        
        return final_results
    
    def _compile_final_results(self, individual_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Compile final debate results."""
        
        return {
            "stock_symbol": self.stock_symbol,
            "analysis_period": self.period,
            "timestamp": datetime.now().isoformat(),
            "individual_analyses": individual_analyses,
            "conversation_history": self.conversation_history,
            "judge_results": self.judge_panel.final_results,
            "total_messages": len(self.conversation_history),
            "total_rounds": self.current_round,
            "agents_participated": len(self.agents),
            "debate_winner": self.judge_panel.final_results.get('winner', 'Unknown')
        }