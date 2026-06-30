# ==============================================================================
# DEVFORGE PLUGIN INSTALLER
# ==============================================================================
# Installs a registered plugin into a project using the PluginManager.
# ==============================================================================

from engine.workspace import Project
from engine.plugin_manager import PluginManager


class PluginInstaller:
    """Handles the installation workflow of registered plugins into a project."""

    @staticmethod
    def install(plugin_name: str, project: Project) -> bool:
        """
        Installs a plugin into the specified Project.
        Underneath, it delegates to the existing PluginManager to merge environment
        variables, register the plugin in devforge.json, and regenerate docker-compose.
        """
        try:
            manager = PluginManager()
            # If the plugin spec has no version, install it directly
            manager.install(plugin_name, project)
            return True
        except SystemExit as e:
            # SystemExit is thrown if the manager fails or exits
            if e.code == 0:
                return True
            return False
        except Exception:
            return False
