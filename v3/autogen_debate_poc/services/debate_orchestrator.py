"""
Debate Orchestrator - Coordinates multi-agent debate using Moderator.
Manages debate flow, round progression, and transcript logging.
"""
import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from pathlib import Path

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.moderator_agent import ModeratorAgent
from services.stock_data_service import StockDataService
from services.prompt_service import PromptService
from services.data_cache_service import DataCacheService

logger = logging.getLogger(__name__)


class DebateOrchestrator:
    """
    Orchestrates multi-agent financial debate with dynamic moderation.
    
    Flow:
    1. Fetch data from Vietcap API
    2. Initialize agents with data and prompts
    3. Run N rounds of debate with moderator controlling speaking order
    4. Synthesize final consensus recommendation
    5. Save transcript to logs
    """
    
    def __init__(
        self,
        rounds: int = 5,
        llm_config: Optional[Dict[str, Any]] = None,
        log_dir: str = "logs",
        use_cache: bool = True,
        cache_max_age_hours: int = 24
    ):
        self.rounds = rounds
        self.llm_config = llm_config or self._get_default_llm_config()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.prompt_service = PromptService()
        self.transcript: List[Dict[str, Any]] = []
        
        # Initialize cache service
        self.cache_service = DataCacheService() if use_cache else None
        self.cache_max_age_hours = cache_max_age_hours
        
    def _get_default_llm_config(self) -> Dict[str, Any]:
        """Get default LLM config (fallback when Gemini not configured)."""
        return {
            "config_list": [{
                "model": "gemini-1.5-flash",
                "api_type": "gemini",
                "api_key": "placeholder"
            }],
            "timeout": 120
        }
    
    async def run_debate(
        self,
        stock_symbol: str,
        period_days: int = 30,
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Run complete debate for given stock symbol.
        
        Args:
            stock_symbol: Stock to analyze (e.g., 'VNM')
            period_days: Historical period for analysis
            on_message: Callback for streaming messages to UI
            
        Returns:
            Dict with transcript and final consensus
        """
        logger.info(f"Starting debate for {stock_symbol}, {self.rounds} rounds")
        
        # Create debate session in database
        session_id = None
        if self.cache_service:
            session_id = self.cache_service.create_debate_session(
                symbol=stock_symbol,
                period_days=period_days,
                rounds=self.rounds,
                data_source="multi"  # vietcap/yfinance/synthetic
            )
            logger.info(f"Created debate session: {session_id}")
        
        # Step 1: Fetch data from Vietcap
        stock_data = await self._fetch_stock_data(stock_symbol, period_days)
        
        # Step 2: Initialize agents
        agents = await self._initialize_agents(stock_data)
        moderator = self._initialize_moderator()
        
        # Step 3: Run debate rounds (with early termination on strong consensus)
        all_analyses = []
        actual_rounds = 0
        
        for round_num in range(1, self.rounds + 1):
            logger.info(f"Starting round {round_num}")
            actual_rounds = round_num
            
            # Moderator determines speaking order
            round_analyses = []
            for agent_name, agent in agents.items():
                # Agent performs analysis
                try:
                    analysis = agent.analyze(stock_symbol, period_days)
                    all_analyses.append(analysis)
                    round_analyses.append(analysis)
                    
                    # Save agent analysis to database
                    if self.cache_service and session_id:
                        self.cache_service.save_agent_analysis(
                            session_id=session_id,
                            agent_name=agent_name,
                            round_number=round_num,
                            analysis=analysis
                        )
                    
                except Exception as e:
                    logger.error(f"Agent {agent_name} analysis failed: {e}")
                    analysis = {"error": str(e), "agent": agent_name}
                
                # Create debate message
                message = {
                    "round": round_num,
                    "agent": agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "analysis": analysis
                }
                
                self.transcript.append(message)
                moderator.record_message(agent_name, analysis, round_num)
                
                # Stream to UI if callback provided
                if on_message:
                    on_message(message)
                
                # Small delay for streaming effect
                await asyncio.sleep(0.3)
            
            # Check for early consensus after each round (if not the first round)
            if round_num >= 2:
                # Check if all agents agree on signal/bias
                signals = []
                for analysis in round_analyses:
                    signal = analysis.get("signal", analysis.get("bias", analysis.get("sentiment_label", "")))
                    if signal:
                        signals.append(signal.lower())
                
                # If all agents agree on buy/sell with high confidence, can terminate early
                if len(set(signals)) == 1 and signals[0] in ["buy", "sell"]:
                    avg_confidence = sum(a.get("confidence", 0) for a in round_analyses) / len(round_analyses)
                    if avg_confidence > 0.75:
                        logger.info(f"Early termination: Strong consensus reached at round {round_num}")
                        break
        
        # Step 4: Moderator synthesizes consensus
        consensus = moderator.synthesize_consensus(all_analyses)
        
        final_message = {
            "round": self.rounds + 1,
            "agent": "Moderator",
            "timestamp": datetime.now().isoformat(),
            "consensus": consensus
        }
        
        self.transcript.append(final_message)
        if on_message:
            on_message(final_message)
        
        # Complete debate session in database
        if self.cache_service and session_id:
            self.cache_service.complete_debate_session(
                session_id=session_id,
                final_decision=consensus.get('decision', 'hold'),
                final_confidence=consensus.get('confidence', 0),
                transcript=self.transcript
            )
            logger.info(f"Completed debate session: {session_id}")
        
        # Step 5: Save transcript
        self._save_transcript(stock_symbol, consensus)
        
        return {
            "stock_symbol": stock_symbol,
            "transcript": self.transcript,
            "consensus": consensus,
            "total_rounds": actual_rounds,
            "max_rounds": self.rounds
        }
    
    async def _fetch_stock_data(self, symbol: str, period_days: int) -> Dict[str, Any]:
        """Fetch stock data using unified stock data service."""
        logger.info(f"Fetching data for {symbol}")
        
        service = StockDataService()
        data = await service.fetch_stock_data(symbol, period_days)
        
        return data
    
    async def _initialize_agents(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize all analysis agents with data and prompts."""
        agents = {}
        
        # Technical Agent
        tech_prompt = self.prompt_service.load_prompt("technical")
        tech_context = self.prompt_service.prepare_technical_context(stock_data)
        tech_prompt_filled = self.prompt_service.inject_data(tech_prompt, tech_context)
        
        agents["TechnicalAnalyst"] = TechnicalAgent(
            system_prompt=tech_prompt_filled,
            llm_config=self.llm_config,
            stock_data=stock_data
        )
        
        # Fundamental Agent
        fund_prompt = self.prompt_service.load_prompt("fundamental")
        fund_context = self.prompt_service.prepare_fundamental_context(stock_data)
        fund_prompt_filled = self.prompt_service.inject_data(fund_prompt, fund_context)
        
        agents["FundamentalAnalyst"] = FundamentalAgent(
            system_prompt=fund_prompt_filled,
            llm_config=self.llm_config,
            stock_data=stock_data
        )
        
        # Sentiment Agent
        sent_prompt = self.prompt_service.load_prompt("sentiment")
        sent_context = self.prompt_service.prepare_sentiment_context(stock_data)
        sent_prompt_filled = self.prompt_service.inject_data(sent_prompt, sent_context)
        
        agents["SentimentAnalyst"] = SentimentAgent(
            system_prompt=sent_prompt_filled,
            llm_config=self.llm_config,
            stock_data=stock_data
        )
        
        logger.info(f"Initialized {len(agents)} agents")
        return agents
    
    def _initialize_moderator(self) -> ModeratorAgent:
        """Initialize moderator agent."""
        mod_prompt = self.prompt_service.load_prompt("moderator")
        mod_context = {
            "symbol": "TBD",
            "current_round": 1,
            "total_rounds": self.rounds,
            "previous_speakers": "None",
            "debate_history": "Starting new debate"
        }
        mod_prompt_filled = self.prompt_service.inject_data(mod_prompt, mod_context)
        
        return ModeratorAgent(
            system_prompt=mod_prompt_filled,
            llm_config=self.llm_config
        )
    
    def _save_transcript(self, symbol: str, consensus: Dict[str, Any]):
        """Save debate transcript to log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"debate_{symbol}_{timestamp}.txt"
        
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"=== Multi-Agent Debate Transcript ===\n")
                f.write(f"Stock: {symbol}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Rounds: {self.rounds}\n")
                f.write(f"\n{'='*60}\n\n")
                
                for msg in self.transcript:
                    round_num = msg.get("round", 0)
                    agent = msg.get("agent", "Unknown")
                    
                    f.write(f"[Round {round_num}] {agent}\n")
                    f.write(f"{'-'*60}\n")
                    
                    if "analysis" in msg:
                        analysis = msg["analysis"]
                        f.write(f"Type: {analysis.get('analysis_type', 'N/A')}\n")
                        f.write(f"Rationale: {analysis.get('rationale', 'N/A')}\n")
                        if "signal" in analysis:
                            f.write(f"Signal: {analysis['signal']}\n")
                        if "bias" in analysis:
                            f.write(f"Bias: {analysis['bias']}\n")
                        f.write(f"Confidence: {analysis.get('confidence', 0):.2f}\n")
                    elif "consensus" in msg:
                        cons = msg["consensus"]
                        f.write(f"FINAL DECISION: {cons.get('decision', 'N/A')}\n")
                        f.write(f"Confidence: {cons.get('confidence', 0):.0%}\n")
                        f.write(f"Consensus: {cons.get('consensus', 'N/A')}\n")
                        f.write(f"Summary: {cons.get('summary', 'N/A')}\n")
                    
                    f.write(f"\n")
                
            logger.info(f"Transcript saved to {log_file}")
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
