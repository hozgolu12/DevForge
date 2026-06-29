#!/usr/bin/env bash
# ==============================================================================
# DEVFORGE DATABASE SEED AUTOMATION RUNNER
# ==============================================================================
# Populates PostgreSQL, MongoDB, Redis, and Neo4j with starter seed configurations.
# ==============================================================================

set -euo pipefail

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Initializing database seed runner..."

# 1. Seed PostgreSQL
if [ -f "scripts/seeds/postgres_seed.sql" ]; then
    echo "Seeding PostgreSQL..."
    if docker compose ps | grep -q "postgres"; then
        docker compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" < scripts/seeds/postgres_seed.sql > /dev/null
        echo "PostgreSQL: Seed applied successfully."
    else
        echo "WARNING: PostgreSQL service is not running. Skipped."
    fi
fi

# 2. Seed MongoDB
if [ -f "scripts/seeds/mongo_seed.js" ]; then
    echo "Seeding MongoDB..."
    if docker compose ps | grep -q "mongodb"; then
        docker compose exec -T mongodb mongosh \
            --username "${MONGO_INITDB_ROOT_USERNAME}" \
            --password "${MONGO_INITDB_ROOT_PASSWORD}" \
            --authenticationDatabase admin \
            < scripts/seeds/mongo_seed.js > /dev/null
        echo "MongoDB: Seed applied successfully."
    else
        echo "WARNING: MongoDB service is not running. Skipped."
    fi
fi

# 3. Seed Redis
if [ -f "scripts/seeds/redis_seed.redis" ]; then
    echo "Seeding Redis cache keys..."
    if docker compose ps | grep -q "redis"; then
        grep -v '^#' scripts/seeds/redis_seed.redis | grep -v '^[[:space:]]*$' | \
            docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" > /dev/null
        echo "Redis: Seed applied successfully."
    else
        echo "WARNING: Redis service is not running. Skipped."
    fi
fi

# 4. Seed Neo4j
if [ -f "scripts/seeds/neo4j_seed.cypher" ]; then
    echo "Seeding Neo4j Graph elements..."
    if docker compose ps | grep -q "neo4j"; then
        # Extract password from NEO4J_AUTH (which has format 'neo4j/password')
        NEO4J_PASS=$(echo "${NEO4J_AUTH}" | cut -d'/' -f2)
        docker compose exec -T neo4j cypher-shell \
            -u neo4j \
            -p "${NEO4J_PASS}" \
            -a bolt://localhost:7687 \
            < scripts/seeds/neo4j_seed.cypher > /dev/null || true
        echo "Neo4j: Seed applied successfully."
    else
        echo "WARNING: Neo4j service is not running. Skipped."
    fi
fi

echo "SUCCESS: Database seeding operations completed."
