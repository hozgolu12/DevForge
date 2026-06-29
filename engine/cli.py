# ==============================================================================
# DEVFORGE CLI — MAIN ENTRY POINT
# ==============================================================================
# Runs inside the devforge-cli:2.0 Docker container.
# Invoked by devforge.ps1 (Windows) and devforge (Bash) wrapper scripts.
# ==============================================================================

import subprocess
import sys
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

DEVFORGE_VERSION = "2.0.0"
CLI_IMAGE = "devforge-cli:2.0"

# Banner printed on help/version
BANNER = """[bold cyan]
██████╗ ███████╗██╗   ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔════╝██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██║  ██║█████╗  ██║   ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║  ██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██████╔╝███████╗ ╚████╔╝ ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═════╝ ╚══════╝  ╚═══╝  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
[/bold cyan]"""


def print_banner():
    console.print(BANNER)
    console.print(
        f"[dim]  v{DEVFORGE_VERSION} · One Docker Command. Unlimited Development.[/dim]\n"
    )


def run_docker_compose(args: list[str], compose_file: str = None) -> int:
    """Run a docker compose command, optionally targeting a specific file."""
    cmd = ["docker", "compose"]
    if compose_file:
        cmd += ["-f", compose_file]
    cmd += args
    result = subprocess.run(cmd)
    return result.returncode


# ──────────────────────────────────────────────────────────────────────────────
# ROOT CLI GROUP
# ──────────────────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.version_option(version=DEVFORGE_VERSION, prog_name="DevForge")
@click.pass_context
def cli(ctx):
    """
    \b
    DevForge v2 — Modular Docker-native developer platform.
    One Docker Command. Unlimited Development.

    \b
    V2 Commands (project-aware):
      new          Create a new project interactively
      init         Initialize the CURRENT directory as a DevForge project
      import       Import an existing project from another directory
      detect       Analyze the current project without modifying any files
      template     Manage code templates
      plugin       Manage service plugins
      start        Start a specific service
      stop         Stop a specific service
      restart      Restart a specific service
      logs         Tail logs for a service
      shell        Open a shell inside a service
      use          Set the active project
      update       Update the DevForge CLI image

    \b
    V1 Commands (platform-wide, unchanged):
      up           Start all platform services
      down         Stop all platform services
      status       Show container status
      doctor       Run system diagnostics
      backup       Back up databases
      restore      Restore databases
      seed         Seed databases
      build-apk    Build Flutter APK
    """
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: new
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("new")
@click.argument("project_name")
@click.option("--no-interactive", is_flag=True, help="Skip wizard, use defaults")
def cmd_new(project_name, no_interactive):
    """Create a new DevForge project with an interactive wizard.

    \b
    Example:
      devforge new socialcross
      devforge new my-api --no-interactive
    """
    from engine.generator import ProjectGenerator
    generator = ProjectGenerator()
    generator.run(project_name, interactive=not no_interactive)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: init
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("init")
@click.option("--no-interactive", is_flag=True, help="Skip wizard, use defaults")
def cmd_init(no_interactive):
    """Initialize the CURRENT directory as a DevForge project.

    \b
    Example:
      cd SocialCross
      devforge init
    """
    import re
    from pathlib import Path
    from engine.generator import ProjectGenerator
    
    workspace_root = Path("/workspace")
    raw_name = workspace_root.name
    project_name = re.sub(r'[^a-zA-Z0-9_-]', '', raw_name).lower()
    
    generator = ProjectGenerator()
    generator.onboard(project_name, workspace_root, interactive=not no_interactive)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: import
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("import")
@click.argument("import_path")
@click.option("--no-interactive", is_flag=True, help="Skip wizard, use defaults")
def cmd_import(import_path, no_interactive):
    """Import an existing project from another directory.

    \b
    Example:
      devforge import D:\\Projects\\SocialCross
    """
    import re
    import shutil
    from pathlib import Path
    from engine.workspace import PROJECTS_DIR
    from engine.generator import ProjectGenerator

    import_target = Path("/import_target")
    if import_target.exists() and import_target.is_dir():
        src_dir = import_target
    else:
        src_dir = Path("/workspace") / import_path
        if not src_dir.exists():
            console.print(f"[red]✗ Import path '{import_path}' not found.[/red]")
            raise SystemExit(1)

    raw_name = src_dir.name
    project_name = re.sub(r'[^a-zA-Z0-9_-]', '', raw_name).lower()

    target_dir = PROJECTS_DIR / project_name
    if target_dir.exists():
        console.print(f"[red]✗ Project '{project_name}' already exists in projects/ directory.[/red]")
        raise SystemExit(1)

    console.print(f"[cyan]Copying project to projects/{project_name}...[/cyan]")
    ignore_patterns = shutil.ignore_patterns(
        '.git', 'node_modules', '.venv', 'venv', 'env', '.devforge', 'build', 'dist', 'target', 'bin', 'obj'
    )
    shutil.copytree(src_dir, target_dir, ignore=ignore_patterns, dirs_exist_ok=True)

    generator = ProjectGenerator()
    generator.onboard(project_name, target_dir, interactive=not no_interactive)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: detect
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("detect")
def cmd_detect():
    """Analyze the current project without modifying any files."""
    from pathlib import Path
    from engine.detection import DetectionEngine

    workspace_root = Path("/workspace")
    detected = DetectionEngine.detect(workspace_root, force=True)

    # Output detected technologies in the exact requested format
    for category in ["Frontend", "Backend", "Mobile", "Database", "Cache", "Vector Database"]:
        techs = detected.get(category, {})
        if techs:
            console.print(f"[bold]{category}[/bold]")
            for tech in techs.keys():
                console.print(f"✓ {tech}")
            console.print("")

    # Separate AI and OCR
    ai_techs = dict(detected.get("AI", {}))
    has_tesseract = ai_techs.pop("Tesseract", False)

    if ai_techs:
        console.print("[bold]AI[/bold]")
        for tech in ai_techs.keys():
            console.print(f"✓ {tech}")
        console.print("")

    if has_tesseract:
        console.print("[bold]OCR[/bold]")
        console.print("✓ Tesseract")
        console.print("")

    for category in ["Messaging", "Monitoring", "Storage"]:
        techs = detected.get(category, {})
        if techs:
            console.print(f"[bold]{category}[/bold]")
            for tech in techs.keys():
                console.print(f"✓ {tech}")
            console.print("")

    if "Docker" in detected and detected["Docker"]:
        console.print("[bold]Docker[/bold]")
        for df in detected["Docker"].keys():
            console.print(f"✓ {df}")
        console.print("")

    if "Package Managers" in detected and detected["Package Managers"]:
        console.print("[bold]Package Managers[/bold]")
        for pm in detected["Package Managers"].keys():
            console.print(f"✓ {pm}")
        console.print("")

    if detected.get("Recommendations"):
        console.print("[bold]Recommendations[/bold]\n")
        for rec in detected["Recommendations"]:
            console.print(f"- {rec}")
        console.print("")

    console.print("No files modified.")


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND GROUP: template
# ──────────────────────────────────────────────────────────────────────────────

@cli.group("template")
def template_group():
    """Manage DevForge code templates.

    \b
    Examples:
      devforge template list
      devforge template install react
      devforge template install react@18
      devforge generate react frontend
    """
    pass


@template_group.command("list")
@click.option("--category", default=None, help="Filter by category (frontend, backend, mobile, ai)")
def template_list(category):
    """List all available templates."""
    from engine.template_engine import TemplateEngine
    TemplateEngine().list_templates(category=category)


@template_group.command("install")
@click.argument("template_spec")
@click.option("--project", default=None, help="Target project name")
def template_install(template_spec, project):
    """Install a template into the current or specified project.

    \b
    TEMPLATE_SPEC can include a version: react@18, nestjs@11, fastapi@0.115
    """
    from engine.template_engine import TemplateEngine
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    TemplateEngine().install(template_spec, proj)


@template_group.command("generate")
@click.argument("template_spec")
@click.argument("output_name")
@click.option("--project", default=None, help="Target project name")
def template_generate(template_spec, output_name, project):
    """Generate a named app from a template.

    \b
    Example:
      devforge generate react frontend
      devforge generate fastapi auth-service
    """
    from engine.template_engine import TemplateEngine
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    TemplateEngine().generate(template_spec, output_name, proj)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND GROUP: plugin
# ──────────────────────────────────────────────────────────────────────────────

@cli.group("plugin")
def plugin_group():
    """Manage DevForge service plugins.

    \b
    Examples:
      devforge plugin list
      devforge plugin install postgres
      devforge plugin install postgres@16
      devforge plugin remove postgres
    """
    pass


@plugin_group.command("list")
@click.option("--category", default=None, help="Filter by category (database, cache, ai, monitoring)")
@click.option("--project", default=None, help="Show status for a specific project")
def plugin_list(category, project):
    """List all available plugins and their installation status."""
    from engine.plugin_manager import PluginManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project, required=False)
    PluginManager().list_plugins(category=category, project=proj)


@plugin_group.command("install")
@click.argument("plugin_spec")
@click.option("--project", default=None, help="Target project name")
def plugin_install(plugin_spec, project):
    """Install a plugin into a project and regenerate compose.

    \b
    PLUGIN_SPEC can include a version: postgres@16, redis@7, mongodb@7
    """
    from engine.plugin_manager import PluginManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    PluginManager().install(plugin_spec, proj)


@plugin_group.command("remove")
@click.argument("plugin_name")
@click.option("--project", default=None, help="Target project name")
def plugin_remove(plugin_name, project):
    """Remove a plugin from a project and regenerate compose."""
    from engine.plugin_manager import PluginManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    PluginManager().remove(plugin_name, proj)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMANDS: per-service management
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("start")
@click.argument("service")
@click.option("--project", default=None, help="Target project name")
@click.option("--profile", default="dev", show_default=True,
              type=click.Choice(["dev", "testing", "production"]),
              help="Environment profile to use")
def cmd_start(service, project, profile):
    """Start a specific service in a project.

    \b
    Example:
      devforge start mongodb
      devforge start postgres --project socialcross
    """
    from engine.service_manager import ServiceManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    ServiceManager().start(service, proj, profile=profile)


@cli.command("stop")
@click.argument("service")
@click.option("--project", default=None, help="Target project name")
def cmd_stop(service, project):
    """Stop a specific service in a project.

    \b
    Example:
      devforge stop mongodb
      devforge stop redis --project socialcross
    """
    from engine.service_manager import ServiceManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    ServiceManager().stop(service, proj)


@cli.command("restart")
@click.argument("service")
@click.option("--project", default=None, help="Target project name")
def cmd_restart(service, project):
    """Restart a specific service in a project."""
    from engine.service_manager import ServiceManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    ServiceManager().restart(service, proj)


@cli.command("logs")
@click.argument("service")
@click.option("--project", default=None, help="Target project name")
@click.option("--tail", default=100, show_default=True, help="Number of log lines to show")
def cmd_logs(service, project, tail):
    """Tail logs for a specific service.

    \b
    Example:
      devforge logs fastapi
      devforge logs mongodb --tail 50 --project socialcross
    """
    from engine.service_manager import ServiceManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    ServiceManager().logs(service, proj, tail=tail)


@cli.command("shell")
@click.argument("service")
@click.option("--project", default=None, help="Target project name")
def cmd_shell(service, project):
    """Open an interactive shell inside a running service container.

    \b
    Example:
      devforge shell postgres
      devforge shell redis --project socialcross
    """
    from engine.service_manager import ServiceManager
    from engine.workspace import WorkspaceManager
    ws = WorkspaceManager()
    proj = ws.resolve_project(project)
    ServiceManager().shell(service, proj)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: up (with profile support)
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("up")
@click.option("--project", default=None, help="Target project name (uses project compose)")
@click.option("--profile", default="dev", show_default=True,
              type=click.Choice(["dev", "testing", "production"]),
              help="Environment profile")
def cmd_up(project, profile):
    """Start services.

    \b
    With --project: starts only that project's services.
    Without --project: starts the full v1 DevForge platform.

    \b
    Examples:
      devforge up                              # v1: all platform services
      devforge up --project socialcross        # v2: project services (dev profile)
      devforge up --project socialcross --profile production
    """
    from engine.workspace import WorkspaceManager
    from engine.service_manager import ServiceManager

    if project:
        ws = WorkspaceManager()
        proj = ws.resolve_project(project)
        ServiceManager().up_all(proj, profile=profile)
    else:
        # v1 fallback — full platform
        console.print("[cyan]Starting DevForge platform services...[/cyan]")
        rc = run_docker_compose(["up", "-d"])
        if rc == 0:
            console.print("[green]✓ DevForge platform is running.[/green]")
        sys.exit(rc)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: use (multi-project active project selection)
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("use")
@click.argument("project_name")
def cmd_use(project_name):
    """Set the active project for subsequent commands.

    \b
    Example:
      devforge use socialcross
      devforge start mongodb   # now operates on socialcross
    """
    from engine.workspace import WorkspaceManager
    WorkspaceManager().set_active_project(project_name)


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: update / self-update
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("update")
def cmd_update():
    """Update the DevForge CLI image to the latest version.

    Rebuilds the devforge-cli Docker image from the current source.
    Your projects, templates, and plugins are never affected.

    \b
    Example:
      devforge update
    """
    console.print(Panel(
        "[cyan]Updating DevForge CLI...[/cyan]\n"
        "[dim]Rebuilding devforge-cli:2.0 from current source[/dim]",
        title="[bold]DevForge Self-Update[/bold]",
        box=box.ROUNDED
    ))
    result = subprocess.run([
        "docker", "build",
        "--no-cache",
        "-t", CLI_IMAGE,
        "-f", "docker/cli/Dockerfile",
        "."
    ])
    if result.returncode == 0:
        console.print("[green]✓ DevForge CLI updated successfully.[/green]")
    else:
        console.print("[red]✗ Update failed. Check Docker output above.[/red]")
        sys.exit(1)


# Alias
cli.add_command(cmd_update, name="self-update")


# ──────────────────────────────────────────────────────────────────────────────
# V2 COMMAND: doctor (enhanced)
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("doctor")
@click.option("--project", default=None, help="Also validate a specific project's workspace")
def cmd_doctor(project):
    """Run comprehensive system health diagnostics.

    Checks Docker, CLI image, registries, ports, disk, memory, and networks.

    \b
    Example:
      devforge doctor
      devforge doctor --project socialcross
    """
    import shutil
    import socket
    from pathlib import Path

    console.print(Panel(
        "[bold cyan]DevForge System Diagnostics[/bold cyan]",
        box=box.ROUNDED
    ))

    checks_passed = 0
    checks_failed = 0

    def check(label: str, ok: bool, detail: str = ""):
        nonlocal checks_passed, checks_failed
        icon = "[green]✓[/green]" if ok else "[red]✗[/red]"
        status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
        line = f"  {icon}  {label:<45} {status}"
        if detail:
            line += f"  [dim]{detail}[/dim]"
        console.print(line)
        if ok:
            checks_passed += 1
        else:
            checks_failed += 1

    # 1. Docker daemon
    r = subprocess.run(["docker", "info"], capture_output=True)
    check("Docker daemon running", r.returncode == 0)

    # 2. Docker version
    r = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    ver = r.stdout.strip() if r.returncode == 0 else "unknown"
    check("Docker version detected", r.returncode == 0, ver)

    # 3. CLI image
    r = subprocess.run(["docker", "image", "inspect", CLI_IMAGE], capture_output=True)
    check(f"CLI image {CLI_IMAGE}", r.returncode == 0,
          "run 'make build-cli' to build" if r.returncode != 0 else "")

    # 4. docker-compose.yml present
    compose_ok = Path("/workspace/docker-compose.yml").exists()
    check("docker-compose.yml present", compose_ok)

    # 5. Compose configuration valid
    if compose_ok:
        r = subprocess.run(["docker", "compose", "config", "-q"],
                           capture_output=True, cwd="/workspace")
        check("Compose configuration valid", r.returncode == 0)

    # 6. Plugin registry
    plugin_reg = Path("/workspace/registry/plugins.yaml").exists()
    check("Plugin registry (registry/plugins.yaml)", plugin_reg)

    # 7. Template registry
    tmpl_reg = Path("/workspace/registry/templates.yaml").exists()
    check("Template registry (registry/templates.yaml)", tmpl_reg)

    # 8. .env file present
    env_ok = Path("/workspace/.env").exists()
    check(".env file configured", env_ok,
          "run 'cp .env.example .env'" if not env_ok else "")

    # 9. Disk space (>= 5 GB free)
    disk = shutil.disk_usage("/workspace")
    free_gb = disk.free / (1024 ** 3)
    check(f"Disk space available", free_gb >= 5.0, f"{free_gb:.1f} GB free")

    # 10. Port conflict checks
    console.print("\n  [dim]Checking key port availability...[/dim]")
    ports_to_check = {
        80: "Nginx HTTP", 443: "Nginx HTTPS",
        5432: "PostgreSQL", 27017: "MongoDB",
        6379: "Redis", 11434: "Ollama",
        3000: "Open WebUI", 9090: "Prometheus",
        3002: "Grafana", 5173: "React",
    }
    for port, name in ports_to_check.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            in_use = s.connect_ex(("127.0.0.1", port)) == 0
        check(f"  Port {port} ({name})", not in_use,
              "IN USE" if in_use else "FREE")

    # 11. Docker network
    r = subprocess.run(
        ["docker", "network", "inspect", "devforge-network"],
        capture_output=True
    )
    check("devforge-network exists", r.returncode == 0,
          "will be created on 'devforge up'" if r.returncode != 0 else "")

    # 12. Project workspace (if requested)
    if project:
        from engine.workspace import WorkspaceManager
        ws = WorkspaceManager()
        proj_path = Path(f"/workspace/projects/{project}")
        check(f"Project '{project}' directory", proj_path.exists())
        manifest_path = proj_path / "devforge.json"
        check(f"Project '{project}' manifest (devforge.json)", manifest_path.exists())
        compose_path = proj_path / "docker-compose.yml"
        check(f"Project '{project}' compose file", compose_path.exists())

    # Summary
    total = checks_passed + checks_failed
    console.print(f"\n  [bold]Results: {checks_passed}/{total} checks passed[/bold]")
    if checks_failed == 0:
        console.print("  [green]✓ System is healthy and ready.[/green]")
    else:
        console.print(f"  [yellow]⚠ {checks_failed} issue(s) found. Review output above.[/yellow]")


# ──────────────────────────────────────────────────────────────────────────────
# V1 PASSTHROUGH COMMANDS (backward compatible)
# ──────────────────────────────────────────────────────────────────────────────

@cli.command("down")
@click.option("--project", default=None, help="Stop only a specific project's services")
def cmd_down(project):
    """Stop services.

    Without --project stops the full v1 platform.
    """
    if project:
        from engine.workspace import WorkspaceManager
        from engine.service_manager import ServiceManager
        ws = WorkspaceManager()
        proj = ws.resolve_project(project)
        ServiceManager().down_all(proj)
    else:
        console.print("[cyan]Stopping DevForge platform...[/cyan]")
        rc = run_docker_compose(["down"])
        sys.exit(rc)


@cli.command("status")
@click.option("--project", default=None, help="Show status for a specific project")
def cmd_status(project):
    """Show container status."""
    if project:
        from engine.workspace import WorkspaceManager
        from engine.service_manager import ServiceManager
        ws = WorkspaceManager()
        proj = ws.resolve_project(project)
        ServiceManager().status(proj)
    else:
        rc = run_docker_compose(["ps"])
        sys.exit(rc)


@cli.command("backup")
def cmd_backup():
    """Back up all active databases."""
    console.print("[cyan]Executing database backups...[/cyan]")
    result = subprocess.run(["bash", "./scripts/db-backup.sh"])
    sys.exit(result.returncode)


@cli.command("restore")
@click.argument("folder")
def cmd_restore(folder):
    """Restore databases from a backup snapshot folder."""
    console.print(f"[cyan]Restoring from snapshot '{folder}'...[/cyan]")
    result = subprocess.run(["bash", "./scripts/db-restore.sh", folder])
    sys.exit(result.returncode)


@cli.command("seed")
def cmd_seed():
    """Seed active databases with starter data."""
    console.print("[cyan]Seeding databases...[/cyan]")
    result = subprocess.run(["bash", "./scripts/db-seed.sh"])
    sys.exit(result.returncode)


@cli.command("build-apk")
def cmd_build_apk():
    """Compile a Flutter Android APK in release mode."""
    console.print("[cyan]Building Flutter release APK...[/cyan]")
    result = subprocess.run(["docker", "compose", "exec", "flutter",
                             "flutter", "build", "apk", "--release"])
    if result.returncode == 0:
        console.print("[green]✓ APK build complete.[/green]")
    sys.exit(result.returncode)


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
