# ==============================================================================
# DEVFORGE AI PLUGIN GENERATION ORCHESTRATOR
# ==============================================================================
# Integrates collectors, prompt engines, AI provider strategies, and logging
# to orchestrate the plugin generation flow with automatic fallback.
# ==============================================================================

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from engine.ai.factory import AIFactory
from engine.ai.models import PluginSpecification
from engine.ai.prompts import SYSTEM_PROMPT_V1, USER_PROMPT_TEMPLATE_V1
from engine.config.ai_config import AIConfig
from engine.detector.knowledge_collector import KnowledgeCollector
from engine.detector.metadata_collector import MetadataCollector


def log_ai_event(project_path: Path, event_type: str, data: Dict[str, Any]):
    """Write a structured JSON log entry to .devforge/logs/ai.log."""
    log_dir = project_path / ".devforge" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "ai.log"
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **data,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        # Prevent logging errors from crashing the CLI execution
        pass


class AIPluginGenerator:
    """Orchestrates AI plugin generation and handles error recovery."""

    @staticmethod
    def generate(
        technology_name: str,
        project_path: Path,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> Optional[PluginSpecification]:
        """
        Runs the full AI plugin generation loop.
        Applies provider overrides and executes fallbacks if they fail.
        """
        # 1. Load active config
        config = AIConfig.load()

        # 2. Gather project metadata context
        metadata = MetadataCollector.collect(project_path)

        # 3. Gather technology knowledge properties
        knowledge = KnowledgeCollector.collect(technology_name)

        # 4. Interpolate prompts
        user_prompt = USER_PROMPT_TEMPLATE_V1.format(
            technology_name=technology_name,
            project_packages=", ".join(metadata["packages"]) or "None",
            project_languages=", ".join(metadata["languages"]) or "None",
            project_docker_images=", ".join(metadata["docker_images"]) or "None",
            project_env_vars=", ".join(metadata["environment_variables"]) or "None",
            known_docs=knowledge["documentation_url"] or "None",
            known_github=knowledge["github_repository"] or "None",
            known_image=knowledge["docker_image"] or "None",
            known_ports=", ".join(str(p) for p in knowledge["default_ports"]),
            known_env=str(knowledge["default_env"]),
            known_health=knowledge["health_endpoint"] or "None",
            known_dependencies=", ".join(knowledge["dependencies"]) or "None",
            known_category=knowledge["category"],
            known_description=knowledge["description"],
        )

        full_prompt = SYSTEM_PROMPT_V1 + "\n" + user_prompt

        # 5. Resolve sequence of providers to try (Override -> Fallbacks -> Default)
        providers_to_try = []
        if provider_override:
            providers_to_try.append((provider_override, model_override))

        for prov_name in config.fallback_order:
            if provider_override and prov_name.lower() == provider_override.lower():
                continue
            providers_to_try.append((prov_name, None))

        if not providers_to_try:
            providers_to_try.append((config.provider, config.model))

        def resolve_model(prov: str, model_opt: Optional[str]) -> str:
            if model_opt:
                return model_opt
            if prov.lower() == config.provider.lower():
                return config.model

            # Check if there are models defined in config
            prov_cfg = config.providers.get(prov)
            if prov_cfg and prov_cfg.models:
                return prov_cfg.models[0]

            # Standard defaults
            defaults = {
                "groq": "llama-3.1-8b-instant",
                "gemini": "gemini-2.0-flash-lite",
                "openai": "gpt-4o-mini",
                "ollama": "qwen3:8b",
            }
            return defaults.get(prov.lower(), "latest")

        # 6. Execute AI strategy calls
        for prov_name, model_opt in providers_to_try:
            model_name = resolve_model(prov_name, model_opt)
            try:
                # Instantiate strategic provider
                provider_client = AIFactory.get_provider(config, prov_name, model_name)

                start_time = time.time()
                spec = provider_client.generate_plugin(full_prompt)
                gen_time = time.time() - start_time

                # Log successful event
                log_ai_event(
                    project_path,
                    "generation_success",
                    {
                        "technology": technology_name,
                        "provider": prov_name,
                        "model": model_name,
                        "generation_time_seconds": gen_time,
                        "token_usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                    },
                )
                return spec

            except Exception as e:
                # Log failure event and continue to fallback
                log_ai_event(
                    project_path,
                    "generation_failure",
                    {
                        "technology": technology_name,
                        "provider": prov_name,
                        "model": model_name,
                        "error": str(e),
                    },
                )
                # Fail silently to user, console warning printed during dry run
                pass

        # All providers failed
        log_ai_event(
            project_path,
            "all_providers_failed",
            {
                "technology": technology_name,
                "tried_providers": [p[0] for p in providers_to_try],
            },
        )
        return None
