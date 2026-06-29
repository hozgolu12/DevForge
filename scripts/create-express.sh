#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE EXPRESS PROJECT SCRIPT
# ==============================================================================
# Creates a new Express project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-express}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Express project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/express/. "$TARGET_DIR/"

# Setup local environment variables
if [ -f "$TARGET_DIR/.env.example" ]; then
    cp "$TARGET_DIR/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: Express project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart express"
