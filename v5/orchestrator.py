"""
Debate orchestrator for coordinating the multi-agent debate.

This module implements the debate flow control:
- Agent coordination and turn management
- Round-based debate structure
- Critique detection and targeting
- Real-time streaming output
- Dynamic debate extension based on consensus

Design Principles:
- Single Responsibility: Handles only debate coordination
- Open/Closed: Extensible debate strategies
- Dependency Inversion: Depends on agent abstractions
"""
from typing import Dict, Any, List
import google.generativeai as genai
from agents import FundamentalAgent, TechnicalAgent, SentimentAgent, ModeratorAgent, JudgeAgent
from data_loader import DataLoader
from config import config
from constants import (
    AgentRole, InvestmentAction, DebateDecision,
    DebateConstants, PromptConstants, SuccessMessages, RegexPatterns
)


class DebateOrchestrator:
    """
    Orchestrates the multi-agent stock debate.
    
    Responsibilities:
    - Manage debate rounds and agent turns
    - Track debate history and context
    - Detect and route critiques between agents
    - Stream real-time debate output
    - Determine when debate should conclude
    """
    
    def __init__(self):
        """Initialize the debate orchestrator and all agents."""
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Initialize agents
        self.fundamental_agent = FundamentalAgent()
        self.technical_agent = TechnicalAgent()
        self.sentiment_agent = SentimentAgent()
        self.moderator_agent = ModeratorAgent()
        self.judge_agent = JudgeAgent()
        
        self.loader = DataLoader()
        self.data_loader = self.loader  # Alias for compatibility
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available stock symbols.
        
        Returns:
            List of stock symbols with available data
        """
        return self.loader.get_available_symbols()
        
    def run_debate(
        self, 
        symbol: str, 
        rounds: int = DebateConstants.DEFAULT_ROUNDS
    ) -> Dict[str, Any]:
        """
        Run a multi-round debate on the given stock symbol.
        
        Args:
            symbol: Stock symbol to debate
            rounds: Minimum number of debate rounds (can extend longer)
            
        Returns:
            Dict containing debate results and final decision
        """
        # RESET AGENT MEMORIES for new debate
        self.fundamental_agent.reset_memory()
        self.technical_agent.reset_memory()
        self.sentiment_agent.reset_memory()
        self.moderator_agent.reset_memory()
        self.judge_agent.reset_memory()
        
        # Get analyses from all agents
        transcript = []
        debate_history = []
        
        print(SuccessMessages.DEBATE_STARTED.format(symbol=symbol))
        
        # Multi-round debate
        for round_num in range(1, rounds + 1):
            print(SuccessMessages.ROUND_STARTED.format(round=round_num))
            
            # Build debate context
            debate_context = ""
            if round_num > 1:
                recent_statements = [
                    entry for entry in 
                    debate_history[-DebateConstants.CONTEXT_WINDOW:]
                ]
                if recent_statements:
                    debate_context = PromptConstants.DEBATE_CONTEXT_HEADER
                    for entry in recent_statements:
                        debate_context += f"- {entry['agent']}: {entry['statement']}\n"
                    debate_context += PromptConstants.BUILD_ON_CONTEXT
            
            # Each agent speaks in turn
            print(f"  {AgentRole.FUNDAMENTAL.value}...")
            fund_analysis = self.fundamental_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': fund_analysis.get('agent', AgentRole.FUNDAMENTAL.value),
                'statement': fund_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': fund_analysis.get('agent', AgentRole.FUNDAMENTAL.value),
                'statement': fund_analysis.get('analysis', ''),
                'round': round_num
            })
            
            print(f"  {AgentRole.TECHNICAL.value}...")
            tech_analysis = self.technical_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': tech_analysis.get('agent', AgentRole.TECHNICAL.value),
                'statement': tech_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': tech_analysis.get('agent', AgentRole.TECHNICAL.value),
                'statement': tech_analysis.get('analysis', ''),
                'round': round_num
            })
            
            print(f"  {AgentRole.SENTIMENT.value}...")
            sent_analysis = self.sentiment_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': sent_analysis.get('agent', AgentRole.SENTIMENT.value),
                'statement': sent_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': sent_analysis.get('agent', AgentRole.SENTIMENT.value),
                'statement': sent_analysis.get('analysis', ''),
                'round': round_num
            })
        
        # Moderator synthesis
        print(f"\n{AgentRole.MODERATOR.value} synthesizing...")
        analyses = [fund_analysis, tech_analysis, sent_analysis]
        full_debate = "\n".join([
            f"{e['agent']}: {e['statement'][:DebateConstants.SUMMARY_LENGTH]}..." 
            for e in debate_history[-DebateConstants.FULL_DEBATE_LENGTH:]
        ])
        moderator_debate_context = f"DEBATE HISTORY:\n{full_debate}\n\nProvide comprehensive synthesis."
        moderator_summary = self.moderator_agent.synthesize(analyses, debate_context=moderator_debate_context)
        transcript.append({
            'agent': AgentRole.MODERATOR.value,
            'statement': moderator_summary,
            'round': rounds + 1
        })
        
        # Judge makes final decision
        print(f"\n{AgentRole.JUDGE.value} making final decision...")
        judge_context = f"FULL DEBATE:\n{full_debate}\n\nMake final verdict based on quality."
        final_decision = self.judge_agent.make_decision(
            analyses, 
            moderator_summary, 
            debate_context=judge_context,
            full_data=getattr(self, 'full_data', None),
            cutoff_date=getattr(self, 'historical_data', {}).get('cutoff_date')
        )
        transcript.append({
            'agent': AgentRole.JUDGE.value,
            'statement': final_decision.get('decision', ''),
            'round': rounds + 2
        })
        
        return {
            "symbol": symbol,
            "rounds": rounds,
            "transcript": transcript,
            "analyses": analyses,
            "moderator_summary": moderator_summary,
            "final_decision": final_decision
        }
    
    def _detect_critique(self, statement: str, previous_agents: List[str]) -> str:
        """
        Detect if a statement contains a critique of another agent.
        
        Args:
            statement: The agent's statement
            previous_agents: List of agent names that spoke before this one
            
        Returns:
            Name of criticized agent or empty string if no critique detected
        """
        statement_lower = statement.lower()
        
        # Check for mentions of other agents
        for agent_name in previous_agents:
            agent_lower = agent_name.lower()
            agent_keywords = [
                agent_lower,
                agent_lower.split()[0],  # Just "fundamental", "technical", etc.
            ]
            
            # Critique indicators
            critique_patterns = [
                "disagrees", "contrary to", "however", "but",
                "overlooks", "ignores", "misses", "incorrect",
                "flawed", "wrong", "challenge", "question",
                "contradicts", "opposed to", "different from"
            ]
            
            # Check if agent is mentioned AND critique pattern exists
            agent_mentioned = any(keyword in statement_lower for keyword in agent_keywords)
            has_critique = any(pattern in statement_lower for pattern in critique_patterns)
            
            if agent_mentioned and has_critique:
                return agent_name
        
        return ""
    
    def _is_no_contribution(self, statement: str) -> bool:
        """
        Detect if a statement provides no meaningful contribution.
        
        Args:
            statement: The agent's statement
            
        Returns:
            True if statement is a no-contribution (e.g., "No data available")
        """
        statement_lower = statement.lower().strip()
        
        # Patterns indicating no contribution
        no_contribution_patterns = [
            "no data available",
            "no data",
            "data not available",
            "insufficient data",
            "unable to analyze",
            "cannot analyze",
            "lack of data",
            "missing data",
            "not enough data",
            "data unavailable",
            "no information available",
            "no news available",
            "no sentiment data",
            "no articles found"
        ]
        
        # Check if statement is very short (likely just saying "no data")
        if len(statement_lower) < 30:
            return any(pattern in statement_lower for pattern in no_contribution_patterns)
        
        # For longer statements, check if they're mostly about lack of data
        pattern_matches = sum(1 for pattern in no_contribution_patterns if pattern in statement_lower)
        
        # If statement mentions "no data" patterns and is relatively short, it's a no-contribution
        if pattern_matches > 0 and len(statement_lower) < 150:
            return True
            
        return False
    
    def run_debate_streaming(
        self, 
        symbol: str, 
        rounds: int = DebateConstants.DEFAULT_ROUNDS,
        should_force_conclude: callable = None,
        cutoff_date: Any = None,
        timeframe: str = "3 months"
    ):
        """
        Run debate with real-time streaming of each agent's response.
        Yields each message as it's generated.
        
        Args:
            symbol: Stock symbol to analyze
            rounds: Minimum number of debate rounds
            should_force_conclude: Optional callback function that returns True to force immediate conclusion
            cutoff_date: Optional date cutoff - agents only see data before this date, judge sees all data
            timeframe: Analysis timeframe (e.g., "1 month", "3 months", "6 months", "1 year")
            
        Yields:
            Dict with agent, statement, round, target (if critique) for each message
        """
        print(SuccessMessages.DEBATE_STARTED.format(symbol=symbol))
        
        # Load data with appropriate filtering
        # Analysts get filtered data (historical only), Judge gets full data
        financial_data = self.loader.load_financial_data(symbol)  # Financial data typically doesn't have dates
        technical_data_historical = self.loader.load_technical_data(symbol, cutoff_date=cutoff_date)
        sentiment_data_historical = self.loader.load_sentiment_data(symbol, cutoff_date=cutoff_date)
        
        # Judge gets unfiltered data for verification
        technical_data_full = self.loader.load_technical_data(symbol, cutoff_date=None)
        sentiment_data_full = self.loader.load_sentiment_data(symbol, cutoff_date=None)
        
        # Store data for agents to access
        self.historical_data = {
            'financial': financial_data,
            'technical': technical_data_historical,
            'sentiment': sentiment_data_historical,
            'cutoff_date': cutoff_date
        }
        
        self.full_data = {
            'financial': financial_data,
            'technical': technical_data_full,
            'sentiment': sentiment_data_full
        }
        
        # RESET AGENT MEMORIES for new debate
        self.fundamental_agent.reset_memory()
        self.technical_agent.reset_memory()
        self.sentiment_agent.reset_memory()
        self.moderator_agent.reset_memory()
        self.judge_agent.reset_memory()
        
        agents = [
            (AgentRole.FUNDAMENTAL.value, self.fundamental_agent),
            (AgentRole.TECHNICAL.value, self.technical_agent),
            (AgentRole.SENTIMENT.value, self.sentiment_agent)
        ]
        
        round_num = 1
        continue_debate = True
        speech_count = {name: 0 for name, _ in agents}  # Track speaking opportunities
        all_analyses = []
        debate_history = []  # Track all statements for context
        
        # Track agent elimination: agent_name -> consecutive no-contribution count
        no_contribution_count = {name: 0 for name, _ in agents}
        eliminated_agents = set()  # Agents that have been eliminated
        ELIMINATION_THRESHOLD = 3  # Eliminate after 3 consecutive no-contributions
        
        while continue_debate:
            print(SuccessMessages.ROUND_STARTED.format(round=round_num))
            round_transcript = []
            
            # MODERATOR OPENS THE ROUND
            print(f"  {AgentRole.MODERATOR.value} opening round {round_num}...")
            
            # Build context about eliminated agents
            elimination_context = ""
            if eliminated_agents:
                active_agents = [name for name, _ in agents if name not in eliminated_agents]
                elimination_context = f"\n\nELIMINATED AGENTS: {', '.join(eliminated_agents)}\nACTIVE AGENTS: {', '.join(active_agents)}"
            
            if round_num == 1:
                moderator_opening = self.moderator_agent.generate_response(
                    f"Open the debate for stock {symbol} with analysis timeframe of {timeframe}. Welcome analysts and ask each to present their initial position in 1-2 sentences. Remind them that all analysis must be relevant for the {timeframe} timeframe."
                )
            else:
                # Provide recent debate context to moderator
                recent_context = "\n".join([
                    f"- {entry['agent']}: {entry['statement'][:DebateConstants.SUMMARY_LENGTH]}..." 
                    for entry in debate_history[-DebateConstants.CONTEXT_WINDOW:]
                ])
                moderator_opening = self.moderator_agent.generate_response(
                    f"""Round {round_num} for {symbol} (timeframe: {timeframe}).

Recent debate:
{recent_context}{elimination_context}

Open this round: Direct agents to address previous points, challenge weak arguments, and introduce NEW insights (no repetition). Remind them their analysis must be valid for the {timeframe} timeframe. Keep it to 1-2 sentences."""
                )
            
            yield {
                'agent': AgentRole.MODERATOR.value,
                'statement': moderator_opening,
                'round': round_num,
                'target': ''
            }
            debate_history.append({
                'agent': AgentRole.MODERATOR.value, 
                'statement': moderator_opening, 
                'round': round_num
            })
            
            # Each agent speaks in turn
            for agent_name, agent in agents:
                # Skip if agent is eliminated
                if agent_name in eliminated_agents:
                    print(f"  ⏭️  {agent_name} (eliminated - no contributions)")
                    continue
                    
                print(f"  📊 {agent_name}...")
                
                # Build debate context from recent history (excluding moderator and judge)
                debate_context = ""
                if round_num > 1:
                    recent_statements = [
                        entry for entry in debate_history[-DebateConstants.CONTEXT_WINDOW:] 
                        if entry['agent'] not in [
                            AgentRole.MODERATOR.value, 
                            AgentRole.JUDGE.value
                        ]
                    ]
                    if recent_statements:
                        debate_context = PromptConstants.DEBATE_CONTEXT_HEADER
                        for entry in recent_statements:
                            debate_context += f"- {entry['agent']}: {entry['statement']}\n"
                        debate_context += PromptConstants.BUILD_ON_CONTEXT
                
                analysis = agent.analyze(symbol, debate_context=debate_context, data=self.historical_data, cutoff_date=cutoff_date, timeframe=timeframe)
                statement = analysis.get('analysis', '')
                all_analyses.append(analysis)
                
                # Check if agent provided meaningful contribution
                is_no_contribution = self._is_no_contribution(statement)
                
                if is_no_contribution:
                    no_contribution_count[agent_name] += 1
                    print(f"    ⚠️  {agent_name} no contribution count: {no_contribution_count[agent_name]}/{ELIMINATION_THRESHOLD}")
                    
                    # Eliminate agent if threshold reached
                    if no_contribution_count[agent_name] >= ELIMINATION_THRESHOLD:
                        eliminated_agents.add(agent_name)
                        elimination_notice = f"🚫 {agent_name} has been eliminated from the debate after {ELIMINATION_THRESHOLD} rounds of no meaningful contribution."
                        print(f"    {elimination_notice}")
                        
                        # Moderator announces elimination
                        yield {
                            'agent': AgentRole.MODERATOR.value,
                            'statement': elimination_notice,
                            'round': round_num,
                            'target': ''
                        }
                        continue  # Skip this agent's turn
                else:
                    # Reset count if agent provides contribution
                    no_contribution_count[agent_name] = 0
                
                # Detect if this is a critique (only after round 1)
                target_agent = ""
                if round_num > 1:
                    previous_agents = [name for name, _ in agents if name != agent_name and name not in eliminated_agents]
                    target_agent = self._detect_critique(statement, previous_agents)
                
                speech_count[agent_name] += 1
                
                yield {
                    'agent': agent_name,
                    'statement': statement,
                    'round': round_num,
                    'target': target_agent
                }
                
                round_transcript.append((agent_name, statement, target_agent))
                debate_history.append({'agent': agent_name, 'statement': statement, 'round': round_num})
                
                # If this was a critique, allow the criticized agent to respond
                if target_agent and target_agent not in eliminated_agents:
                    print(f"  🎯 {target_agent} responds to critique...")
                    
                    # Find the criticized agent
                    for resp_name, resp_agent in agents:
                        if resp_name == target_agent:
                            # Build context for response
                            response_context = f"CRITIQUE DIRECTED AT YOU:\n{agent_name} stated: {statement}\n\nRespond to this critique with NEW counterarguments or clarifications. Remember: your analysis must be valid for the {timeframe} timeframe."
                            response_analysis = resp_agent.analyze(symbol, debate_context=response_context, data=self.historical_data, cutoff_date=cutoff_date, timeframe=timeframe)
                            response_statement = response_analysis.get('analysis', '')
                            all_analyses.append(response_analysis)
                            
                            speech_count[resp_name] += 1
                            
                            yield {
                                'agent': resp_name,
                                'statement': response_statement,
                                'round': round_num,
                                'target': '',
                                'is_response': True
                            }
                            
                            round_transcript.append((resp_name, response_statement, ''))
                            debate_history.append({'agent': resp_name, 'statement': response_statement, 'round': round_num})
                            break
            
            # Check if user forced conclusion
            if should_force_conclude and should_force_conclude():
                print("\n🔔 User requested immediate conclusion. Judge will now deliver verdict...")
                continue_debate = False
                break
            
            # JUDGE COMMENTARY AFTER EACH ROUND
            print(f"  👨‍⚖️ Judge commentary...")
            round_summary = "\n".join([f"- {name}: {stmt[:150]}..." for name, stmt, _ in round_transcript])
            judge_commentary = self.judge_agent.generate_response(
                f"""Provide brief high-level commentary (1-2 sentences) on Round {round_num}:

{round_summary}

Evaluate: Are agents introducing NEW insights? Which arguments are most compelling? Any gaps to address?"""
            )
            
            yield {
                'agent': 'Judge',
                'statement': judge_commentary,
                'round': round_num,
                'target': '',
                'is_commentary': True
            }
            debate_history.append({'agent': 'Judge', 'statement': judge_commentary, 'round': round_num})
            
            # After minimum rounds, check with judge if debate should continue
            if round_num >= rounds:
                print("\n⚖️  Judge evaluating if more debate needed...")
                
                # Prepare transcript summary for judge
                transcript_summary = "\n\n".join([
                    f"Round {round_num}:\n" + "\n".join([
                        f"- {name}: {stmt[:DebateConstants.SUMMARY_LENGTH]}..."
                        for name, stmt, _ in round_transcript
                    ])
                ])
                
                judge_check = self.judge_agent.generate_response(
                    f"""Current round: {round_num}
Minimum rounds completed: {rounds}

Recent debate transcript:
{transcript_summary}

Should the debate {DebateDecision.CONTINUE.value} or {DebateDecision.CONCLUDE.value}?
- Respond "{DebateDecision.CONTINUE.value}: [reason]" if more debate needed
- Respond "{DebateDecision.CONCLUDE.value}" if ready for final verdict"""
                )
                
                if DebateDecision.CONTINUE.value in judge_check.upper():
                    print(f"  → {AgentRole.JUDGE.value}: {judge_check}")
                    round_num += 1
                    continue_debate = True
                else:
                    print(f"  → {AgentRole.JUDGE.value}: Ready to conclude")
                    continue_debate = False
            else:
                round_num += 1
        
        # Get final analyses from each agent (with full debate context)
        # Only include analyses from non-eliminated agents
        final_debate_context = "FULL DEBATE SUMMARY:\n" + "\n".join([
            f"Round {e['round']} - {e['agent']}: {e['statement'][:DebateConstants.SUMMARY_LENGTH]}..." 
            for e in debate_history[-DebateConstants.FULL_DEBATE_LENGTH * 2:]
        ])
        
        final_analyses = []
        
        # Only get final analysis from active (non-eliminated) agents
        if AgentRole.FUNDAMENTAL.value not in eliminated_agents:
            final_analyses.append(self.fundamental_agent.analyze(symbol, debate_context=final_debate_context, data=self.historical_data, cutoff_date=cutoff_date, timeframe=timeframe))
        
        if AgentRole.TECHNICAL.value not in eliminated_agents:
            final_analyses.append(self.technical_agent.analyze(symbol, debate_context=final_debate_context, data=self.historical_data, cutoff_date=cutoff_date, timeframe=timeframe))
        
        if AgentRole.SENTIMENT.value not in eliminated_agents:
            final_analyses.append(self.sentiment_agent.analyze(symbol, debate_context=final_debate_context, data=self.historical_data, cutoff_date=cutoff_date, timeframe=timeframe))
        
        # Add note about eliminated agents for judge context
        elimination_note = ""
        if eliminated_agents:
            elimination_note = f"\n\nNOTE: The following agents were eliminated due to lack of meaningful contribution: {', '.join(eliminated_agents)}"
        
        # Moderator final synthesis
        print(f"\n{AgentRole.MODERATOR.value} final synthesis...")
        full_debate = "\n\n".join([
            f"Round {e['round']} - {e['agent']}: {e['statement']}" 
            for e in debate_history
        ])
        moderator_debate_context = (
            f"COMPLETE DEBATE TRANSCRIPT for {symbol} (timeframe: {timeframe}):\n{full_debate[:PromptConstants.MAX_DATA_LENGTH * 2]}{elimination_note}\n\n"
            "Provide comprehensive synthesis. Remember: all analysis is for the {timeframe} timeframe."
        )
        moderator_summary = self.moderator_agent.synthesize(final_analyses, debate_context=moderator_debate_context)
        yield {
            'agent': AgentRole.MODERATOR.value,
            'statement': moderator_summary,
            'round': round_num,
            'target': ''
        }
        
        # Judge makes final decision
        print(f"\n{AgentRole.JUDGE.value} making final verdict...")
        judge_debate_context = (
            f"ENTIRE DEBATE HISTORY for {symbol} (timeframe: {timeframe}):\n{full_debate[:PromptConstants.MAX_DATA_LENGTH * 3]}{elimination_note}\n\n"
            "Make your final verdict based on the full debate quality and evidence. Remember: all analysis and your decision is specifically for the {timeframe} timeframe."
        )
        final_decision = self.judge_agent.make_decision(
            final_analyses, 
            moderator_summary, 
            debate_context=judge_debate_context,
            full_data=self.full_data,
            cutoff_date=cutoff_date,
            timeframe=timeframe
        )
        yield {
            'agent': AgentRole.JUDGE.value,
            'statement': final_decision.get('decision', ''),
            'round': round_num + 1,
            'target': ''
        }
    
    def run_full_debate(
        self, 
        symbol: str, 
        timeframe: str = "1M", 
        min_rounds: int = DebateConstants.DEFAULT_ROUNDS
    ) -> dict:
        """
        Run full debate for compatibility with app.py.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe for analysis
            min_rounds: Minimum number of debate rounds
            
        Returns:
            Dictionary containing debate transcript and decision
        """
        result = self.run_debate(symbol, rounds=min_rounds)
        
        # Add timeframe to result
        result['timeframe'] = timeframe
        
        return result
    
    def format_debate_output(self, result: Dict[str, Any]) -> str:
        """Format debate results for display."""
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"DEBATE RESULTS: {result['symbol']}")
        output.append(f"{'='*80}\n")
        
        # Individual analyses
        for analysis in result['analyses']:
            agent_name = analysis.get('agent', 'Unknown')
            output.append(f"\n{agent_name}:")
            output.append("-" * 40)
            output.append(analysis.get('analysis', 'No analysis available'))
            if 'error' in analysis:
                output.append(f"⚠️  Error: {analysis['error']}")
            output.append("")
        
        # Moderator summary
        output.append(f"\nModerator Summary:")
        output.append("-" * 40)
        output.append(result['moderator_summary'])
        output.append("")
        
        # Final decision
        output.append(f"\n{'='*80}")
        output.append("FINAL INVESTMENT DECISION")
        output.append(f"{'='*80}")
        output.append(result['final_decision'].get('decision', 'No decision made'))
        output.append(f"{'='*80}\n")
        
        return "\n".join(output)
