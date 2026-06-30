# ==============================================================================
# DEVFORGE OLLAMA PROVIDER STRATEGY
# ==============================================================================
# Invokes local Ollama API to generate plugin specifications.
# ==============================================================================

import httpx
from engine.ai.models import PluginSpecification
from engine.ai.provider import AIProvider, extract_json
from engine.config.ai_config import AIConfig


class OllamaProvider(AIProvider):
    """Offline Ollama API Strategy implementation."""

    def generate_plugin(self, prompt: str) -> PluginSpecification:
        # Resolve base URL from configuration or default
        base_url = None
        if "ollama" in self.config.providers:
            base_url = self.config.providers["ollama"].base_url
        base_url = base_url or "http://ollama:11434"

        url = f"{base_url.rstrip('/')}/api/generate"

        # Prepare generate request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        # Request structured JSON format from Ollama if supported and enabled
        if self.config.structured_output:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.config.request_timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to Ollama service at {url}: {e}")

        result = response.json()
        content = result.get("response", "")
        if not content:
            raise ValueError("Ollama returned an empty response.")

        parsed_data = extract_json(content)
        return PluginSpecification(**parsed_data)
