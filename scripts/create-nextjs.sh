#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE NEXTJS PROJECT SCRIPT
# ==============================================================================
# Creates a new Next.js project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-nextjs}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Next.js project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/nextjs/. "$TARGET_DIR/"

echo "SUCCESS: Next.js project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart nextjs"
