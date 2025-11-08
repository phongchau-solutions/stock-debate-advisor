"""
Debate Orchestrator using Microsoft Autogen for Multi-Agent Financial Analysis
"""
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import streamlit as st

try:
    from autogen import GroupChat, GroupChatManager, ConversableAgent
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    # Fallback classes for development
    from gemini_client import GeminiConversableAgent
    class GroupChat:
        def __init__(self, *args, **kwargs):
            pass
    
    class GroupChatManager:
        def __init__(self, *args, **kwargs):
            pass
    
    class ConversableAgent:
        def __init__(self, *args, **kwargs):
            pass

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent


class DebateOrchestrator:
    """Orchestrates multi-agent financial debate using Autogen."""
    
    def __init__(
        self, 
        gemini_api_key: str,
        max_rounds: int = 5,
        debate_topic: str = "Vietnamese Stock Investment Decision",
        update_callback: Optional[Callable] = None
    ):
        """Initialize the debate orchestrator."""
        self.gemini_api_key = gemini_api_key
        self.max_rounds = max_rounds
        self.debate_topic = debate_topic
        self.update_callback = update_callback
        
        # Debate state
        self.debate_messages = []
        self.current_round = 0
        self.final_decision = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize Autogen components if available
        if AUTOGEN_AVAILABLE:
            self._initialize_autogen()
        else:
            self.logger.warning("Autogen not available, using fallback implementation")
    
    def _initialize_agents(self):
        """Initialize the financial analysis agents."""
        try:
            self.technical_agent = TechnicalAgent(
                gemini_api_key=self.gemini_api_key,
                max_consecutive_auto_reply=2
            )
            
            self.fundamental_agent = FundamentalAgent(
                gemini_api_key=self.gemini_api_key,
                max_consecutive_auto_reply=2
            )
            
            self.sentiment_agent = SentimentAgent(
                gemini_api_key=self.gemini_api_key,
                max_consecutive_auto_reply=2
            )
            
            self.agents = [self.technical_agent, self.fundamental_agent, self.sentiment_agent]
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            raise
    
    def _initialize_autogen(self):
        """Initialize Autogen group chat and manager."""
        try:
            # Create a human proxy agent for coordination
            self.coordinator = ConversableAgent(
                name="DebateCoordinator",
                system_message="""You are a debate coordinator for financial analysis.
                Your role is to facilitate structured debate between Technical, Fundamental, and Sentiment analysts.
                
                Debate Rules:
                1. Each agent presents their analysis
                2. Agents can challenge or support others' reasoning
                3. Maintain focus on the target stock and time period
                4. Drive toward a consensus decision: BUY/HOLD/SELL
                5. Ensure each round has substantive discussion
                
                End the debate when consensus is reached or after 5 rounds.
                """,
                llm_config={
                    "config_list": [{
                        "model": "custom_gemini",
                        "api_key": self.gemini_api_key,
                        "api_type": "custom"
                    }],
                    "timeout": 120,
                },
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1
            )
            
            # Create group chat
            self.group_chat = GroupChat(
                agents=[self.coordinator] + self.agents,
                messages=[],
                max_round=self.max_rounds,
                speaker_selection_method="round_robin"
            )
            
            # Create group chat manager
            self.chat_manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config={
                    "config_list": [{
                        "model": "custom_gemini",
                        "api_key": self.gemini_api_key,
                        "api_type": "custom"
                    }],
                    "timeout": 120,
                }
            )
            
            self.logger.info("Autogen group chat initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Autogen: {e}")
            raise
    
    async def conduct_debate(
        self, 
        stock_symbol: str, 
        period: str,
        stock_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conduct the multi-agent debate."""
        try:
            self.logger.info(f"Starting debate for {stock_symbol} over {period}")
            
            # Step 1: Individual agent analysis
            individual_analyses = await self._gather_individual_analyses(
                stock_symbol, period, stock_data
            )
            
            # Step 2: Conduct structured debate
            if AUTOGEN_AVAILABLE:
                debate_transcript = await self._conduct_autogen_debate(
                    stock_symbol, period, individual_analyses
                )
            else:
                debate_transcript = await self._conduct_fallback_debate(
                    stock_symbol, period, individual_analyses
                )
            
            # Step 3: Generate final decision
            final_decision = await self._generate_final_decision(
                stock_symbol, individual_analyses, debate_transcript
            )
            
            # Step 4: Compile results
            results = {
                "stock_symbol": stock_symbol,
                "analysis_period": period,
                "timestamp": datetime.now().isoformat(),
                "individual_analyses": individual_analyses,
                "debate_transcript": debate_transcript,
                "final_decision": final_decision,
                "total_rounds": len(debate_transcript),
                "agents_participated": len(self.agents)
            }
            
            self.logger.info("Debate completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error conducting debate: {e}")
            raise
    
    async def _gather_individual_analyses(
        self, 
        stock_symbol: str, 
        period: str,
        stock_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gather initial analysis from each agent."""
        self.logger.info("Gathering individual agent analyses")
        
        # Prepare data context
        data_context = stock_data or {}
        
        analyses = {}
        
        try:
            # Technical analysis
            self._update_progress("Analyzing technical indicators...")
            technical_analysis = await self.technical_agent.analyze_data(
                stock_symbol, period, data_context
            )
            analyses["technical"] = technical_analysis
            
            # Fundamental analysis
            self._update_progress("Analyzing fundamental metrics...")
            fundamental_analysis = await self.fundamental_agent.analyze_data(
                stock_symbol, period, data_context
            )
            analyses["fundamental"] = fundamental_analysis
            
            # Sentiment analysis
            self._update_progress("Analyzing market sentiment...")
            sentiment_analysis = await self.sentiment_agent.analyze_data(
                stock_symbol, period, data_context
            )
            analyses["sentiment"] = sentiment_analysis
            
            self.logger.info("Individual analyses completed")
            return analyses
            
        except Exception as e:
            self.logger.error(f"Error in individual analyses: {e}")
            raise
    
    async def _conduct_autogen_debate(
        self,
        stock_symbol: str,
        period: str,
        individual_analyses: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Conduct debate using Autogen framework."""
        debate_transcript = []
        
        try:
            # Initial message to start the debate
            initial_message = f"""
            Let's analyze {stock_symbol} for investment decision over {period}.
            
            Individual Analysis Summary:
            
            Technical Analysis: {individual_analyses['technical'].get('signal', 'neutral')} 
            (Confidence: {individual_analyses['technical'].get('confidence', 0.5):.2f})
            
            Fundamental Analysis: {individual_analyses['fundamental'].get('bias', 'hold')}
            (Confidence: {individual_analyses['fundamental'].get('confidence', 0.5):.2f})
            
            Sentiment Analysis: {individual_analyses['sentiment'].get('sentiment', 'neutral')}
            (Confidence: {individual_analyses['sentiment'].get('confidence', 0.5):.2f})
            
            Please debate these findings and reach a consensus on BUY/HOLD/SELL recommendation.
            Each agent should present their case and respond to others' arguments.
            """
            
            # Add callback for message tracking
            def message_callback(sender, message, recipient, silent):
                debate_message = {
                    "round": len(debate_transcript) + 1,
                    "speaker": sender.name if hasattr(sender, 'name') else 'Unknown',
                    "role": getattr(sender, 'role', 'Unknown'),
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                debate_transcript.append(debate_message)
                self._update_progress(f"Round {len(debate_transcript)}: {sender.name}")
            
            # Start the group chat
            self.coordinator.initiate_chat(
                self.chat_manager,
                message=initial_message,
                silent=False
            )
            
            return debate_transcript
            
        except Exception as e:
            self.logger.error(f"Error in Autogen debate: {e}")
            return await self._conduct_fallback_debate(stock_symbol, period, individual_analyses)
    
    async def _conduct_fallback_debate(
        self,
        stock_symbol: str,
        period: str,
        individual_analyses: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback debate implementation without Autogen."""
        debate_transcript = []
        
        self.logger.info("Using fallback debate implementation")
        
        # Round 1: Initial positions
        self._update_progress("Round 1: Initial positions")
        
        # Technical agent opening
        tech_message = self._create_agent_message(
            self.technical_agent,
            f"Based on my technical analysis of {stock_symbol}, I see a {individual_analyses['technical'].get('signal', 'neutral')} signal. "
            f"The current price shows {individual_analyses['technical'].get('rationale', 'mixed indicators')}",
            1
        )
        debate_transcript.append(tech_message)
        
        # Fundamental agent opening
        fund_message = self._create_agent_message(
            self.fundamental_agent,
            f"From a fundamental perspective, {stock_symbol} appears {individual_analyses['fundamental'].get('valuation', 'fairly valued')}. "
            f"My recommendation is {individual_analyses['fundamental'].get('bias', 'hold')} based on "
            f"{individual_analyses['fundamental'].get('rationale', 'financial metrics analysis')}",
            1
        )
        debate_transcript.append(fund_message)
        
        # Sentiment agent opening  
        sent_message = self._create_agent_message(
            self.sentiment_agent,
            f"Market sentiment for {stock_symbol} is currently {individual_analyses['sentiment'].get('sentiment', 'neutral')}. "
            f"News analysis shows {individual_analyses['sentiment'].get('rationale', 'mixed sentiment signals')}",
            1
        )
        debate_transcript.append(sent_message)
        
        # Round 2: Cross-examination
        self._update_progress("Round 2: Cross-examination")
        
        # Technical challenges fundamental
        tech_challenge = self._create_agent_message(
            self.technical_agent,
            f"While the fundamental analysis suggests {individual_analyses['fundamental'].get('bias', 'hold')}, "
            f"the technical indicators show momentum that might override fundamental valuation in the short term. "
            f"Price action often leads fundamental recognition.",
            2
        )
        debate_transcript.append(tech_challenge)
        
        # Fundamental responds to technical
        fund_response = self._create_agent_message(
            self.fundamental_agent,
            f"Technical signals can be misleading without fundamental backing. "
            f"The company's {individual_analyses['fundamental'].get('key_metrics', {}).get('roe', 'N/A')}% ROE "
            f"and debt levels suggest sustainable value that technical analysis might miss.",
            2
        )
        debate_transcript.append(fund_response)
        
        # Round 3: Sentiment integration
        self._update_progress("Round 3: Sentiment integration")
        
        sent_integration = self._create_agent_message(
            self.sentiment_agent,
            f"Both technical and fundamental views need to consider market psychology. "
            f"Current sentiment score of {individual_analyses['sentiment'].get('sentiment_score', 0):.2f} "
            f"suggests {individual_analyses['sentiment'].get('news_impact', 'moderate')} impact from recent news.",
            3
        )
        debate_transcript.append(sent_integration)
        
        # Round 4: Consensus building
        self._update_progress("Round 4: Building consensus")
        
        # Each agent adjusts position
        for i, (agent, analysis_key) in enumerate(zip(self.agents, ['technical', 'fundamental', 'sentiment'])):
            adjustment_message = self._create_agent_message(
                agent,
                f"Considering all perspectives, I maintain my {individual_analyses[analysis_key].get('bias', individual_analyses[analysis_key].get('signal', 'neutral'))} stance "
                f"but acknowledge the points raised by other analysts. Confidence level: "
                f"{individual_analyses[analysis_key].get('confidence', 0.5):.2f}",
                4
            )
            debate_transcript.append(adjustment_message)
        
        # Round 5: Final decision
        self._update_progress("Round 5: Final decision")
        
        final_message = self._create_agent_message(
            {"name": "DebateCoordinator", "role": "Coordinator"},
            f"After thorough debate, we need to reach a consensus on {stock_symbol}. "
            f"Considering technical signals, fundamental valuation, and market sentiment, "
            f"the analysis points toward a balanced investment decision.",
            5
        )
        debate_transcript.append(final_message)
        
        return debate_transcript
    
    def _create_agent_message(self, agent, content: str, round_num: int) -> Dict[str, Any]:
        """Create a standardized agent message."""
        if isinstance(agent, dict):
            name = agent.get("name", "Unknown")
            role = agent.get("role", "Unknown")
        else:
            name = getattr(agent, 'name', agent.__class__.__name__)
            role = getattr(agent, 'role', 'Analyst')
        
        return {
            "round": round_num,
            "speaker": name,
            "role": role,
            "message": content,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_final_decision(
        self,
        stock_symbol: str,
        individual_analyses: Dict[str, Any],
        debate_transcript: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate final investment decision based on debate."""
        
        # Collect all recommendations
        technical_signal = individual_analyses['technical'].get('signal', 'neutral')
        fundamental_bias = individual_analyses['fundamental'].get('bias', 'hold')
        sentiment = individual_analyses['sentiment'].get('sentiment', 'neutral')
        
        # Map signals to scores
        signal_scores = {
            'bullish': 1, 'buy': 1, 'positive': 1,
            'bearish': -1, 'sell': -1, 'negative': -1,
            'neutral': 0, 'hold': 0
        }
        
        tech_score = signal_scores.get(technical_signal, 0)
        fund_score = signal_scores.get(fundamental_bias, 0)
        sent_score = signal_scores.get(sentiment, 0)
        
        # Weight by confidence
        tech_confidence = individual_analyses['technical'].get('confidence', 0.5)
        fund_confidence = individual_analyses['fundamental'].get('confidence', 0.5)
        sent_confidence = individual_analyses['sentiment'].get('confidence', 0.5)
        
        weighted_score = (
            tech_score * tech_confidence + 
            fund_score * fund_confidence + 
            sent_score * sent_confidence
        ) / (tech_confidence + fund_confidence + sent_confidence)
        
        # Determine final action
        if weighted_score > 0.3:
            action = "BUY"
        elif weighted_score < -0.3:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Calculate overall confidence
        overall_confidence = (tech_confidence + fund_confidence + sent_confidence) / 3
        
        # Generate rationale using Gemini
        rationale_prompt = f"""
        Based on the multi-agent debate for {stock_symbol}, provide a comprehensive rationale for the {action} recommendation.
        
        Individual Analysis Summary:
        - Technical: {technical_signal} (confidence: {tech_confidence:.2f})
        - Fundamental: {fundamental_bias} (confidence: {fund_confidence:.2f})
        - Sentiment: {sentiment} (confidence: {sent_confidence:.2f})
        
        Debate highlights:
        {self._extract_debate_highlights(debate_transcript)}
        
        Provide a clear, concise rationale for the investment decision.
        """
        
        try:
            rationale = self.technical_agent.generate_llm_response(rationale_prompt)
        except:
            rationale = f"Consensus recommendation based on weighted analysis of technical, fundamental, and sentiment factors."
        
        # Calculate target price (average of individual targets)
        tech_target = individual_analyses['technical'].get('target_price', 0)
        fund_target = individual_analyses['fundamental'].get('fair_value', 0)
        target_price = (tech_target + fund_target) / 2 if tech_target and fund_target else tech_target or fund_target or 0
        
        final_decision = {
            "action": action,
            "confidence": overall_confidence,
            "target_price": target_price,
            "rationale": rationale,
            "weighted_score": weighted_score,
            "individual_signals": {
                "technical": technical_signal,
                "fundamental": fundamental_bias,
                "sentiment": sentiment
            },
            "risk_assessment": self._assess_overall_risk(individual_analyses),
            "key_factors": self._extract_key_factors(individual_analyses)
        }
        
        return final_decision
    
    def _extract_debate_highlights(self, debate_transcript: List[Dict[str, Any]]) -> str:
        """Extract key points from debate transcript."""
        highlights = []
        for message in debate_transcript[-3:]:  # Last 3 messages
            speaker = message.get('speaker', 'Unknown')
            content = message.get('message', '')[:200] + "..." if len(message.get('message', '')) > 200 else message.get('message', '')
            highlights.append(f"{speaker}: {content}")
        
        return "\n".join(highlights)
    
    def _assess_overall_risk(self, individual_analyses: Dict[str, Any]) -> str:
        """Assess overall investment risk."""
        risks = []
        
        # Technical risks
        tech_confidence = individual_analyses['technical'].get('confidence', 0.5)
        if tech_confidence < 0.6:
            risks.append("Technical signals show uncertainty")
        
        # Fundamental risks
        fund_risks = individual_analyses['fundamental'].get('risk_factors', [])
        risks.extend(fund_risks[:2])  # Top 2 fundamental risks
        
        # Sentiment risks
        sent_confidence = individual_analyses['sentiment'].get('confidence', 0.5)
        if sent_confidence < 0.6:
            risks.append("Market sentiment is mixed or uncertain")
        
        if len(risks) > 3:
            return "HIGH - Multiple risk factors identified"
        elif len(risks) > 1:
            return "MEDIUM - Some risk factors present"
        else:
            return "LOW - Minimal risk factors identified"
    
    def _extract_key_factors(self, individual_analyses: Dict[str, Any]) -> List[str]:
        """Extract key decision factors."""
        factors = []
        
        # Technical factors
        tech_indicators = individual_analyses['technical'].get('key_indicators', {})
        if tech_indicators.get('trend') == 'upward':
            factors.append("Positive price trend")
        
        # Fundamental factors
        valuation = individual_analyses['fundamental'].get('valuation', '')
        if valuation:
            factors.append(f"Stock appears {valuation}")
        
        # Sentiment factors
        sent_impact = individual_analyses['sentiment'].get('news_impact', '')
        if sent_impact in ['high', 'medium']:
            factors.append(f"News sentiment has {sent_impact} impact")
        
        return factors[:5]  # Top 5 factors
    
    def _update_progress(self, message: str):
        """Update progress via callback."""
        if self.update_callback:
            self.update_callback(message)
        self.logger.info(message)