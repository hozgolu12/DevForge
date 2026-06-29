#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE DATABASE RESTORE AUTOMATION SCRIPT
# ==============================================================================
# Restores DevForge database states from a specified backup folder.
# Usage: ./scripts/db-restore.sh backups/YYYYMMDD_HHMMSS
# ==============================================================================

set -euo pipefail

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

TARGET_BACKUP_DIR=${1:-""}

if [ -z "$TARGET_BACKUP_DIR" ]; then
    echo "ERROR: Please specify a backup directory path."
    echo "Usage: ./scripts/db-restore.sh backups/YYYYMMDD_HHMMSS"
    exit 1
fi

if [ ! -d "$TARGET_BACKUP_DIR" ]; then
    echo "ERROR: Backup directory '$TARGET_BACKUP_DIR' does not exist."
    exit 1
fi

echo "Initializing database restoration from: $TARGET_BACKUP_DIR"

# 1. PostgreSQL Restore
if [ -f "${TARGET_BACKUP_DIR}/postgres_backup.sql" ]; then
    echo "Restoring PostgreSQL database..."
    if docker compose ps | grep -q "postgres"; then
        # Drop existing connection and recreate database tables
        docker compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" > /dev/null
        docker compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" < "${TARGET_BACKUP_DIR}/postgres_backup.sql" > /dev/null
        echo "PostgreSQL restoration complete."
    else
        echo "ERROR: PostgreSQL service is not running. Failed to restore."
    fi
else
    echo "PostgreSQL backup file not found. Skipped."
fi

# 2. MongoDB Restore
if [ -f "${TARGET_BACKUP_DIR}/mongo_backup.archive" ]; then
    echo "Restoring MongoDB database..."
    if docker compose ps | grep -q "mongodb"; then
        docker compose exec -T mongodb mongorestore \
            --username "${MONGO_INITDB_ROOT_USERNAME}" \
            --password "${MONGO_INITDB_ROOT_PASSWORD}" \
            --authenticationDatabase admin \
            --drop \
            --archive < "${TARGET_BACKUP_DIR}/mongo_backup.archive" > /dev/null
        echo "MongoDB restoration complete."
    else
        echo "ERROR: MongoDB service is not running. Failed to restore."
    fi
else
    echo "MongoDB backup file not found. Skipped."
fi

# 3. Redis Restore
if [ -f "${TARGET_BACKUP_DIR}/redis_backup.rdb" ]; then
    echo "Restoring Redis cache..."
    if docker compose ps | grep -q "redis"; then
        echo "Stopping Redis service to replace memory cache database..."
        docker compose stop redis > /dev/null
        docker compose cp "${TARGET_BACKUP_DIR}/redis_backup.rdb" redis:/data/dump.rdb
        docker compose start redis > /dev/null
        echo "Redis restoration complete."
    else
        echo "ERROR: Redis service is not running. Failed to restore."
    fi
else
    echo "Redis backup file not found. Skipped."
fi

# 4. Neo4j Restore
if [ -f "${TARGET_BACKUP_DIR}/neo4j_data_backup.tar.gz" ]; then
    echo "Restoring Neo4j Graph database..."
    if docker compose ps | grep -q "neo4j"; then
        echo "Stopping Neo4j service to overwrite files..."
        docker compose stop neo4j > /dev/null
        # Extract files inside the running target container volume path
        # Wait, since container is stopped, we can temporarily start a helper or extract via volume path,
        # or start container, copy archive, extract, and restart. Let's do start-copy-extract:
        docker compose start neo4j > /dev/null
        docker compose cp "${TARGET_BACKUP_DIR}/neo4j_data_backup.tar.gz" neo4j:/tmp/neo4j_backup.tar.gz
        docker compose exec -T neo4j sh -c "rm -rf /data/* && tar -xzf /tmp/neo4j_backup.tar.gz -C /data && rm /tmp/neo4j_backup.tar.gz"
        docker compose restart neo4j > /dev/null
        echo "Neo4j restoration complete."
    else
        echo "ERROR: Neo4j service is not running. Failed to restore."
    fi
else
    echo "Neo4j backup archive not found. Skipped."
fi

echo "SUCCESS: Database restoration operations completed."
