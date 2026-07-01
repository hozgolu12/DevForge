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

$cmdArgs = $args
# Flatten arguments if passed as a nested array (e.g. from wrapper functions)
if ($args[0] -is [System.Array]) {
    $cmdArgs = $args[0]
}
$command = $cmdArgs[0]

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

$isProjectCmd = ($cmdArgs -contains "--project") -or ($cmdArgs -contains "-p") -or ($cmdArgs -contains "--all") -or ($cmdArgs -contains "-a") -or ($cmdArgs -contains "--help") -or ($cmdArgs -contains "-h")

if ($V2_COMMANDS -contains $command -or $isProjectCmd) {

    # Resolve DevForge root directory (where this script resides)
    $DEVFORGE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (-not $DEVFORGE_ROOT) {
        $DEVFORGE_ROOT = $PSScriptRoot
    }

    # Auto-build: detect if CLI image exists, build it automatically if missing
    $imageExists = docker image inspect $CLI_IMAGE 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[DevForge] CLI image '$CLI_IMAGE' not found. Building automatically..." -ForegroundColor Yellow
        docker build -t $CLI_IMAGE -f "$DEVFORGE_ROOT/$CLI_DOCKERFILE" "$DEVFORGE_ROOT"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[DevForge] ERROR: Failed to build CLI image. Is Docker running?" -ForegroundColor Red
            exit 1
        }
        Write-Host "[DevForge] CLI image built successfully." -ForegroundColor Green
    }

    # Handle import volume mapping
    $importVolumeOpts = @()
    if ($command -eq "import" -and $cmdArgs.Count -ge 2) {
        $importPath = $cmdArgs[1]
        $absImportPath = Resolve-Path $importPath -ErrorAction SilentlyContinue
        if ($absImportPath) {
            $absImportPathString = $absImportPath.Path
            $importVolumeOpts = @("-v", "${absImportPathString}:/import_target")
        }
    }

    # Handle .env file forwarding if present in current directory
    $envFileOpts = @()
    if (Test-Path "$PWD/.env") {
        $envFileOpts = @("--env-file", "$PWD/.env")
    }

    # Run the CLI engine inside an ephemeral container
    # --rm          : container auto-removes after command completes
    # -it           : interactive terminal (required for questionary wizard)
    # -v PWD        : mounts workspace so generated files appear on host
    # -v docker.sock: allows the CLI to run docker compose commands
    docker run --rm -it `
        -e GROQ_API_KEY `
        -e GEMINI_API_KEY `
        -e OPENAI_API_KEY `
        $envFileOpts `
        -v "${PWD}:/workspace" `
        $importVolumeOpts `
        -v "${DEVFORGE_ROOT}:/devforge" `
        -v "/var/run/docker.sock:/var/run/docker.sock" `
        $CLI_IMAGE @cmdArgs

    exit $LASTEXITCODE
}

switch ($command) {
    "up" {
        Write-Header "Starting DevForge Services"
        docker compose up -d
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to start DevForge services."
            exit $LASTEXITCODE
        }
        Write-Success "DevForge is running."
        break
    }
    "down" {
        Write-Header "Stopping DevForge Services"
        docker compose down
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to stop DevForge services."
            exit $LASTEXITCODE
        }
        Write-Success "DevForge has stopped."
        break
    }
    "restart" {
        $service = $cmdArgs[1]
        if ($service) {
            Write-Header "Restarting DevForge service '$service'"
            docker compose restart $service
        } else {
            Write-Header "Restarting all DevForge services"
            docker compose restart
        }
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to restart DevForge services."
            exit $LASTEXITCODE
        }
        Write-Success "Restart complete."
        break
    }
    "status" {
        Write-Header "DevForge Container Status"
        docker compose ps
        break
    }
    "logs" {
        $service = $cmdArgs[1]
        if (-not $service) {
            Write-ErrorMsg "Please specify a service name. Usage: .\devforge.ps1 logs <service>"
            exit 1
        }
        Write-Header "Output logs for '$service' (Press Ctrl+C to exit)"
        docker compose logs -f --tail=100 $service
        break
    }
    "shell" {
        $service = $cmdArgs[1]
        if (-not $service) {
            Write-ErrorMsg "Please specify a service name. Usage: .\devforge.ps1 shell <service>"
            exit 1
        }
        Write-Header "Opening shell inside container '$service'"
        $container_ids = @(docker compose ps -q $service)
        $container_id = $container_ids[0]
        if ($container_id) {
            $shell = "sh"
            foreach ($sh in @("zsh", "bash")) {
                docker exec $container_id sh -c "command -v $sh" >$null 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $shell = $sh
                    break
                }
            }
            docker compose exec $service $shell
        } else {
            Write-ErrorMsg "Container for '$service' is not running."
        }
        break
    }
    "create" {
        $template = $cmdArgs[1]
        $name = $cmdArgs[2]
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
        break
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
        docker compose config -q >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [VALID]" -ForegroundColor Green
        } else {
            Write-Host " [INVALID]" -ForegroundColor Red
            docker compose config
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
        break
    }
    "backup" {
        Write-Header "Executing database backups"
        bash "./scripts/db-backup.sh"
        break
    }
    "restore" {
        $folder = $cmdArgs[1]
        if (-not $folder) {
            Write-ErrorMsg "Please specify a backup directory. Usage: .\devforge.ps1 restore backups/YYYYMMDD_HHMMSS"
            exit 1
        }
        Write-Header "Restoring databases from snapshot '$folder'"
        bash "./scripts/db-restore.sh" $folder
        break
    }
    "seed" {
        Write-Header "Seeding active databases"
        bash "./scripts/db-seed.sh"
        break
    }
    "build-apk" {
        Write-Header "Compiling Flutter release APK"
        $flutterPath = $null
        if (Test-Path "pubspec.yaml") {
            $flutterPath = Resolve-Path "pubspec.yaml"
        } elseif (Test-Path "projects/sample-flutter/pubspec.yaml") {
            $flutterPath = Resolve-Path "projects/sample-flutter/pubspec.yaml"
        } else {
            $found = Get-ChildItem -Filter "pubspec.yaml" -Recurse -ErrorAction SilentlyContinue | 
                     Where-Object { $_.FullName -notmatch "\\(\.git|\.devforge|node_modules|build|\.venv)\\ " } | 
                     Select-Object -First 1
            if ($found) {
                $flutterPath = $found.FullName
            }
        }

        if (-not $flutterPath) {
            Write-ErrorMsg "No Flutter project (pubspec.yaml) found in the current directory or subdirectories."
            exit 1
        }

        $flutterDir = Split-Path -Parent $flutterPath
        Write-Host "Found Flutter project at: $flutterDir" -ForegroundColor Yellow

        $FLUTTER_IMAGE = "devforge-flutter"
        $imageExists = docker image inspect $FLUTTER_IMAGE 2>$null
        if ($LASTEXITCODE -ne 0) {
            $DEVFORGE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
            if (-not $DEVFORGE_ROOT) { $DEVFORGE_ROOT = $PSScriptRoot }

            Write-Host "[DevForge] Flutter compiler image '$FLUTTER_IMAGE' not found. Building automatically (this may take a few minutes)..." -ForegroundColor Yellow
            docker build -t $FLUTTER_IMAGE -f "$DEVFORGE_ROOT/docker/flutter/Dockerfile" "$DEVFORGE_ROOT"
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[DevForge] ERROR: Failed to build Flutter compiler image." -ForegroundColor Red
                exit 1
            }
            Write-Host "[DevForge] Flutter compiler image built successfully." -ForegroundColor Green
        }

        docker run --rm `
            -v "${flutterDir}:/workspace" `
            -w /workspace `
            -v "devforge_gradle_cache:/home/devforge/.gradle" `
            -v "devforge_pub_cache:/home/devforge/.pub-cache" `
            $FLUTTER_IMAGE bash -c "flutter pub get && flutter build apk --release"

        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Failed to compile Flutter release APK."
            exit $LASTEXITCODE
        }
        Write-Success "APK compilation finished."
        break
    }
    "build" {
        $sub = $cmdArgs[1]
        if ($sub -eq "apk") {
            Write-Header "Compiling Flutter release APK"
            $flutterPath = $null
            if (Test-Path "pubspec.yaml") {
                $flutterPath = Resolve-Path "pubspec.yaml"
            } elseif (Test-Path "projects/sample-flutter/pubspec.yaml") {
                $flutterPath = Resolve-Path "projects/sample-flutter/pubspec.yaml"
            } else {
                $found = Get-ChildItem -Filter "pubspec.yaml" -Recurse -ErrorAction SilentlyContinue | 
                         Where-Object { $_.FullName -notmatch "\\(\.git|\.devforge|node_modules|build|\.venv)\\ " } | 
                         Select-Object -First 1
                if ($found) {
                    $flutterPath = $found.FullName
                }
            }

            if (-not $flutterPath) {
                Write-ErrorMsg "No Flutter project (pubspec.yaml) found in the current directory or subdirectories."
                exit 1
            }

            $flutterDir = Split-Path -Parent $flutterPath
            Write-Host "Found Flutter project at: $flutterDir" -ForegroundColor Yellow

            $FLUTTER_IMAGE = "devforge-flutter"
            $imageExists = docker image inspect $FLUTTER_IMAGE 2>$null
            if ($LASTEXITCODE -ne 0) {
                $DEVFORGE_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
                if (-not $DEVFORGE_ROOT) { $DEVFORGE_ROOT = $PSScriptRoot }

                Write-Host "[DevForge] Flutter compiler image '$FLUTTER_IMAGE' not found. Building automatically (this may take a few minutes)..." -ForegroundColor Yellow
                docker build -t $FLUTTER_IMAGE -f "$DEVFORGE_ROOT/docker/flutter/Dockerfile" "$DEVFORGE_ROOT"
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "[DevForge] ERROR: Failed to build Flutter compiler image." -ForegroundColor Red
                    exit 1
                }
                Write-Host "[DevForge] Flutter compiler image built successfully." -ForegroundColor Green
            }

            docker run --rm `
                -v "${flutterDir}:/workspace" `
                -w /workspace `
                -v "devforge_gradle_cache:/home/devforge/.gradle" `
                -v "devforge_pub_cache:/home/devforge/.pub-cache" `
                $FLUTTER_IMAGE bash -c "flutter pub get && flutter build apk --release"

            if ($LASTEXITCODE -ne 0) {
                Write-ErrorMsg "Failed to compile Flutter release APK."
                exit $LASTEXITCODE
            }
            Write-Success "APK compilation finished."
        } else {
            Write-Header "Building custom DevForge images"
            docker compose build
            if ($LASTEXITCODE -ne 0) {
                Write-ErrorMsg "Failed to build DevForge images."
                exit $LASTEXITCODE
            }
            Write-Success "Build complete."
        }
        break
    }
    default {
        if ($command -and $command -ne "help" -and $command -ne "commands") {
            Write-ErrorMsg "Unknown command '$command'`n"
        }
        Write-Host "DevForge local developer platform CLI" -ForegroundColor Cyan
        Write-Host "Usage: .\devforge.ps1 <command> [arguments]"
        
        Write-Host "`nProject-aware Commands (v2):" -ForegroundColor Green
        Write-Host "  new              Create a new project interactively"
        Write-Host "  init             Initialize the current directory as a project"
        Write-Host "  import <path>    Import an existing project from another directory"
        Write-Host "  detect           Scan the current project for technologies"
        Write-Host "  template         Manage code templates"
        Write-Host "  plugin           Manage service plugins (list, install, remove, create)"
        Write-Host "  use <project>    Set the active project for subsequent commands"
        Write-Host "  start <svc>      Start a specific project service"
        Write-Host "  stop <svc>       Stop a specific project service"
        Write-Host "  restart <svc>    Restart a specific project service"
        Write-Host "  logs <svc>       Tail logs for a project service"
        Write-Host "  shell <svc>      Open a shell inside a project service container"
        Write-Host "  update           Update the DevForge CLI image"

        Write-Host "`nPlatform-wide Commands (v1):" -ForegroundColor Green
        Write-Host "  up               Start all platform services"
        Write-Host "  down             Stop all platform services"
        Write-Host "  restart          Restart all platform services"
        Write-Host "  status           Show running platform containers status"
        Write-Host "  logs             View tailing logs for platform services"
        Write-Host "  shell            Open interactive terminal inside a platform container"
        Write-Host "  create <t> <n>   Scaffold a standalone template project"
        Write-Host "  doctor           Run platform health diagnostics"
        Write-Host "  backup           Back up platform databases"
        Write-Host "  restore <f>      Restore database state from snapshot folder <f>"
        Write-Host "  seed             Populate databases with starter data"
        Write-Host "  build            Build custom DevForge platform images"
        Write-Host "  build apk        Compile Flutter Android APK release target"
    }
}
