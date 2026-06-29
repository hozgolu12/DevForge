#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE NODE PACKAGE UPDATE SCRIPT
# ==============================================================================
# Triggers 'npm update' inside running containers or one-off containers.
# ==============================================================================

set -euo pipefail

SERVICE=${1:-all}

update_service() {
    local svc=$1
    echo "Updating npm packages for service '$svc'..."

    # Check if container is running
    if docker compose exec "$svc" true 2>/dev/null; then
        echo "Container '$svc' is running, running 'npm update' in-place..."
        docker compose exec "$svc" npm update
    else
        echo "Container '$svc' is not running, launching a temporary container to update..."
        docker compose run --rm --entrypoint "npm update" "$svc"
    fi
}

if [ "$SERVICE" = "all" ]; then
    for svc in react nextjs express nestjs; do
        update_service "$svc"
    done
else
    update_service "$SERVICE"
fi

echo "SUCCESS: Package updates completed."
