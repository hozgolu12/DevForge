# ==============================================================================
# DEVFORGE GROQ PROVIDER STRATEGY
# ==============================================================================
# Invokes Groq Chat Completions API directly using httpx.
# Avoids importing the groq SDK to minimize container size.
# ==============================================================================

import os
import httpx
from engine.ai.models import PluginSpecification
from engine.ai.provider import AIProvider, extract_json
from engine.config.ai_config import AIConfig


class GroqProvider(AIProvider):
    """Groq API Strategy implementation using direct REST requests."""

    def generate_plugin(self, prompt: str) -> PluginSpecification:
        # Load API key from config or environment
        api_key = None
        if "groq" in self.config.providers:
            api_key = self.config.providers["groq"].api_key
        api_key = api_key or os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "Groq API Key not found. Please set GROQ_API_KEY environment variable "
                "or define it in devforge-ai.yaml"
            )

        base_url = None
        if "groq" in self.config.providers:
            base_url = self.config.providers["groq"].base_url
        base_url = base_url or "https://api.groq.com/openai/v1"

        url = f"{base_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Setup standard chat completion payload (OpenAI-compatible)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional DevForge plugin builder. Return ONLY JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        # Request structured JSON format from Groq if enabled
        if self.config.structured_output:
            payload["response_format"] = {"type": "json_object"}

        try:
            with httpx.Client(timeout=self.config.request_timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to Groq API service: {e}")

        result = response.json()
        
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError(f"Groq API returned unexpected response format: {result}")

        if not content:
            raise ValueError("Groq API returned an empty response.")

        parsed_data = extract_json(content)
        return PluginSpecification(**parsed_data)
