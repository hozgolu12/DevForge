#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE DJANGO PROJECT SCRIPT
# ==============================================================================
# Creates a new Django project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-django}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Django project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/django/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/django/.env.example" ]; then
    cp "templates/django/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: Django project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart django"
