"""
Microsoft Autogen orchestrated debate system for Vietnamese stock analysis.
This module uses Autogen's conversational AI framework to orchestrate debates
between Technical, Fundamental, and Sentiment agents for stock recommendations.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the new Autogen API components
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.components.models import OpenAIChatCompletionClient
from autogen_core.components.models import ChatCompletionModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.analyzer_agent import AnalyzerAgent
from agents.crawler_agent import CrawlerAgent
from integrations.zstock_adapter import ZStockAdapter

logger = logging.getLogger(__name__)


class AutogenStockDebate:
    """Microsoft Autogen orchestrated stock analysis debate system."""
    
    def __init__(self, log_dir: str = "debate_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize data sources
        self.crawler = CrawlerAgent()
        self.analyzer = AnalyzerAgent()
        
        # Autogen configuration
        self.config_list = [
            {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY", "sk-fake-key-for-local-testing"),
                "base_url": "https://api.openai.com/v1",
                "api_type": "openai"
            }
        ]
        
        # Use local LLM config if OpenAI key not available
        if not os.getenv("OPENAI_API_KEY"):
            self.config_list = [
                {
                    "model": "microsoft/DialoGPT-medium",
                    "api_key": "fake-key",
                    "base_url": "http://localhost:8000/v1",  # Local LLM server
                    "api_type": "openai"
                }
            ]
            
    def _setup_debate_agents(self, stock_symbol: str, stock_data: Dict[str, Any]) -> tuple[ConversableAgent, ConversableAgent, ConversableAgent, ConversableAgent]:
        """Setup Autogen conversable agents for the debate."""
        
        # Extract key financial data for context
        latest_price = stock_data.get("prices", {}).get("individual_histories", {}).get(stock_symbol, {}).get("latest_close", "N/A")
        fundamentals = stock_data.get("fundamentals", {}).get(stock_symbol, {})
        latest_ratios = fundamentals.get("latest_ratios", {})
        
        # Common context for all agents
        stock_context = f"""
STOCK ANALYSIS CONTEXT FOR {stock_symbol}:
- Current Price: {latest_price:,} VND
- P/E Ratio: {latest_ratios.get('pe', 'N/A')}
- ROE: {latest_ratios.get('roe', 'N/A'):.1%} if available
- Revenue: {latest_ratios.get('revenue', 'N/A'):,} VND if available
- Net Profit: {latest_ratios.get('net_profit', 'N/A'):,} VND if available

MARKET CONTEXT:
- VN-Index: {stock_data.get('market_context', {}).get('indices', {}).get('VNINDEX', {}).get('latest_close', 'N/A')}
- VN30: {stock_data.get('market_context', {}).get('indices', {}).get('VN30', {}).get('latest_close', 'N/A')}

NEWS & SENTIMENT:
{stock_data.get('news_analysis', {}).get('message', 'No recent news analysis available')}

Your task is to analyze this stock for a 30-day investment recommendation: BUY, HOLD, or SELL.
"""

        # Technical Analysis Agent
        technical_agent = ConversableAgent(
            name="TechnicalAnalyst",
            system_message=f"""You are a Vietnamese stock market Technical Analysis expert.
{stock_context}

Focus on TECHNICAL INDICATORS and PRICE ACTION analysis:
- Chart patterns and price movements
- Support and resistance levels  
- Volume analysis and momentum indicators
- Moving averages and trend analysis
- RSI, MACD, and other technical indicators
- Historical price patterns for {stock_symbol}

Provide specific technical reasoning for your BUY/HOLD/SELL recommendation.
Be concise but analytical. Challenge other agents' viewpoints with technical evidence.
""",
            llm_config={"config_list": self.config_list, "temperature": 0.7},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        # Fundamental Analysis Agent  
        fundamental_agent = ConversableAgent(
            name="FundamentalAnalyst",
            system_message=f"""You are a Vietnamese stock market Fundamental Analysis expert.
{stock_context}

Focus on COMPANY FUNDAMENTALS and BUSINESS ANALYSIS:
- Financial ratios and profitability metrics
- Revenue growth and profit margins
- Business model and competitive position
- Industry trends in Vietnam market
- Balance sheet strength and debt levels
- Management quality and corporate governance
- Valuation relative to peers and historical metrics

Provide specific fundamental reasoning for your BUY/HOLD/SELL recommendation.
Be analytical and challenge technical/sentiment viewpoints with fundamental facts.
""",
            llm_config={"config_list": self.config_list, "temperature": 0.7},
            human_input_mode="NEVER", 
            max_consecutive_auto_reply=3,
        )

        # Sentiment Analysis Agent
        sentiment_agent = ConversableAgent(
            name="SentimentAnalyst", 
            system_message=f"""You are a Vietnamese stock market Sentiment Analysis expert.
{stock_context}

Focus on MARKET SENTIMENT and BEHAVIORAL FACTORS:
- News sentiment and media coverage
- Investor sentiment and market psychology
- Social media trends and retail investor behavior
- Institutional investor positioning
- Market timing and sentiment cycles
- Vietnamese market-specific sentiment factors
- Economic and political sentiment impacts

Provide specific sentiment-based reasoning for your BUY/HOLD/SELL recommendation.
Challenge technical and fundamental analyses with sentiment and behavioral insights.
""",
            llm_config={"config_list": self.config_list, "temperature": 0.7},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        # Moderator Agent
        moderator = ConversableAgent(
            name="DebateModerator",
            system_message=f"""You are the Debate Moderator for {stock_symbol} stock analysis.

Your role:
1. Facilitate structured debate between Technical, Fundamental, and Sentiment analysts
2. Ensure each agent provides specific evidence for their recommendations
3. Challenge weak arguments and ask for clarification
4. Keep the debate focused on the 30-day investment decision
5. After minimum 5 rounds, synthesize the final recommendation

Ground rules:
- Each agent must provide specific BUY/HOLD/SELL recommendation with confidence level
- Challenge agents to defend their positions with concrete evidence
- Encourage disagreement and robust debate
- Focus on actionable insights for {stock_symbol}

At the end, provide a FINAL SYNTHESIS with the consensus recommendation.
""",
            llm_config={"config_list": self.config_list, "temperature": 0.5},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
        )

        return technical_agent, fundamental_agent, sentiment_agent, moderator

    def _create_debate_log_file(self, stock_symbol: str) -> Path:
        """Create a log file for the debate conversation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"debate_{stock_symbol}_{timestamp}.txt"
        log_path = self.log_dir / log_filename
        
        # Write header to log file
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"AUTOGEN STOCK DEBATE LOG\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Stock Symbol: {stock_symbol}\n")
            f.write(f"Debate Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Topic: Should I BUY/HOLD/SELL {stock_symbol} in the next 30 days?\n")
            f.write(f"=" * 50 + "\n\n")
            
        return log_path

    def conduct_stock_debate(
        self, 
        stock_symbol: str,
        max_rounds: int = 8,
        min_rounds: int = 5
    ) -> Dict[str, Any]:
        """Conduct an Autogen-orchestrated debate on a Vietnamese stock."""
        
        logger.info(f"Starting Autogen debate for {stock_symbol}")
        
        # Step 1: Gather stock data
        logger.info("Gathering stock data...")
        crawl_inputs = {
            "tickers": [stock_symbol],
            "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"), 
            "period": "quarterly",
            "include_market": True,
            "include_news": True,
        }
        
        stock_data = self.crawler.process(crawl_inputs, session_id=f"debate-{stock_symbol}")
        
        # Step 2: Create log file
        log_path = self._create_debate_log_file(stock_symbol)
        logger.info(f"Debate log will be saved to: {log_path}")
        
        # Step 3: Setup Autogen agents
        technical_agent, fundamental_agent, sentiment_agent, moderator = self._setup_debate_agents(
            stock_symbol, stock_data.payload
        )
        
        # Step 4: Create GroupChat for structured debate
        agents_list = [moderator, technical_agent, fundamental_agent, sentiment_agent]
        
        group_chat = GroupChat(
            agents=agents_list,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="round_robin",  # Ensures fair participation
            allow_repeat_speaker=True
        )
        
        # Step 5: Create GroupChat Manager
        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": self.config_list, "temperature": 0.6}
        )
        
        # Step 6: Start the debate
        initial_message = f"""
Let's begin the stock analysis debate for {stock_symbol} (Vietnamese stock market).

DEBATE TOPIC: Should investors BUY, HOLD, or SELL {stock_symbol} over the next 30 days?

Current market context has been provided to all agents. Each analyst should:
1. State their recommendation (BUY/HOLD/SELL) with confidence level
2. Provide 3-5 key supporting arguments
3. Challenge other analysts' viewpoints with evidence
4. Defend their position when challenged

We need at least {min_rounds} rounds of discussion before reaching consensus.

Technical Analyst, please start with your analysis and recommendation.
"""

        # Initiate the group chat
        try:
            chat_result = moderator.initiate_chat(
                manager,
                message=initial_message,
                max_turns=max_rounds
            )
            
            # Step 7: Log the conversation
            self._save_debate_to_log(log_path, group_chat.messages, stock_data.payload)
            
            # Step 8: Extract final recommendations
            final_recommendations = self._extract_recommendations(group_chat.messages)
            
            return {
                "stock_symbol": stock_symbol,
                "debate_result": chat_result,
                "log_file": str(log_path),
                "recommendations": final_recommendations,
                "total_messages": len(group_chat.messages),
                "stock_data_summary": {
                    "current_price": stock_data.payload.get("prices", {}).get("individual_histories", {}).get(stock_symbol, {}).get("latest_close"),
                    "pe_ratio": stock_data.payload.get("fundamentals", {}).get(stock_symbol, {}).get("latest_ratios", {}).get("pe"),
                    "roe": stock_data.payload.get("fundamentals", {}).get(stock_symbol, {}).get("latest_ratios", {}).get("roe")
                }
            }
            
        except Exception as e:
            logger.error(f"Error during debate: {e}")
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\nERROR: Debate failed with error: {e}\n")
            raise

    def _save_debate_to_log(self, log_path: Path, messages: List[Dict], stock_data: Dict[str, Any]):
        """Save the complete debate conversation to log file."""
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write("STOCK DATA SUMMARY:\n")
            f.write("-" * 30 + "\n")
            
            # Write stock data summary
            for symbol, data in stock_data.get("fundamentals", {}).items():
                ratios = data.get("latest_ratios", {})
                f.write(f"{symbol}: Price={stock_data.get('prices', {}).get('individual_histories', {}).get(symbol, {}).get('latest_close', 'N/A')}, ")
                f.write(f"P/E={ratios.get('pe', 'N/A')}, ROE={ratios.get('roe', 'N/A')}\n")
            
            f.write("\nDEBATE CONVERSATION:\n")
            f.write("-" * 30 + "\n\n")
            
            # Write all messages
            for i, message in enumerate(messages, 1):
                speaker = message.get("name", "Unknown")
                content = message.get("content", "")
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                f.write(f"[{i:02d}] {timestamp} - {speaker}:\n")
                f.write(f"{content}\n")
                f.write("-" * 80 + "\n\n")
            
            f.write("DEBATE COMPLETED\n")
            f.write("=" * 50 + "\n")

    def _extract_recommendations(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract final recommendations from the debate messages."""
        recommendations = {
            "technical": {"recommendation": "UNKNOWN", "confidence": 0.0, "reasoning": ""},
            "fundamental": {"recommendation": "UNKNOWN", "confidence": 0.0, "reasoning": ""},
            "sentiment": {"recommendation": "UNKNOWN", "confidence": 0.0, "reasoning": ""},
            "consensus": {"recommendation": "UNKNOWN", "confidence": 0.0, "reasoning": ""}
        }
        
        # Simple extraction based on agent names and common recommendation patterns
        for message in messages:
            speaker = message.get("name", "").lower()
            content = message.get("content", "").upper()
            
            # Look for explicit recommendations
            if "BUY" in content or "SELL" in content or "HOLD" in content:
                rec = "BUY" if "BUY" in content else ("SELL" if "SELL" in content else "HOLD")
                
                if "technical" in speaker:
                    recommendations["technical"]["recommendation"] = rec
                elif "fundamental" in speaker:
                    recommendations["fundamental"]["recommendation"] = rec
                elif "sentiment" in speaker:
                    recommendations["sentiment"]["recommendation"] = rec
                elif "moderator" in speaker and "FINAL" in content:
                    recommendations["consensus"]["recommendation"] = rec
        
        return recommendations


def main():
    """Main function to run the Autogen stock debate."""
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    debate_system = AutogenStockDebate()
    
    # Conduct debate for VNM (Vinamilk)
    try:
        result = debate_system.conduct_stock_debate(
            stock_symbol="VNM",
            max_rounds=10, 
            min_rounds=5
        )
        
        print(f"\n{'='*60}")
        print(f"DEBATE COMPLETED FOR {result['stock_symbol']}")
        print(f"{'='*60}")
        print(f"Log file: {result['log_file']}")
        print(f"Total messages: {result['total_messages']}")
        print(f"Stock data: {result['stock_data_summary']}")
        print(f"\nRecommendations:")
        for agent, rec in result['recommendations'].items():
            print(f"  {agent.capitalize()}: {rec['recommendation']}")
        
    except Exception as e:
        logger.error(f"Debate failed: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()