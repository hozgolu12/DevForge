# ==============================================================================
# DEVFORGE PLUGIN MANAGER
# ==============================================================================
# Manages DevForge service plugins with versioning support.
# Handles: list, install, remove operations.
# After install/remove, regenerates the project's compose files.
# ==============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.table import Table
from rich import box

from engine.workspace import Project, WORKSPACE_ROOT

console = Console()

PLUGINS_DIR = WORKSPACE_ROOT / "plugins"
REGISTRY_FILE = WORKSPACE_ROOT / "registry" / "plugins.yaml"


def _parse_spec(spec: str) -> tuple[str, Optional[str]]:
    """Parse 'postgres@16' into ('postgres', '16') or 'postgres' into ('postgres', None)."""
    if "@" in spec:
        name, version = spec.split("@", 1)
        return name.strip(), version.strip()
    return spec.strip(), None


class PluginManager:
    """Manages plugin lifecycle for DevForge projects."""

    def _load_registry(self) -> dict:
        if not REGISTRY_FILE.exists():
            console.print("[red]✗ Plugin registry not found at registry/plugins.yaml[/red]")
            raise SystemExit(1)
        with open(REGISTRY_FILE) as f:
            return yaml.safe_load(f) or {}

    def list_plugins(self, category: Optional[str], project: Optional[Project]):
        """Display all available plugins with install status."""
        data = self._load_registry()
        all_plugins = data.get("plugins", [])

        if category:
            all_plugins = [p for p in all_plugins if p.get("category") == category]

        # Load installed plugins from project manifest (if any)
        installed: set[str] = set()
        installed_versions: dict[str, str] = {}
        if project and project.exists():
            manifest = project.load_manifest()
            installed = set(manifest.get("plugins", []))
            installed_versions = manifest.get("plugin_versions", {})

        table = Table(
            title="[bold cyan]DevForge Plugin Registry[/bold cyan]",
            box=box.ROUNDED,
            show_lines=True,
        )
        table.add_column("Plugin", style="bold cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Versions", style="green")
        table.add_column("Description")
        table.add_column("Status", justify="center")

        for p in all_plugins:
            name = p["name"]
            versions = ", ".join(str(v) for v in p.get("versions", [p.get("version", "latest")]))

            if name in installed:
                ver = installed_versions.get(name, "default")
                status = f"[green]● installed[/green] [dim]({ver})[/dim]"
            else:
                status = "[dim]○ available[/dim]"

            table.add_row(
                name,
                p.get("category", "—"),
                versions,
                p.get("description", ""),
                status,
            )

        console.print(table)
        if project:
            console.print(f"\n[dim]Active project: [bold]{project.name}[/bold][/dim]")
        console.print(
            "[dim]Install with: devforge plugin install <name>[@version][/dim]"
        )

    def install(self, plugin_spec: str, project: Project):
        """Add a plugin to a project and regenerate compose files."""
        name, version = _parse_spec(plugin_spec)

        # Validate plugin exists
        plugin_path = PLUGINS_DIR / name
        if not plugin_path.exists():
            # Try versioned path
            if version:
                plugin_path = PLUGINS_DIR / f"{name}@{version}"
            if not plugin_path.exists():
                console.print(
                    f"[red]✗ Plugin '{name}' not found in plugins/ directory.[/red]"
                )
                raise SystemExit(1)

        # Load and update manifest
        manifest = project.load_manifest()
        plugins: list = manifest.get("plugins", [])
        versions: dict = manifest.get("plugin_versions", {})

        if name in plugins:
            console.print(
                f"[yellow]⚠ Plugin '[bold]{name}[/bold]' is already installed in '{project.name}'.[/yellow]"
            )
            return

        plugins.append(name)
        if version:
            versions[name] = version
        manifest["plugins"] = plugins
        manifest["plugin_versions"] = versions

        # Add default ports from plugin manifest
        plugin_manifest_path = plugin_path / "plugin.yaml"
        if plugin_manifest_path.exists():
            with open(plugin_manifest_path) as f:
                plugin_data = yaml.safe_load(f)
            for port_def in plugin_data.get("ports", []):
                env_key = port_def.get("env_key", "")
                host_port = port_def.get("host")
                if env_key and host_port:
                    # Store in ports map under the service name
                    manifest.setdefault("ports", {})[name] = host_port

            # Merge new env vars into manifest
            new_env = plugin_data.get("env", {})
            manifest.setdefault("env", {}).update(new_env)

        project.save_manifest(manifest)
        console.print(
            f"[green]✓[/green] Plugin '[bold]{name}[/bold]' installed into '{project.name}'."
        )

        # Regenerate compose files
        self._regenerate_compose(project, manifest)

    def remove(self, plugin_name: str, project: Project):
        """Remove a plugin from a project and regenerate compose files."""
        manifest = project.load_manifest()
        plugins: list = manifest.get("plugins", [])

        if plugin_name not in plugins:
            console.print(
                f"[yellow]⚠ Plugin '[bold]{plugin_name}[/bold]' is not installed in '{project.name}'.[/yellow]"
            )
            return

        plugins.remove(plugin_name)
        manifest["plugins"] = plugins
        manifest.get("plugin_versions", {}).pop(plugin_name, None)
        manifest.get("ports", {}).pop(plugin_name, None)

        project.save_manifest(manifest)
        console.print(
            f"[green]✓[/green] Plugin '[bold]{plugin_name}[/bold]' removed from '{project.name}'."
        )

        # Regenerate compose files
        self._regenerate_compose(project, manifest)

    @staticmethod
    def _regenerate_compose(project: Project, manifest: dict):
        """Trigger compose regeneration after plugin changes."""
        from engine.composer import ComposeGenerator
        console.print("[cyan]  Regenerating compose files...[/cyan]")
        ComposeGenerator().write_compose_files(
            project=project,
            plugins=manifest.get("plugins", []),
            plugin_versions=manifest.get("plugin_versions", {}),
            frameworks=manifest.get("frameworks", {}),
            ports=manifest.get("ports", {}),
        )
