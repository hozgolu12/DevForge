# ==============================================================================
# DEVFORGE AI PROVIDER FACTORY
# ==============================================================================
# Resolves and instantiates the chosen AIProvider Strategy.
# ==============================================================================

from typing import Optional
from engine.ai.provider import AIProvider
from engine.ai.groq_provider import GroqProvider
from engine.ai.gemini_provider import GeminiProvider
from engine.ai.openai_provider import OpenAIProvider
from engine.ai.ollama_provider import OllamaProvider
from engine.config.ai_config import AIConfig


class AIFactory:
    """Factory class to construct concrete AIProvider strategies."""

    @staticmethod
    def get_provider(
        config: AIConfig,
        provider_name: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> AIProvider:
        """
        Instantiate the requested AIProvider.
        Falls back to active provider in config if not overridden.
        """
        resolved_name = (provider_name or config.provider).lower().strip()

        if resolved_name == "groq":
            return GroqProvider(config, model_override)
        elif resolved_name == "gemini":
            return GeminiProvider(config, model_override)
        elif resolved_name == "openai":
            return OpenAIProvider(config, model_override)
        elif resolved_name == "ollama":
            return OllamaProvider(config, model_override)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
