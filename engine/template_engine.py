# ==============================================================================
# DEVFORGE TEMPLATE ENGINE
# ==============================================================================
# Manages DevForge code templates with versioning support.
# Handles: list, install, generate operations.
# ==============================================================================

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import yaml
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table
from rich import box

from engine.workspace import Project, get_devforge_root, WORKSPACE_ROOT

console = Console()

TEMPLATES_DIR = get_devforge_root() / "templates"
REGISTRY_FILE = get_devforge_root() / "registry" / "templates.yaml"


def _parse_spec(spec: str) -> tuple[str, Optional[str]]:
    """Parse 'react@18' into ('react', '18') or 'react' into ('react', None)."""
    if "@" in spec:
        name, version = spec.split("@", 1)
        return name.strip(), version.strip()
    return spec.strip(), None


class TemplateEngine:
    """Manages DevForge code templates with versioning."""

    def _load_registry(self) -> dict:
        if not REGISTRY_FILE.exists():
            console.print("[red]✗ Template registry not found at registry/templates.yaml[/red]")
            raise SystemExit(1)
        with open(REGISTRY_FILE) as f:
            return yaml.safe_load(f) or {}

    def list_templates(self, category: Optional[str] = None):
        """Display all available templates in a rich table."""
        data = self._load_registry()
        templates = data.get("templates", [])

        if category:
            templates = [t for t in templates if t.get("category") == category]

        table = Table(
            title="[bold cyan]Available Templates[/bold cyan]",
            box=box.ROUNDED,
            show_lines=True,
        )
        table.add_column("Name", style="bold cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Versions", style="green")
        table.add_column("Description")

        for t in templates:
            versions = ", ".join(str(v) for v in t.get("versions", [t.get("version", "latest")]))
            table.add_row(
                t["name"],
                t.get("category", "—"),
                versions,
                t.get("description", ""),
            )

        console.print(table)
        console.print(f"\n[dim]Install with: devforge template install <name>[@version][/dim]")

    def install(self, template_spec: str, project: Project):
        """Copy and render a template into the project directory."""
        name, version = _parse_spec(template_spec)
        src = self._resolve_template_path(name, version)

        if not src:
            console.print(f"[red]✗ Template '{template_spec}' not found.[/red]")
            raise SystemExit(1)

        dst = project.path / name
        if dst.exists():
            console.print(
                f"[yellow]⚠ Directory '{dst.relative_to(WORKSPACE_ROOT)}' already exists.[/yellow]"
            )
            raise SystemExit(1)

        shutil.copytree(src, dst)
        self._render_directory(dst, {"project_name": project.name})
        console.print(
            f"[green]✓[/green] Template '[bold]{template_spec}[/bold]' installed → "
            f"{dst.relative_to(WORKSPACE_ROOT)}"
        )

    def generate(self, template_spec: str, output_name: str, project: Project):
        """Generate a named app directory from a template."""
        name, version = _parse_spec(template_spec)
        src = self._resolve_template_path(name, version)

        if not src:
            console.print(f"[red]✗ Template '{template_spec}' not found.[/red]")
            raise SystemExit(1)

        dst = project.path / output_name
        if dst.exists():
            console.print(
                f"[red]✗ Directory '{output_name}' already exists in project.[/red]"
            )
            raise SystemExit(1)

        shutil.copytree(src, dst)
        self._render_directory(dst, {
            "project_name": project.name,
            "app_name": output_name,
        })
        console.print(
            f"[green]✓[/green] Generated '[bold]{output_name}[/bold]' from template "
            f"'{template_spec}' → {dst.relative_to(WORKSPACE_ROOT)}"
        )

    def _resolve_template_path(
        self, name: str, version: Optional[str]
    ) -> Optional[Path]:
        """Locate a template directory, respecting version suffixes."""
        if version:
            versioned = TEMPLATES_DIR / f"{name}@{version}"
            if versioned.exists():
                return versioned

        default = TEMPLATES_DIR / name
        return default if default.exists() else None

    def _render_directory(self, directory: Path, context: dict):
        """Recursively render Jinja2 variables inside all text files."""
        env = Environment(loader=FileSystemLoader(str(directory)))
        for file_path in directory.rglob("*"):
            if file_path.is_file() and not self._is_binary(file_path):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if "{{" in content:
                        rendered = Environment().from_string(content).render(**context)
                        file_path.write_text(rendered, encoding="utf-8")
                except (UnicodeDecodeError, Exception):
                    pass  # Skip files that can't be decoded

    @staticmethod
    def _is_binary(path: Path) -> bool:
        """Heuristic binary file check."""
        binary_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
            ".woff", ".woff2", ".ttf", ".eot",
            ".pyc", ".pyo", ".so", ".dll",
            ".zip", ".tar", ".gz",
        }
        return path.suffix.lower() in binary_extensions
