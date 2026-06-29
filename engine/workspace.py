# ==============================================================================
# DEVFORGE WORKSPACE MANAGER
# ==============================================================================
# Manages the devforge.json manifest and .devforge/ hidden directory
# for each generated project. Also tracks the active project for
# multi-project workflows.
# ==============================================================================

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

# Path mappings (inside the container, /workspace = host DevForge root)
WORKSPACE_ROOT = Path("/workspace")
PROJECTS_DIR = WORKSPACE_ROOT / "projects"
GLOBAL_STATE_FILE = WORKSPACE_ROOT / ".devforge" / "active_project"


class Project:
    """Represents a DevForge v2 project with its manifest and paths."""

    def __init__(self, name: str):
        self.name = name
        self.path = PROJECTS_DIR / name
        self.manifest_path = self.path / "devforge.json"
        self.devforge_dir = self.path / ".devforge"
        self.generated_dir = self.devforge_dir / "generated"
        self.cache_dir = self.devforge_dir / "cache"
        self.logs_dir = self.devforge_dir / "logs"
        self.metadata_dir = self.devforge_dir / "metadata"

    @property
    def compose_file(self) -> Path:
        return self.path / "docker-compose.yml"

    def compose_for_profile(self, profile: str) -> Path:
        return self.generated_dir / f"docker-compose.{profile}.yml"

    def exists(self) -> bool:
        return self.path.exists() and self.manifest_path.exists()

    def load_manifest(self) -> dict:
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"No devforge.json found in projects/{self.name}. "
                f"Run 'devforge new {self.name}' to create it."
            )
        with open(self.manifest_path) as f:
            return json.load(f)

    def save_manifest(self, data: dict):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"[dim]  Updated devforge.json for '{self.name}'[/dim]")

    def ensure_devforge_dir(self):
        """Create the hidden .devforge/ workspace directory structure."""
        for d in [
            self.devforge_dir,
            self.generated_dir,
            self.cache_dir,
            self.logs_dir,
            self.metadata_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

        # Write a .gitignore inside .devforge/ to exclude caches and logs
        gitignore = self.devforge_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(
                "# DevForge internal directory\ncache/\nlogs/\n"
            )

    @staticmethod
    def build_manifest(
        name: str,
        project_type: str,
        frameworks: dict,
        plugins: list[str],
        plugin_versions: dict,
        ports: dict,
        env_vars: dict,
        ci_cd: Optional[str],
    ) -> dict:
        return {
            "name": name,
            "version": "1.0.0",
            "devforge_version": "2.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project_type": project_type,
            "frameworks": frameworks,
            "plugins": plugins,
            "plugin_versions": plugin_versions,
            "ports": ports,
            "env_file": ".env",
            "ci_cd": ci_cd,
            "compose_file": "docker-compose.yml",
            "active_profile": "dev",
        }


class WorkspaceManager:
    """Manages workspace state including the active project."""

    def set_active_project(self, project_name: str):
        """Set the global active project."""
        project = Project(project_name)
        if not project.path.exists():
            console.print(
                f"[red]✗ Project '{project_name}' not found in projects/[/red]"
            )
            raise SystemExit(1)

        GLOBAL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        GLOBAL_STATE_FILE.write_text(project_name)
        console.print(
            f"[green]✓ Active project set to '[bold]{project_name}[/bold]'.[/green]"
        )

    def get_active_project(self) -> Optional[str]:
        """Read the current active project name."""
        if GLOBAL_STATE_FILE.exists():
            name = GLOBAL_STATE_FILE.read_text().strip()
            return name if name else None
        return None

    def resolve_project(self, name: Optional[str], required: bool = True) -> Optional[Project]:
        """
        Resolve a project by name, falling back to the active project.
        If required=True and no project can be found, exits with an error.
        """
        project_name = name or self.get_active_project()

        if not project_name:
            if required:
                console.print(
                    "[red]✗ No project specified and no active project set.[/red]\n"
                    "  Use [bold]devforge use <project>[/bold] to set an active project,\n"
                    "  or pass [bold]--project <name>[/bold] to this command."
                )
                raise SystemExit(1)
            return None

        project = Project(project_name)
        if required and not project.path.exists():
            console.print(
                f"[red]✗ Project '{project_name}' does not exist in projects/[/red]"
            )
            raise SystemExit(1)

        return project

    def list_projects(self) -> list[str]:
        """Return all project names that have a devforge.json manifest."""
        if not PROJECTS_DIR.exists():
            return []
        return [
            d.name
            for d in PROJECTS_DIR.iterdir()
            if d.is_dir() and (d / "devforge.json").exists()
        ]
