# ==============================================================================
# DEVFORGE GEMINI PROVIDER STRATEGY
# ==============================================================================
# Invokes Google Generative AI REST API directly using httpx.
# Avoids importing the heavy google-generativeai SDK to minimize container size.
# ==============================================================================

import os
import httpx
from engine.ai.models import PluginSpecification
from engine.ai.provider import AIProvider, extract_json
from engine.config.ai_config import AIConfig


class GeminiProvider(AIProvider):
    """Google Gemini API Strategy implementation using direct REST requests."""

    def generate_plugin(self, prompt: str) -> PluginSpecification:
        # Load API key from config or environment
        api_key = None
        if "gemini" in self.config.providers:
            api_key = self.config.providers["gemini"].api_key
        api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "Gemini API Key not found. Please set GEMINI_API_KEY environment variable "
                "or define it in devforge-ai.yaml"
            )

        # Build direct REST API endpoint for Gemini v1beta
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"

        # Setup request body structure
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
            },
        }

        # Request structured JSON format if enabled
        if self.config.structured_output:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            with httpx.Client(timeout=self.config.request_timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to Gemini API service: {e}")

        result = response.json()
        
        # Parse output from standard Gemini API response structure
        try:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ValueError(f"Gemini API returned unexpected response format: {result}")

        if not content:
            raise ValueError("Gemini API returned an empty response.")

        parsed_data = extract_json(content)
        return PluginSpecification(**parsed_data)
