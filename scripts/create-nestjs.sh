#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE NESTJS PROJECT SCRIPT
# ==============================================================================
# Creates a new NestJS project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-nestjs}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating NestJS project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/nestjs/. "$TARGET_DIR/"

echo "SUCCESS: NestJS project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart nestjs"
