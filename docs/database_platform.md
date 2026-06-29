# DevForge Database Platform Operations Guide

This guide details active configurations, connections, credentials, administrative web UIs, and automation utilities for the DevForge database platform.

---

## 1. Database Connections & Internal Networking

All databases are connected via the internal bridge network `devforge-network`. Workspace services must connect using the internal service DNS names and ports:

| Database | Service Name | Internal Port | External Port | Default DB/Auth Scheme |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL** | `postgres` | `5432` | `5432` | `postgresql://postgres:postgres@postgres:5432/devforge` |
| **MongoDB** | `mongodb` | `27017` | `27017` | `mongodb://admin:admin@mongodb:27017/devforge` |
| **Redis** | `redis` | `6379` | `6379` | `redis://:admin@redis:6379/0` |
| **Neo4j** | `neo4j` | `7474` (HTTP) / `7687` (Bolt) | `7474` / `7687` | `bolt://neo4j:neo4j@neo4j:7687` |
| **Qdrant** | `qdrant` | `6333` (HTTP) / `6334` (gRPC) | `6333` / `6334` | `http://qdrant:6333` (with X-API-KEY header) |
| **ChromaDB** | `chromadb` | `8000` | `8000` | `http://chromadb:8000` (with authorization token header) |

---

## 2. Administrative Web UIs

DevForge deploys optional, lightweight admin UIs to manage database schemas, documents, and keys.

### UI Reference table

| UI Service | DB Managed | Access URL | Credentials |
| :--- | :--- | :--- | :--- |
| **pgAdmin 4** | PostgreSQL | `http://localhost:5050` | User: `admin@devforge.local` / Pass: `admin` |
| **Mongo Express** | MongoDB | `http://localhost:8087` | User: `admin` / Pass: `admin` |
| **Redis Commander** | Redis | `http://localhost:8086` | Auto-authenticates via container env |
| **Neo4j Browser** | Neo4j | `http://localhost:7474` | User: `neo4j` / Pass: `neo4j` |
| **Qdrant Dashboard** | Qdrant | `http://localhost:6333/dashboard/` | Accessible via token/direct |

---

## 3. Database Seeding

To populate your database with starter tables, collections, key-value pairs, and graph networks:
```bash
# Seeding PostgreSQL, MongoDB, Redis, and Neo4j
./scripts/db-seed.sh
```

### Seed scripts location
- `scripts/seeds/postgres_seed.sql`: Creates `users` and `tasks` tables and inserts records.
- `scripts/seeds/mongo_seed.js`: Drops and populates the `projects` collection in the `devforge` database.
- `scripts/seeds/redis_seed.redis`: Seeds system keys and active port configurations.
- `scripts/seeds/neo4j_seed.cypher`: Creates integrated node relationships matching the DevForge architecture.

---

## 4. Backups and Restores

DevForge provides simple, automated bash scripts to manage database states.

### Backing Up Databases
Run the backup script to capture snapshots of all active databases:
```bash
./scripts/db-backup.sh
```
This saves timestamped dump archives in the local `backups/` directory (e.g. `backups/20260629_120000/`).

### Restoring Database State
Restore databases from a snapshot by specifying the directory name:
```bash
./scripts/db-restore.sh backups/YYYYMMDD_HHMMSS
```
*Note: The restore script drops existing target schemas/collections and replaces them with the archive content.*
