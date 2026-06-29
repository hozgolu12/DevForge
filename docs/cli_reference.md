# DevForge CLI Reference Guide

The DevForge Command Line Interface (CLI) provides a unified command set to manage your containers, scaffold new projects, manage plugins and templates, run backups and restores, and perform diagnostics.

DevForge v2 introduces a **containerized CLI engine** — v2 commands run inside an ephemeral `devforge-cli:2.0` Docker container. The container is **built automatically** the first time a v2 command is used.

**Host requirements**: Docker Desktop + Git + VS Code only.

---

## 1. Quickstart & Setup

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\devforge.ps1 <command> [arguments]
```

### Linux / macOS / Git Bash
```bash
chmod +x devforge
./devforge <command> [arguments]
```

---

## 2. DevForge v2 Commands (New)

v2 commands are routed to the `devforge-cli:2.0` container automatically. The CLI image is built on first use — no manual step required.

---

### Project Generation

#### `new <project-name>`
Launches the interactive project wizard. Asks for project type, frameworks, databases, AI tools, CI/CD, and more. Generates a complete project with compose file, env, manifest, and CI/CD workflows.

```powershell
.\devforge.ps1 new socialcross
.\devforge.ps1 new my-api
```

**What gets generated:**
```
projects/<name>/
├── devforge.json             ← workspace manifest
├── docker-compose.yml        ← only selected services
├── .env + .env.example
├── .devforge/                ← hidden workspace directory
│   ├── generated/            ← profile compose variants
│   ├── cache/, logs/, metadata/
├── frontend/                 ← scaffolded if selected
├── backend/                  ← scaffolded if selected
└── .github/workflows/ci.yml  ← if GitHub Actions selected
```

---

### Template Management

#### `template list [--category <category>]`
List all available templates with versions.
```powershell
.\devforge.ps1 template list
.\devforge.ps1 template list --category backend
```

#### `template install <name>[@version] [--project <name>]`
Install a template into the active or specified project. Supports versioning.
```powershell
.\devforge.ps1 template install react
.\devforge.ps1 template install react@18
.\devforge.ps1 template install nestjs@11 --project socialcross
```

#### `generate <template>[@version] <output-name> [--project <name>]`
Generate a named app directory from a template.
```powershell
.\devforge.ps1 generate react frontend
.\devforge.ps1 generate fastapi auth-service --project socialcross
```

---

### Plugin Management

#### `plugin list [--category <category>] [--project <name>]`
List all plugins with availability and installation status.
```powershell
.\devforge.ps1 plugin list
.\devforge.ps1 plugin list --category database
.\devforge.ps1 plugin list --project socialcross
```

**Available categories**: `database`, `database-ui`, `cache`, `cache-ui`, `messaging`, `storage`, `ai`, `ai-ui`, `vector-db`, `monitoring`, `proxy`, `auth`

#### `plugin install <name>[@version] [--project <name>]`
Add a plugin to a project. Automatically regenerates the compose file.
```powershell
.\devforge.ps1 plugin install postgres
.\devforge.ps1 plugin install postgres@16
.\devforge.ps1 plugin install redis@7 --project socialcross
```

#### `plugin remove <name> [--project <name>]`
Remove a plugin from a project. Regenerates compose file.
```powershell
.\devforge.ps1 plugin remove mongodb
```

---

### Per-Service Management

All per-service commands read the active project's `devforge.json` to locate the generated compose file. Use `--project` to target a specific project.

#### `start <service> [--project <name>] [--profile dev|testing|production]`
Start a specific service.
```powershell
.\devforge.ps1 start postgres
.\devforge.ps1 start mongodb --project socialcross
.\devforge.ps1 start fastapi --profile production
```

#### `stop <service> [--project <name>]`
Stop a specific service.
```powershell
.\devforge.ps1 stop redis
.\devforge.ps1 stop mongodb --project socialcross
```

#### `restart <service> [--project <name>]`
Restart a specific service.
```powershell
.\devforge.ps1 restart fastapi
```

#### `logs <service> [--project <name>] [--tail N]`
Tail logs for a specific service.
```powershell
.\devforge.ps1 logs fastapi
.\devforge.ps1 logs mongodb --tail 50 --project socialcross
```

#### `shell <service> [--project <name>]`
Open an interactive shell inside a service container.
```powershell
.\devforge.ps1 shell postgres
.\devforge.ps1 shell redis --project socialcross
```

---

### Project Profiles

#### `up [--project <name>] [--profile dev|testing|production]`
Start all services for a project using a specific profile.
```powershell
.\devforge.ps1 up --project socialcross                     # dev (default)
.\devforge.ps1 up --project socialcross --profile testing
.\devforge.ps1 up --project socialcross --profile production
```

Profile variants are generated at:
```
projects/<name>/.devforge/generated/docker-compose.dev.yml
projects/<name>/.devforge/generated/docker-compose.testing.yml
projects/<name>/.devforge/generated/docker-compose.production.yml
```

---

### Multi-Project Management

#### `use <project-name>`
Set the active project for all subsequent commands (removes need for `--project`).
```powershell
.\devforge.ps1 use socialcross
.\devforge.ps1 start mongodb     # now operates on socialcross
```

---

### CLI Self-Update

#### `update` / `self-update`
Rebuild the `devforge-cli:2.0` image from the current source. Preserves all projects, templates, and plugins.
```powershell
.\devforge.ps1 update
.\devforge.ps1 self-update
```

---

### Enhanced Doctor

#### `doctor [--project <name>]`
Comprehensive system health check covering:
- Docker daemon status
- Docker version
- CLI image availability
- `docker-compose.yml` presence and validity
- Plugin registry integrity
- Template registry integrity
- `.env` file presence
- Disk space (warns if < 5 GB)
- Key port availability (80, 443, 5432, 27017, 6379, 11434...)
- `devforge-network` Docker network
- Project workspace (if `--project` specified)

```powershell
.\devforge.ps1 doctor
.\devforge.ps1 doctor --project socialcross
```

---

## 3. DevForge v1 Commands (All Unchanged)

All original v1 commands continue to work exactly as before. These operate on the full platform `docker-compose.yml`.

| Command | Description |
|---|---|
| `up` | Start all platform services |
| `down` | Stop all platform services |
| `restart [service]` | Restart all or one service |
| `status` | Show container status |
| `logs <service>` | Tail service logs |
| `shell <service>` | Open shell in container |
| `create <template> <name>` | Scaffold project from template (v1) |
| `doctor` | System diagnostics |
| `backup` | Back up all databases |
| `restore <folder>` | Restore from backup snapshot |
| `seed` | Seed databases |
| `build-apk` | Build Flutter APK |

---

## 4. Makefile Reference

| Target | Description |
|---|---|
| `make build-cli` | Build `devforge-cli:2.0` image |
| `make rebuild-cli` | Rebuild CLI image from scratch |
| `make up` | Start all v1 platform services |
| `make down` | Stop all v1 services |
| `make build` | Build all custom Docker images |
| `make rebuild` | Rebuild all images (no cache) |
| `make clean` | Stop + remove all volumes |
| `make logs` | Tail all service logs |
| `make status` | Show container status |
| `make doctor` | Run system diagnostics |
| `make backup` | Backup all databases |
| `make restore` | Restore from backup |
| `make create-react name=<n>` | Create React project (v1) |
| `make create-fastapi name=<n>` | Create FastAPI project (v1) |
| `make flutter-build-apk` | Build Flutter APK |

---

## 5. Workspace Manifest (devforge.json)

Every generated project contains a `devforge.json` at its root:

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
  "env_file": ".env",
  "ci_cd": "github-actions",
  "compose_file": "docker-compose.yml",
  "active_profile": "dev"
}
```

---

## 6. Available Plugins

| Plugin | Category | Versions |
|---|---|---|
| `postgres` | database | 15, 16, 17 |
| `mongodb` | database | 6, 7, 8 |
| `neo4j` | database | 5 |
| `pgadmin` | database-ui | 8.4 |
| `mongo-express` | database-ui | 1.0.2 |
| `redis` | cache | 7, 8 |
| `redis-commander` | cache-ui | latest |
| `rabbitmq` | messaging | 3.12, 3.13 |
| `minio` | storage | latest |
| `ollama` | ai | latest |
| `open-webui` | ai-ui | latest |
| `chromadb` | vector-db | 0.4, 0.5 |
| `qdrant` | vector-db | 1.8, 1.9 |
| `prometheus` | monitoring | 2.51 |
| `grafana` | monitoring | 10.4 |
| `loki` | monitoring | 2.9, 3.0 |
| `cadvisor` | monitoring | 0.49 |
| `nginx` | proxy | 1.24, 1.25 |
| `keycloak` | auth | 23, 24 |

---

## 7. Available Templates

| Template | Category | Versions |
|---|---|---|
| `react` | frontend | 18, 19 |
| `nextjs` | frontend | 14, 15 |
| `fastapi` | backend | 0.110, 0.115 |
| `flask` | backend | 3.0 |
| `django` | backend | 5.0 |
| `express` | backend | 4.18 |
| `nestjs` | backend | 10, 11 |
| `springboot` | backend | 3.2 |
| `flutter` | mobile | 3.22 |
| `ai` | ai | 1.0 |
