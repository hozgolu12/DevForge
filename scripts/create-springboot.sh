#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE CREATE SPRING BOOT PROJECT SCRIPT
# ==============================================================================
# Creates a new Spring Boot project under projects/ from the template.
# ==============================================================================

set -euo pipefail

PROJECT_NAME=${1:-sample-springboot}
TARGET_DIR="projects/$PROJECT_NAME"

echo "Creating Spring Boot project '$PROJECT_NAME' from template..."

if [ -d "$TARGET_DIR" ]; then
    echo "ERROR: Directory '$TARGET_DIR' already exists."
    exit 1
fi

mkdir -p "$TARGET_DIR"
cp -rp templates/springboot/. "$TARGET_DIR/"

# Create dynamic .env inside target project if needed
if [ -f "templates/springboot/.env.example" ]; then
    cp "templates/springboot/.env.example" "$TARGET_DIR/.env"
fi

echo "SUCCESS: Spring Boot project '$PROJECT_NAME' created at '$TARGET_DIR'."
echo "To run the project: docker compose restart springboot"
