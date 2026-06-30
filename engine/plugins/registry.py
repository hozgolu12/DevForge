# ==============================================================================
# DEVFORGE PLUGIN REGISTRY MANAGEMENT
# ==============================================================================
# Interfaces with the offline registry file (registry/plugins.yaml).
# Appends newly generated plugins dynamically so they can be installed.
# ==============================================================================

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from engine.ai.models import PluginSpecification
from engine.workspace import get_devforge_root


class PluginRegistry:
    """Manages the registration and resolution of DevForge plugins."""

    @staticmethod
    def get_registry_file() -> Path:
        """Returns the absolute path to the plugins.yaml registry file."""
        return get_devforge_root() / "registry" / "plugins.yaml"

    @classmethod
    def plugin_exists(cls, name: str) -> bool:
        """Checks if a plugin name is registered."""
        return cls.find_plugin(name) is not None

    @classmethod
    def find_plugin(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Finds a plugin by name in the registry.
        Priority resolution:
        1. Official Plugins (non-generated path)
        2. Generated Plugins (plugins/generated/ path)
        3. Draft Plugins (other paths)
        """
        # Map common tech names to plugin identifiers
        tech_map = {
            "postgresql": "postgres",
            "mongodb": "mongodb",
            "redis": "redis",
            "neo4j": "neo4j",
            "rabbitmq": "rabbitmq",
            "minio": "minio",
            "chromadb": "chromadb",
            "qdrant": "qdrant",
            "ollama": "ollama",
            "prometheus": "prometheus",
            "grafana": "grafana",
            "loki": "loki",
            "cadvisor": "cadvisor",
            "nginx": "nginx",
            "keycloak": "keycloak",
        }
        name_clean = name.lower().strip()
        name_clean = tech_map.get(name_clean, name_clean)
        
        reg_file = cls.get_registry_file()
        if not reg_file.exists():
            return None

        try:
            with open(reg_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return None

        plugins = data.get("plugins", [])
        matched_plugins = [p for p in plugins if p.get("name") == name_clean]

        if not matched_plugins:
            return None

        # Resolve according to Priority: Official -> Generated -> Draft
        official = []
        generated = []
        draft = []

        for p in matched_plugins:
            path = p.get("path", "")
            if "plugins/generated" in path:
                generated.append(p)
            elif "draft" in path or p.get("status") == "draft":
                draft.append(p)
            else:
                official.append(p)

        if official:
            return official[0]
        if generated:
            return generated[0]
        if draft:
            return draft[0]

        return matched_plugins[0]

    @classmethod
    def register_plugin(cls, spec: PluginSpecification, relative_path: str) -> bool:
        """
        Appends the generated plugin to registry/plugins.yaml.
        Ensures we do not create duplicate service or plugin names.
        """
        reg_file = cls.get_registry_file()
        reg_file.parent.mkdir(parents=True, exist_ok=True)

        data = {"plugins": []}
        if reg_file.exists():
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                pass

        plugins = data.setdefault("plugins", [])

        # Check if already registered (with the same path) to avoid duplicate entries
        for p in plugins:
            if p.get("name") == spec.plugin_name and p.get("path") == relative_path:
                return True

        # Build registry entry
        new_entry = {
            "name": spec.plugin_name,
            "display_name": spec.display_name,
            "category": spec.category,
            "versions": [spec.version],
            "default_version": spec.version,
            "description": spec.description,
            "path": relative_path,
            "docs": f"{relative_path}/README.md",
        }

        if spec.dependencies:
            new_entry["depends_on"] = spec.dependencies

        plugins.append(new_entry)

        try:
            with open(reg_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception:
            return False
