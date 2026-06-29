#!/usr/bin/env bash

# ==============================================================================
# DEVFORGE PLATFORM BACKUP TOOL
# ==============================================================================
# Runs native hot-backups on active containers and stores them in the backups/ dir.
# ==============================================================================

set -euo pipefail

BACKUP_DIR="backups/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting DevForge platform backups into: $BACKUP_DIR"

# Source active env vars if available
if [ -f ".env" ]; then
    # Load variables excluding comments
    export $(grep -v '^#' .env | xargs)
fi

# Helper to check if a container is running
is_running() {
    local container_name=$1
    if [ "$(docker ps -q -f name="$container_name")" ]; then
        return 0
    else
        return 1
    fi
}

# 1. PostgreSQL Backup
if is_running "devforge-postgres"; then
    echo " -> Backing up PostgreSQL..."
    docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/postgres_backup.sql"
    echo "    PostgreSQL backup completed."
else
    echo " -> Skipping PostgreSQL: container not running."
fi

# 2. MongoDB Backup
if is_running "devforge-mongodb"; then
    echo " -> Backing up MongoDB..."
    docker compose exec -T mongodb mongodump \
        --username "$MONGO_INITDB_ROOT_USERNAME" \
        --password "$MONGO_INITDB_ROOT_PASSWORD" \
        --authenticationDatabase admin \
        --archive > "$BACKUP_DIR/mongo_backup.archive"
    echo "    MongoDB backup completed."
else
    echo " -> Skipping MongoDB: container not running."
fi

# 3. Redis Backup
if is_running "devforge-redis"; then
    echo " -> Backing up Redis..."
    # Force background save
    docker compose exec -T redis redis-cli -a "$REDIS_PASSWORD" SAVE > /dev/null
    # Copy RDB snapshot file out of container
    docker cp devforge-redis:/data/dump.rdb "$BACKUP_DIR/redis_dump.rdb"
    echo "    Redis backup completed."
else
    echo " -> Skipping Redis: container not running."
fi

# 4. Qdrant Backup
if is_running "devforge-qdrant"; then
    echo " -> Backing up Qdrant Vector DB..."
    # Request snapshot via REST API
    SNAPSHOT_INFO=$(curl -s -X POST -H "api-key: $QDRANT_API_KEY" http://localhost:6333/snapshots)
    SNAPSHOT_NAME=$(echo "$SNAPSHOT_INFO" | jq -r '.result.name')
    if [ "$SNAPSHOT_NAME" != "null" ]; then
        # Download snapshot from container local filesystem
        docker cp "devforge-qdrant:/qdrant/storage/snapshots/$SNAPSHOT_NAME" "$BACKUP_DIR/$SNAPSHOT_NAME"
        echo "    Qdrant snapshot completed: $SNAPSHOT_NAME"
    else
        echo "    Failed to trigger Qdrant snapshot: $SNAPSHOT_INFO"
    fi
else
    echo " -> Skipping Qdrant: container not running."
fi

# 5. ChromaDB Backup
if is_running "devforge-chromadb"; then
    echo " -> Backing up ChromaDB SQLite storage..."
    # Safe copy since ChromaDB is sqlite-backed
    docker cp devforge-chromadb:/chroma/data "$BACKUP_DIR/chroma_data"
    echo "    ChromaDB backup completed."
else
    echo " -> Skipping ChromaDB: container not running."
fi

# Compress all backups
echo "Compressing backups..."
tar -czf "${BACKUP_DIR}.tar.gz" -C "$BACKUP_DIR" .
rm -rf "$BACKUP_DIR"

echo "===================================================="
echo "SUCCESS: DevForge backups saved to ${BACKUP_DIR}.tar.gz"
echo "===================================================="
