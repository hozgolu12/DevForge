# DevForge

[![Docker Compose Validation](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/compose-validate.yml/badge.svg)](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/compose-validate.yml)
[![Docker Build Validation](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/docker-build-validate.yml/badge.svg)](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/docker-build-validate.yml)
[![Security Scan](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/security-scan.yml/badge.svg)](https://github.com/hozgolu12/Bus_Reservation_System/actions/workflows/security-scan.yml)

> **One Docker Command. Unlimited Development.**

DevForge is a production-grade, containerized developer platform designed to run all language environments, database clusters, and AI tools locally. The only requirements on the host machine are **Docker Desktop**, **Git**, and **VS Code**. No languages or databases need to be installed directly on your operating system.

---

## Overview

DevForge isolates development tools into secure containers that work together out-of-the-box. Developers can build applications in React, Node, Python, Spring Boot, or AI ecosystems (Ollama, ChromaDB, Qdrant) without package manager conflicts, system path corruption, or version collisions.

---

## Architecture

DevForge is built using a modular, decoupled architecture where individual service instances are connected via an internal network. An Nginx Ingress Controller serves as the reverse proxy router for web frontends, dashboards, and APIs.

For detailed design blueprints, check out the [Architecture Guide](file:///D:/coding/DevForge/docs/architecture.md).

---

## Repository Structure

```text
DevForge/
├── .devcontainer/             # VS Code Dev Container configurations
│   ├── devcontainer.json      # Remote container workspace options
│   ├── docker-compose.yml     # Dev container service definition
│   └── Dockerfile             # Development container environment build
├── .github/                   # CI/CD Workflows
│   └── workflows/             # GitHub Actions files
│       ├── compose-validate.yml
│       ├── docker-build-validate.yml
│       ├── lint-validation.yml
│       └── security-scan.yml
├── docker/                    # Custom configurations and Dockerfiles
│   ├── base/                  # Standard hardened base system image
│   ├── chromadb/              # Chroma Vector Database settings
│   ├── mongodb/               # MongoDB configuration and overrides
│   ├── neo4j/                 # Neo4j Graph Database settings
│   ├── nginx/                 # Nginx Ingress and Dashboard
│   ├── ollama/                # Ollama LLM execution service
│   ├── open-webui/            # Open WebUI frontend dashboard
│   ├── postgres/              # PostgreSQL database custom settings
│   ├── qdrant/                # Qdrant Vector search settings
│   └── redis/                 # Redis Cache custom configuration
├── docs/                      # Technical Documentation
│   └── architecture.md
├── projects/                  # Developer workspaces container mounts
├── scripts/                   # Platform shell automation
│   ├── backup.sh              # Database hot-backup routines
│   ├── doctor.sh              # Host diagnostics validator
│   ├── format.sh              # Line-ending converter and permissions
│   ├── lint.sh                # Syntactic analysis checker
│   └── restore.sh             # Database recovery routines
├── templates/                 # Custom layout code structures
├── .env.example               # Config template containing instructions
├── docker-compose.override.yml# Local overrides
├── docker-compose.yml         # Main compose service topology
├── LICENSE                    # MIT License file
├── Makefile                   # Execution scripts shortkeys
└── README.md                  # This file
```

---

## Installation

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v25.0+ recommended)
* [Git](https://git-scm.com/)
* [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

### Clone and Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/hozgolu12/Bus_Reservation_System.git DevForge
   cd DevForge
   ```
2. Initialize environment parameters:
   ```bash
   cp .env.example .env
   ```
3. Run the doctor command to verify system readiness:
   ```bash
   make doctor
   ```

---

## Quick Start

Start the complete environment using the local Makefile:
```bash
make up
```

Once online, open your browser and navigate to:
* **Developer Control Panel**: [http://localhost](http://localhost) (Nginx gateway status and proxy endpoints dashboard)
* **Local AI Assistant**: [http://localhost:3000](http://localhost:3000) (Open WebUI connected to Ollama)
* **Neo4j Graph Browser**: [http://localhost:7474](http://localhost:7474) (Neo4j browser tool)
* **Qdrant Vector Console**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard) (Qdrant storage browser)

---

## Docker Commands

| Command | Action |
|---|---|
| `make up` | Starts all platform containers in detached mode |
| `make down` | Shuts down platform containers and networks |
| `make restart` | Restarts all containers |
| `make build` | Compiles custom Dockerfiles |
| `make rebuild`| Re-compiles from scratch (bypassing caches) and restarts |
| `make clean` | Shuts down containers, removes named volumes and networks |
| `make logs` | Monitors console stdout for all active services |
| `make status` | Queries execution metrics for active services |
| `make shell` | Enters CLI terminal inside Nginx container (or `make shell SERVICE=postgres`) |
| `make doctor` | Runs platform prerequisite verification |
| `make backup` | Performs hot-backups on running databases |
| `make restore` | Restores backup archives to active containers |

---

## Networking

All containers are isolated within the `devforge-network` bridge. Inter-service database calls do not go through host ports, they communicate internally:
* PostgreSQL connection URI: `postgresql://postgres_admin:password@postgres:5432/devforge_db`
* MongoDB connection URI: `mongodb://mongo_admin:password@mongodb:27017`
* Redis connection URI: `redis://:password@redis:6379`
* ChromaDB API endpoint: `http://chromadb:8000`
* Ollama API endpoint: `http://ollama:11434`

---

## Volumes

To prevent data loss, the following persistent named volumes are registered:
* `devforge_pgdata` - PostgreSQL databases
* `devforge_mongodata` - MongoDB files
* `devforge_redisdata` - Redis snapshots
* `devforge_neo4jdata` - Graph datasets
* `devforge_qdrantdata` - Vector indexes
* `devforge_chromadata` - Chroma DB files
* `devforge_ollamadata` - Large Language Model files

---

## Environment Variables

All parameters are configured in the active `.env` file. Groupings include:
* **Ingress**: `NGINX_PORT`, `NGINX_SECURE_PORT`
* **Databases**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, `REDIS_PASSWORD`, `NEO4J_AUTH`
* **AI & Indexes**: `QDRANT_API_KEY`, `CHROMA_AUTH_TOKEN`, `OLLAMA_MODELS_PATH`

---

## Troubleshooting

### Port Collision
**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated.`
**Fix**: Edit the `.env` file and modify the port values (e.g., change `NGINX_PORT=80` to `NGINX_PORT=8080`). Run `make up` again.

### Database Credentials Refused
**Error**: `FATAL: password authentication failed for user "postgres_admin"`
**Fix**: If you changed database passwords in `.env` after databases have already been initialized, the volume data still holds the old passwords. Reset the volume data using `make clean` (WARNING: this deletes all database data) and restart.

---

## FAQ

#### Can I use GPUs with Ollama?
Yes. Open `docker-compose.override.yml`, find the `ollama` section, and uncomment the `deploy.resources.reservations` section to enable Nvidia GPU pass-through.

#### Where do I put my source code?
Store your project files under the `projects/` directory. You can mount folders into custom future containers mapped in your `docker-compose.override.yml`.

---

## Contribution Guide

1. Create a development branch from `main`.
2. Ensure changes comply with lint and security protocols by running `make lint` and `make doctor`.
3. Format shell files using `make format`.
4. Open a Pull Request detailing your enhancements.

---

## Roadmap

* [x] Add Node/React project templates
* [x] Add Python/FastAPI backend blueprints
* [x] Add AI/ML development ecosystem (PyTorch, TensorFlow, LangChain, OCR, Whisper)
* [x] Add Java/Spring Boot development environment (JDK 21, Maven, Gradle)
* [ ] Deploy SSL routing in local gateway configurations
* [ ] Setup local Docker Registry cache
