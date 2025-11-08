"""
Simplified Debate Orchestrator with Direct Gemini Integration
"""
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import google.generativeai as genai

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent


class SimpleDebateOrchestrator:
    """Simplified orchestrator that uses pure Gemini without Autogen complications."""
    
    def __init__(
        self, 
        gemini_api_key: str,
        max_rounds: int = 5,
        debate_topic: str = "Vietnamese Stock Investment Decision",
        update_callback: Optional[Callable[[str], None]] = None
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
        
        # Configure Gemini
        try:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            self.logger.info("Gemini configured successfully")
        except Exception as e:
            self.logger.error(f"Error configuring Gemini: {e}")
            self.gemini_model = None
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize the financial analysis agents."""
        try:
            self.technical_agent = TechnicalAgent(
                gemini_api_key=self.gemini_api_key
            )
            
            self.fundamental_agent = FundamentalAgent(
                gemini_api_key=self.gemini_api_key
            )
            
            self.sentiment_agent = SentimentAgent(
                gemini_api_key=self.gemini_api_key
            )
            
            self.agents = [self.technical_agent, self.fundamental_agent, self.sentiment_agent]
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
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
            debate_transcript = await self._conduct_simple_debate(
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
    
    async def _conduct_simple_debate(
        self,
        stock_symbol: str,
        period: str,
        individual_analyses: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Conduct debate using conversational approach similar to ChatGPT/Gemini."""
        debate_transcript = []
        
        self.logger.info("Starting conversational debate")
        
        # Extract key data for conversation
        tech_signal = individual_analyses.get('technical', {}).get('signal', 'neutral')
        tech_confidence = individual_analyses.get('technical', {}).get('confidence', 0.5)
        fund_bias = individual_analyses.get('fundamental', {}).get('bias', 'hold')
        fund_valuation = individual_analyses.get('fundamental', {}).get('valuation', 'fairly valued')
        sentiment = individual_analyses.get('sentiment', {}).get('sentiment', 'neutral')
        news_impact = individual_analyses.get('sentiment', {}).get('news_impact', 'low')
        
        # Round 1: Opening statements
        self._update_progress("Round 1: Opening statements")
        
        tech_opening = await self._generate_conversational_message(
            "TechnicalAnalyst",
            f"Hello everyone! I've completed my technical analysis of {stock_symbol}. Looking at the charts and indicators over the {period} period, I'm seeing a {tech_signal} signal with {tech_confidence:.1%} confidence. The price action, volume patterns, and momentum indicators are all pointing in this direction. What are your thoughts on the fundamental and sentiment side?",
            individual_analyses,
            []
        )
        debate_transcript.append(tech_opening)
        
        # Fundamental responds to technical
        fund_response = await self._generate_conversational_message(
            "FundamentalAnalyst", 
            f"Interesting perspective on the technicals! From my fundamental analysis, {stock_symbol} appears {fund_valuation} right now. I'm leaning towards a {fund_bias} recommendation based on the company's financial health, earnings outlook, and valuation metrics. @TechnicalAnalyst, your {tech_signal} signal - does that align with what you're seeing in terms of support/resistance levels?",
            individual_analyses,
            debate_transcript
        )
        debate_transcript.append(fund_response)
        
        # Technical responds back
        tech_response = await self._generate_conversational_message(
            "TechnicalAnalyst",
            f"@FundamentalAnalyst, great question! The {tech_signal} signal I'm seeing does have some interesting interactions with key levels. However, I'm curious about your {fund_bias} recommendation - are there any specific catalysts in the fundamental data that could accelerate price movement? @SentimentAnalyst, what's the market feeling about this stock lately?",
            individual_analyses,
            debate_transcript
        )
        debate_transcript.append(tech_response)
        
        # Round 2: Sentiment joins the conversation
        self._update_progress("Round 2: Cross-analysis discussion")
        
        sentiment_entry = await self._generate_conversational_message(
            "SentimentAnalyst",
            f"Thanks for bringing me in! The sentiment picture for {stock_symbol} is quite {sentiment} right now with {news_impact} impact from recent news flow. @FundamentalAnalyst, your {fund_bias} view is interesting - I'm seeing some {sentiment} sentiment that could either support or challenge that thesis. @TechnicalAnalyst, sentiment can often be a leading indicator for your technical patterns. Have you noticed any divergences?",
            individual_analyses,
            debate_transcript
        )
        debate_transcript.append(sentiment_entry)
        
        # Cross-examination round using Gemini for natural responses
        if self.gemini_model:
            try:
                # Generate more natural back-and-forth
                debate_responses = await self._generate_debate_round(
                    stock_symbol, individual_analyses, debate_transcript
                )
                debate_transcript.extend(debate_responses)
                
            except Exception as e:
                self.logger.error(f"Error generating debate round: {e}")
        
        # Round 3: Consensus building conversation
        self._update_progress("Round 3: Building consensus")
        
        # Moderator summarizes and asks for final thoughts
        moderator_summary = await self._generate_conversational_message(
            "DebateModerator",
            f"Excellent discussion everyone! Let me summarize what I'm hearing: Technical analysis shows {tech_signal}, fundamentals suggest {fund_bias}, and sentiment is {sentiment}. Before we finalize our recommendation, let me ask each of you - what's your biggest concern about the opposing viewpoints, and what would change your mind?",
            individual_analyses,
            debate_transcript
        )
        debate_transcript.append(moderator_summary)
        
        # Final round of responses
        final_responses = await self._generate_final_consensus_round(
            stock_symbol, individual_analyses, debate_transcript
        )
        debate_transcript.extend(final_responses)
        
        return debate_transcript
    
    async def _generate_conversational_message(
        self,
        speaker: str,
        content: str,
        individual_analyses: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a conversational message from an agent."""
        
        # Map speaker to role
        role_map = {
            "TechnicalAnalyst": "Technical Analysis Expert",
            "FundamentalAnalyst": "Fundamental Analysis Expert", 
            "SentimentAnalyst": "Sentiment Analysis Expert",
            "DebateModerator": "Debate Moderator"
        }
        
        role = role_map.get(speaker, "Expert")
        
        # If Gemini is available, enhance the message
        if self.gemini_model and len(conversation_history) > 0:
            try:
                # Build context from conversation history
                context = self._build_conversation_context(conversation_history)
                
                enhance_prompt = f"""
                You are {speaker}, a {role} in a financial debate. 
                
                Previous conversation:
                {context}
                
                Your role: {self._get_agent_expertise(speaker)}
                
                Current message to enhance: "{content}"
                
                Make this message more conversational, natural, and engaging while maintaining professionalism. 
                Keep the core information but make it sound like a real expert having a discussion.
                Include references to other analysts' points when appropriate.
                Maximum 150 words.
                """
                
                response = self.gemini_model.generate_content(enhance_prompt)
                if response.text and len(response.text.strip()) > 0:
                    content = response.text.strip()
                    
            except Exception as e:
                self.logger.error(f"Error enhancing message: {e}")
        
        return self._create_agent_message(speaker, role, content, len(conversation_history) // 3 + 1)
    
    async def _generate_debate_round(
        self,
        stock_symbol: str,
        individual_analyses: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate a round of natural debate responses."""
        responses = []
        
        if not self.gemini_model:
            return responses
        
        try:
            context = self._build_conversation_context(conversation_history)
            
            # Generate responses for each agent
            agents = ["FundamentalAnalyst", "SentimentAnalyst", "TechnicalAnalyst"]
            
            for i, agent in enumerate(agents):
                prompt = f"""
                You are {agent} in a professional financial debate about {stock_symbol}.
                
                Previous conversation:
                {context}
                
                Your expertise: {self._get_agent_expertise(agent)}
                
                Generate a natural, conversational response (100-120 words) that:
                1. Responds to points made by other analysts
                2. Adds new insights from your area of expertise
                3. Asks thoughtful questions or challenges assumptions
                4. Maintains professional but conversational tone
                5. References specific data or analysis when relevant
                
                Make it feel like a real expert discussion, not a formal report.
                """
                
                response = self.gemini_model.generate_content(prompt)
                if response.text:
                    message = self._create_agent_message(
                        agent,
                        self._get_agent_role(agent),
                        response.text.strip(),
                        len(conversation_history) // 3 + 2
                    )
                    responses.append(message)
                    
                    # Add to context for next agent
                    conversation_history.append(message)
                    context = self._build_conversation_context(conversation_history)
                    
        except Exception as e:
            self.logger.error(f"Error generating debate round: {e}")
        
        return responses
    
    async def _generate_final_consensus_round(
        self,
        stock_symbol: str,
        individual_analyses: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate final consensus-building responses."""
        responses = []
        
        if not self.gemini_model:
            return responses
        
        try:
            context = self._build_conversation_context(conversation_history[-6:])  # Last 6 messages
            
            # Each agent gives final thoughts
            agents = ["TechnicalAnalyst", "FundamentalAnalyst", "SentimentAnalyst"]
            
            for agent in agents:
                prompt = f"""
                You are {agent} wrapping up a financial debate about {stock_symbol}.
                
                Recent conversation:
                {context}
                
                Your expertise: {self._get_agent_expertise(agent)}
                
                Give your final thoughts (80-100 words):
                1. Acknowledge valid points from other analysts
                2. State your final recommendation with confidence level
                3. Mention your biggest concern or risk factor
                4. Keep it conversational and conclusive
                
                This is your final statement in the debate.
                """
                
                response = self.gemini_model.generate_content(prompt)
                if response.text:
                    message = self._create_agent_message(
                        agent,
                        self._get_agent_role(agent),
                        response.text.strip(),
                        len(conversation_history) // 3 + 3
                    )
                    responses.append(message)
                    
        except Exception as e:
            self.logger.error(f"Error generating consensus round: {e}")
        
        return responses
    
    def _build_conversation_context(self, messages: List[Dict[str, Any]]) -> str:
        """Build conversation context for Gemini prompts."""
        context_lines = []
        for msg in messages[-8:]:  # Last 8 messages
            speaker = msg.get('speaker', 'Unknown')
            content = msg.get('message', '')
            context_lines.append(f"{speaker}: {content[:200]}...")  # Truncate for context
        return "\n".join(context_lines)
    
    def _get_agent_expertise(self, agent: str) -> str:
        """Get agent expertise description."""
        expertise = {
            "TechnicalAnalyst": "Chart patterns, price action, volume analysis, momentum indicators, support/resistance levels",
            "FundamentalAnalyst": "Financial statements, valuation metrics, company fundamentals, earnings analysis, sector comparison",
            "SentimentAnalyst": "Market sentiment, news analysis, social media sentiment, market psychology, retail vs institutional sentiment"
        }
        return expertise.get(agent, "Financial analysis")
    
    def _get_agent_role(self, agent: str) -> str:
        """Get agent role title."""
        roles = {
            "TechnicalAnalyst": "Technical Analysis Expert",
            "FundamentalAnalyst": "Fundamental Analysis Expert",
            "SentimentAnalyst": "Sentiment Analysis Expert"
        }
        return roles.get(agent, "Financial Expert")
    
    def _create_agent_message(self, name: str, role: str, content: str, round_num: int) -> Dict[str, Any]:
        """Create a standardized agent message."""
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
        technical_signal = individual_analyses.get('technical', {}).get('signal', 'neutral')
        fundamental_bias = individual_analyses.get('fundamental', {}).get('bias', 'hold')
        sentiment = individual_analyses.get('sentiment', {}).get('sentiment', 'neutral')
        
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
        tech_confidence = individual_analyses.get('technical', {}).get('confidence', 0.5)
        fund_confidence = individual_analyses.get('fundamental', {}).get('confidence', 0.5)
        sent_confidence = individual_analyses.get('sentiment', {}).get('confidence', 0.5)
        
        total_confidence = tech_confidence + fund_confidence + sent_confidence
        if total_confidence > 0:
            weighted_score = (
                tech_score * tech_confidence + 
                fund_score * fund_confidence + 
                sent_score * sent_confidence
            ) / total_confidence
        else:
            weighted_score = 0
        
        # Determine final action
        if weighted_score > 0.3:
            action = "BUY"
        elif weighted_score < -0.3:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Calculate overall confidence
        overall_confidence = total_confidence / 3 if total_confidence > 0 else 0.5
        
        # Generate rationale using Gemini if available
        rationale = f"Consensus recommendation based on weighted analysis: Technical ({technical_signal}), Fundamental ({fundamental_bias}), Sentiment ({sentiment})"
        
        if self.gemini_model:
            try:
                rationale_prompt = f"""
                Provide a comprehensive investment rationale for the {action} recommendation on {stock_symbol}.
                
                Analysis Summary:
                - Technical: {technical_signal} (confidence: {tech_confidence:.1%})
                - Fundamental: {fundamental_bias} (confidence: {fund_confidence:.1%})  
                - Sentiment: {sentiment} (confidence: {sent_confidence:.1%})
                
                Write a clear, professional rationale for Vietnamese investors.
                """
                
                response = self.gemini_model.generate_content(rationale_prompt)
                if response.text:
                    rationale = response.text
                    
            except Exception as e:
                self.logger.error(f"Error generating rationale: {e}")
        
        # Calculate target price
        tech_target = individual_analyses.get('technical', {}).get('target_price', 0)
        fund_target = individual_analyses.get('fundamental', {}).get('fair_value', 0)
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
    
    def _assess_overall_risk(self, individual_analyses: Dict[str, Any]) -> str:
        """Assess overall investment risk."""
        risks = []
        
        # Technical risks
        tech_confidence = individual_analyses.get('technical', {}).get('confidence', 0.5)
        if tech_confidence < 0.6:
            risks.append("Technical uncertainty")
        
        # Fundamental risks
        fund_risks = individual_analyses.get('fundamental', {}).get('risk_factors', [])
        risks.extend(fund_risks[:2])  # Top 2 risks
        
        # Sentiment risks
        sent_confidence = individual_analyses.get('sentiment', {}).get('confidence', 0.5)
        if sent_confidence < 0.6:
            risks.append("Mixed sentiment")
        
        if len(risks) > 3:
            return "HIGH"
        elif len(risks) > 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_key_factors(self, individual_analyses: Dict[str, Any]) -> List[str]:
        """Extract key decision factors."""
        factors = []
        
        # Technical factors
        tech_indicators = individual_analyses.get('technical', {}).get('key_indicators', {})
        if tech_indicators.get('trend') == 'upward':
            factors.append("Positive price trend")
        
        # Fundamental factors
        valuation = individual_analyses.get('fundamental', {}).get('valuation', '')
        if valuation:
            factors.append(f"Stock appears {valuation}")
        
        # Sentiment factors
        sent_impact = individual_analyses.get('sentiment', {}).get('news_impact', '')
        if sent_impact in ['high', 'medium']:
            factors.append(f"News sentiment has {sent_impact} impact")
        
        return factors[:5]  # Top 5 factors
    
    def _update_progress(self, message: str):
        """Update progress via callback."""
        if self.update_callback:
            self.update_callback(message)
        self.logger.info(message)