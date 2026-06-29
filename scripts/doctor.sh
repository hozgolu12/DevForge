#!/usr/bin/env bash

# ==============================================================================
# DEVFORGE PLATFORM DOCTOR (DIAGNOSTIC TOOL)
# ==============================================================================
# Validates developer host dependencies, configuration settings, and folders.
# ==============================================================================

set -euo pipefail

# ANSI color codes
NC='\033[0m'
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'

echo -e "${BOLD}${CYAN}====================================================${NC}"
echo -e "${BOLD}${CYAN}            DevForge Platform Doctor                ${NC}"
echo -e "${BOLD}${CYAN}====================================================${NC}"
echo ""

errors=0
warnings=0

check_cmd() {
    local cmd=$1
    local name=$2
    echo -n -e "Checking ${BOLD}${name}${NC} (${cmd})... "
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓ Found${NC}"
        return 0
    else
        echo -e "${RED}✗ Missing${NC}"
        return 1
    fi
}

# 1. System Command Checks
if ! check_cmd "docker" "Docker CLI"; then
    errors=$((errors + 1))
fi

if ! check_cmd "git" "Git VCS"; then
    errors=$((errors + 1))
fi

# 2. Check Docker Compose (support both compose V2 and V1 check)
echo -n -e "Checking ${BOLD}Docker Compose V2${NC}... "
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ Active (${$(docker compose version 2>&1)})${NC}"
else
    echo -e "${RED}✗ Missing (docker compose command failed)${NC}"
    errors=$((errors + 1))
fi

# 3. Check Docker Daemon connection
echo -n -e "Checking ${BOLD}Docker Daemon socket${NC}... "
if docker info &> /dev/null; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Unreachable (Is Docker Desktop running?)${NC}"
    errors=$((errors + 1))
fi

# 4. Check Environment File
echo -n -e "Checking ${BOLD}.env configuration file${NC}... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Configured${NC}"
else
    echo -e "${YELLOW}⚠ Missing (Created from .env.example)${NC}"
    warnings=$((warnings + 1))
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "  -> ${GREEN}Auto-generated .env from .env.example${NC}"
    fi
fi

# 5. Check Required Platform Directories
required_dirs=("docker" "projects" "templates" "scripts" "docs")
for dir in "${required_dirs[@]}"; do
    echo -n -e "Verifying folder ${BOLD}${dir}/${NC}... "
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        mkdir -p "$dir"
        echo -e "${YELLOW}⚠ Created missing directory${NC}"
        warnings=$((warnings + 1))
    fi
done

echo ""
echo -e "${BOLD}${CYAN}====================================================${NC}"
if [ $errors -eq 0 ]; then
    if [ $warnings -eq 0 ]; then
        echo -e "${GREEN}${BOLD}SUCCESS: DevForge environment is healthy and ready!${NC}"
    else
        echo -e "${YELLOW}${BOLD}SUCCESS with warnings: DevForge is configured, but check warnings above.${NC}"
    fi
else
    echo -e "${RED}${BOLD}CRITICAL: DevForge has $errors unresolved diagnostic error(s). Please fix them before proceeding.${NC}"
    exit 1
fi
echo -e "${BOLD}${CYAN}====================================================${NC}"
