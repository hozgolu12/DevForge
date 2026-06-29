#!/usr/bin/env bash

# ==============================================================================
# DEVFORGE PLATFORM RESTORE TOOL
# ==============================================================================
# Unpacks a backup tarball and restores stateful databases to active containers.
# ==============================================================================

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_backup_archive.tar.gz>"
    exit 1
fi

BACKUP_ARCHIVE=$1

if [ ! -f "$BACKUP_ARCHIVE" ]; then
    echo "Error: Backup archive file '$BACKUP_ARCHIVE' not found."
    exit 1
fi

TEMP_DIR="backups/tmp_restore_$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "Extracting backup archive $BACKUP_ARCHIVE..."
tar -xzf "$BACKUP_ARCHIVE" -C "$TEMP_DIR"

# Source environment variables
if [ -f ".env" ]; then
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

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# 1. Restore PostgreSQL
if [ -f "$TEMP_DIR/postgres_backup.sql" ]; then
    if is_running "devforge-postgres"; then
        echo " -> Restoring PostgreSQL..."
        docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$TEMP_DIR/postgres_backup.sql"
        echo "    PostgreSQL restore completed."
    else
        echo " -> Skipping PostgreSQL: container not running."
    fi
fi

# 2. Restore MongoDB
if [ -f "$TEMP_DIR/mongo_backup.archive" ]; then
    if is_running "devforge-mongodb"; then
        echo " -> Restoring MongoDB..."
        docker compose exec -T mongodb mongorestore \
            --username "$MONGO_INITDB_ROOT_USERNAME" \
            --password "$MONGO_INITDB_ROOT_PASSWORD" \
            --authenticationDatabase admin \
            --archive --drop < "$TEMP_DIR/mongo_backup.archive"
        echo "    MongoDB restore completed."
    else
        echo " -> Skipping MongoDB: container not running."
    fi
fi

# 3. Restore Redis
if [ -f "$TEMP_DIR/redis_dump.rdb" ]; then
    if is_running "devforge-redis"; then
        echo " -> Restoring Redis..."
        echo "    Stopping Redis container briefly to restore snapshot..."
        docker compose stop redis
        docker cp "$TEMP_DIR/redis_dump.rdb" devforge-redis:/data/dump.rdb
        docker compose start redis
        echo "    Redis restore completed."
    else
        echo " -> Skipping Redis: container not running."
    fi
fi

# 4. Restore ChromaDB
if [ -d "$TEMP_DIR/chroma_data" ]; then
    if is_running "devforge-chromadb"; then
        echo " -> Restoring ChromaDB..."
        docker cp "$TEMP_DIR/chroma_data/." devforge-chromadb:/chroma/data/
        echo "    ChromaDB restore completed."
    else
        echo " -> Skipping ChromaDB: container not running."
    fi
fi

# Note: Qdrant snapshots can be restored via their REST API. Since Qdrant snapshots are complete DB snapshots,
# the database can import them directly if needed.

echo "===================================================="
echo "SUCCESS: DevForge database restore completed successfully."
echo "===================================================="
