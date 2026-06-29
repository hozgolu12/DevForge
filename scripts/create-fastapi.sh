#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE FASTAPI PROJECT SCRIPT
# ==============================================================================
# Creates a new FastAPI project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-fastapi}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating FastAPI project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/fastapi/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/fastapi/.env.example" ]; then
    cp "templates/fastapi/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: FastAPI project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart fastapi"
