"""
Base agent class for the financial debate system.
"""
import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import google.generativeai as genai
from gemini_client import GeminiConversableAgent


class BaseFinancialAgent(GeminiConversableAgent, ABC):
    """Base class for financial analysis agents."""
    
    def __init__(
        self,
        name: str,
        role: str,
        system_message: str,
        gemini_api_key: str,
        model_name: str = "gemini-1.5-flash",
        **kwargs
    ):
        """Initialize the financial agent."""
        self.role = role
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel(model_name)
        
        # Initialize with GeminiConversableAgent
        super().__init__(
            name=name,
            role=role,
            system_message=system_message,
            gemini_api_key=gemini_api_key,
            model_name=model_name,
            **kwargs
        )
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(name)
    
    @abstractmethod
    async def analyze_data(self, stock_symbol: str, period: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data specific to this agent's role."""
        pass
    
    def generate_llm_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate response using Gemini."""
        try:
            full_prompt = f"{self.system_message}\n\n{prompt}"
            if context:
                full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
    def format_message(self, content: str, signal_data: Optional[Dict] = None) -> str:
        """Format message for debate."""
        formatted = f"**{self.name} ({self.role})**:\n\n{content}"
        
        if signal_data:
            formatted += f"\n\n**Analysis Summary:**\n"
            formatted += f"```json\n{json.dumps(signal_data, indent=2)}\n```"
            
        return formatted