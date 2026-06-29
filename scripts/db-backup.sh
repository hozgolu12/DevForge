#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE DATABASE BACKUP AUTOMATION SCRIPT
# ==============================================================================
# Backs up active DevForge database services to the local backups/ directory.
# ==============================================================================

set -euo pipefail

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

BACKUP_PARENT_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_PARENT_DIR}/${TIMESTAMP}"

echo "Initializing DevForge database backup..."
mkdir -p "$BACKUP_DIR"

# 1. PostgreSQL Backup
echo "Backing up PostgreSQL database..."
if docker compose ps | grep -q "postgres"; then
    docker compose exec -T postgres pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" > "${BACKUP_DIR}/postgres_backup.sql"
    echo "PostgreSQL backup completed: ${BACKUP_DIR}/postgres_backup.sql"
else
    echo "WARNING: PostgreSQL service is not running. Skipped."
fi

# 2. MongoDB Backup
echo "Backing up MongoDB database..."
if docker compose ps | grep -q "mongodb"; then
    docker compose exec -T mongodb mongodump \
        --username "${MONGO_INITDB_ROOT_USERNAME}" \
        --password "${MONGO_INITDB_ROOT_PASSWORD}" \
        --authenticationDatabase admin \
        --archive > "${BACKUP_DIR}/mongo_backup.archive"
    echo "MongoDB backup completed: ${BACKUP_DIR}/mongo_backup.archive"
else
    echo "WARNING: MongoDB service is not running. Skipped."
fi

# 3. Redis Backup
echo "Backing up Redis cache..."
if docker compose ps | grep -q "redis"; then
    # Force saving snapshot first
    docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" save > /dev/null 2>&1 || true
    # Copy RDB file from container
    docker compose cp redis:/data/dump.rdb "${BACKUP_DIR}/redis_backup.rdb"
    echo "Redis backup completed: ${BACKUP_DIR}/redis_backup.rdb"
else
    echo "WARNING: Redis service is not running. Skipped."
fi

# 4. Neo4j Backup
echo "Backing up Neo4j Graph Database (APOC Export)..."
if docker compose ps | grep -q "neo4j"; then
    # We can export database structure and nodes using cypher shell or copying data
    docker compose exec -T neo4j tar -czf - -C /data . > "${BACKUP_DIR}/neo4j_data_backup.tar.gz" || true
    echo "Neo4j database files tar backup completed: ${BACKUP_DIR}/neo4j_data_backup.tar.gz"
else
    echo "WARNING: Neo4j service is not running. Skipped."
fi

echo "SUCCESS: Database backups stored in: ${BACKUP_DIR}"
