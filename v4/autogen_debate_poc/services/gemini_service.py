"""
Gemini LLM Service Wrapper
Handles API calls, retries, structured output, and streaming.
"""
import logging
import json
import time
import os
from typing import Optional, Dict, Any, List
from enum import Enum

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError
import backoff

logger = logging.getLogger(__name__)


class ModelVersion(Enum):
    """Available Gemini models."""
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"


class GeminiService:
    """
    Wrapper for Google Gemini API with retry logic and structured output.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: ModelVersion = ModelVersion.GEMINI_2_0_FLASH,
        temperature: float = 0.7,
        max_retries: int = 3,
    ):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google API key. If None, reads from GEMINI_API_KEY env var.
            model: Gemini model version to use.
            temperature: LLM temperature (0.0-1.0). Higher = more creative.
            max_retries: Max retry attempts on API failures.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not provided and not found in environment"
            )
        
        genai.configure(api_key=self.api_key)
        self.model_name = model.value
        self.temperature = temperature
        self.max_retries = max_retries
        
        logger.info(f"Initialized GeminiService with model {self.model_name}")

    @backoff.on_exception(
        backoff.expo,
        (GoogleAPICallError, Exception),
        max_tries=3,
        max_time=60,
    )
    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate a response from Gemini.
        
        Args:
            prompt: User message.
            system_instruction: System prompt/instruction.
            json_mode: If True, request JSON-formatted output.
            
        Returns:
            Generated text response.
        """
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    top_p=0.9,
                    top_k=40,
                ),
            )
            
            # Add JSON mode hint if requested
            user_prompt = prompt
            if json_mode:
                user_prompt += "\n\nRespond ONLY with valid JSON, no markdown, no explanation."
            
            response = model.generate_content(user_prompt)
            
            if not response.text:
                logger.warning("Gemini returned empty response")
                return ""
            
            return response.text
        
        except GoogleAPICallError as e:
            logger.error(f"Gemini API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            raise

    def generate_json_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        expected_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a JSON-formatted response from Gemini.
        
        Args:
            prompt: User message.
            system_instruction: System prompt.
            expected_schema: Expected JSON schema (for validation).
            
        Returns:
            Parsed JSON response as dictionary.
        """
        raw_response = self.generate_response(
            prompt,
            system_instruction=system_instruction,
            json_mode=True,
        )
        
        try:
            # Try to extract JSON if it's wrapped in markdown code blocks
            if "```json" in raw_response:
                json_str = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                json_str = raw_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = raw_response
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini: {e}\nRaw: {raw_response}")
            return {"error": "Invalid JSON response", "raw": raw_response}

    def stream_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ):
        """
        Stream a response from Gemini (yields text chunks).
        
        Args:
            prompt: User message.
            system_instruction: System prompt.
            
        Yields:
            Text chunks from the response.
        """
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                ),
            )
            
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise

    def batch_generate(
        self,
        prompts: List[str],
        system_instruction: Optional[str] = None,
    ) -> List[str]:
        """
        Generate responses for multiple prompts (sequential).
        
        Args:
            prompts: List of prompts.
            system_instruction: System prompt (shared).
            
        Returns:
            List of generated responses.
        """
        responses = []
        for prompt in prompts:
            response = self.generate_response(
                prompt,
                system_instruction=system_instruction,
            )
            responses.append(response)
            time.sleep(0.5)  # Rate limiting
        
        return responses


def create_gemini_service(
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash",
) -> GeminiService:
    """
    Factory function to create a GeminiService instance.
    
    Args:
        api_key: Optional API key override.
        model: Model name or version.
        
    Returns:
        Initialized GeminiService.
    """
    try:
        model_enum = ModelVersion[model.upper().replace("-", "_")]
    except KeyError:
        model_enum = ModelVersion.GEMINI_2_0_FLASH
    
    return GeminiService(api_key=api_key, model=model_enum)
