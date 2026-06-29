#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE AI PROJECT SCRIPT
# ==============================================================================
# Creates a new AI project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-ai}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating AI project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/ai/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/ai/.env.example" ]; then
    cp "templates/ai/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: AI project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart ai"
