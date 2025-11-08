"""
Debate agents for the Gemini Multi-Agent Stock Debate PoC.
Simplified implementation for v5.
"""
from typing import Dict, Any, List
from pathlib import Path
import google.generativeai as genai
from config import config
from data_loader import DataLoader


def load_prompt(agent_name: str) -> str:
    """Load system prompt from prompts directory."""
    prompt_file = Path(__file__).parent / "prompts" / f"{agent_name}.txt"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"You are a {agent_name.replace('_', ' ')}."


class BaseAgent:
    """Base class for all debate agents with conversation memory."""
    
    def __init__(self, name: str, role: str, prompt_file: str = None):
        self.name = name
        self.role = role
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        # Conversation memory - stores all previous statements from this agent
        self.conversation_history: List[str] = []
        
        # Load system prompt
        if prompt_file:
            self.system_prompt = load_prompt(prompt_file)
        else:
            self.system_prompt = f"You are {role}."
    
    def add_to_memory(self, statement: str):
        """Add a statement to this agent's conversation history."""
        self.conversation_history.append(statement)
    
    def get_memory_context(self) -> str:
        """Get formatted memory context for prompt."""
        if not self.conversation_history:
            return "This is your first statement in the debate."
        
        memory_text = "YOUR PREVIOUS STATEMENTS IN THIS DEBATE:\n"
        for i, stmt in enumerate(self.conversation_history, 1):
            memory_text += f"{i}. {stmt}\n"
        memory_text += "\n⚠️ CRITICAL: You MUST NOT repeat any of these points. Introduce NEW analysis, data, or perspectives."
        return memory_text
    
    def reset_memory(self):
        """Reset conversation history (for new debates)."""
        self.conversation_history = []
        
    def generate_response(self, prompt: str, include_memory: bool = True) -> str:
        """Generate response using Gemini with conversation memory."""
        try:
            # Build full prompt with system prompt, memory, and user prompt
            full_prompt = f"{self.system_prompt}\n\n"
            
            if include_memory:
                full_prompt += f"{self.get_memory_context()}\n\n"
            
            full_prompt += prompt
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config.TEMPERATURE,
                    max_output_tokens=config.MAX_TOKENS,
                )
            )
            
            # Store the response in memory
            response_text = response.text
            if include_memory:

                self.add_to_memory(response_text)
            
            return response_text
        except Exception as e:
            return f"Error generating response: {e}"


class FundamentalAgent(BaseAgent):
    """Analyzes fundamental data (financials)."""
    
    def __init__(self, name: str = "Fundamental Analyst"):
        super().__init__(name, "Fundamental Analysis Expert", "fundamental_agent")
        self.loader = DataLoader()
        
    def analyze(self, symbol: str, debate_context: str = "") -> Dict[str, Any]:
        """Analyze fundamental data with debate context."""
        try:
            financial_data = self.loader.load_financial_data(symbol)
            
            prompt = f"""Stock Symbol: {symbol}

Financial Data (latest):
{str(financial_data)[:1500]}

{debate_context}

CRITICAL INSTRUCTIONS:
1. Provide EXACTLY 1-2 sentences with specific numbers
2. End with "BUY/HOLD/SELL because [specific reason]"
3. If responding to criticism, address it directly
4. Use numbers to support your position

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "financial_statements"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": f"Unable to analyze: {e}",
                "error": str(e)
            }


class TechnicalAgent(BaseAgent):
    """Analyzes technical indicators and price data."""
    
    def __init__(self, name: str = "Technical Analyst"):
        super().__init__(name, "Technical Analysis Expert", "technical_agent")
        self.loader = DataLoader()
        
    def analyze(self, symbol: str, debate_context: str = "") -> Dict[str, Any]:
        """Analyze technical data (OHLC) with debate context."""
        try:
            ohlc_data = self.loader.load_technical_data(symbol)
            
            if not ohlc_data:
                return {
                    "agent": self.name,
                    "analysis": "No technical data available",
                    "error": "Data not found"
                }
            
            summary = ohlc_data.get('summary', {})
            latest = summary.get('price_stats', {}).get('latest_close', 0)
            high = summary.get('price_stats', {}).get('high', 0)
            low = summary.get('price_stats', {}).get('low', 0)
            
            prompt = f"""Stock Symbol: {symbol}

Technical Data:
- Latest: {latest:,.0f} VND
- High: {high:,.0f} VND  
- Low: {low:,.0f} VND

{debate_context}

CRITICAL INSTRUCTIONS:
1. Provide EXACTLY 1-2 sentences with specific price levels
2. End with "BUY/HOLD/SELL because [specific technical reason]"
3. If responding to criticism, address it directly
4. Use specific price points and trends

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "ohlc_prices"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": f"Unable to analyze: {e}",
                "error": str(e)
            }


class SentimentAgent(BaseAgent):
    """Analyzes sentiment from news."""
    
    def __init__(self, name: str = "Sentiment Analyst"):
        super().__init__(name, "Sentiment Analysis Expert", "sentiment_agent")
        self.loader = DataLoader()
        
    def analyze(self, symbol: str, debate_context: str = "") -> Dict[str, Any]:
        """Analyze sentiment from news data with debate context."""
        try:
            news_data = self.loader.load_sentiment_data(symbol)
            
            if not news_data:
                return {
                    "agent": self.name,
                    "analysis": "No news data available",
                    "error": "Data not found"
                }
            
            articles = news_data.get('articles', [])
            summary = news_data.get('summary', {})
            
            # Get first article title
            first_title = articles[0].get('title', 'N/A') if articles else 'No news'
            
            prompt = f"""Stock Symbol: {symbol}

News Headlines:
{first_title}

Total articles: {summary.get('total_articles', 0)}

{debate_context}

CRITICAL INSTRUCTIONS:
1. Provide EXACTLY 1-2 sentences analyzing sentiment
2. End with "BUY/HOLD/SELL because [specific sentiment reason]"
3. If responding to criticism, address it directly
4. Use specific headlines or trends as evidence

Your response:"""
            
            response = self.generate_response(prompt)
            
            return {
                "agent": self.name,
                "analysis": response.strip(),
                "data_source": "news_articles"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "analysis": f"Unable to complete analysis: {e}",
                "error": str(e)
            }
class ModeratorAgent(BaseAgent):
    """Moderates the debate and synthesizes arguments."""
    
    def __init__(self, name: str = "Moderator"):
        super().__init__(name, "Debate Moderator", "moderator_agent")
        
    def synthesize(self, analyses: list[Dict[str, Any]], debate_context: str = "") -> str:
        """Synthesize all agent analyses with debate context."""
        prompt = f"""You are a debate moderator. Review these investment analyses and provide:
1. Summary of key points
2. Areas of agreement and disagreement
3. Which arguments are most compelling

Analyses:
{chr(10).join([f"{a.get('agent', 'Unknown')}: {a.get('analysis', 'N/A')}" for a in analyses])}

{debate_context}

Provide a balanced summary highlighting the strongest arguments.
"""
        
        return self.generate_response(prompt)


class JudgeAgent(BaseAgent):
    """Makes final investment decision."""
    
    def __init__(self, name: str = "Judge"):
        super().__init__(name, "Investment Decision Judge", "judge_agent")
        
    def make_decision(self, analyses: list[Dict[str, Any]], moderator_summary: str, debate_context: str = "") -> Dict[str, Any]:
        """Make final investment decision with debate context."""
        prompt = f"""You are an investment judge. Based on all analyses, make a FINAL investment decision:

All Analyses:
{chr(10).join([f"{a.get('agent', 'Unknown')}: {a.get('analysis', 'N/A')[:500]}" for a in analyses])}

Moderator Summary:
{moderator_summary}

{debate_context}

Provide your FINAL decision in this format:
FINAL DECISION: [BUY/HOLD/SELL]
CONFIDENCE: [1-10]
RATIONALE: [2-3 sentences explaining the decision]
KEY FACTORS: [List 3-5 key factors that influenced your decision]
"""
        
        response = self.generate_response(prompt)
        
        return {
            "agent": self.name,
            "decision": response
        }
