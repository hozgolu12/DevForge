#!/usr/bin/env bash

# ==============================================================================
# DEVFORGE PLATFORM LINTER
# ==============================================================================
# Validates code syntax, Docker Compose syntax, and shell files.
# ==============================================================================

set -euo pipefail

errors=0

echo "Linting DevForge platform configurations..."

# 1. Docker Compose validation
echo -n "Checking docker-compose.yml syntax... "
if docker compose config -q &> /dev/null; then
    echo "OK"
else
    echo "ERROR (Invalid Docker Compose configuration)"
    errors=$((errors + 1))
fi

# 2. Shell scripts syntax validation
echo "Checking shell scripts syntax..."
find scripts/ -name "*.sh" -type f | while read -r file; do
    echo -n "  Testing $file... "
    if bash -n "$file"; then
        echo "OK"
    else
        echo "SYNTAX ERROR"
        errors=$((errors + 1))
    fi
done

# 3. Check environment file variables structure
if [ -f ".env.example" ]; then
    echo -n "Validating .env.example format... "
    if grep -q "=" .env.example; then
        echo "OK"
    else
        echo "Warning: .env.example looks empty or invalid"
        errors=$((errors + 1))
    fi
fi

if [ $errors -eq 0 ]; then
    echo "===================================================="
    echo "SUCCESS: All files successfully linted (no errors)."
    echo "===================================================="
    exit 0
else
    echo "===================================================="
    echo "FAILED: Linting found $errors syntax/configuration error(s)."
    echo "===================================================="
    exit 1
fi
