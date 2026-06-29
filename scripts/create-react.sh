#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE REACT PROJECT SCRIPT
# ==============================================================================
# Creates a new React project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-react}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating React project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/react/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/react/.env.example" ]; then
    cp "templates/react/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: React project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart react"
