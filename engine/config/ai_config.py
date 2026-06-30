# ==============================================================================
# DEVFORGE AI CONFIGURATION PARSER
# ==============================================================================
# Loads, parses, and validates the devforge-ai.yaml file using Pydantic.
# Automatically expands environment variables inside the config strings.
# ==============================================================================

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from engine.workspace import get_devforge_root

# Regular expression to find ${ENV_VAR} or $ENV_VAR patterns
ENV_VAR_PATTERN = re.compile(r'\$\{(\w+)\}|\$(\w+)')


def expand_env_vars(val: str) -> str:
    """Expand environment variables in a string value."""
    if not isinstance(val, str):
        return val

    def replacer(match):
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return ENV_VAR_PATTERN.sub(replacer, val)


def deep_expand_env_vars(data: any) -> any:
    """Recursively expand environment variables in dicts and lists."""
    if isinstance(data, dict):
        return {k: deep_expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_expand_env_vars(item) for item in data]
    elif isinstance(data, str):
        return expand_env_vars(data)
    return data


class ProviderConfig(BaseModel):
    """Configuration specific to a single AI provider."""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = Field(default_factory=list)


class AIConfig(BaseModel):
    """Main DevForge AI Configuration Model."""
    provider: str = "groq"
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.2
    max_tokens: int = 4096
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)
    fallback_order: List[str] = Field(default_factory=list)
    structured_output: bool = True
    cache_plugins: bool = True
    cache_responses: bool = True
    request_timeout: int = 120
    max_retries: int = 3

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AIConfig":
        """
        Load the configuration from the specified path, project root,
        or DevForge root. Falls back to default values if not found.
        """
        search_paths = []
        if config_path:
            search_paths.append(config_path)

        # Look in workspace root (/workspace)
        search_paths.append(Path("/workspace/devforge-ai.yaml"))
        # Look in DevForge root
        search_paths.append(get_devforge_root() / "devforge-ai.yaml")

        config_data = {}
        for path in search_paths:
            if path and path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw_data = yaml.safe_load(f) or {}
                        config_data = deep_expand_env_vars(raw_data)
                        break
                except Exception:
                    # Fail silently to search next path
                    pass

        # Return model initialized with file data or defaults
        return cls(**config_data)
