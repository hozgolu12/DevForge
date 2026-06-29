# ==============================================================================
# DEVFORGE PROJECT GENERATOR
# ==============================================================================
# Drives the interactive project creation wizard.
# Scaffolds framework code, generates compose, .env, devforge.json,
# .devforge/ workspace structure, and optional CI/CD workflow files.
# ==============================================================================

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Optional
import yaml

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich import box

from engine.workspace import WorkspaceManager, Project, WORKSPACE_ROOT, PROJECTS_DIR, get_devforge_root
from engine.composer import ComposeGenerator
from engine.detection import DetectionEngine
from engine.validation import Validator

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


DOCKERFILES = {
    "react": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
""",
    "nextjs": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
""",
    "vue": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
""",
    "angular": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 4200
CMD ["npm", "run", "start"]
""",
    "svelte": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
""",
    "fastapi": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""",
    "flask": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
""",
    "django": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
""",
    "nestjs": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 4000
CMD ["npm", "run", "start:dev"]
""",
    "express": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5000
CMD ["npm", "run", "dev"]
""",
    "springboot": """FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
""",
    "aspnetcore": """FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .
EXPOSE 80
ENTRYPOINT ["dotnet", "app.dll"]
""",
    "flutter": """FROM ghcr.io/cirruslabs/flutter:3.22.0
WORKDIR /app
COPY . .
RUN flutter pub get
"""
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
        templates_dir = get_devforge_root() / "templates"
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
        import secrets

        # Load existing env vars if .env exists to preserve them
        existing_env = {}
        env_file = project.path / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            existing_env[k.strip()] = v.strip()
            except Exception:
                pass

        def gen_secret(plugin_name: str) -> str:
            mapping = {
                "postgres": "pg",
                "mongodb": "mongo",
                "chromadb": "chroma",
                "rabbitmq": "rabbit",
            }
            prefix = mapping.get(plugin_name, plugin_name).replace("-", "_")
            return f"devforge_{prefix}_{secrets.token_hex(6)}"

        env_lines = [
            "# ==============================================================================",
            f"# {project.name.upper()} — GENERATED BY DEVFORGE v2",
            "# ==============================================================================",
            "",
            "DEVFORGE_ENV=development",
            f"DEVFORGE_PROJECT={project.name}",
            "",
        ]

        written_keys = {"DEVFORGE_ENV", "DEVFORGE_PROJECT"}

        plugins_dir = get_devforge_root() / "plugins"
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
                    key_upper = key.upper()
                    is_secret = any(x in key_upper for x in ["PASSWORD", "TOKEN", "SECRET", "API_KEY", "AUTH"])
                    
                    if is_secret:
                        existing_val = existing_env.get(key)
                        if existing_val and existing_val != str(value):
                            value = existing_val
                        else:
                            secret_val = gen_secret(plugin_name)
                            if key == "NEO4J_AUTH":
                                value = f"neo4j/{secret_val}"
                            else:
                                value = secret_val
                    else:
                        if key in existing_env:
                            value = existing_env[key]

                    env_lines.append(f"{key}={value}")
                    written_keys.add(key)
                env_lines.append("")

        # Append port overrides
        env_lines.append("# --- PORTS ---")
        for service, port in ports.items():
            port_key = f"{service.upper().replace('-', '_')}_PORT"
            env_lines.append(f"{port_key}={port}")
            written_keys.add(port_key)

        # Preserve custom/other existing env variables
        custom_lines = []
        for key, val in existing_env.items():
            if key not in written_keys:
                custom_lines.append(f"{key}={val}")
        
        if custom_lines:
            env_lines.append("")
            env_lines.append("# --- CUSTOM ENV VARIABLES ---")
            env_lines.extend(custom_lines)

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

    # ──────────────────────────────────────────────────────────────────────────
    # ONBOARDING (EXISTING PROJECTS)
    # ──────────────────────────────────────────────────────────────────────────

    def onboard(self, project_name: str, project_path: Path, interactive: bool = True):
        """
        Onboards an existing project by scanning it, validating configuration,
        asking user about Dockerfiles/docker-compose, and generating DevForge files.
        """
        console.print(Panel(
            f"[bold cyan]Onboarding existing project: {project_name}[/bold cyan]\n"
            f"[dim]Path: {project_path}[/dim]",
            title="[bold]DevForge Existing Project Onboarding[/bold]",
            box=box.ROUNDED,
        ))

        # 1. Run detection
        console.print("[cyan]Scanning project directory...[/cyan]")
        detected = DetectionEngine.detect(project_path, force=True)

        # Print detected tech
        console.print("\n[bold green]✓ Scan Complete.[/bold green] Detected technologies:")
        for category, techs in detected.items():
            if category in ("Recommendations", "Docker", "Package Managers"):
                continue
            if isinstance(techs, dict) and techs:
                console.print(f"  [bold cyan]{category}[/bold cyan]")
                for tech in techs.keys():
                    console.print(f"    ✓ {tech}")
        
        # Package managers
        if "Package Managers" in detected and detected["Package Managers"]:
            console.print("  [bold cyan]Package Managers[/bold cyan]")
            for pm in detected["Package Managers"].keys():
                console.print(f"    ✓ {pm}")

        # Docker files
        if "Docker" in detected and detected["Docker"]:
            console.print("  [bold cyan]Docker[/bold cyan]")
            for df in detected["Docker"].keys():
                console.print(f"    ✓ {df}")

        # Recommendations
        if detected.get("Recommendations"):
            console.print("\n[bold yellow]Recommendations[/bold yellow]")
            for rec in detected["Recommendations"]:
                console.print(f"  - {rec}")
        console.print("")

        # 2. Map detected tech to frameworks and plugins
        frameworks = {
            "frontend": None,
            "backend": None,
            "mobile": None,
            "ai": None,
            "ocr": False,
            "stt": False
        }

        # Map frontend
        for fw in ["react", "nextjs", "vue", "angular", "svelte"]:
            for k in detected.get("Frontend", {}).keys():
                if k.lower().replace(".", "").replace("-", "") == fw:
                    frameworks["frontend"] = fw

        # Map backend
        for fw in ["nestjs", "express", "fastapi", "flask", "django", "springboot", "aspnetcore"]:
            for k in detected.get("Backend", {}).keys():
                normalized = k.lower().replace(" ", "").replace(".", "").replace("-", "")
                if normalized == fw:
                    frameworks["backend"] = fw

        # Map mobile
        for m in ["flutter", "android"]:
            for k in detected.get("Mobile", {}).keys():
                if k.lower() == m:
                    frameworks["mobile"] = m

        # Map AI / OCR / STT
        for k in detected.get("AI", {}).keys():
            normalized = k.lower()
            if normalized in ("langchain", "llamaindex"):
                frameworks["ai"] = normalized
            elif normalized == "tesseract":
                frameworks["ocr"] = True
            elif normalized == "whisper":
                frameworks["stt"] = True

        # Auto-enable plugins
        plugins = []
        tech_plugin_map = {
            "MongoDB": "mongodb",
            "PostgreSQL": "postgres",
            "Neo4j": "neo4j",
            "Redis": "redis",
            "ChromaDB": "chromadb",
            "Qdrant": "qdrant",
            "Ollama": "ollama",
            "RabbitMQ": "rabbitmq",
            "MinIO": "minio",
            "Prometheus": "prometheus",
            "Grafana": "grafana",
            "Loki": "loki",
            "Nginx": "nginx",
        }

        # Scan for DBs/Caches/Vector DBs/AI runners/etc. to enable plugins
        for cat in ("Database", "Cache", "Vector Database", "AI", "Messaging", "Monitoring", "Storage"):
            if cat in detected:
                for tech in detected[cat].keys():
                    plugin = tech_plugin_map.get(tech)
                    if plugin:
                        plugins.append(plugin)
                        # Also auto-add dependencies like open-webui if ollama is detected
                        if plugin == "ollama" and "Ollama" in detected.get("AI", {}):
                            plugins.append("open-webui")
                        # Add database UIs if database is enabled
                        if plugin == "postgres" and interactive:
                            if questionary.confirm("Include pgAdmin (PostgreSQL UI)?", default=True).ask():
                                plugins.append("pgadmin")
                        elif plugin == "postgres" and not interactive:
                            plugins.append("pgadmin")
                        
                        if plugin == "mongodb" and interactive:
                            if questionary.confirm("Include Mongo Express (MongoDB UI)?", default=True).ask():
                                plugins.append("mongo-express")
                        elif plugin == "mongodb" and not interactive:
                            plugins.append("mongo-express")

                        if plugin == "redis" and interactive:
                            if questionary.confirm("Include Redis Commander (Redis UI)?", default=False).ask():
                                plugins.append("redis-commander")

        # Deduplicate preserving order
        seen = set()
        plugins = [p for p in plugins if not (p in seen or seen.add(p))]

        # Build port map
        ports = {}
        for item in ([frameworks["frontend"], frameworks["backend"], frameworks["mobile"]] + plugins):
            if item and item in DEFAULT_PORTS:
                ports[item] = DEFAULT_PORTS[item]

        config = {
            "project_name": project_name,
            "project_type": "Onboarded Existing Project",
            "frameworks": frameworks,
            "plugins": plugins,
            "plugin_versions": {},
            "ports": ports,
            "env_vars": {}
        }

        # 3. Validate
        console.print("[cyan]Validating stack configuration...[/cyan]")
        validation_results = Validator.validate(project_path, config)

        if validation_results["errors"]:
            console.print("[bold red]✗ Validation Failed with errors:[/bold red]")
            for err in validation_results["errors"]:
                console.print(f"  - {err}")
            raise SystemExit(1)

        if validation_results["warnings"]:
            console.print("[bold yellow]⚠ Validation Warnings:[/bold yellow]")
            for warn in validation_results["warnings"]:
                console.print(f"  - {warn}")

        # 4. Handle existing Dockerfiles
        has_dockerfiles = "Dockerfile" in detected.get("Docker", {})
        dockerfile_action = "Replace"
        if has_dockerfiles:
            if interactive:
                dockerfile_action = questionary.select(
                    "Existing Dockerfile(s) detected. How would you like to handle them?",
                    choices=["Reuse", "Improve", "Replace"],
                    style=STYLE,
                ).ask()
                if dockerfile_action is None:
                    raise SystemExit(0)
            else:
                dockerfile_action = "Reuse"  # Safe default

        # 5. Handle existing docker-compose
        has_compose = "docker-compose.yml" in detected.get("Docker", {})
        compose_action = "Replace"
        if has_compose:
            if interactive:
                compose_action = questionary.select(
                    "Existing docker-compose.yml detected. How would you like to handle it?",
                    choices=["Reuse", "Merge", "Replace"],
                    style=STYLE,
                ).ask()
                if compose_action is None:
                    raise SystemExit(0)
            else:
                compose_action = "Merge"  # Safe default

        # 6. Create Project workspace structure
        project = Project(project_name, path=project_path)
        project.ensure_devforge_dir()

        # 7. Generate Dockerfiles only if missing or Replace selected
        self._generate_or_improve_dockerfiles(project_path, frameworks, dockerfile_action)

        # 8. Generate docker-compose.yml based on compose action
        self._generate_or_merge_compose(project, config, compose_action)

        # 9. Generate .env and .env.example
        self._generate_env(project, config["plugins"], config["ports"])

        # 10. Generate DevForge files: devforge.json, services.yaml, workspace.json, README.devforge.md
        self._generate_devforge_files(project, config, project_path)

        # 11. Generate gitignore
        self._generate_gitignore(project)

        # Set active project
        WorkspaceManager().set_active_project(project_name)

        # Summary
        console.print(Panel(
            f"[bold green]✓ Project '{project_name}' onboarded successfully![/bold green]\n\n"
            f"[dim]Location:[/dim]  {project_path}\n"
            f"[dim]Plugins:[/dim]   {', '.join(config['plugins']) or 'none'}\n"
            f"[dim]Dockerfiles:[/dim] {dockerfile_action}\n"
            f"[dim]Compose:[/dim]     {compose_action}\n\n"
            "[bold]Next steps:[/bold]\n"
            f"  devforge up --project {project_name}\n"
            f"  devforge logs postgres --project {project_name}",
            title="[bold]Onboarding Summary[/bold]",
            box=box.ROUNDED,
        ))

    def _generate_or_improve_dockerfiles(self, project_path: Path, frameworks: dict, action: str):
        # Identify where to generate Dockerfile(s)
        targets = []
        if frameworks.get("frontend"):
            fw = frameworks["frontend"]
            path = project_path / "frontend"
            if not path.exists():
                path = project_path
            targets.append((path, fw))
        if frameworks.get("backend"):
            fw = frameworks["backend"]
            path = project_path / "backend"
            if not path.exists():
                path = project_path
            targets.append((path, fw))

        for target_dir, fw in targets:
            dockerfile_path = target_dir / "Dockerfile"
            if action == "Replace" or not dockerfile_path.exists():
                df_content = DOCKERFILES.get(fw)
                if df_content:
                    dockerfile_path.write_text(df_content, encoding="utf-8")
                    console.print(f"  [green]✓[/green] Generated Dockerfile for {fw} at {dockerfile_path.relative_to(project_path)}")
            elif action == "Improve":
                self._improve_dockerfile_file(dockerfile_path)

    def _improve_dockerfile_file(self, filepath: Path):
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            improvements = []
            
            if "user" not in content.lower():
                improvements.append(
                    "\n# DEVFORGE v2 SECURITY HARDENING: Consider running as non-root user\n"
                    "# Example for Alpine Node:\n"
                    "# USER node\n"
                    "# Example for Debian/Ubuntu:\n"
                    "# RUN groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup -m appuser\n"
                    "# USER appuser\n"
                )

            if "apt-get install" in content and "rm -rf /var/lib/apt/lists" not in content:
                improvements.append(
                    "\n# DEVFORGE v2 PERFORMANCE OPTIMIZATION: Clean up package manager caches\n"
                    "# Example: RUN apt-get update && apt-get install -y --no-install-recommends <pkgs> && rm -rf /var/lib/apt/lists/*\n"
                )

            if improvements:
                header = (
                    "# ==============================================================================\n"
                    "# DEVFORGE v2 AUTOMATED DOCKERFILE IMPROVEMENTS\n"
                    "# ==============================================================================\n"
                )
                improved_content = header + content + "".join(improvements)
                filepath.write_text(improved_content, encoding="utf-8")
                console.print(f"  [green]✓[/green] Added improvements to {filepath.name}")
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not improve Dockerfile '{filepath}': {e}")

    def _generate_or_merge_compose(self, project: Project, config: dict, action: str):
        composer = ComposeGenerator()
        
        rendered_content = composer.generate(
            project=project,
            plugins=config["plugins"],
            plugin_versions=config["plugin_versions"],
            frameworks=config["frameworks"],
            ports=config["ports"],
            profile="dev"
        )

        compose_file = project.compose_file

        if action == "Replace" or not compose_file.exists():
            compose_file.write_text(rendered_content, encoding="utf-8")
            console.print(f"  [green]✓[/green] Generated docker-compose.yml")
        elif action == "Merge":
            try:
                with open(compose_file, "r", encoding="utf-8") as f:
                    existing_data = yaml.safe_load(f) or {}
                
                generated_data = yaml.safe_load(rendered_content) or {}
                
                if not isinstance(existing_data, dict):
                    existing_data = {}
                
                merged_data = dict(existing_data)
                merged_data.setdefault("services", {}).update(generated_data.get("services", {}))
                merged_data.setdefault("volumes", {}).update(generated_data.get("volumes", {}))
                merged_data.setdefault("networks", {}).update(generated_data.get("networks", {}))
                
                # Normalize merged compose file to use CustomAnchorDumper and keep anchors
                from engine.composer import CustomAnchorDumper, DEFAULT_LOGGING, SECURITY_DEFAULTS
                
                # Ensure they are defined at the top level of merged data
                has_logging = "x-logging" in merged_data or any(
                    isinstance(svc, dict) and "logging" in svc
                    for svc in merged_data.get("services", {}).values()
                )
                
                ordered_merged = {}
                if has_logging:
                    ordered_merged["x-logging"] = DEFAULT_LOGGING
                ordered_merged["x-security-defaults"] = SECURITY_DEFAULTS
                
                for k, v in merged_data.items():
                    if k not in ["x-logging", "x-security-defaults"]:
                        ordered_merged[k] = v
                        
                for svc_name, svc_cfg in ordered_merged.get("services", {}).items():
                    if isinstance(svc_cfg, dict):
                        if svc_cfg.get("logging") == DEFAULT_LOGGING:
                            svc_cfg["logging"] = ordered_merged["x-logging"]
                            
                with open(compose_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        ordered_merged,
                        f,
                        Dumper=CustomAnchorDumper,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                    )
                
                console.print(f"  [green]✓[/green] Merged services into docker-compose.yml")
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed to merge compose: {e}. Overwriting as fallback.")
                compose_file.write_text(rendered_content, encoding="utf-8")

        composer.write_compose_files(
            project=project,
            plugins=config["plugins"],
            plugin_versions=config["plugin_versions"],
            frameworks=config["frameworks"],
            ports=config["ports"],
            skip_dev=(action in ["Reuse", "Merge"]),
        )

    def _generate_devforge_files(self, project: Project, config: dict, project_path: Path):
        manifest = Project.build_manifest(
            name=config["project_name"],
            project_type=config["project_type"],
            frameworks=config["frameworks"],
            plugins=config["plugins"],
            plugin_versions=config["plugin_versions"],
            ports=config["ports"],
            env_vars={},
            ci_cd=None,
        )
        project.save_manifest(manifest)
        console.print(f"  [green]✓[/green] Updated devforge.json")

        services_list = []
        for p in config["plugins"]:
            services_list.append({
                "name": p,
                "port": config["ports"].get(p, 0),
                "status": "enabled"
            })
        services_data = {"services": services_list}
        services_yaml_path = project.devforge_dir / "services.yaml"
        with open(services_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(services_data, f, default_flow_style=False)
        console.print(f"  [green]✓[/green] Created .devforge/services.yaml")

        from datetime import datetime, timezone
        workspace_data = {
            "project_name": config["project_name"],
            "path": str(project_path.resolve()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active_profile": "dev"
        }
        workspace_json_path = project.devforge_dir / "workspace.json"
        with open(workspace_json_path, "w", encoding="utf-8") as f:
            json.dump(workspace_data, f, indent=2)
        console.print(f"  [green]✓[/green] Created .devforge/workspace.json")

        readme_content = f"""# DevForge Project: {config['project_name']}

This directory is managed as a DevForge project.

## Project Details
- **Project Name**: `{config['project_name']}`
- **Project Path**: `{project_path}`
- **Enabled Plugins**: {', '.join(config['plugins']) or 'None'}
- **Detected Frameworks**:
  - Frontend: `{config['frameworks']['frontend'] or 'None'}`
  - Backend: `{config['frameworks']['backend'] or 'None'}`
  - Mobile: `{config['frameworks']['mobile'] or 'None'}`

## Command Guide

Start all DevForge infrastructure services:
```bash
devforge up
```

Stop all services:
```bash
devforge down
```

Check status of containers:
```bash
devforge status
```

Open a shell inside a service (e.g. postgres):
```bash
devforge shell postgres
```
"""
        (project.path / "README.devforge.md").write_text(readme_content, encoding="utf-8")
        console.print(f"  [green]✓[/green] Created README.devforge.md")
