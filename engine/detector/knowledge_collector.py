# ==============================================================================
# DEVFORGE KNOWLEDGE COLLECTOR
# ==============================================================================
# Holds static structural knowledge about developer technologies. Enriching prompts
# with default ports, images, and variables ensures higher quality AI results.
# ==============================================================================

from typing import Any, Dict


class KnowledgeCollector:
    """Enriches plugin prompts with standard technical details for known technologies."""

    # Static catalog of popular developer services
    KNOWLEDGE_BASE = {
        "supabase": {
            "documentation_url": "https://supabase.com/docs",
            "github_repository": "https://github.com/supabase/supabase",
            "docker_image": "supabase/postgres",
            "default_ports": [54321],
            "default_env": {
                "POSTGRES_PASSWORD": "postgres_password_change_me",
                "JWT_SECRET": "supabase_jwt_secret_change_me_in_prod",
            },
            "health_endpoint": "/health",
            "dependencies": ["postgres"],
            "category": "database",
            "description": "Supabase is an open source Firebase alternative providing database, auth, and storage.",
        },
        "pgvector": {
            "documentation_url": "https://github.com/pgvector/pgvector",
            "github_repository": "https://github.com/pgvector/pgvector",
            "docker_image": "pgvector/pgvector",
            "default_ports": [5432],
            "default_env": {
                "POSTGRES_DB": "vectordb",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres_password_change_me",
            },
            "health_endpoint": None,
            "dependencies": ["postgres"],
            "category": "vector-db",
            "description": "Open-source vector similarity search for Postgres, supporting L2 distance, cosine distance, and inner product.",
        },
        "milvus": {
            "documentation_url": "https://milvus.io/docs",
            "github_repository": "https://github.com/milvus-io/milvus",
            "docker_image": "milvusdb/milvus",
            "default_ports": [19530, 9091],
            "default_env": {
                "ETCD_ENDPOINTS": "etcd:2379",
                "MINIO_ADDRESS": "minio:9000",
            },
            "health_endpoint": "/healthz",
            "dependencies": ["etcd", "minio"],
            "category": "vector-db",
            "description": "Milvus is an open-source vector database built to power AI applications and similarity search.",
        },
        "temporal": {
            "documentation_url": "https://docs.temporal.io",
            "github_repository": "https://github.com/temporalio/temporal",
            "docker_image": "temporalio/auto-setup",
            "default_ports": [7233, 8233],
            "default_env": {
                "DB": "postgresql",
                "DB_PORT": "5432",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PWD": "postgres_password_change_me",
                "BIND_ON_IP": "0.0.0.0",
            },
            "health_endpoint": "/health",
            "dependencies": ["postgres"],
            "category": "service",
            "description": "Temporal orchestrates workflow-centric applications, ensuring reliable microservices orchestration.",
        },
        "appwrite": {
            "documentation_url": "https://appwrite.io/docs",
            "github_repository": "https://github.com/appwrite/appwrite",
            "docker_image": "appwrite/appwrite",
            "default_ports": [80, 443],
            "default_env": {
                "_APP_ENV": "development",
                "_APP_OPENSSL_KEY_V1": "secret-key",
            },
            "health_endpoint": "/v1/health",
            "dependencies": ["redis", "mariadb"],
            "category": "service",
            "description": "Appwrite is an open-source backend-as-a-service platform for web, mobile, and flutter developers.",
        },
        "convex": {
            "documentation_url": "https://docs.convex.dev",
            "github_repository": "https://github.com/convex-dev/convex",
            "docker_image": "convex-dev/convex",
            "default_ports": [3210],
            "default_env": {},
            "health_endpoint": None,
            "dependencies": [],
            "category": "service",
            "description": "Convex is a reactive backend platform for fullstack applications.",
        },
        "meilisearch": {
            "documentation_url": "https://docs.meilisearch.com",
            "github_repository": "https://github.com/meilisearch/meilisearch",
            "docker_image": "getmeili/meilisearch",
            "default_ports": [7700],
            "default_env": {
                "MEILI_ENV": "development",
                "MEILI_MASTER_KEY": "meilisearch_master_key_change_me_in_prod",
            },
            "health_endpoint": "/health",
            "dependencies": [],
            "category": "service",
            "description": "Meilisearch is a lightning-fast, ultra-relevant search engine designed for building instant search experiences.",
        },
        "typesense": {
            "documentation_url": "https://typesense.org/docs",
            "github_repository": "https://github.com/typesense/typesense",
            "docker_image": "typesense/typesense",
            "default_ports": [8108],
            "default_env": {
                "TYPESENSE_API_KEY": "typesense_api_key_change_me_in_prod",
                "TYPESENSE_DATA_DIR": "/data",
            },
            "health_endpoint": "/health",
            "dependencies": [],
            "category": "service",
            "description": "Typesense is a fast, typo-tolerant search engine built for developers.",
        },
    }

    @classmethod
    def collect(cls, technology_name: str) -> Dict[str, Any]:
        """
        Retrieves known characteristics for a technology name.
        Uses fallback defaults if the technology is completely new to the registry.
        """
        tech_key = technology_name.lower().strip()

        # Try exact or partial matches in the knowledge base
        matched_info = None
        for key, info in cls.KNOWLEDGE_BASE.items():
            if key in tech_key or tech_key in key:
                matched_info = info
                break

        if matched_info:
            return matched_info

        # Safe fallback assumptions for unknown technologies
        category = "service"
        if any(db_word in tech_key for db_word in ("db", "sql", "store", "cache", "search", "vector")):
            category = "database"

        return {
            "documentation_url": f"https://github.com/search?q={technology_name}",
            "github_repository": f"https://github.com/{tech_key}/{tech_key}",
            "docker_image": f"{tech_key}/{tech_key}",
            "default_ports": [8080],
            "default_env": {
                f"{technology_name.upper().replace('-', '_')}_ENV": "development"
            },
            "health_endpoint": None,
            "dependencies": [],
            "category": category,
            "description": f"AI-generated plugin for {technology_name} service integration.",
        }
