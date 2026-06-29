#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE FLUTTER PROJECT SCRIPT
# ==============================================================================
# Creates a new Flutter project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-flutter}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Flutter project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/flutter/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/flutter/.env.example" ]; then
    cp "templates/flutter/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: Flutter project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To build the release APK: docker compose exec flutter flutter build apk --release"
