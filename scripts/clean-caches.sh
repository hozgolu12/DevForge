#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE NODE CACHE & BUILD PURGE SCRIPT
# ==============================================================================
# Cleans build outputs, local node_modules, and triggers package cache clears.
# ==============================================================================

set -euo pipefail

echo "Cleaning up DevForge Node platform caches and build outputs..."

# Clean container npm cache if they are running
for svc in react nextjs express nestjs; do
    if docker compose exec "$svc" true 2>/dev/null; then
        echo "Clearing npm cache inside running container '$svc'..."
        docker compose exec "$svc" npm cache clean --force || true
    fi
done

# Purge local build artifacts, local node_modules if present on host mount
echo "Purging local build targets and package directories under 'projects/'..."
find projects/ -maxdepth 3 -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find projects/ -maxdepth 3 -name "dist" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find projects/ -maxdepth 3 -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find projects/ -maxdepth 3 -name ".turbo" -type d -prune -exec rm -rf {} + 2>/dev/null || true

echo "SUCCESS: DevForge Node platform cleaning completed."
