"""
Moderator and Judge agents for streaming debate orchestration
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import google.generativeai as genai

from system_prompts import SystemPrompts


class ModeratorAgent:
    """Moderator agent that controls debate flow and manages turns."""
    
    def __init__(self, gemini_api_key: str, update_callback: Optional[Callable] = None):
        """Initialize moderator with Gemini API."""
        self.logger = logging.getLogger(__name__)
        self.update_callback = update_callback
        
        # Initialize Gemini
        try:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.logger.info("Moderator initialized with Gemini API")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini API: {e}")
            self.gemini_model = None
        
        # Debate state
        self.current_round = 0
        self.turn_order = ['TechnicalAnalyst', 'FundamentalAnalyst', 'SentimentAnalyst']
        self.current_speaker_index = 0
        self.conversation_history = []
        
        # Round structure
        self.round_structure = {
            1: {"name": "Opening Statements", "turns_per_agent": 1},
            2: {"name": "Cross-Examination", "turns_per_agent": 2}, 
            3: {"name": "Rebuttal Round", "turns_per_agent": 1},
            4: {"name": "Final Arguments", "turns_per_agent": 1}
        }
    
    async def start_debate(self, stock_symbol: str, period: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start and moderate the debate."""
        self.stock_symbol = stock_symbol
        self.period = period
        self.stock_data = stock_data
        
        opening_message = await self._generate_opening_statement()
        return opening_message
    
    async def _generate_opening_statement(self) -> Dict[str, Any]:
        """Generate moderator opening statement."""
        
        prompt = f"""
        {SystemPrompts.MODERATOR}
        
        You are starting a debate about {self.stock_symbol} for the {self.period} period.
        
        Generate a compelling opening statement (100-120 words) that:
        1. Welcome everyone to the debate
        2. Briefly introduce the stock and analysis period
        3. Set expectations for the debate format
        4. Call the first analyst to speak
        
        End by addressing @TechnicalAnalyst to begin with their analysis.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text if response.text else f"Welcome to our Vietnamese stock market debate on {self.stock_symbol}! Today we'll analyze this stock over the {self.period} timeframe. @TechnicalAnalyst, please start us off with your technical analysis."
            
        except Exception as e:
            self.logger.error(f"Error generating opening: {e}")
            content = f"Welcome to our debate on {self.stock_symbol} for the {self.period} period. Let's begin! @TechnicalAnalyst, please share your technical analysis."
        
        message = {
            "round": 1,
            "speaker": "DebateModerator",
            "role": "Debate Moderator",
            "message": content,
            "timestamp": datetime.now().isoformat(),
            "next_speaker": "TechnicalAnalyst"
        }
        
        self.conversation_history.append(message)
        return message
    
    async def get_next_instruction(self, last_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate next moderator instruction based on conversation flow."""
        
        # Add last message to history
        self.conversation_history.append(last_message)
        
        # Determine next action
        next_speaker = self._determine_next_speaker()
        
        if not next_speaker:
            return None  # Debate finished
        
        # Generate contextual moderator response
        moderator_response = await self._generate_contextual_response(next_speaker)
        return moderator_response
    
    def _determine_next_speaker(self) -> Optional[str]:
        """Determine who should speak next based on debate flow."""
        
        # Count messages per round per agent
        current_round = self._get_current_round()
        agents_in_round = self._count_agent_messages_in_round(current_round)
        
        # Check if current round is complete
        max_turns = self.round_structure.get(current_round, {}).get('turns_per_agent', 1)
        
        # Find next agent who hasn't reached max turns
        for agent in self.turn_order:
            if agents_in_round.get(agent, 0) < max_turns:
                return agent
        
        # Round complete, move to next round
        if current_round < 4:
            self.current_round = current_round + 1
            return self.turn_order[0]  # Start next round with technical analyst
        
        return None  # Debate finished
    
    def _get_current_round(self) -> int:
        """Determine current round based on conversation history."""
        if not self.conversation_history:
            return 1
            
        # Count non-moderator messages to determine round
        analyst_messages = [msg for msg in self.conversation_history 
                          if 'Analyst' in msg.get('speaker', '')]
        
        total_turns = len(analyst_messages)
        
        if total_turns <= 3:  # Opening statements (1 per agent)
            return 1
        elif total_turns <= 9:  # Cross-examination (2 per agent)
            return 2
        elif total_turns <= 12:  # Rebuttal (1 per agent)
            return 3
        else:
            return 4  # Final arguments
    
    def _count_agent_messages_in_round(self, round_num: int) -> Dict[str, int]:
        """Count messages per agent in specific round."""
        
        # Determine message range for round
        if round_num == 1:
            start_idx, end_idx = 0, 3
        elif round_num == 2:
            start_idx, end_idx = 3, 9
        elif round_num == 3:
            start_idx, end_idx = 9, 12
        else:  # round 4
            start_idx, end_idx = 12, 15
        
        # Count messages per agent in range
        analyst_messages = [msg for msg in self.conversation_history 
                          if 'Analyst' in msg.get('speaker', '')]
        
        round_messages = analyst_messages[start_idx:end_idx]
        
        counts = {}
        for msg in round_messages:
            speaker = msg.get('speaker', '')
            counts[speaker] = counts.get(speaker, 0) + 1
        
        return counts
    
    async def _generate_contextual_response(self, next_speaker: str) -> Dict[str, Any]:
        """Generate contextual moderator response to guide next speaker."""
        
        current_round = self._get_current_round()
        round_name = self.round_structure.get(current_round, {}).get('name', f'Round {current_round}')
        
        # Build conversation context
        recent_context = self._build_conversation_context()
        
        prompt = f"""
        {SystemPrompts.MODERATOR}
        
        Current Debate Context:
        Stock: {self.stock_symbol}
        Period: {self.period}
        Round: {current_round} - {round_name}
        Next Speaker: {next_speaker}
        
        Recent conversation:
        {recent_context}
        
        Generate a natural moderator transition (60-80 words) that:
        1. Briefly acknowledges the previous speaker's point
        2. Asks {next_speaker} a specific, engaging question
        3. References something specific from the conversation
        4. Maintains debate momentum
        
        Address {next_speaker} directly with @ symbol.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text if response.text else f"Thank you for that insight! @{next_speaker}, what's your perspective on this analysis?"
            
        except Exception as e:
            self.logger.error(f"Error generating moderator response: {e}")
            content = f"Interesting points! @{next_speaker}, please share your analysis."
        
        message = {
            "round": current_round,
            "speaker": "DebateModerator",
            "role": "Debate Moderator", 
            "message": content,
            "timestamp": datetime.now().isoformat(),
            "next_speaker": next_speaker
        }
        
        self.conversation_history.append(message)
        return message
    
    def _build_conversation_context(self) -> str:
        """Build recent conversation context for prompts."""
        recent_messages = self.conversation_history[-4:] if len(self.conversation_history) > 4 else self.conversation_history
        
        context_lines = []
        for msg in recent_messages:
            speaker = msg.get('speaker', 'Unknown')
            content = msg.get('message', '')[:150]
            context_lines.append(f"{speaker}: {content}...")
        
        return "\n".join(context_lines)
    
    def is_debate_finished(self) -> bool:
        """Check if debate is finished."""
        return self._get_current_round() > 4


class JudgeAgent:
    """Base judge agent for evaluating debate performance."""
    
    def __init__(self, judge_id: str, gemini_api_key: str, focus_area: str):
        """Initialize judge agent."""
        self.judge_id = judge_id
        self.focus_area = focus_area
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini
        try:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini for {judge_id}: {e}")
            self.gemini_model = None
        
        # Evaluation history
        self.round_evaluations = {}
        self.agent_scores = {'TechnicalAnalyst': [], 'FundamentalAnalyst': [], 'SentimentAnalyst': []}
    
    async def evaluate_round(self, round_num: int, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate agents' performance in a specific round."""
        
        # Get messages from this round
        round_messages = self._extract_round_messages(round_num, conversation_history)
        
        # Generate evaluation
        evaluation = await self._generate_round_evaluation(round_num, round_messages)
        
        # Store evaluation
        self.round_evaluations[round_num] = evaluation
        
        return evaluation
    
    async def final_evaluation(self, full_conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide final evaluation and vote for best debater."""
        
        prompt = f"""
        {SystemPrompts.get_agent_prompt(self.judge_id)}
        
        FINAL EVALUATION TASK:
        
        Full debate transcript:
        {self._build_full_context(full_conversation)}
        
        Provide your final evaluation:
        1. Rate each analyst 1-10 on your focus criteria
        2. Provide brief rationale for each score
        3. Vote for the BEST OVERALL DEBATER
        4. Explain your final decision
        
        Keep response concise (150-200 words).
        
        Format:
        TechnicalAnalyst: X/10 - [brief rationale]
        FundamentalAnalyst: X/10 - [brief rationale] 
        SentimentAnalyst: X/10 - [brief rationale]
        
        WINNER: [Agent] - [reasoning]
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text if response.text else "All analysts performed well. TechnicalAnalyst wins for clear analysis."
            
            # Parse scores and winner
            final_scores = self._parse_final_scores(content)
            
        except Exception as e:
            self.logger.error(f"Error in final evaluation: {e}")
            content = "Evaluation complete."
            final_scores = {'TechnicalAnalyst': 7, 'FundamentalAnalyst': 7, 'SentimentAnalyst': 7}
        
        return {
            "judge": self.judge_id,
            "focus_area": self.focus_area,
            "final_scores": final_scores,
            "evaluation_text": content,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_round_messages(self, round_num: int, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract messages from specific round."""
        return [msg for msg in conversation_history if msg.get('round') == round_num and 'Analyst' in msg.get('speaker', '')]
    
    async def _generate_round_evaluation(self, round_num: int, round_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate evaluation for a specific round."""
        
        context = "\n".join([f"{msg.get('speaker')}: {msg.get('message', '')[:200]}..." for msg in round_messages])
        
        prompt = f"""
        {SystemPrompts.get_agent_prompt(self.judge_id)}
        
        ROUND {round_num} EVALUATION:
        
        Round messages:
        {context}
        
        Evaluate each analyst's performance this round (1-10 scale):
        - Focus on your specialty area: {self.focus_area}
        - Provide brief feedback for each
        - Keep evaluation objective and constructive
        
        Max 100 words total.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content = response.text if response.text else f"Round {round_num} evaluation complete."
            
        except Exception as e:
            self.logger.error(f"Error evaluating round {round_num}: {e}")
            content = f"Round {round_num} completed successfully."
        
        return {
            "round": round_num,
            "judge": self.judge_id,
            "evaluation": content,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_full_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build full conversation context."""
        analyst_messages = [msg for msg in conversation_history if 'Analyst' in msg.get('speaker', '')]
        
        context_lines = []
        for msg in analyst_messages:
            speaker = msg.get('speaker', 'Unknown')
            content = msg.get('message', '')
            round_num = msg.get('round', 0)
            context_lines.append(f"Round {round_num} - {speaker}: {content[:200]}...")
        
        return "\n".join(context_lines)
    
    def _parse_final_scores(self, evaluation_text: str) -> Dict[str, int]:
        """Parse final scores from evaluation text."""
        scores = {}
        
        # Simple parsing - look for patterns like "TechnicalAnalyst: 8/10"
        import re
        pattern = r'(TechnicalAnalyst|FundamentalAnalyst|SentimentAnalyst):\s*(\d+)/10'
        matches = re.findall(pattern, evaluation_text)
        
        for agent, score in matches:
            scores[agent] = int(score)
        
        # Default scores if parsing fails
        for agent in ['TechnicalAnalyst', 'FundamentalAnalyst', 'SentimentAnalyst']:
            if agent not in scores:
                scores[agent] = 7
        
        return scores


class JudgePanel:
    """Panel of three judges to evaluate the debate."""
    
    def __init__(self, gemini_api_key: str):
        """Initialize judge panel."""
        self.judges = [
            JudgeAgent('judge1', gemini_api_key, 'Portfolio Construction & Risk Management'),
            JudgeAgent('judge2', gemini_api_key, 'Analytical Methodology & Data Usage'),
            JudgeAgent('judge3', gemini_api_key, 'Market Context & Communication Quality')
        ]
        self.final_results = {}
    
    async def evaluate_round(self, round_num: int, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Have all judges evaluate a round."""
        evaluations = []
        
        for judge in self.judges:
            evaluation = await judge.evaluate_round(round_num, conversation_history)
            evaluations.append(evaluation)
        
        return evaluations
    
    async def final_judging(self, full_conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Conduct final judging and determine winner."""
        
        final_evaluations = []
        total_scores = {'TechnicalAnalyst': 0, 'FundamentalAnalyst': 0, 'SentimentAnalyst': 0}
        
        # Get final evaluations from all judges
        for judge in self.judges:
            evaluation = await judge.final_evaluation(full_conversation)
            final_evaluations.append(evaluation)
            
            # Add to total scores
            for agent, score in evaluation['final_scores'].items():
                total_scores[agent] += score
        
        # Determine winner
        winner = max(total_scores, key=total_scores.get)
        
        # Calculate average scores
        avg_scores = {agent: score/3 for agent, score in total_scores.items()}
        
        self.final_results = {
            "winner": winner,
            "total_scores": total_scores,
            "average_scores": avg_scores,
            "judge_evaluations": final_evaluations,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.final_results