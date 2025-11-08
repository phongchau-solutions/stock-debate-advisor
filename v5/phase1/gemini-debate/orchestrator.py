"""
Debate orchestrator for coordinating the multi-agent debate.
"""
from typing import Dict, Any, List
import google.generativeai as genai
from agents import FundamentalAgent, TechnicalAgent, SentimentAgent, ModeratorAgent, JudgeAgent
from data_loader import DataLoader
from config import config


class DebateOrchestrator:
    """Orchestrates the multi-agent stock debate."""
    
    def __init__(self):
        """Initialize the debate orchestrator."""
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
        """Get list of available stock symbols."""
        return self.loader.get_available_symbols()
        
    def run_debate(self, symbol: str, rounds: int = 10) -> Dict[str, Any]:
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
        
        print(f"\n🔍 Starting multi-round debate for {symbol}...")
        
        # Multi-round debate
        for round_num in range(1, rounds + 1):
            print(f"\n📊 Round {round_num}...")
            
            # Build debate context
            debate_context = ""
            if round_num > 1:
                recent_statements = [entry for entry in debate_history[-6:]]
                if recent_statements:
                    debate_context = "RECENT DEBATE CONTEXT:\n"
                    for entry in recent_statements:
                        debate_context += f"- {entry['agent']}: {entry['statement']}\n"
                    debate_context += "\nBuild on these points with NEW insights. Do not repeat.\n"
            
            # Each agent speaks in turn
            print("  💼 Fundamental analyst...")
            fund_analysis = self.fundamental_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': fund_analysis.get('agent', 'Fundamental Analyst'),
                'statement': fund_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': fund_analysis.get('agent', 'Fundamental Analyst'),
                'statement': fund_analysis.get('analysis', ''),
                'round': round_num
            })
            
            print("  📈 Technical analyst...")
            tech_analysis = self.technical_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': tech_analysis.get('agent', 'Technical Analyst'),
                'statement': tech_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': tech_analysis.get('agent', 'Technical Analyst'),
                'statement': tech_analysis.get('analysis', ''),
                'round': round_num
            })
            
            print("  📰 Sentiment analyst...")
            sent_analysis = self.sentiment_agent.analyze(symbol, debate_context=debate_context)
            transcript.append({
                'agent': sent_analysis.get('agent', 'Sentiment Analyst'),
                'statement': sent_analysis.get('analysis', ''),
                'round': round_num
            })
            debate_history.append({
                'agent': sent_analysis.get('agent', 'Sentiment Analyst'),
                'statement': sent_analysis.get('analysis', ''),
                'round': round_num
            })
        
        # Moderator synthesis
        print("\n⚖️  Moderator synthesizing...")
        analyses = [fund_analysis, tech_analysis, sent_analysis]
        full_debate = "\n".join([f"{e['agent']}: {e['statement'][:100]}..." for e in debate_history[-9:]])
        moderator_debate_context = f"DEBATE HISTORY:\n{full_debate}\n\nProvide comprehensive synthesis."
        moderator_summary = self.moderator_agent.synthesize(analyses, debate_context=moderator_debate_context)
        transcript.append({
            'agent': 'Moderator',
            'statement': moderator_summary,
            'round': rounds + 1
        })
        
        # Judge makes final decision
        print("\n⚖️  Judge making final decision...")
        judge_context = f"FULL DEBATE:\n{full_debate}\n\nMake final verdict based on quality."
        final_decision = self.judge_agent.make_decision(analyses, moderator_summary, debate_context=judge_context)
        transcript.append({
            'agent': 'Judge',
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
    
    def run_debate_streaming(self, symbol: str, rounds: int = 10):
        """
        Run debate with real-time streaming of each agent's response.
        Yields each message as it's generated.
        
        Args:
            symbol: Stock symbol to analyze
            rounds: Minimum number of debate rounds (default 10)
            
        Yields:
            Dict with agent, statement, round, target (if critique) for each message
        """
        print(f"\n🔍 Starting multi-agent debate for {symbol}...")
        
        # RESET AGENT MEMORIES for new debate
        self.fundamental_agent.reset_memory()
        self.technical_agent.reset_memory()
        self.sentiment_agent.reset_memory()
        self.moderator_agent.reset_memory()
        self.judge_agent.reset_memory()
        
        agents = [
            ('Fundamental Analyst', self.fundamental_agent),
            ('Technical Analyst', self.technical_agent),
            ('Sentiment Analyst', self.sentiment_agent)
        ]
        
        round_num = 1
        continue_debate = True
        speech_count = {name: 0 for name, _ in agents}  # Track speaking opportunities
        all_analyses = []
        debate_history = []  # Track all statements for context
        
        while continue_debate:
            print(f"\n🔄 Round {round_num}...")
            round_transcript = []
            
            # MODERATOR OPENS THE ROUND
            print(f"  ⚖️ Moderator opening round {round_num}...")
            if round_num == 1:
                moderator_opening = self.moderator_agent.generate_response(
                    f"Open the debate for stock {symbol}. Welcome analysts and ask each to present their initial position in 1-2 sentences."
                )
            else:
                # Provide recent debate context to moderator
                recent_context = "\n".join([f"- {entry['agent']}: {entry['statement'][:100]}..." 
                                           for entry in debate_history[-6:]])  # Last 6 statements
                moderator_opening = self.moderator_agent.generate_response(
                    f"""Round {round_num} for {symbol}.

Recent debate:
{recent_context}

Open this round: Direct agents to address previous points, challenge weak arguments, and introduce NEW insights (no repetition). Keep it to 1-2 sentences."""
                )
            
            yield {
                'agent': 'Moderator',
                'statement': moderator_opening,
                'round': round_num,
                'target': ''
            }
            debate_history.append({'agent': 'Moderator', 'statement': moderator_opening, 'round': round_num})
            
            # Each agent speaks in turn
            for agent_name, agent in agents:
                print(f"  📊 {agent_name}...")
                
                # Build debate context from recent history (last 4-6 statements excluding moderator)
                debate_context = ""
                if round_num > 1:
                    recent_statements = [entry for entry in debate_history[-6:] 
                                       if entry['agent'] != 'Moderator' and entry['agent'] != 'Judge']
                    if recent_statements:
                        debate_context = "RECENT DEBATE CONTEXT:\n"
                        for entry in recent_statements:
                            debate_context += f"- {entry['agent']}: {entry['statement']}\n"
                        debate_context += "\nBuild on these points with NEW insights. Do not repeat.\n"
                
                analysis = agent.analyze(symbol, debate_context=debate_context)
                statement = analysis.get('analysis', '')
                all_analyses.append(analysis)
                
                # Detect if this is a critique (only after round 1)
                target_agent = ""
                if round_num > 1:
                    previous_agents = [name for name, _ in agents if name != agent_name]
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
                if target_agent:
                    print(f"  🎯 {target_agent} responds to critique...")
                    
                    # Find the criticized agent
                    for resp_name, resp_agent in agents:
                        if resp_name == target_agent:
                            # Build context for response
                            response_context = f"CRITIQUE DIRECTED AT YOU:\n{agent_name} stated: {statement}\n\nRespond to this critique with NEW counterarguments or clarifications."
                            response_analysis = resp_agent.analyze(symbol, debate_context=response_context)
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
                        f"- {name}: {stmt[:150]}..."
                        for name, stmt, _ in round_transcript
                    ])
                ])
                
                judge_check = self.judge_agent.generate_response(
                    f"""Current round: {round_num}
Minimum rounds completed: {rounds}

Recent debate transcript:
{transcript_summary}

Should the debate CONTINUE or CONCLUDE?
- Respond "CONTINUE: [reason]" if more debate needed
- Respond "CONCLUDE" if ready for final verdict"""
                )
                
                if "CONTINUE" in judge_check.upper():
                    print(f"  → Judge: {judge_check}")
                    round_num += 1
                    continue_debate = True
                else:
                    print("  → Judge: Ready to conclude")
                    continue_debate = False
            else:
                round_num += 1
        
        # Get final analyses from each agent (with full debate context)
        final_debate_context = "FULL DEBATE SUMMARY:\n" + "\n".join([
            f"Round {e['round']} - {e['agent']}: {e['statement'][:100]}..." 
            for e in debate_history[-12:]  # Last 12 entries for context
        ])
        
        final_analyses = [
            self.fundamental_agent.analyze(symbol, debate_context=final_debate_context),
            self.technical_agent.analyze(symbol, debate_context=final_debate_context),
            self.sentiment_agent.analyze(symbol, debate_context=final_debate_context)
        ]
        
        # Moderator final synthesis
        print("\n⚖️  Moderator final synthesis...")
        full_debate = "\n\n".join([f"Round {e['round']} - {e['agent']}: {e['statement']}" 
                                   for e in debate_history])
        moderator_debate_context = f"COMPLETE DEBATE TRANSCRIPT:\n{full_debate[:3000]}\n\nProvide comprehensive synthesis."
        moderator_summary = self.moderator_agent.synthesize(final_analyses, debate_context=moderator_debate_context)
        yield {
            'agent': 'Moderator',
            'statement': moderator_summary,
            'round': round_num,
            'target': ''
        }
        
        # Judge makes final decision
        print("\n👨‍⚖️  Judge making final verdict...")
        judge_debate_context = f"ENTIRE DEBATE HISTORY:\n{full_debate[:4000]}\n\nMake your final verdict based on the full debate quality and evidence."
        final_decision = self.judge_agent.make_decision(final_analyses, moderator_summary, debate_context=judge_debate_context)
        yield {
            'agent': 'Judge',
            'statement': final_decision.get('decision', ''),
            'round': round_num + 1,
            'target': ''
        }
    
    def run_full_debate(self, symbol: str, timeframe: str = "1M", min_rounds: int = 10) -> dict:
        """
        Run full debate for compatibility with app.py.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe for analysis
            min_rounds: Minimum number of debate rounds (default 10)
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
