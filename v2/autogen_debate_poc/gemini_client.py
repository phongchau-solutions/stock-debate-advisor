"""
Custom Gemini LLM Client for Autogen Integration
"""
import json
import logging
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai

try:
    from autogen import ConversableAgent
except ImportError:
    # For newer autogen versions
    from autogen_agentchat.agents import AssistantAgent as ConversableAgent


class GeminiLLMClient:
    """Custom LLM client for Google Gemini integration with Autogen."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize Gemini client."""
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def create_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Create completion using Gemini API."""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Format response in OpenAI-compatible format
            return {
                "choices": [{
                    "message": {
                        "content": response.text,
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.text.split()) if response.text else 0,
                    "total_tokens": len(prompt.split()) + (len(response.text.split()) if response.text else 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in Gemini completion: {e}")
            # Return fallback response
            return {
                "choices": [{
                    "message": {
                        "content": f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)[:100]}",
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini prompt."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System Instructions: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)


class GeminiConversableAgent(ConversableAgent):
    """Custom ConversableAgent that uses Gemini instead of OpenAI."""
    
    def __init__(
        self,
        name: str,
        role: str,
        system_message: str,
        gemini_api_key: str,
        model_name: str = "gemini-1.5-flash",
        **kwargs
    ):
        """Initialize agent with Gemini client."""
        self.role = role
        self.gemini_client = GeminiLLMClient(gemini_api_key, model_name)
        
        # Create a dummy config since we'll override the client
        llm_config = {
            "config_list": [{
                "model": model_name,
                "api_key": "dummy",  # We'll override this
                "api_type": "gemini"
            }],
            "timeout": 120,
        }
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            **kwargs
        )
        
        # Override the LLM client with our Gemini client
        self._client = self.gemini_client
        
        # Set up logging
        self.logger = logging.getLogger(name)
    
    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["ConversableAgent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """Generate reply using Gemini."""
        try:
            if messages is None:
                messages = self._oai_messages[sender] if sender else []
            
            # Add system message if not present
            if messages and messages[0].get("role") != "system":
                messages = [{"role": "system", "content": self.system_message}] + messages
            elif not messages:
                messages = [{"role": "system", "content": self.system_message}]
            
            # Use Gemini client for completion
            response = self.gemini_client.create_completion(messages)
            
            if response and response.get("choices"):
                reply = response["choices"][0]["message"]["content"]
                self.logger.info(f"Generated reply: {reply[:100]}...")
                return reply
            else:
                return "I apologize, but I couldn't generate a response at this time."
                
        except Exception as e:
            self.logger.error(f"Error generating reply: {e}")
            return f"Error generating response: {str(e)}"
    
    async def a_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["ConversableAgent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """Async version of generate_reply."""
        # For now, just call the sync version
        # In a production system, you'd want to use aiohttp for async HTTP calls
        return self.generate_reply(messages, sender, **kwargs)