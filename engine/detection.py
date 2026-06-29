# ==============================================================================
# DEVFORGE DETECTION ENGINE
# ==============================================================================
# Analyzes the workspace/project directory using multi-layer heuristics to
# identify frameworks, databases, caches, AI libraries, message queues, etc.
# Stores results in memory and caches to .devforge/cache/detection.json.
# ==============================================================================

import json
import os
from pathlib import Path
from typing import Optional, Any
import yaml

class DetectionEngine:
    """Reusable detection engine that scans and identifies project technologies."""

    # In-memory cache
    _cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def detect(cls, project_path: Path, force: bool = False) -> dict[str, Any]:
        """
        Scan the project directory. Checks memory and file cache unless force=True.
        """
        path_str = str(project_path.resolve())
        
        if not force and path_str in cls._cache:
            return cls._cache[path_str]

        # Check disk cache
        cache_file = project_path / ".devforge" / "cache" / "detection.json"
        if not force and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                cls._cache[path_str] = cached_data
                return cached_data
            except Exception:
                pass

        # Perform actual detection
        results = cls._perform_detection(project_path)
        cls._cache[path_str] = results

        # Save to disk cache if .devforge/cache directory exists
        if (project_path / ".devforge" / "cache").exists():
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
            except Exception:
                pass

        return results

    @classmethod
    def _perform_detection(cls, project_path: Path) -> dict[str, Any]:
        results = {
            "Frontend": {},
            "Backend": {},
            "Mobile": {},
            "Database": {},
            "Cache": {},
            "Vector Database": {},
            "AI": {},
            "Messaging": {},
            "Monitoring": {},
            "Storage": {},
            "Docker": {},
            "Package Managers": {},
            "Recommendations": []
        }

        # Subdirectory and file collection
        ignore_dirs = {
            ".git", "node_modules", ".venv", "venv", "env", 
            ".devforge", "build", "dist", "target", "bin", "obj", 
            "out", ".idea", ".vscode"
        }

        all_files = []
        package_jsons = []
        requirements_files = []
        pubspecs = []
        pom_xmls = []
        gradle_files = []
        csproj_files = []
        dockerfiles = []
        compose_files = []
        python_files = []
        js_ts_files = []

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                filepath = Path(root) / file
                all_files.append(filepath)

                # Check filenames
                file_lower = file.lower()
                if file == "package.json":
                    package_jsons.append(filepath)
                elif file in ("requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock"):
                    requirements_files.append(filepath)
                elif file == "pubspec.yaml":
                    pubspecs.append(filepath)
                elif file == "pom.xml":
                    pom_xmls.append(filepath)
                elif file in ("build.gradle", "build.gradle.kts"):
                    gradle_files.append(filepath)
                elif file.endswith(".csproj"):
                    csproj_files.append(filepath)
                elif file_lower == "dockerfile" or "dockerfile" in file_lower:
                    dockerfiles.append(filepath)
                elif file in ("docker-compose.yml", "docker-compose.yaml"):
                    compose_files.append(filepath)
                elif file.endswith(".py"):
                    python_files.append(filepath)
                elif file.endswith((".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte")):
                    js_ts_files.append(filepath)

        # Parse package.json dependencies
        js_deps = set()
        for pj in package_jsons:
            try:
                with open(pj, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key in ("dependencies", "devDependencies"):
                        deps = data.get(key, {})
                        if isinstance(deps, dict):
                            js_deps.update(deps.keys())
            except Exception:
                pass

        # Parse python dependencies
        py_deps = set()
        for req in requirements_files:
            try:
                with open(req, "r", encoding="utf-8", errors="ignore") as f:
                    if req.name == "requirements.txt":
                        for line in f:
                            cleaned = line.strip().split("#")[0].strip()
                            if not cleaned:
                                continue
                            # Extract base dependency name
                            dep_name = cleaned.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip().lower()
                            if dep_name:
                                py_deps.add(dep_name)
                    elif req.name == "pyproject.toml":
                        # Simple word checking
                        content = f.read()
                        for line in content.splitlines():
                            if "=" in line:
                                left = line.split("=")[0].strip().strip('"').strip("'").lower()
                                if left:
                                    py_deps.add(left)
            except Exception:
                pass

        # Parse pubspec.yaml
        pub_deps = set()
        for ps in pubspecs:
            try:
                with open(ps, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        deps = data.get("dependencies", {})
                        if isinstance(deps, dict):
                            pub_deps.update(deps.keys())
            except Exception:
                pass

        # Parse java/maven/gradle content
        java_content = ""
        for pom in pom_xmls:
            try:
                with open(pom, "r", encoding="utf-8", errors="ignore") as f:
                    java_content += f.read()
            except Exception:
                pass
        for grad in gradle_files:
            try:
                with open(grad, "r", encoding="utf-8", errors="ignore") as f:
                    java_content += f.read()
            except Exception:
                pass

        # --------------------------------------------------
        # HEURISTICS: Frontend
        # --------------------------------------------------
        if "react" in js_deps or any("react" in str(p).lower() for p in js_ts_files[:20]):
            results["Frontend"]["React"] = True
        if "next" in js_deps or any("next.config" in p.name for p in all_files):
            results["Frontend"]["Next.js"] = True
        if "vue" in js_deps or any(p.suffix == ".vue" for p in js_ts_files[:20]):
            results["Frontend"]["Vue"] = True
        if "@angular/core" in js_deps or any("angular.json" in p.name for p in all_files):
            results["Frontend"]["Angular"] = True
        if "svelte" in js_deps or any("svelte.config" in p.name for p in all_files):
            results["Frontend"]["Svelte"] = True

        # --------------------------------------------------
        # HEURISTICS: Backend
        # --------------------------------------------------
        if "@nestjs/core" in js_deps or any("nest-cli.json" in p.name for p in all_files):
            results["Backend"]["NestJS"] = True
        if "express" in js_deps and not results["Backend"].get("NestJS"):
            results["Backend"]["Express"] = True
        if "fastapi" in py_deps or any(cls._file_contains(p, ["from fastapi import", "FastAPI("]) for p in python_files[:15]):
            results["Backend"]["FastAPI"] = True
        if "flask" in py_deps or any(cls._file_contains(p, ["from flask import", "Flask("]) for p in python_files[:15]):
            results["Backend"]["Flask"] = True
        if "django" in py_deps or any("manage.py" in p.name for p in all_files):
            results["Backend"]["Django"] = True
        if "spring-boot" in java_content or "org.springframework.boot" in java_content:
            results["Backend"]["Spring Boot"] = True
        if csproj_files or any(cls._file_contains(p, ["WebApplication.CreateBuilder"]) for p in all_files if p.name == "Program.cs"):
            results["Backend"]["ASP.NET Core"] = True

        # --------------------------------------------------
        # HEURISTICS: Mobile
        # --------------------------------------------------
        if "flutter" in pub_deps or pubspecs:
            results["Mobile"]["Flutter"] = True
        elif any("AndroidManifest.xml" in p.name for p in all_files):
            results["Mobile"]["Android"] = True

        # --------------------------------------------------
        # HEURISTICS: Databases
        # --------------------------------------------------
        if "mongodb" in js_deps or "mongoose" in js_deps or "pymongo" in py_deps or "motor" in py_deps:
            results["Database"]["MongoDB"] = True
        if "pg" in js_deps or "sequelize" in js_deps or "typeorm" in js_deps or "psycopg2" in py_deps or "psycopg" in py_deps or "asyncpg" in py_deps or "postgresql" in java_content:
            results["Database"]["PostgreSQL"] = True
        if "mysql" in js_deps or "mysql2" in js_deps or "mysqlclient" in py_deps or "pymysql" in py_deps:
            results["Database"]["MySQL"] = True
        if "mariadb" in js_deps or "mariadb" in py_deps:
            results["Database"]["MariaDB"] = True
        if "neo4j-driver" in js_deps or "neo4j" in py_deps:
            results["Database"]["Neo4j"] = True

        # --------------------------------------------------
        # HEURISTICS: Cache
        # --------------------------------------------------
        if "redis" in js_deps or "ioredis" in js_deps or "redis" in py_deps:
            results["Cache"]["Redis"] = True

        # --------------------------------------------------
        # HEURISTICS: Vector Database
        # --------------------------------------------------
        if "chromadb" in py_deps or "chromadb" in js_deps or any(cls._file_contains(p, ["import chromadb"]) for p in python_files[:15]):
            results["Vector Database"]["ChromaDB"] = True
        if "qdrant-client" in py_deps or "@qdrant/js-client-rest" in js_deps or any(cls._file_contains(p, ["QdrantClient"]) for p in python_files[:15]):
            results["Vector Database"]["Qdrant"] = True
        if "pymilvus" in py_deps or "@zilliz/milvus2-sdk-node" in js_deps:
            results["Vector Database"]["Milvus"] = True
        if "weaviate-client" in py_deps or "weaviate-client" in js_deps:
            results["Vector Database"]["Weaviate"] = True

        # --------------------------------------------------
        # HEURISTICS: AI
        # --------------------------------------------------
        if "openai" in py_deps or "openai" in js_deps:
            results["AI"]["OpenAI"] = True
        if "ollama" in py_deps or "ollama" in js_deps:
            results["AI"]["Ollama"] = True
        if "langchain" in py_deps or "langchain" in js_deps or "langchain-core" in py_deps:
            results["AI"]["LangChain"] = True
        if "llama-index" in py_deps or "llamaindex" in js_deps:
            results["AI"]["LlamaIndex"] = True
        if "transformers" in py_deps or "huggingface_hub" in py_deps:
            results["AI"]["HuggingFace"] = True
        if "openai-whisper" in py_deps or "whisper" in py_deps:
            results["AI"]["Whisper"] = True
        if "pytesseract" in py_deps or "tesseract" in py_deps:
            results["AI"]["Tesseract"] = True

        # --------------------------------------------------
        # HEURISTICS: Messaging
        # --------------------------------------------------
        if "amqplib" in js_deps or "pika" in py_deps:
            results["Messaging"]["RabbitMQ"] = True
        if "kafkajs" in js_deps or "kafka-python" in py_deps or "confluent-kafka" in py_deps:
            results["Messaging"]["Kafka"] = True

        # --------------------------------------------------
        # HEURISTICS: Monitoring
        # --------------------------------------------------
        if "prom-client" in js_deps or "prometheus-client" in py_deps or any("prometheus.yml" in p.name for p in all_files):
            results["Monitoring"]["Prometheus"] = True
        if any("grafana" in str(p).lower() for p in all_files):
            results["Monitoring"]["Grafana"] = True
        if any("loki" in str(p).lower() for p in all_files):
            results["Monitoring"]["Loki"] = True

        # --------------------------------------------------
        # HEURISTICS: Storage
        # --------------------------------------------------
        if "minio" in js_deps or "minio" in py_deps:
            results["Storage"]["MinIO"] = True

        # --------------------------------------------------
        # HEURISTICS: Docker
        # --------------------------------------------------
        if dockerfiles:
            results["Docker"]["Dockerfile"] = True
        if compose_files:
            results["Docker"]["docker-compose.yml"] = True

        # --------------------------------------------------
        # HEURISTICS: Package Managers
        # --------------------------------------------------
        if package_jsons:
            results["Package Managers"]["npm"] = True
        if requirements_files:
            results["Package Managers"]["pip"] = True
        if pubspecs:
            results["Package Managers"]["pub"] = True

        # --------------------------------------------------
        # RECOMMENDATIONS GENERATION
        # --------------------------------------------------
        db_detected = len(results["Database"]) > 0 or len(results["Cache"]) > 0 or len(results["Vector Database"]) > 0
        if db_detected and not results["Monitoring"].get("Grafana"):
            results["Recommendations"].append("Grafana recommended")
        if (results["Backend"].get("NestJS") or results["Backend"].get("Express")) and not results["Messaging"].get("RabbitMQ"):
            results["Recommendations"].append("RabbitMQ optional")

        # Cleanup empty categories
        for cat in list(results.keys()):
            if cat != "Recommendations" and isinstance(results[cat], dict) and not results[cat]:
                del results[cat]

        return results

    @staticmethod
    def _file_contains(filepath: Path, keywords: list[str]) -> bool:
        """Helper to scan a file for specific keywords."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return any(kw in content for kw in keywords)
        except Exception:
            return False
