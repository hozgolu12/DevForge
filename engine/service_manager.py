# ==============================================================================
# DEVFORGE SERVICE MANAGER
# ==============================================================================
# Handles per-service operations for generated DevForge v2 projects.
# All docker compose calls target the project's generated compose file,
# resolved from the project's devforge.json manifest.
# ==============================================================================

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich import box

from engine.workspace import Project

console = Console()


class ServiceManager:
    """Delegates per-service docker compose commands to the correct project compose file."""

    def _compose_file(self, project: Project, profile: str = "dev") -> str:
        """
        Resolve the compose file path for a given profile.
        Falls back to the default docker-compose.yml if the profile variant
        doesn't exist yet.
        """
        if profile != "dev":
            profile_compose = project.compose_for_profile(profile)
            if profile_compose.exists():
                return str(profile_compose)

        if project.compose_file.exists():
            return str(project.compose_file)

        console.print(
            f"[red]✗ No compose file found for project '{project.name}'.[/red]\n"
            f"  Run [bold]devforge new {project.name}[/bold] first."
        )
        raise SystemExit(1)

    def _run(self, args: list[str], compose_file: str) -> int:
        """Execute a docker compose command against a specific file."""
        cmd = ["docker", "compose", "-f", compose_file] + args
        result = subprocess.run(cmd)
        return result.returncode

    # ──────────────────────────────────────────────────────────────────────────
    # Per-service commands
    # ──────────────────────────────────────────────────────────────────────────

    def start(self, service: str, project: Project, profile: str = "dev"):
        compose = self._compose_file(project, profile)
        console.print(
            f"[cyan]Starting [bold]{service}[/bold] "
            f"in '[bold]{project.name}[/bold]' (profile: {profile})...[/cyan]"
        )
        rc = self._run(["up", "-d", service], compose)
        if rc == 0:
            console.print(f"[green]✓[/green] [bold]{service}[/bold] is running.")
        sys.exit(rc)

    def stop(self, service: str, project: Project):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Stopping [bold]{service}[/bold] in '[bold]{project.name}[/bold]'...[/cyan]"
        )
        rc = self._run(["stop", service], compose)
        if rc == 0:
            console.print(f"[green]✓[/green] [bold]{service}[/bold] stopped.")
        sys.exit(rc)

    def restart(self, service: str, project: Project):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Restarting [bold]{service}[/bold] in '[bold]{project.name}[/bold]'...[/cyan]"
        )
        rc = self._run(["restart", service], compose)
        if rc == 0:
            console.print(f"[green]✓[/green] [bold]{service}[/bold] restarted.")
        sys.exit(rc)

    def logs(self, service: str, project: Project, tail: int = 100):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Tailing logs for [bold]{service}[/bold] "
            f"in '[bold]{project.name}[/bold]' (press Ctrl+C to exit)...[/cyan]\n"
        )
        rc = self._run(["logs", "-f", f"--tail={tail}", service], compose)
        sys.exit(rc)

    def shell(self, service: str, project: Project):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Opening shell in [bold]{service}[/bold] "
            f"('[bold]{project.name}[/bold]')...[/cyan]"
        )
        # Try zsh → bash → sh in order of preference
        for shell in ["zsh", "bash", "sh"]:
            result = subprocess.run(
                ["docker", "compose", "-f", compose, "exec", service, shell]
            )
            if result.returncode == 0:
                break
        sys.exit(result.returncode)

    def status(self, project: Project):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Container status for '[bold]{project.name}[/bold]':[/cyan]"
        )
        rc = self._run(["ps"], compose)
        sys.exit(rc)

    # ──────────────────────────────────────────────────────────────────────────
    # Full project up / down
    # ──────────────────────────────────────────────────────────────────────────

    def up_all(self, project: Project, profile: str = "dev"):
        compose = self._compose_file(project, profile)
        console.print(
            f"[cyan]Starting all services for '[bold]{project.name}[/bold]' "
            f"(profile: [bold]{profile}[/bold])...[/cyan]"
        )
        rc = self._run(["up", "-d"], compose)
        if rc == 0:
            self._print_access_info(project, profile)
        sys.exit(rc)

    def down_all(self, project: Project):
        compose = self._compose_file(project)
        console.print(
            f"[cyan]Stopping all services for '[bold]{project.name}[/bold]'...[/cyan]"
        )
        rc = self._run(["down"], compose)
        if rc == 0:
            console.print(
                f"[green]✓[/green] All services for '[bold]{project.name}[/bold]' stopped."
            )
        sys.exit(rc)

    def _print_access_info(self, project: Project, profile: str):
        """Print access URLs after a successful up."""
        try:
            manifest = project.load_manifest()
            ports = manifest.get("ports", {})
            plugins = manifest.get("plugins", [])
        except Exception:
            return

        lines = []
        url_map = {
            "react": ("React App", "http://localhost"),
            "nextjs": ("Next.js App", "http://localhost"),
            "fastapi": ("FastAPI Docs", "http://localhost", "/docs"),
            "django": ("Django", "http://localhost"),
            "express": ("Express API", "http://localhost"),
            "nestjs": ("NestJS API", "http://localhost"),
            "nginx": ("Nginx Dashboard", "http://localhost:80"),
            "pgadmin": ("pgAdmin", "http://localhost:5050"),
            "mongo-express": ("Mongo Express", "http://localhost:8087"),
            "redis-commander": ("Redis Commander", "http://localhost:8086"),
            "grafana": ("Grafana", "http://localhost:3002"),
            "prometheus": ("Prometheus", "http://localhost:9090"),
            "open-webui": ("Open WebUI (AI)", "http://localhost:3000"),
            "qdrant": ("Qdrant Console", "http://localhost:6333/dashboard"),
            "keycloak": ("Keycloak Auth", "http://localhost:8085"),
            "minio": ("MinIO Console", "http://localhost:9001"),
            "rabbitmq": ("RabbitMQ UI", "http://localhost:15672"),
        }

        for service, info in url_map.items():
            if service in plugins or service in manifest.get("frameworks", {}).values():
                port = ports.get(service)
                label = info[0]
                base_url = info[1]
                suffix = info[2] if len(info) > 2 else ""
                if port:
                    url = f"http://localhost:{port}{suffix}"
                else:
                    url = f"{base_url}{suffix}"
                lines.append(f"  [cyan]{label:<25}[/cyan] {url}")

        if lines:
            console.print(Panel(
                "\n".join(lines),
                title=f"[bold green]✓ {project.name} is running ({profile} profile)[/bold green]",
                box=box.ROUNDED,
            ))
