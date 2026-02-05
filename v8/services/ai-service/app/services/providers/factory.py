"""AI provider factory."""

from app.config import get_settings
from app.schemas.ai import AIProvider
from app.services.providers.base import AIProviderBase
from app.services.providers.claude import ClaudeProvider
from app.services.providers.gemini import GeminiProvider
from app.services.providers.openai import OpenAIProvider

settings = get_settings()


def get_ai_provider(provider: AIProvider = None) -> AIProviderBase:
    """
    Get AI provider instance.

    Args:
        provider: Provider to use (defaults to configured default)

    Returns:
        AI provider instance
    """
    if provider is None:
        provider = AIProvider(settings.default_ai_provider)

    if provider == AIProvider.GEMINI:
        return GeminiProvider(settings.google_api_key, settings.gemini_model)
    elif provider == AIProvider.OPENAI:
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    elif provider == AIProvider.CLAUDE:
        return ClaudeProvider(settings.anthropic_api_key, settings.claude_model)
    else:
        raise ValueError(f"Unknown provider: {provider}")
