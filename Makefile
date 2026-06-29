# DevForge Platform Automation Makefile
.PHONY: up down restart build rebuild clean logs status doctor shell lint format backup restore node-shell create-react create-next create-express create-nest install update-node python-shell create-fastapi create-flask create-django

# Default service for shell command
SERVICE ?= nginx

# Start all containers in background
up:
	@echo "Starting DevForge services..."
	docker compose up -d

# Stop and remove containers, networks
down:
	@echo "Stopping DevForge services..."
	docker compose down

# Restart all services
restart:
	@echo "Restarting DevForge services..."
	docker compose restart

# Build all custom images
build:
	@echo "Building custom DevForge images..."
	docker compose build

# Rebuild all images from scratch (no cache) and start
rebuild:
	@echo "Rebuilding DevForge images from scratch..."
	docker compose build --no-cache
	docker compose up -d --force-recreate

# Clean up containers, networks, volumes and orphan containers
clean:
	@echo "Cleaning up DevForge containers, networks, and persistent volumes..."
	docker compose down -v --remove-orphans

# View logs from all services (follow output)
logs:
	docker compose logs -f

# Check container status
status:
	docker compose ps

# Run system doctor diagnostic script
doctor:
	@echo "Running DevForge system diagnostics..."
	@bash ./scripts/doctor.sh

# Open terminal shell into a container (usage: make shell SERVICE=postgres)
shell:
	@echo "Opening shell in service: $(SERVICE)..."
	docker compose exec $(SERVICE) sh || docker compose exec $(SERVICE) bash || docker compose run --entrypoint sh $(SERVICE)

# Lint docker-compose and configuration files
lint:
	@echo "Validating Docker Compose configuration..."
	docker compose config -q
	@echo "Linting scripts and configurations..."
	@bash ./scripts/lint.sh

# Format files
format:
	@echo "Formatting configurations and scripts..."
	@bash ./scripts/format.sh

# Backup service databases (usage: make backup)
backup:
	@echo "Backing up databases..."
	@bash ./scripts/backup.sh

# Restore service databases (usage: make restore)
restore:
	@echo "Restoring databases..."
	@bash ./scripts/restore.sh

# Open bash shell into a node container (usage: make node-shell NODE_SERVICE=express)
NODE_SERVICE ?= express
node-shell:
	@echo "Opening shell in node service: $(NODE_SERVICE)..."
	docker compose exec $(NODE_SERVICE) bash || docker compose exec $(NODE_SERVICE) sh || docker compose run --entrypoint bash $(NODE_SERVICE)

# Create React project from template (usage: make create-react name=my-app)
create-react:
	@bash ./scripts/create-react.sh $(name)

# Create Next.js project from template (usage: make create-next name=my-app)
create-next:
	@bash ./scripts/create-nextjs.sh $(name)

# Create Express project from template (usage: make create-express name=my-app)
create-express:
	@bash ./scripts/create-express.sh $(name)

# Create NestJS project from template (usage: make create-nest name=my-app)
create-nest:
	@bash ./scripts/create-nestjs.sh $(name)

# Install npm dependencies (usage: make install SERVICE=react)
install:
	@bash ./scripts/install-deps.sh $(SERVICE)

# Update npm packages (usage: make update-node SERVICE=react)
update-node:
	@bash ./scripts/update-packages.sh $(SERVICE)

# Open bash shell into a python container (usage: make python-shell PYTHON_SERVICE=fastapi)
PYTHON_SERVICE ?= fastapi
python-shell:
	@echo "Opening shell in python service: $(PYTHON_SERVICE)..."
	docker compose exec $(PYTHON_SERVICE) zsh || docker compose exec $(PYTHON_SERVICE) bash || docker compose exec $(PYTHON_SERVICE) sh || docker compose run --entrypoint bash $(PYTHON_SERVICE)

# Create FastAPI project from template (usage: make create-fastapi name=my-app)
create-fastapi:
	@bash ./scripts/create-fastapi.sh $(name)

# Create Flask project from template (usage: make create-flask name=my-app)
create-flask:
	@bash ./scripts/create-flask.sh $(name)

# Create Django project from template (usage: make create-django name=my-app)
create-django:
	@bash ./scripts/create-django.sh $(name)
