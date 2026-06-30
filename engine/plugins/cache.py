# ==============================================================================
# DEVFORGE PLUGIN GENERATION CACHE
# ==============================================================================
# Checks and manages previously generated plugins under plugins/generated/.
# Prevents unnecessary LLM costs and speeds up project onboarding.
# ==============================================================================

from pathlib import Path
from engine.workspace import get_devforge_root


class PluginCache:
    """Manages the generated plugin cache."""

    @staticmethod
    def get_generated_dir() -> Path:
        """Returns the absolute path to the plugins/generated directory."""
        return get_devforge_root() / "plugins" / "generated"

    @classmethod
    def exists(cls, plugin_name: str) -> bool:
        """
        Check if the plugin exists in the generated cache.
        A valid cached plugin must have a plugin.yaml manifest.
        """
        name_clean = plugin_name.lower().strip()
        plugin_dir = cls.get_generated_dir() / name_clean
        return plugin_dir.exists() and (plugin_dir / "plugin.yaml").exists()

    @classmethod
    def get_path(cls, plugin_name: str) -> Path:
        """Gets the path to the cached plugin directory."""
        name_clean = plugin_name.lower().strip()
        return cls.get_generated_dir() / name_clean

    @classmethod
    def clear(cls, plugin_name: str) -> bool:
        """Clears the cached files for a specific plugin if they exist."""
        import shutil
        name_clean = plugin_name.lower().strip()
        plugin_dir = cls.get_generated_dir() / name_clean
        if plugin_dir.exists():
            try:
                shutil.rmtree(plugin_dir)
                return True
            except Exception:
                pass
        return False
