# ==============================================================================
# DEVFORGE PROJECT GENERATOR
# ==============================================================================
# Drives the interactive project creation wizard.
# Scaffolds framework code, generates compose, .env, devforge.json,
# .devforge/ workspace structure, and optional CI/CD workflow files.
# ==============================================================================

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich import box

from engine.workspace import WorkspaceManager, Project, WORKSPACE_ROOT, PROJECTS_DIR
from engine.composer import ComposeGenerator

console = Console()

# Custom questionary style matching DevForge's cyan palette
STYLE = Style([
    ("qmark",       "fg:#00d4aa bold"),
    ("question",    "fg:#ffffff bold"),
    ("answer",      "fg:#00d4aa bold"),
    ("pointer",     "fg:#00d4aa bold"),
    ("highlighted", "fg:#00d4aa bold"),
    ("selected",    "fg:#00d4aa"),
    ("separator",   "fg:#888888"),
    ("instruction", "fg:#888888"),
])

# ──────────────────────────────────────────────────────────────────────────────
# PROJECT TYPE DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────

PROJECT_TYPES = {
    "Full Stack Application": {
        "description": "Frontend + Backend + Database",
        "defaults": {
            "frontend": "react", "backend": "fastapi",
            "database": ["postgres"], "cache": ["redis"],
        },
    },
    "REST API": {
        "description": "Backend API only",
        "defaults": {
            "frontend": None, "backend": "fastapi",
            "database": ["postgres"], "cache": [],
        },
    },
    "Microservices": {
        "description": "Multiple backend services + message queue",
        "defaults": {
            "frontend": None, "backend": "nestjs",
            "database": ["postgres", "mongodb"],
            "queue": ["rabbitmq"], "cache": ["redis"],
        },
    },
    "AI Agent": {
        "description": "LLM-powered agent with vector memory",
        "defaults": {
            "frontend": None, "backend": "fastapi",
            "ai": "langchain",
            "vector_db": ["qdrant"], "llm": ["ollama"],
        },
    },
    "RAG Application": {
        "description": "Retrieval-Augmented Generation pipeline",
        "defaults": {
            "frontend": "react", "backend": "fastapi",
            "ai": "langchain",
            "vector_db": ["chromadb", "qdrant"], "llm": ["ollama"],
            "database": ["postgres"],
        },
    },
    "Flutter Mobile App": {
        "description": "Cross-platform mobile application",
        "defaults": {
            "mobile": "flutter", "backend": "fastapi",
            "database": ["postgres"],
        },
    },
    "Chrome Extension": {
        "description": "Browser extension with optional backend",
        "defaults": {
            "frontend": "react", "backend": None,
        },
    },
    "CLI Tool": {
        "description": "Command-line application",
        "defaults": {
            "frontend": None, "backend": "fastapi", "database": [],
        },
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# PLUGIN → DEFAULT PORT MAPPING
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_PORTS: dict[str, int] = {
    "react": 5173, "nextjs": 3001,
    "express": 5001, "nestjs": 4000,
    "fastapi": 8081, "flask": 5002,
    "django": 8082, "springboot": 8084,
    "flutter": 0, "ai": 8083,
    "postgres": 5432, "pgadmin": 5050,
    "mongodb": 27017, "mongo-express": 8087,
    "redis": 6379, "redis-commander": 8086,
    "neo4j": 7474, "rabbitmq": 5672,
    "minio": 9000, "ollama": 11434,
    "open-webui": 3000, "chromadb": 8000,
    "qdrant": 6333, "prometheus": 9090,
    "grafana": 3002, "loki": 3100,
    "cadvisor": 8089, "nginx": 80,
    "keycloak": 8085,
}


class ProjectGenerator:
    """Interactive wizard that scaffolds a complete DevForge v2 project."""

    def run(self, project_name: str, interactive: bool = True):
        console.print(Panel(
            f"[bold cyan]Creating project: {project_name}[/bold cyan]\n"
            "[dim]Answer the questions below to configure your stack.[/dim]",
            title="[bold]DevForge New Project[/bold]",
            box=box.ROUNDED,
        ))

        target = PROJECTS_DIR / project_name
        if target.exists():
            console.print(
                f"[red]✗ Project '{project_name}' already exists at projects/{project_name}[/red]"
            )
            raise SystemExit(1)

        if interactive:
            config = self._run_wizard(project_name)
        else:
            config = self._default_config(project_name)

        self._scaffold(config)

    # ──────────────────────────────────────────────────────────────────────────
    # WIZARD
    # ──────────────────────────────────────────────────────────────────────────

    def _run_wizard(self, project_name: str) -> dict:
        # Step 0: Project type
        project_type = questionary.select(
            "Project type:",
            choices=[
                questionary.Choice(
                    title=f"{pt}  [dim]— {PROJECT_TYPES[pt]['description']}[/dim]",
                    value=pt
                )
                for pt in PROJECT_TYPES
            ],
            style=STYLE,
        ).ask()

        if project_type is None:
            raise SystemExit(0)  # User cancelled

        # Step 1: Frontend framework
        frontend = questionary.select(
            "Frontend framework:",
            choices=["React", "Next.js", "None"],
            style=STYLE,
        ).ask()
        frontend = None if frontend == "None" else frontend.lower().replace(".", "")

        # Step 2: Backend framework
        backend = questionary.select(
            "Backend framework:",
            choices=["FastAPI", "Flask", "Django", "Express", "NestJS", "Spring Boot", "None"],
            style=STYLE,
        ).ask()
        backend = None if backend == "None" else backend.lower().replace(" ", "")

        # Step 3: AI framework
        ai_framework = questionary.select(
            "AI / LLM framework:",
            choices=["LangChain", "LlamaIndex", "None"],
            style=STYLE,
        ).ask()
        ai_framework = None if ai_framework == "None" else ai_framework.lower().replace(" ", "")

        # Step 4: Database(s)
        databases = questionary.checkbox(
            "Databases (space to select, enter to confirm):",
            choices=["PostgreSQL", "MongoDB", "Neo4j", "None"],
            style=STYLE,
        ).ask() or []
        databases = [d.lower() for d in databases if d != "None"]
        db_map = {"postgresql": "postgres", "mongodb": "mongodb", "neo4j": "neo4j"}
        databases = [db_map.get(d, d) for d in databases]

        # Step 5: Cache
        cache = questionary.select(
            "Cache layer:",
            choices=["Redis", "None"],
            style=STYLE,
        ).ask()
        cache_plugins = ["redis"] if cache == "Redis" else []

        # Step 6: Message queue
        queue = questionary.select(
            "Message queue:",
            choices=["RabbitMQ", "None"],
            style=STYLE,
        ).ask()
        queue_plugins = ["rabbitmq"] if queue == "RabbitMQ" else []

        # Step 7: Vector database
        vector_dbs = questionary.checkbox(
            "Vector database:",
            choices=["ChromaDB", "Qdrant", "None"],
            style=STYLE,
        ).ask() or []
        vector_plugins = [v.lower() for v in vector_dbs if v != "None"]

        # Step 8: LLM runner
        llm = questionary.select(
            "Local LLM runner:",
            choices=["Ollama (with Open WebUI)", "Ollama only", "None"],
            style=STYLE,
        ).ask()
        llm_plugins = []
        if llm == "Ollama (with Open WebUI)":
            llm_plugins = ["ollama", "open-webui"]
        elif llm == "Ollama only":
            llm_plugins = ["ollama"]

        # Step 9: Object storage
        storage = questionary.select(
            "Object storage:",
            choices=["MinIO", "None"],
            style=STYLE,
        ).ask()
        storage_plugins = ["minio"] if storage == "MinIO" else []

        # Step 10: Reverse proxy
        proxy = questionary.select(
            "Reverse proxy:",
            choices=["Nginx", "None"],
            style=STYLE,
        ).ask()
        proxy_plugins = ["nginx"] if proxy == "Nginx" else []

        # Step 11: Monitoring
        monitoring = questionary.select(
            "Monitoring stack:",
            choices=["Prometheus + Grafana + Loki", "None"],
            style=STYLE,
        ).ask()
        monitoring_plugins = (
            ["prometheus", "grafana", "loki", "cadvisor"]
            if monitoring != "None" else []
        )

        # Step 12: Authentication
        auth = questionary.select(
            "Authentication provider:",
            choices=["Keycloak", "None"],
            style=STYLE,
        ).ask()
        auth_plugins = ["keycloak"] if auth == "Keycloak" else []

        # Step 13: Mobile
        mobile = questionary.select(
            "Mobile application:",
            choices=["Flutter (Android/iOS)", "None"],
            style=STYLE,
        ).ask()
        mobile = "flutter" if mobile != "None" else None

        # Step 14: OCR
        ocr = questionary.confirm(
            "Include OCR support (Tesseract)?", default=False, style=STYLE
        ).ask()

        # Step 15: Speech Recognition
        stt = questionary.confirm(
            "Include Speech Recognition (Whisper)?", default=False, style=STYLE
        ).ask()

        # Step 16: CI/CD
        cicd = questionary.select(
            "CI/CD provider:",
            choices=["GitHub Actions", "GitLab CI", "None"],
            style=STYLE,
        ).ask()
        cicd = None if cicd == "None" else cicd.lower().replace(" ", "-")

        # Step 17: DB admin UIs
        db_uis = []
        if "postgres" in databases:
            if questionary.confirm("Include pgAdmin (PostgreSQL UI)?", default=True).ask():
                db_uis.append("pgadmin")
        if "mongodb" in databases:
            if questionary.confirm("Include Mongo Express (MongoDB UI)?", default=True).ask():
                db_uis.append("mongo-express")
        if "redis" in cache_plugins:
            if questionary.confirm("Include Redis Commander (Redis UI)?", default=False).ask():
                db_uis.append("redis-commander")

        # Assemble full plugin list
        plugins = (
            databases + cache_plugins + queue_plugins + vector_plugins
            + llm_plugins + storage_plugins + proxy_plugins
            + monitoring_plugins + auth_plugins + db_uis
        )
        # Deduplicate preserving order
        seen = set()
        plugins = [p for p in plugins if not (p in seen or seen.add(p))]

        # Build port map from selected plugins + frameworks
        ports = {}
        for item in ([frontend, backend, mobile] + plugins):
            if item and item in DEFAULT_PORTS:
                ports[item] = DEFAULT_PORTS[item]

        return {
            "project_name": project_name,
            "project_type": project_type,
            "frameworks": {
                "frontend": frontend,
                "backend": backend,
                "ai": ai_framework,
                "mobile": mobile,
                "ocr": ocr,
                "stt": stt,
            },
            "plugins": plugins,
            "plugin_versions": {},  # default versions
            "ports": ports,
            "ci_cd": cicd,
        }

    def _default_config(self, project_name: str) -> dict:
        """Non-interactive defaults — FastAPI + React + Postgres + Redis."""
        return {
            "project_name": project_name,
            "project_type": "Full Stack Application",
            "frameworks": {
                "frontend": "react", "backend": "fastapi",
                "ai": None, "mobile": None,
                "ocr": False, "stt": False,
            },
            "plugins": ["postgres", "redis"],
            "plugin_versions": {},
            "ports": {"react": 5173, "fastapi": 8081, "postgres": 5432, "redis": 6379},
            "ci_cd": None,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # SCAFFOLD
    # ──────────────────────────────────────────────────────────────────────────

    def _scaffold(self, config: dict):
        name = config["project_name"]
        project = Project(name)

        console.print(f"\n[cyan]Scaffolding project '[bold]{name}[/bold]'...[/cyan]\n")

        # 1. Create project directory and .devforge/ workspace
        project.path.mkdir(parents=True, exist_ok=True)
        project.ensure_devforge_dir()
        console.print(f"  [green]✓[/green] Created projects/{name}/")
        console.print(f"  [green]✓[/green] Created projects/{name}/.devforge/")

        # 2. Scaffold framework code from templates
        self._scaffold_frameworks(project, config["frameworks"])

        # 3. Generate compose files (dev + testing + production profiles)
        composer = ComposeGenerator()
        composer.write_compose_files(
            project=project,
            plugins=config["plugins"],
            plugin_versions=config["plugin_versions"],
            frameworks=config["frameworks"],
            ports=config["ports"],
        )

        # 4. Generate .env and .env.example
        self._generate_env(project, config["plugins"], config["ports"])

        # 5. Write devforge.json manifest
        manifest = Project.build_manifest(
            name=name,
            project_type=config["project_type"],
            frameworks=config["frameworks"],
            plugins=config["plugins"],
            plugin_versions=config["plugin_versions"],
            ports=config["ports"],
            env_vars={},
            ci_cd=config["ci_cd"],
        )
        project.save_manifest(manifest)
        console.print(f"  [green]✓[/green] Created devforge.json")

        # 6. Generate CI/CD workflow files
        if config["ci_cd"]:
            self._generate_cicd(project, config["ci_cd"], config["frameworks"])

        # 7. Generate root .gitignore for the project
        self._generate_gitignore(project)

        # 8. Set this project as active
        WorkspaceManager().set_active_project(name)

        # Summary
        console.print(Panel(
            f"[bold green]✓ Project '{name}' created successfully![/bold green]\n\n"
            f"[dim]Location:[/dim]  projects/{name}/\n"
            f"[dim]Type:[/dim]      {config['project_type']}\n"
            f"[dim]Plugins:[/dim]   {', '.join(config['plugins']) or 'none'}\n"
            f"[dim]CI/CD:[/dim]     {config['ci_cd'] or 'none'}\n\n"
            "[bold]Next steps:[/bold]\n"
            f"  devforge up --project {name}\n"
            f"  devforge start postgres --project {name}",
            title="[bold]Done[/bold]",
            box=box.ROUNDED,
        ))

    def _scaffold_frameworks(self, project: Project, frameworks: dict):
        """Copy framework templates into the project directory."""
        templates_dir = WORKSPACE_ROOT / "templates"
        framework_map = {
            "frontend": {"react": "react", "nextjs": "nextjs"},
            "backend": {
                "fastapi": "fastapi", "flask": "flask",
                "django": "django", "express": "express",
                "nestjs": "nestjs", "springboot": "springboot",
            },
            "mobile": {"flutter": "flutter"},
            "ai": {"langchain": "ai", "llamaindex": "ai"},
        }
        output_map = {
            "frontend": "frontend",
            "backend": "backend",
            "mobile": "mobile",
            "ai": "ai",
        }

        for fw_type, fw_value in frameworks.items():
            if not fw_value or fw_type in ("ocr", "stt"):
                continue
            template_key = framework_map.get(fw_type, {}).get(fw_value)
            if not template_key:
                continue
            src = templates_dir / template_key
            dst = project.path / output_map.get(fw_type, fw_type)
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                console.print(
                    f"  [green]✓[/green] Scaffolded {fw_type} ({fw_value}) → {dst.relative_to(WORKSPACE_ROOT)}"
                )
            else:
                console.print(
                    f"  [yellow]⚠[/yellow]  Template '{template_key}' not found in templates/ — skipping"
                )

    def _generate_env(self, project: Project, plugins: list[str], ports: dict):
        """Generate .env and .env.example from plugin manifests."""
        import yaml as _yaml

        env_lines = [
            "# ==============================================================================",
            f"# {project.name.upper()} — GENERATED BY DEVFORGE v2",
            "# ==============================================================================",
            "",
            "DEVFORGE_ENV=development",
            f"DEVFORGE_PROJECT={project.name}",
            "",
        ]

        plugins_dir = WORKSPACE_ROOT / "plugins"
        for plugin_name in plugins:
            manifest_path = plugins_dir / plugin_name / "plugin.yaml"
            if not manifest_path.exists():
                continue
            with open(manifest_path) as f:
                manifest = _yaml.safe_load(f)
            env_vars = manifest.get("env", {})
            if env_vars:
                env_lines.append(f"# --- {plugin_name.upper()} ---")
                for key, value in env_vars.items():
                    env_lines.append(f"{key}={value}")
                env_lines.append("")

        # Append port overrides
        env_lines.append("# --- PORTS ---")
        for service, port in ports.items():
            env_lines.append(f"{service.upper().replace('-', '_')}_PORT={port}")

        content = "\n".join(env_lines)
        (project.path / ".env").write_text(content, encoding="utf-8")
        (project.path / ".env.example").write_text(content, encoding="utf-8")
        console.print(f"  [green]✓[/green] Generated .env and .env.example")

    def _generate_cicd(self, project: Project, cicd: str, frameworks: dict):
        """Generate CI/CD workflow files."""
        if cicd == "github-actions":
            wf_dir = project.path / ".github" / "workflows"
            wf_dir.mkdir(parents=True, exist_ok=True)
            content = self._github_actions_template(project.name, frameworks)
            (wf_dir / "ci.yml").write_text(content, encoding="utf-8")
            console.print(f"  [green]✓[/green] Generated .github/workflows/ci.yml")

        elif cicd == "gitlab-ci":
            content = self._gitlab_ci_template(project.name, frameworks)
            (project.path / ".gitlab-ci.yml").write_text(content, encoding="utf-8")
            console.print(f"  [green]✓[/green] Generated .gitlab-ci.yml")

    def _github_actions_template(self, project_name: str, frameworks: dict) -> str:
        backend = frameworks.get("backend", "")
        frontend = frameworks.get("frontend", "")
        lines = [
            f"# GitHub Actions CI — {project_name}",
            "# Generated by DevForge v2",
            "name: CI",
            "",
            "on:",
            "  push:",
            "    branches: [main, develop]",
            "  pull_request:",
            "    branches: [main]",
            "",
            "jobs:",
        ]
        if backend in ("fastapi", "flask", "django"):
            lines += [
                "  backend:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-python@v5",
                "        with:",
                "          python-version: '3.12'",
                "      - run: pip install -r backend/requirements.txt",
                "      - run: pytest backend/tests/ -v",
                "",
            ]
        if frontend in ("react", "nextjs"):
            lines += [
                "  frontend:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-node@v4",
                "        with:",
                "          node-version: '20'",
                "      - run: cd frontend && npm ci && npm run build",
                "",
            ]
        lines += [
            "  compose-validate:",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "      - run: docker compose -f docker-compose.yml config -q",
        ]
        return "\n".join(lines)

    def _gitlab_ci_template(self, project_name: str, frameworks: dict) -> str:
        return (
            f"# GitLab CI — {project_name}\n"
            "# Generated by DevForge v2\n\n"
            "stages:\n  - validate\n  - test\n  - build\n\n"
            "compose-validate:\n"
            "  stage: validate\n"
            "  image: docker:latest\n"
            "  script:\n"
            "    - docker compose -f docker-compose.yml config -q\n"
        )

    def _generate_gitignore(self, project: Project):
        content = (
            "# DevForge Project\n"
            ".env\n"
            ".devforge/cache/\n"
            ".devforge/logs/\n"
            "node_modules/\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".venv/\n"
            "build/\n"
            "dist/\n"
        )
        (project.path / ".gitignore").write_text(content, encoding="utf-8")
        console.print(f"  [green]✓[/green] Generated .gitignore")
