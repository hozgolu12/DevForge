#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE DEPENDENCY INSTALLATION SCRIPT
# ==============================================================================
# Installs dependencies for a specific service or all Node.js services.
# ==============================================================================

set -euo pipefail

SERVICE=${1:-all}

install_service() {
    local svc=$1
    echo "Installing npm dependencies for service '$svc'..."

    # Check if container is running
    if docker compose exec "$svc" true 2>/dev/null; then
        echo "Container '$svc' is running, running 'npm install' in-place..."
        docker compose exec "$svc" npm install
    else
        echo "Container '$svc' is not running, launching a temporary container to install..."
        docker compose run --rm --entrypoint "npm install" "$svc"
    fi
}

if [ "$SERVICE" = "all" ]; then
    for svc in react nextjs express nestjs; do
        install_service "$svc"
    done
else
    install_service "$SERVICE"
fi

echo "SUCCESS: Dependencies installed."
