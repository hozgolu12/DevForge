# DevForge

[![Docker Compose Validation](https://github.com/hozgolu12/DevForge/actions/workflows/compose-validate.yml/badge.svg)](https://github.com/hozgolu12/DevForge/actions/workflows/compose-validate.yml)
[![Docker Build Validation](https://github.com/hozgolu12/DevForge/actions/workflows/docker-build-validate.yml/badge.svg)](https://github.com/hozgolu12/DevForge/actions/workflows/docker-build-validate.yml)
[![Security Scan](https://github.com/hozgolu12/DevForge/actions/workflows/security-scan.yml/badge.svg)](https://github.com/hozgolu12/DevForge/actions/workflows/security-scan.yml)

> **One Docker Command. Unlimited Development.**

DevForge is a production-grade, modular, containerized developer platform. It runs all language runtimes, database clusters, AI tools, and monitoring stacks locally inside Docker. The only requirements on the host machine are **Docker Desktop**, **Git**, and **VS Code**. No languages, runtimes, or databases need to be installed on your operating system.

---

## What's New in v2

DevForge v2 evolves from a static "everything on" platform into a **modular, project-aware developer platform** — comparable to tools like `create-next-app`, Yeoman, Cookiecutter, and Nx — while remaining 100% Docker-native.

| Feature | v1 | v2 |
|---|---|---|
| Project creation | `devforge create <template>` | `devforge new <name>` — interactive wizard |
| Project onboarding | ❌ | ✅ `devforge init` & `devforge import <path>` |
| Codebase detection | ❌ | ✅ `devforge detect` |
| Compose strategy | Single monolithic file | Project-specific, only selected services |
| Plugin system | ❌ | ✅ `devforge plugin install postgres@16` |
| Template versioning | ❌ | ✅ `react@18`, `nestjs@11`, `fastapi@0.115` |
| Service profiles | ❌ | ✅ `--profile dev/testing/production` |
| Multi-project | ❌ | ✅ `devforge use socialcross` |
| CLI engine | Shell scripts | Containerized Python engine (auto-built) |
| Workspace manifest | ❌ | ✅ `devforge.json` per project |
| v1 compatibility | — | ✅ All v1 commands unchanged |
| AI Plugin Generation | ❌ | ✅ Dynamic AI plugin generation for unknown tech (Supabase, Milvus, etc.) |

---

## Overview

DevForge isolates all development tools into secure Docker containers that work together out-of-the-box. Developers can build applications in React, Node.js, Python, Java, Flutter, or AI/ML ecosystems (Ollama, LangChain, ChromaDB, Qdrant) without package manager conflicts, system path corruption, or version collisions.

### Platform Capabilities

| Pillar | What's included |
|---|---|
| 🧱 **Language Runtimes** | Node.js, Python, Java (JDK 21), Flutter / Android SDK |
| 🗄️ **Database Cluster** | PostgreSQL, MongoDB, Redis, Neo4j + admin UIs |
| 🤖 **AI / ML Ecosystem** | Ollama, Open WebUI, ChromaDB, Qdrant, LangChain, Whisper, OCR |
| 📦 **Infrastructure** | Nginx, RabbitMQ, MinIO, Keycloak |
| 📊 **Observability** | Prometheus, Grafana, Loki, cAdvisor |
| 🔧 **CLI Engine** | Containerized v2 CLI + full v1 backward compatibility |

---

## Architecture

DevForge v2 uses a two-layer architecture:

**Layer 1 — CLI Engine (ephemeral)**
The `devforge-cli:2.0` Docker image runs as an ephemeral container for each command, mounts the workspace, generates files, then self-destructs via `--rm`. No background process remains.

**Layer 2 — Project Services (persistent)**
Each generated project gets its own `docker-compose.yml` containing only the services it selected. Services run persistently until explicitly stopped.

```
Host Machine  ──►  devforge.ps1 / devforge (thin wrapper)
                          │
                          ▼  docker run --rm -it
               devforge-cli:2.0 (ephemeral)
               ├── reads:  plugins/, registry/, templates/
               └── writes: projects/<name>/
                                ├── devforge.json
                                ├── docker-compose.yml  (only selected services)
                                ├── .env
                                ├── .devforge/
                                │   ├── generated/  (profile variants)
                                │   ├── cache/
                                │   └── logs/
                                └── frontend/, backend/, mobile/
```

For detailed design blueprints, see the [Architecture Guide](docs/architecture.md).

---

## Repository Structure

```text
DevForge/
├── .devcontainer/                  # VS Code Dev Container configurations
├── .github/                        # CI/CD GitHub Actions workflows
│   └── workflows/
│       ├── compose-validate.yml
│       ├── docker-build-validate.yml
│       ├── lint-validation.yml
│       ├── sbom-generation.yml
│       └── security-scan.yml
│
├── docker/                         # Custom Dockerfiles and service configs
│   ├── cli/                        # NEW v2: devforge-cli image
│   │   └── Dockerfile
│   ├── base/                       # Hardened base image
│   ├── nginx/                      # Nginx reverse proxy
│   ├── postgres/                   # PostgreSQL
│   ├── mongodb/                    # MongoDB
│   ├── redis/                      # Redis
│   ├── neo4j/                      # Neo4j graph database
│   ├── ollama/                     # Ollama LLM runner
│   ├── open-webui/                 # Open WebUI chat interface
│   ├── chromadb/                   # ChromaDB vector database
│   ├── qdrant/                     # Qdrant vector search
│   ├── grafana/                    # Grafana dashboards
│   ├── prometheus/                 # Prometheus metrics
│   ├── loki/                       # Loki log aggregation
│   ├── python/                     # Python runtime image
│   ├── node/                       # Node.js runtime image
│   ├── java/                       # JDK 21 + Maven image
│   ├── flutter/                    # Flutter + Android SDK image
│   └── ai/                         # AI/ML Python environment
│
├── engine/                         # NEW v2: CLI Python engine (runs inside container)
│   ├── __init__.py
│   ├── cli.py                      # Main Click CLI entry point
│   ├── generator.py                # Interactive project wizard (devforge new)
│   ├── composer.py                 # Compose generation from plugin fragments
│   ├── template_engine.py          # Template management + versioning
│   ├── plugin_manager.py           # Plugin lifecycle + versioning
│   ├── workspace.py                # devforge.json + .devforge/ management
│   └── service_manager.py          # Per-service start/stop/logs/shell
│
├── plugins/                        # NEW v2: Plugin definitions (19 plugins)
│   ├── postgres/                   # plugin.yaml + compose.fragment.yaml
│   ├── pgadmin/
│   ├── mongodb/
│   ├── mongo-express/
│   ├── redis/
│   ├── redis-commander/
│   ├── neo4j/
│   ├── rabbitmq/
│   ├── minio/
│   ├── ollama/
│   ├── open-webui/
│   ├── chromadb/
│   ├── qdrant/
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   ├── cadvisor/
│   ├── nginx/
│   └── keycloak/
│
├── registry/                       # NEW v2: Offline plugin/template index
│   ├── plugins.yaml                # Versioned plugin registry
│   └── templates.yaml              # Versioned template registry
│
├── templates/                      # Code starter templates
│   ├── react/                      # React + Vite + TypeScript + Tailwind
│   ├── nextjs/                     # Next.js App Router
│   ├── express/                    # Express.js REST API
│   ├── nestjs/                     # NestJS framework
│   ├── fastapi/                    # FastAPI + async routers
│   ├── flask/                      # Flask microservice
│   ├── django/                     # Django with core app
│   ├── springboot/                 # Spring Boot 3 + JDK 21
│   ├── flutter/                    # Flutter mobile app
│   ├── ai/                         # AI/ML agent (LangChain, ChromaDB, Whisper)
│   └── shared/                     # Shared ESLint / Prettier / tsconfig
│
├── projects/                       # Developer workspaces (generated projects live here)
├── scripts/                        # Platform shell automation (v1)
│   ├── backup.sh / restore.sh      # Database backup & recovery
│   ├── db-backup.sh / db-restore.sh
│   ├── db-seed.sh                  # Database seeding
│   ├── doctor.sh                   # System diagnostics
│   ├── lint.sh / format.sh
│   ├── install-deps.sh
│   └── create-*.sh                 # Per-template scaffold scripts (v1)
│
├── docs/                           # Technical documentation
│   ├── architecture.md
│   ├── cli_reference.md            # UPDATED: full v1 + v2 command reference
│   ├── database_platform.md
│   ├── node_platform.md
│   ├── flutter_workflow.md
│   └── observability_platform.md
│
├── docker-compose.yml              # v1 full-platform compose (unchanged)
├── docker-compose.override.yml     # Local developer overrides
├── requirements.engine.txt         # NEW v2: CLI engine Python deps (container-only)
├── devforge                        # Bash CLI wrapper (Linux/macOS/Git Bash)
├── devforge.ps1                    # PowerShell CLI wrapper (Windows)
├── Makefile                        # Shortcut commands
└── .env / .env.example             # Platform configuration
```

---

## Installation

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v25.0+ recommended)
* [Git](https://git-scm.com/)
* [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

That's it. No Python, Node.js, Java, Flutter, or any other runtime required on your host.

### Clone and Setup
```bash
git clone https://github.com/hozgolu12/DevForge.git
cd DevForge
cp .env.example .env
```

### Run Diagnostics
```powershell
# Windows
.\devforge.ps1 doctor

# Linux / macOS / Git Bash
./devforge doctor
```

> [!TIP]
> **Global CLI Shortcut:** To run `devforge` globally from any folder:
> - **PowerShell (Windows):** Run `Add-Content -Path $PROFILE -Value 'function devforge { & "C:\path\to\DevForge\devforge.ps1" $args }'` (replace with your actual folder path) to register it permanently.
> - **Bash/Zsh (Linux/macOS):** Add `alias devforge="/path/to/DevForge/devforge"` to your `~/.bashrc` or `~/.zshrc` file.

---

## Quick Start

### Option A — v2: Create a New Project (Recommended)

The interactive wizard generates a project with only the services you need:

```powershell
# Windows
.\devforge.ps1 new socialcross

# Linux / macOS
./devforge new socialcross
```

The wizard asks:

| Step | Question |
|---|---|
| 1 | Project type (Full Stack / REST API / Microservices / AI Agent / RAG / Flutter / CLI) |
| 2 | Frontend framework (React / Next.js / None) |
| 3 | Backend framework (FastAPI / Django / NestJS / Spring Boot / ...) |
| 4 | AI framework (LangChain / LlamaIndex / None) |
| 5 | Database (PostgreSQL / MongoDB / Neo4j) |
| 6 | Cache (Redis) |
| 7 | Message queue (RabbitMQ) |
| 8 | Vector database (ChromaDB / Qdrant) |
| 9 | LLM runner (Ollama) |
| 10 | Object storage (MinIO) |
| 11 | Reverse proxy (Nginx) |
| 12 | Monitoring (Prometheus + Grafana + Loki) |
| 13 | Authentication (Keycloak) |
| 14 | Mobile (Flutter) |
| 15 | OCR / Speech Recognition |
| 16 | CI/CD provider (GitHub Actions / GitLab CI) |

Then start only your project's services:

```powershell
.\devforge.ps1 up --project socialcross
.\devforge.ps1 up --project socialcross --profile production
```

---

### Option B — v1: Start the Full Platform

Start all services at once (original behaviour, unchanged):

```powershell
.\devforge.ps1 up
```

Once running, open your browser:

| Dashboard | URL |
|---|---|
| Nginx Developer Panel | http://localhost |
| Local AI (Open WebUI) | http://localhost:3000 |
| Neo4j Browser | http://localhost:7474 |
| Qdrant Console | http://localhost:6333/dashboard |
| pgAdmin | http://localhost:5050 |
| Mongo Express | http://localhost:8087 |
| Redis Commander | http://localhost:8086 |
| Grafana | http://localhost:3002 |
| Prometheus | http://localhost:9090 |

---

### Option C — v2: Onboard an Existing Project

You can onboard an existing project into DevForge in two ways:

#### 1. Initialize In-Place (Keep files where they are)
If you want to keep your project files in their current folder and run them directly from there:
```powershell
cd /path/to/your/existing/project
# Run the DevForge init command pointing to your DevForge script path
D:\Coding\DevForge\devforge.ps1 init
```

#### 2. Import into Workspace (Copy files to projects/)
If you want to copy your existing project into DevForge's managed `projects/` directory:
```powershell
cd D:\Coding\DevForge
# Import the project into the DevForge projects/ directory
.\devforge.ps1 import D:\Projects\SocialCross
```

Either method automatically runs the **Detection Engine** to identify frameworks and packages, validates ports/dependencies, and prompts you to safely merge or reuse any existing Docker/Compose configurations.

---

## CLI Commands

### v2 Commands (New)

```powershell
# Project wizard & onboarding
devforge new <project-name>
devforge init
devforge import <path>
devforge detect

# Plugin management (with versioning)
devforge plugin list
devforge plugin install postgres
devforge plugin install postgres@16
devforge plugin remove mongodb

# Template management (with versioning)
devforge template list
devforge template install react@18
devforge generate fastapi auth-service

# Per-service control
devforge start mongodb
devforge stop redis
devforge restart fastapi
devforge logs fastapi --tail 50
devforge shell postgres

# Project profiles
devforge up --project socialcross --profile dev
devforge up --project socialcross --profile production

# Multi-project management
devforge use socialcross
devforge start mongodb --project socialcross

# CLI self-update (rebuilds the CLI image)
devforge update

# Enhanced diagnostics
devforge doctor
devforge doctor --project socialcross
```

### v1 Commands (All Unchanged)

```powershell
devforge up              # Start all platform services
devforge down            # Stop all platform services
devforge restart [svc]   # Restart one or all services
devforge status          # Show container status
devforge logs <svc>      # Tail logs
devforge shell <svc>     # Open shell in container
devforge create <t> <n>  # Scaffold from v1 template
devforge doctor          # System diagnostics
devforge backup          # Backup all databases
devforge restore <path>  # Restore from snapshot
devforge seed            # Seed databases
devforge build apk       # Compile Flutter release APK (alias: build-apk)
```

### Makefile Shortcuts

| Target | Description |
|---|---|
| `make build-cli` | **NEW** Build `devforge-cli:2.0` image |
| `make rebuild-cli` | **NEW** Rebuild CLI image from scratch |
| `make up` | Start all v1 platform services |
| `make down` | Stop all services |
| `make build` | Build all custom Docker images |
| `make rebuild` | Rebuild all images (no cache) |
| `make clean` | Stop + remove all volumes |
| `make logs` | Tail all service logs |
| `make status` | Show container status |
| `make doctor` | Run diagnostics |
| `make backup` | Backup all databases |
| `make restore` | Restore databases |
| `make shell SERVICE=postgres` | Open shell in container |
| `make create-react name=my-app` | Create React project (v1) |
| `make create-fastapi name=my-api` | Create FastAPI project (v1) |
| `make flutter-build-apk` | Build Flutter APK |

---

## Plugin System

Plugins are self-contained service definitions under `plugins/`. Each has a manifest (`plugin.yaml`) and a Docker Compose snippet (`compose.fragment.yaml`).

### Available Plugins

| Plugin | Category | Versions |
|---|---|---|
| `postgres` | database | 15, **16**, 17 |
| `mongodb` | database | 6, **7**, 8 |
| `neo4j` | database | **5** |
| `pgadmin` | database-ui | 8.4 |
| `mongo-express` | database-ui | 1.0.2 |
| `redis` | cache | **7**, 8 |
| `redis-commander` | cache-ui | latest |
| `rabbitmq` | messaging | 3.12, **3.13** |
| `minio` | storage | latest |
| `ollama` | ai | latest |
| `open-webui` | ai-ui | latest |
| `chromadb` | vector-db | 0.4, **0.5** |
| `qdrant` | vector-db | 1.8, **1.9** |
| `prometheus` | monitoring | **2.51** |
| `grafana` | monitoring | **10.4** |
| `loki` | monitoring | 2.9, **3.0** |
| `cadvisor` | monitoring | **0.49** |
| `nginx` | proxy | 1.24, **1.25** |
| `keycloak` | auth | 23, **24** |

*Bold = default version*

---

## Workspace Manifest

Every v2 project contains a `devforge.json` manifest:

```json
{
  "name": "socialcross",
  "version": "1.0.0",
  "devforge_version": "2.0.0",
  "created_at": "2026-06-29T13:00:00Z",
  "project_type": "Full Stack Application",
  "frameworks": {
    "frontend": "react",
    "backend": "fastapi",
    "ai": "langchain",
    "mobile": null
  },
  "plugins": ["postgres", "redis", "ollama", "qdrant", "nginx"],
  "plugin_versions": { "postgres": "16" },
  "ports": {
    "react": 5173,
    "fastapi": 8081,
    "postgres": 5432,
    "redis": 6379
  },
  "ci_cd": "github-actions",
  "active_profile": "dev"
}
```

DevForge uses this manifest to manage all project operations — no manual compose editing required.

---

## Service Profiles

Each generated project includes three profile-specific compose files:

| Profile | File | Use case |
|---|---|---|
| `dev` (default) | `docker-compose.yml` | Hot-reload, debug logging, relaxed security |
| `testing` | `.devforge/generated/docker-compose.testing.yml` | CI pipelines, test isolation |
| `production` | `.devforge/generated/docker-compose.production.yml` | `restart: always`, minimal logging, strict security |

```powershell
.\devforge.ps1 up --project socialcross --profile dev
.\devforge.ps1 up --project socialcross --profile production
```

---

## Networking

All containers communicate on an internal Docker bridge — no host ports needed for inter-service calls:

```
# v1 platform network
devforge-network

# v2 project network (isolated per project)
devforge-<project-name>-network
```

Internal connection strings (use inside containers):

| Service | URI |
|---|---|
| PostgreSQL | `postgresql://postgres_admin:password@postgres:5432/devforge_db` |
| MongoDB | `mongodb://mongo_admin:password@mongodb:27017` |
| Redis | `redis://:password@redis:6379` |
| ChromaDB | `http://chromadb:8000` |
| Qdrant | `http://qdrant:6333` |
| Ollama | `http://ollama:11434` |
| RabbitMQ | `amqp://admin:admin@rabbitmq:5672` |

---

## Persistent Volumes

Named Docker volumes prevent data loss across restarts:

| Volume | Data |
|---|---|
| `pgdata` | PostgreSQL databases |
| `mongodata` | MongoDB files |
| `redisdata` | Redis snapshots |
| `neo4jdata` | Neo4j graph data |
| `qdrantdata` | Qdrant vector indexes |
| `chromadata` | ChromaDB embeddings |
| `ollamadata` | Downloaded LLM models |
| `grafanadata` | Grafana dashboards |
| `miniodata` | MinIO object storage |
| `webuidata` | Open WebUI sessions |

---

## Environment Variables

All parameters are configured in `.env`. Copy from `.env.example` before first run:

```bash
cp .env.example .env
```

Key groups:

| Group | Variables |
|---|---|
| Ingress | `NGINX_PORT`, `NGINX_SECURE_PORT` |
| PostgreSQL | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` |
| MongoDB | `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, `MONGO_PORT` |
| Redis | `REDIS_PASSWORD`, `REDIS_PORT` |
| Neo4j | `NEO4J_AUTH`, `NEO4J_PORT_HTTP`, `NEO4J_PORT_BOLT` |
| AI | `QDRANT_API_KEY`, `CHROMA_AUTH_TOKEN`, `OLLAMA_MODELS_PATH`, `WEBUI_SECRET_KEY` |
| Monitoring | `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `PROMETHEUS_PORT` |
| Storage | `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` |
| Messaging | `RABBITMQ_USER`, `RABBITMQ_PASSWORD` |
| Auth | `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD` |

---

## AI Plugin Generation System

DevForge features a production-grade **AI Plugin Generation System** designed to dynamically detect unknown technologies (e.g. Supabase, Milvus, Temporal, Convex, Appwrite, etc.) in your projects, enrich their metadata, query an AI model to generate a custom plugin, validate it, render the configuration files, and install it.

All AI logic and SDKs run strictly **inside** the containerized `devforge-cli:2.0` environment.

### Workflow Pipeline

```
Project ──► Scan (devforge detect) ──► Unknown Technology?
                                              │
                                              ▼ (Yes)
                                    Enrich (Metadata & Knowledge)
                                              │
                                              ▼
                                    Check Plugin Cache (generated/) ──► Found?
                                              │                           │
                                              ▼ (No)                      ▼ (Yes)
                                    AI Plugin Generator ──────────► Reuse Plugin
                                              │
                                              ▼
                                    Plugin Validator (Schema, Ports, Compose)
                                              │
                                              ▼
                                    Plugin Renderer (Jinja Templates)
                                              │
                                              ▼
                                    Plugin Registry (plugins.yaml)
                                              │
                                              ▼
                                    Install Plugin (Y/N/V)
```

### Configuration (`devforge-ai.yaml`)

Configuration file is loaded from `/workspace/devforge-ai.yaml` or `/devforge/devforge-ai.yaml`. It manages active model settings, caching policies, timeouts, and fallbacks.

```yaml
provider: groq
model: llama-3.1-8b-instant
temperature: 0.2
max_tokens: 4096

providers:
  groq:
    api_key: ${GROQ_API_KEY}
    base_url: https://api.groq.com/openai/v1
    models:
      - llama-3.1-8b-instant
      - llama-3.3-70b-versatile
  gemini:
    api_key: ${GEMINI_API_KEY}
    models:
      - gemini-2.0-flash-lite
  ollama:
    base_url: http://ollama:11434
    models:
      - qwen3:8b
```

### CLI Command Reference

Scan the active workspace and generate/install plugins dynamically:
```powershell
# Default interactive mode
.\devforge.ps1 detect

# Non-interactive mode (auto-accepts and installs)
.\devforge.ps1 detect --yes

# Override the AI Provider and Model
.\devforge.ps1 detect --provider gemini --model gemini-2.0-flash-lite
```

Pass the required provider keys via shell environment variables to make them available in the CLI container:
```powershell
$env:GROQ_API_KEY="your-groq-key"
$env:GEMINI_API_KEY="your-gemini-key"
```

---

## Troubleshooting

### Port Collision
**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated.`
**Fix**: Edit `.env` and change `NGINX_PORT=80` to a free port (e.g., `8080`). Run `make up` again.

### Database Credentials Refused
**Error**: `FATAL: password authentication failed for user "postgres_admin"`
**Fix**: If you changed passwords in `.env` after the volume was initialized, the old credentials are stored in the volume. Reset with `make clean` (**destructive** — deletes all data) and restart.

### CLI Image Not Found
**Error**: `Unable to find image 'devforge-cli:2.0'`
**Fix**: This should auto-build on first use. If it fails, build manually:
```powershell
make build-cli
```

### v2 Wizard Hangs / Not Interactive
**Cause**: Running inside a non-TTY shell (e.g., CI pipeline without `-it`).
**Fix**: Add `--no-interactive` flag:
```powershell
.\devforge.ps1 new my-project --no-interactive
```

### GPU Not Detected by Ollama
**Fix**: Open `docker-compose.override.yml`, find the `ollama` section, and uncomment the `deploy.resources.reservations` block to enable Nvidia GPU pass-through.

---

## FAQ

#### Does v2 break my existing v1 setup?
No. All v1 commands (`up`, `down`, `create`, `doctor`, `backup`, etc.) work exactly as before. The existing `docker-compose.yml` is untouched.

#### Where does my source code live?
- **v1**: `projects/` directory (mounted into containers via the root compose)
- **v2**: `projects/<project-name>/` (generated per project with its own compose)

#### Can I use GPU with Ollama?
Yes. Uncomment the `deploy.resources.reservations` section in `docker-compose.override.yml` (v1) or in the generated project's compose (v2).

#### How do I add a new service to an existing v2 project?
```powershell
.\devforge.ps1 plugin install rabbitmq --project socialcross
```
The compose file regenerates automatically.

#### How do I update the DevForge CLI?
```powershell
.\devforge.ps1 update
```

---

## Contribution Guide

1. Create a branch from `main`.
2. Run `make lint` and `make doctor` before committing.
3. Format shell scripts with `make format`.
4. Open a Pull Request with a clear description of your changes.

---

## Roadmap

* [x] Add Node/React project templates
* [x] Add Python/FastAPI backend blueprints
* [x] Add AI/ML development ecosystem (PyTorch, TensorFlow, LangChain, OCR, Whisper)
* [x] Add Java/Spring Boot development environment (JDK 21, Maven, Gradle)
* [x] Add Flutter/Android mobile application environment
* [x] Deploy database admin dashboards (pgAdmin, Mongo Express, Redis Commander)
* [x] Integrate observability stack (Prometheus, Grafana, Loki, cAdvisor)
* [x] Add middleware (MinIO, RabbitMQ)
* [x] Develop unified CLI (devforge.ps1 and devforge)
* [x] Harden production deployments (Trivy, SBOM, Docker build validation)
* [x] **v2: Containerized CLI engine (no host Python required)**
* [x] **v2: Interactive project generator with 17-step wizard**
* [x] **v2: Plugin system with versioning (19 plugins)**
* [x] **v2: Template versioning (react@18, nestjs@11, fastapi@0.115)**
* [x] **v2: Project-specific compose generation**
* [x] **v2: Service profiles (dev / testing / production)**
* [x] **v2: Multi-project management (devforge use)**
* [x] **v2: Workspace manifest (devforge.json)**
* [x] **v2: Auto CLI image build on first use**
* [x] **v2: Enhanced doctor with 12+ health checks**
* [ ] Deploy SSL routing in local gateway configurations
* [ ] Setup local Docker Registry cache
* [ ] Remote plugin registry (pull plugins from GitHub)
* [ ] DevForge Cloud Sync (share manifests across team)
