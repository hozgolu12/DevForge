# ==============================================================================
# DEVFORGE AI PROVIDER BASE CLASS
# ==============================================================================
# Declares the strategy interface that all AI API providers must implement.
# Also defines the shared extract_json utility for parsing AI responses.
# ==============================================================================

import json
import re
from abc import ABC, abstractmethod
from typing import Optional
from engine.ai.models import PluginSpecification
from engine.config.ai_config import AIConfig


def extract_json(text: str) -> dict:
    """
    Robust utility to extract and parse a JSON object from text.
    Handles raw JSON, markdown-wrapped JSON blocks, and extra leading/trailing text.
    """
    text = text.strip()
    
    # Check for markdown code blocks and clean them
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1)
        else:
            # Fallback: manually strip the first and last lines if they are backticks
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

    # Try direct JSON parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Find first '{' and last '}' as final fallback
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError as e:
                raise ValueError(f"Found JSON bounds, but parsing failed: {e}. Raw content:\n{text[start:end+1]}")
        raise ValueError(f"No JSON object boundaries found in raw string:\n{text}")


class AIProvider(ABC):
    """Abstract Strategy class representing an LLM Provider."""

    def __init__(self, config: AIConfig, model_override: Optional[str] = None):
        self.config = config
        self.model = model_override or config.model

    @abstractmethod
    def generate_plugin(self, prompt: str) -> PluginSpecification:
        """
        Executes the LLM request to generate a structured PluginSpecification.
        Should parse and validate the JSON output from the AI.
        """
        pass
