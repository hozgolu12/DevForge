# ==============================================================================
# DEVFORGE METADATA COLLECTOR
# ==============================================================================
# Scans the active project to extract languages, dependencies, and environment
# context. This helps the AI customize the generated plugin.
# ==============================================================================

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
import yaml


class MetadataCollector:
    """Scans and collects project metadata."""

    @staticmethod
    def collect(project_path: Path) -> Dict[str, Any]:
        """
        Inspect standard project configuration files and extract metadata.
        """
        metadata = {
            "packages": [],
            "languages": [],
            "frameworks": [],
            "ports": [],
            "environment_variables": [],
            "docker_images": [],
            "github_urls": [],
            "raw_text_snippets": {},
        }

        # 1. Parse package.json (Node/JS)
        pj = project_path / "package.json"
        if pj.exists():
            try:
                metadata["languages"].append("JavaScript/TypeScript")
                with open(pj, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata["packages"].extend(list(data.get("dependencies", {}).keys()))
                    metadata["packages"].extend(list(data.get("devDependencies", {}).keys()))
                    if "repository" in data:
                        repo = data["repository"]
                        if isinstance(repo, dict) and "url" in repo:
                            metadata["github_urls"].append(repo["url"])
                        elif isinstance(repo, str):
                            metadata["github_urls"].append(repo)
            except Exception:
                pass

        # 2. Parse requirements.txt (Python)
        reqs = project_path / "requirements.txt"
        if reqs.exists():
            try:
                metadata["languages"].append("Python")
                with open(reqs, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            dep = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                            if dep:
                                metadata["packages"].append(dep)
            except Exception:
                pass

        # 3. Parse pyproject.toml (Python Poetry/Flit)
        pyproj = project_path / "pyproject.toml"
        if pyproj.exists():
            try:
                metadata["languages"].append("Python")
                content = pyproj.read_text(encoding="utf-8", errors="ignore")
                deps = re.findall(r'^[a-zA-Z0-9_-]+\s*=\s*[\{\"\']', content, re.MULTILINE)
                for dep in deps:
                    name = dep.split("=")[0].strip()
                    metadata["packages"].append(name)
            except Exception:
                pass

        # 4. Parse Cargo.toml (Rust)
        cargo = project_path / "Cargo.toml"
        if cargo.exists():
            try:
                metadata["languages"].append("Rust")
                content = cargo.read_text(encoding="utf-8", errors="ignore")
                deps = re.findall(r'^([a-zA-Z0-9_-]+)\s*=\s*', content, re.MULTILINE)
                metadata["packages"].extend(deps)
            except Exception:
                pass

        # 5. Parse go.mod (Go)
        gomod = project_path / "go.mod"
        if gomod.exists():
            try:
                metadata["languages"].append("Go")
                content = gomod.read_text(encoding="utf-8", errors="ignore")
                deps = re.findall(r'^\s*([a-zA-Z0-9_\-\./]+)\s+v[0-9]', content, re.MULTILINE)
                metadata["packages"].extend(deps)
            except Exception:
                pass

        # 6. Parse composer.json (PHP)
        composer = project_path / "composer.json"
        if composer.exists():
            try:
                metadata["languages"].append("PHP")
                with open(composer, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata["packages"].extend(list(data.get("require", {}).keys()))
            except Exception:
                pass

        # 7. Java checks
        if (project_path / "pom.xml").exists():
            metadata["languages"].append("Java")
        if (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists():
            metadata["languages"].append("Java/Kotlin")

        # 8. Scan for Dockerfiles and Compose Files
        for root, dirs, files in os.walk(project_path):
            # Skip build and system directories
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "venv", "env", ".devforge"}]
            for file in files:
                if "dockerfile" in file.lower():
                    df_path = Path(root) / file
                    try:
                        content = df_path.read_text(encoding="utf-8", errors="ignore")
                        from_matches = re.findall(r'^\s*FROM\s+(\S+)', content, re.IGNORECASE | re.MULTILINE)
                        for fm in from_matches:
                            metadata["docker_images"].append(fm)
                        expose_matches = re.findall(r'^\s*EXPOSE\s+(\d+)', content, re.IGNORECASE | re.MULTILINE)
                        for em in expose_matches:
                            metadata["ports"].append(int(em))
                        env_matches = re.findall(r'^\s*ENV\s+(\w+)', content, re.IGNORECASE | re.MULTILINE)
                        for envm in env_matches:
                            metadata["environment_variables"].append(envm)
                    except Exception:
                        pass
                elif file in ("docker-compose.yml", "docker-compose.yaml", "compose.yaml"):
                    compose_path = Path(root) / file
                    try:
                        content = compose_path.read_text(encoding="utf-8", errors="ignore")
                        data = yaml.safe_load(content) or {}
                        if isinstance(data, dict) and "services" in data:
                            for svc in data["services"].values():
                                if isinstance(svc, dict):
                                    if "image" in svc:
                                        metadata["docker_images"].append(svc["image"])
                                    if "ports" in svc:
                                        for p in svc["ports"]:
                                            if isinstance(p, str):
                                                port_part = p.split(":")[-1]
                                                port_digits = re.findall(r'\d+', port_part)
                                                if port_digits:
                                                    metadata["ports"].append(int(port_digits[0]))
                                            elif isinstance(p, int):
                                                metadata["ports"].append(p)
                                    if "environment" in svc:
                                        env = svc["environment"]
                                        if isinstance(env, dict):
                                            metadata["environment_variables"].extend(list(env.keys()))
                                        elif isinstance(env, list):
                                            for item in env:
                                                if "=" in item:
                                                    metadata["environment_variables"].append(item.split("=")[0])
                    except Exception:
                        pass

        # 9. Read README for GitHub URLs and descriptions
        readme = project_path / "README.md"
        if not readme.exists():
            readme = project_path / "README"
        if readme.exists():
            try:
                content = readme.read_text(encoding="utf-8", errors="ignore")
                github_matches = re.findall(r'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_\-\.]+', content)
                metadata["github_urls"].extend(github_matches)
                metadata["raw_text_snippets"]["readme_snippet"] = content[:1500]
            except Exception:
                pass

        # 10. Scan Git configuration
        git_config = project_path / ".git" / "config"
        if git_config.exists():
            try:
                content = git_config.read_text(encoding="utf-8", errors="ignore")
                urls = re.findall(r'url\s*=\s*(\S+)', content)
                for u in urls:
                    if u.startswith("git@") or "github.com" in u:
                        u_clean = u.replace("git@", "https://").replace(":", "/").replace(".git", "")
                        metadata["github_urls"].append(u_clean)
            except Exception:
                pass

        # Deduplicate and sort lists
        metadata["packages"] = sorted(list(set(metadata["packages"])))
        metadata["languages"] = sorted(list(set(metadata["languages"])))
        metadata["frameworks"] = sorted(list(set(metadata["frameworks"])))
        metadata["ports"] = sorted(list(set(metadata["ports"])))
        metadata["environment_variables"] = sorted(list(set(metadata["environment_variables"])))
        metadata["docker_images"] = sorted(list(set(metadata["docker_images"])))
        metadata["github_urls"] = sorted(list(set(metadata["github_urls"])))

        return metadata
