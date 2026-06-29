#!/usr/bin/env bash

# ==============================================================================
# DEVFORGE PLATFORM FORMATTER
# ==============================================================================
# Cleans shell scripts, fixes file permissions, and sanitizes line endings.
# ==============================================================================

set -euo pipefail

echo "Formatting DevForge platform scripts..."

# 1. Enforce executable permissions on all shell files
echo "Adjusting file permissions..."
find scripts/ -name "*.sh" -type f -exec chmod +x {} +
chmod +x Makefile || true

# 2. Convert CRLF line endings to LF to prevent Windows execution issues in containers
echo "Converting Windows line endings (CRLF) to Unix (LF)..."
find scripts/ -name "*.sh" -type f | while read -r file; do
    if [ -f "$file" ]; then
        # Replace CRLF with LF in-place
        sed -i 's/\r$//' "$file"
        echo "  Sanitized line endings for $file"
    fi
done

echo "===================================================="
echo "SUCCESS: DevForge formatting complete."
echo "===================================================="
