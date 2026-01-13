"""
Debate Orchestrator for coordinating the multi-agent debate using CrewAI.

This module implements the debate flow control:
- Agent coordination and turn management
- Round-based debate structure
- Real-time output streaming
- Dynamic debate extension based on consensus

Design Principles:
- CrewAI for agent orchestration
- Single Responsibility: Handles debate coordination
- Open/Closed: Extensible debate strategies
"""
from typing import Dict, Any, List, Tuple
import google.generativeai as genai
from crewai import Crew
from agents import DebateAgents, AnalysisTasks
from data_loader import DataLoader, NumberFormatter
from config import config
from constants import (
    AgentRole, InvestmentAction, DebateDecision,
    DebateConstants, PromptConstants, SuccessMessages, ErrorMessages
)


class DebateOrchestrator:
    """
    Orchestrates multi-agent stock debate using CrewAI.
    
    Responsibilities:
    - Manage debate rounds and structure
    - Track debate history and context
    - Stream real-time debate output
    - Determine when debate should conclude
    """
    
    def __init__(self):
        """Initialize the debate orchestrator and agents."""
        # Configure Gemini API
        config.validate()
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Initialize factories
        self.agent_factory = DebateAgents()
        self.task_factory = AnalysisTasks()
        self.loader = DataLoader()
        self.formatter = NumberFormatter()
        
        # Debate state
        self.debate_transcript: List[Dict[str, str]] = []
        self.current_symbol: str = ""
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available stock symbols.
        
        Returns:
            List of stock symbols with available data
        """
        return self.loader.get_available_symbols()
    
    def prepare_data(self, symbol: str) -> Dict[str, str]:
        """
        Prepare and format all data for debate.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary with formatted financial, technical, and sentiment data
        """
        # Load all data
        financial_data = self.loader.load_financial_data(symbol)
        technical_data = self.loader.load_technical_data(symbol)
        news_data = self.loader.load_news_data(symbol)
        
        # Format for presentation
        financial_str = self._format_financial_data(financial_data)
        technical_str = self._format_technical_data(technical_data)
        news_str = self._format_news_data(news_data)
        
        return {
            'financial': financial_str,
            'technical': technical_str,
            'news': news_str
        }
    
    def _format_financial_data(self, data: Dict) -> str:
        """Format financial data for presentation."""
        if not data:
            return "No financial data available"
        
        lines = ["**FINANCIAL METRICS:**"]
        for key, value in list(data.items())[:10]:  # Limit to 10 metrics
            if not key.endswith('_raw'):
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_technical_data(self, data: Dict) -> str:
        """Format technical data for presentation."""
        if not data or 'summary' not in data:
            return "No technical data available"
        
        stats = data['summary'].get('price_stats', {})
        lines = ["**TECHNICAL DATA (Latest 30 Days):**"]
        lines.append(f"- Latest Close: {stats.get('latest_close', 'N/A'):,.0f} VND")
        lines.append(f"- 30-Day High: {stats.get('high', 'N/A'):,.0f} VND")
        lines.append(f"- 30-Day Low: {stats.get('low', 'N/A'):,.0f} VND")
        lines.append(f"- Recent Volume: {stats.get('volume', 'N/A'):,.0f}")
        return "\n".join(lines)
    
    def _format_news_data(self, data: Dict) -> str:
        """Format news data for presentation."""
        if not data or not data.get('articles'):
            return "No recent news available"
        
        lines = ["**RECENT NEWS & SENTIMENT:**"]
        for i, article in enumerate(data['articles'][:5], 1):
            title = article.get('title', 'Untitled')
            date = article.get('date', 'Unknown date')
            lines.append(f"{i}. [{date}] {title}")
        return "\n".join(lines)
    
    def run_debate(
        self, 
        symbol: str, 
        rounds: int = DebateConstants.DEFAULT_ROUNDS
    ) -> Dict[str, Any]:
        """
        Run a multi-round debate on the given stock symbol using CrewAI.
        
        Args:
            symbol: Stock symbol to debate
            rounds: Minimum number of debate rounds
            
        Returns:
            Dict containing debate results and final decision
        """
        self.current_symbol = symbol
        self.debate_transcript = []
        
        print(f"\n{SuccessMessages.DEBATE_STARTED.format(symbol=symbol)}")
        print(f"{'='*60}")
        
        # Prepare data
        data = self.prepare_data(symbol)
        
        # Create agents
        print("\n📋 Creating debate agents...")
        fundamental_agent = self.agent_factory.create_fundamental_agent()
        technical_agent = self.agent_factory.create_technical_agent()
        sentiment_agent = self.agent_factory.create_sentiment_agent()
        moderator_agent = self.agent_factory.create_moderator_agent()
        judge_agent = self.agent_factory.create_judge_agent()
        
        # Run debate rounds
        debate_notes = ""
        
        for round_num in range(1, min(rounds + 1, DebateConstants.MAX_ROUNDS + 1)):
            print(f"\n{SuccessMessages.ROUND_STARTED.format(round=round_num)}")
            print("-" * 60)
            
            # Create tasks for this round
            fund_task = self.task_factory.create_fundamental_analysis_task(
                fundamental_agent, symbol, data['financial'], round_num
            )
            tech_task = self.task_factory.create_technical_analysis_task(
                technical_agent, symbol, data['technical'], round_num
            )
            sent_task = self.task_factory.create_sentiment_analysis_task(
                sentiment_agent, symbol, data['news'], round_num
            )
            
            # Create crew for this round's analysis
            analysis_crew = Crew(
                agents=[fundamental_agent, technical_agent, sentiment_agent],
                tasks=[fund_task, tech_task, sent_task],
                verbose=config.VERBOSE,
                memory=config.CREW_MEMORY
            )
            
            # Execute analysis
            print(f"🔄 Executing analysis round {round_num}...")
            analysis_result = analysis_crew.kickoff()
            
            # Record outputs
            self.debate_transcript.append({
                'round': round_num,
                'analysis': str(analysis_result)
            })
            
            print(f"✅ Round {round_num} Analysis Complete")
            
            # Run moderation after first round
            if round_num == 1:
                mod_task = self.task_factory.create_moderation_task(
                    moderator_agent, symbol, str(analysis_result)
                )
                
                mod_crew = Crew(
                    agents=[moderator_agent],
                    tasks=[mod_task],
                    verbose=config.VERBOSE,
                    memory=config.CREW_MEMORY
                )
                
                print(f"\n🎭 Moderator synthesizing debate...")
                moderation_result = mod_crew.kickoff()
                debate_notes = str(moderation_result)
                print(f"✅ Moderation Complete")
        
        # Final judgment
        print(f"\n{'='*60}")
        print(f"⚖️  Judge making final decision...")
        
        # Prepare debate summary
        debate_summary = self._build_debate_summary(data, debate_notes)
        
        # Create final task
        judge_task = self.task_factory.create_final_judgment_task(
            judge_agent, symbol, debate_summary
        )
        
        judge_crew = Crew(
            agents=[judge_agent],
            tasks=[judge_task],
            verbose=config.VERBOSE,
            memory=config.CREW_MEMORY
        )
        
        final_result = judge_crew.kickoff()
        
        print(f"✅ Final Judgment Complete")
        print(f"{'='*60}\n")
        
        # Parse final result
        final_verdict = self._parse_verdict(str(final_result))
        
        return {
            'symbol': symbol,
            'verdict': final_verdict,
            'debate_transcript': self.debate_transcript,
            'debate_notes': debate_notes,
            'final_result': str(final_result)
        }
    
    def _build_debate_summary(self, data: Dict, moderation: str) -> str:
        """Build a comprehensive debate summary."""
        summary = f"""
## Debate Summary for {self.current_symbol}

### Data Context
{data['financial']}

{data['technical']}

{data['news']}

### Moderation Summary
{moderation}

### Analysis Transcript
{chr(10).join([t['analysis'] for t in self.debate_transcript[-2:]])}
"""
        return summary
    
    def _parse_verdict(self, judgment: str) -> Dict[str, Any]:
        """Parse the judge's verdict from their output."""
        lines = judgment.split('\n')
        
        verdict = {
            'recommendation': 'HOLD',  # Default
            'confidence': 'Medium',
            'rationale': [],
            'raw_output': judgment
        }
        
        # Extract recommendation
        for line in lines:
            if 'BUY' in line and 'RECOMMENDATION' in line:
                verdict['recommendation'] = 'BUY'
                break
            elif 'SELL' in line and 'RECOMMENDATION' in line:
                verdict['recommendation'] = 'SELL'
                break
        
        # Extract confidence
        for line in lines:
            if 'Confidence' in line:
                if 'High' in line:
                    verdict['confidence'] = 'High'
                elif 'Low' in line:
                    verdict['confidence'] = 'Low'
                break
        
        # Extract rationale
        in_rationale = False
        for line in lines:
            if 'Rationale' in line:
                in_rationale = True
                continue
            if in_rationale and line.strip().startswith('-'):
                verdict['rationale'].append(line.strip()[1:].strip())
        
        return verdict
    
    def stream_debate(
        self,
        symbol: str,
        rounds: int = DebateConstants.DEFAULT_ROUNDS,
        callback=None
    ):
        """
        Run debate with streaming callback for UI updates.
        
        Args:
            symbol: Stock symbol
            rounds: Number of rounds
            callback: Function to call with updates
            
        Yields:
            Debate output chunks
        """
        result = self.run_debate(symbol, rounds)
        
        if callback:
            callback(f"Debate Complete for {symbol}", "final")
        
        yield result
