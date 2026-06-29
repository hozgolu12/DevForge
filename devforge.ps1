# ==============================================================================
# DEVFORGE PLATFORM POWERSHELL COMMAND LINE INTERFACE (CLI)
# ==============================================================================
# Native Windows PowerShell entrypoint to manage the DevForge local platform.
# v1 commands: up, down, restart, status, logs, shell, create, doctor,
#              backup, restore, seed, build-apk
# v2 commands: new, template, plugin, start, stop, generate, use, update,
#              self-update  (routed to devforge-cli:2.0 container)
# Usage: .\devforge.ps1 <command> [arguments]
# ==============================================================================

$command = $args[0]

# Helper function to print headers
function Write-Header($text) {
    Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

# Helper function to print success messages
function Write-Success($text) {
    Write-Host "SUCCESS: $text" -ForegroundColor Green
}

# Helper function to print error messages
function Write-ErrorMsg($text) {
    Write-Host "ERROR: $text" -ForegroundColor Red
}

# ==============================================================================
# DEVFORGE v2 — CLI CONTAINER ROUTING
# ==============================================================================
# V2 commands are routed to the devforge-cli:2.0 Docker container.
# The container is built automatically if it does not exist.
# All generated files are written to the mounted workspace on the host.
# ==============================================================================

$CLI_IMAGE   = "devforge-cli:2.0"
$CLI_DOCKERFILE = "docker/cli/Dockerfile"

# Commands handled by the v2 Python CLI engine (inside container)
$V2_COMMANDS = @("new", "template", "plugin", "start", "stop", "generate", "use", "update", "self-update", "init", "import", "detect")

if ($V2_COMMANDS -contains $command) {

    # Auto-build: detect if CLI image exists, build it automatically if missing
    $imageExists = docker image inspect $CLI_IMAGE 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[DevForge] CLI image '$CLI_IMAGE' not found. Building automatically..." -ForegroundColor Yellow
        docker build -t $CLI_IMAGE -f $CLI_DOCKERFILE . --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[DevForge] ERROR: Failed to build CLI image. Is Docker running?" -ForegroundColor Red
            exit 1
        }
        Write-Host "[DevForge] CLI image built successfully." -ForegroundColor Green
    }

    # Resolve DevForge root directory (where this script resides)
    $DEVFORGE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (-not $DEVFORGE_ROOT) {
        $DEVFORGE_ROOT = $PSScriptRoot
    }

    # Handle import volume mapping
    $importVolumeOpts = @()
    if ($command -eq "import" -and $args.Count -ge 2) {
        $importPath = $args[1]
        $absImportPath = Resolve-Path $importPath -ErrorAction SilentlyContinue
        if ($absImportPath) {
            $absImportPathString = $absImportPath.Path
            $importVolumeOpts = @("-v", "${absImportPathString}:/import_target")
        }
    }

    # Run the CLI engine inside an ephemeral container
    # --rm          : container auto-removes after command completes
    # -it           : interactive terminal (required for questionary wizard)
    # -v PWD        : mounts workspace so generated files appear on host
    # -v docker.sock: allows the CLI to run docker compose commands
    docker run --rm -it `
        -v "${PWD}:/workspace" `
        $importVolumeOpts `
        -v "${DEVFORGE_ROOT}:/devforge" `
        -v "/var/run/docker.sock:/var/run/docker.sock" `
        $CLI_IMAGE @args

    exit $LASTEXITCODE
}

switch ($command) {
    "up" {
        Write-Header "Starting DevForge Services"
        docker-compose up -d
        Write-Success "DevForge is running."
    }
    "down" {
        Write-Header "Stopping DevForge Services"
        docker-compose down
        Write-Success "DevForge has stopped."
    }
    "restart" {
        $service = $args[1]
        if ($service) {
            Write-Header "Restarting DevForge service '$service'"
            docker-compose restart $service
        } else {
            Write-Header "Restarting all DevForge services"
            docker-compose restart
        }
        Write-Success "Restart complete."
    }
    "status" {
        Write-Header "DevForge Container Status"
        docker-compose ps
    }
    "logs" {
        $service = $args[1]
        if (-not $service) {
            Write-ErrorMsg "Please specify a service name. Usage: .\devforge.ps1 logs <service>"
            exit 1
        }
        Write-Header "Output logs for '$service' (Press Ctrl+C to exit)"
        docker-compose logs -f --tail=100 $service
    }
    "shell" {
        $service = $args[1]
        if (-not $service) {
            Write-ErrorMsg "Please specify a service name. Usage: .\devforge.ps1 shell <service>"
            exit 1
        }
        Write-Header "Opening shell inside container '$service'"
        docker-compose exec $service zsh || docker-compose exec $service bash || docker-compose exec $service sh
    }
    "create" {
        $template = $args[1]
        $name = $args[2]
        if (-not $template -or -not $name) {
            Write-ErrorMsg "Usage: .\devforge.ps1 create <template> <project_name>"
            Write-Host "Available templates: react, nextjs, express, nestjs, fastapi, flask, django, springboot, flutter, ai"
            exit 1
        }
        Write-Header "Scaffolding project '$name' from template '$template'"
        if (Test-Path "scripts/create-$template.sh") {
            # Execute create script inside Git Bash wrapper or WSL
            bash "./scripts/create-$template.sh" $name
        } else {
            Write-ErrorMsg "Template '$template' does not exist."
        }
    }
    "doctor" {
        Write-Header "DevForge Diagnostic Doctor"
        
        # Check Docker Daemon
        Write-Host "Checking Docker daemon status..." -NoNewline
        docker info >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [RUNNING]" -ForegroundColor Green
        } else {
            Write-Host " [STOPPED]" -ForegroundColor Red
            Write-ErrorMsg "Docker Desktop daemon is not running on your host machine."
        }

        # Check Compose Topology
        Write-Host "Checking Compose configuration syntax..." -NoNewline
        docker-compose config -q >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [VALID]" -ForegroundColor Green
        } else {
            Write-Host " [INVALID]" -ForegroundColor Red
            docker-compose config
        }

        # Check Configured Ports
        Write-Host "`nChecking configured dev ports availability on localhost..."
        $ports = @{
            "Nginx Ingress" = 8080
            "React Web" = 5173
            "FastAPI API" = 8081
            "Django App" = 8082
            "AI Dev Service" = 8083
            "Spring Boot API" = 8084
            "pgAdmin 4" = 5050
            "Mongo Express" = 8087
            "Redis Commander" = 8086
        }

        foreach ($p in $ports.Keys) {
            $val = $ports[$p]
            $connection = New-Object System.Net.Sockets.TcpClient
            try {
                $connection.Connect("127.0.0.1", $val)
                Write-Host "Port $val ($p):" -NoNewline
                Write-Host " [IN USE/RESOLVING]" -ForegroundColor Green
                $connection.Close()
            } catch {
                Write-Host "Port $val ($p):" -NoNewline
                Write-Host " [FREE]" -ForegroundColor Yellow
            }
        }
    }
    "backup" {
        Write-Header "Executing database backups"
        bash "./scripts/db-backup.sh"
    }
    "restore" {
        $folder = $args[1]
        if (-not $folder) {
            Write-ErrorMsg "Please specify a backup directory. Usage: .\devforge.ps1 restore backups/YYYYMMDD_HHMMSS"
            exit 1
        }
        Write-Header "Restoring databases from snapshot '$folder'"
        bash "./scripts/db-restore.sh" $folder
    }
    "seed" {
        Write-Header "Seeding active databases"
        bash "./scripts/db-seed.sh"
    }
    "build-apk" {
        Write-Header "Compiling Flutter release APK"
        docker-compose exec flutter flutter build apk --release
        Write-Success "APK compilation finished."
    }
    default {
        Write-Host "DevForge local developer platform CLI" -ForegroundColor Cyan
        Write-Host "Usage: .\devforge.ps1 <command> [arguments]"
        Write-Host "`nAvailable Commands:"
        Write-Host "  up               Start all DevForge services"
        Write-Host "  down             Stop all DevForge services"
        Write-Host "  restart [svc]    Restart a specific or all services"
        Write-Host "  status           Show running containers status"
        Write-Host "  logs <svc>       View tailing logs for a service"
        Write-Host "  shell <svc>      Open interactive terminal inside a container"
        Write-Host "  create <t> <n>   Generate project <n> from template <t>"
        Write-Host "  doctor           Run platform health diagnostics"
        Write-Host "  backup           Back up active databases"
        Write-Host "  restore <f>      Restore database state from snapshot folder <f>"
        Write-Host "  seed             Populate databases with starter data"
        Write-Host "  build-apk        Compile Flutter Android APK release target"
    }
}
