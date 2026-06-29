#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE FLASK PROJECT SCRIPT
# ==============================================================================
# Creates a new Flask project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-flask}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Flask project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/flask/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/flask/.env.example" ]; then
    cp "templates/flask/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: Flask project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart flask"
