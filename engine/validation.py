# ==============================================================================
# DEVFORGE VALIDATION ENGINE
# ==============================================================================
# Performs configuration and syntax sanity checks on project stack selection,
# port mappings, environment variables, Dockerfiles, and compose files.
# ==============================================================================

import os
from pathlib import Path
import re
from typing import Any
import yaml

class Validator:
    """Validates stack configuration, ports, env, and files before generation."""

    @classmethod
    def validate(cls, project_path: Path, config: dict[str, Any]) -> dict[str, list[str]]:
        """
        Runs all validation checks on the proposed config.
        Returns a dict of validation lists grouped by: 'errors' and 'warnings'.
        """
        results = {
            "errors": [],
            "warnings": []
        }

        # 1. Validate stack / framework selections (unsupported combinations)
        cls._validate_stack_combinations(config, results)

        # 2. Validate plugin dependencies (missing plugins)
        cls._validate_plugin_dependencies(project_path, config, results)

        # 3. Validate port conflicts
        cls._validate_ports(config, results)

        # 4. Validate existing Dockerfiles
        cls._validate_existing_dockerfiles(project_path, config, results)

        # 5. Validate existing docker-compose
        cls._validate_existing_compose(project_path, config, results)

        # 6. Validate duplicate services
        cls._validate_duplicate_services(project_path, config, results)

        # 7. Validate missing env variables
        cls._validate_env_variables(project_path, config, results)

        return results

    @classmethod
    def _validate_stack_combinations(cls, config: dict[str, Any], results: dict[str, list[str]]):
        frameworks = config.get("frameworks", {})
        
        # Check multiple frontends
        frontends = [fw for fw in ["react", "nextjs", "vue", "angular", "svelte"] if frameworks.get("frontend") == fw]
        if len(frontends) > 1:
            results["errors"].append(f"Multiple frontend frameworks selected: {', '.join(frontends)}")

        # Check multiple mobile
        mobiles = [m for m in ["flutter", "android"] if frameworks.get("mobile") == m]
        if len(mobiles) > 1:
            results["errors"].append(f"Multiple mobile frameworks selected: {', '.join(mobiles)}")

    @classmethod
    def _validate_plugin_dependencies(cls, project_path: Path, config: dict[str, Any], results: dict[str, list[str]]):
        from engine.workspace import get_devforge_root
        
        plugins = set(config.get("plugins", []))
        registry_file = get_devforge_root() / "registry" / "plugins.yaml"
        
        if not registry_file.exists():
            return

        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                reg_data = yaml.safe_load(f) or {}
            
            plugin_defs = {p["name"]: p for p in reg_data.get("plugins", [])}
            
            for p_name in plugins:
                p_def = plugin_defs.get(p_name)
                if not p_def:
                    continue
                
                depends = p_def.get("depends_on", [])
                for dep in depends:
                    if dep not in plugins:
                        results["errors"].append(f"Plugin '{p_name}' depends on '{dep}', which is not enabled.")
        except Exception as e:
            results["warnings"].append(f"Could not validate plugin dependencies: {e}")

    @classmethod
    def _validate_ports(cls, config: dict[str, Any], results: dict[str, list[str]]):
        ports = config.get("ports", {})
        port_to_services = {}
        for svc, port in ports.items():
            if not port:
                continue
            port_val = int(port)
            port_to_services.setdefault(port_val, []).append(svc)

        for port_val, services in port_to_services.items():
            if len(services) > 1:
                results["errors"].append(f"Port conflict: Port {port_val} is used by multiple services: {', '.join(services)}")

    @classmethod
    def _validate_existing_dockerfiles(cls, project_path: Path, config: dict[str, Any], results: dict[str, list[str]]):
        # Scan for existing Dockerfiles and run basic syntax verification
        for root, _, files in os.walk(project_path):
            if ".devforge" in root or "node_modules" in root or ".venv" in root or ".git" in root:
                continue
            for file in files:
                if "dockerfile" in file.lower():
                    filepath = Path(root) / file
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        # A valid Dockerfile must contain a FROM instruction
                        if not re.search(r"^\s*FROM\s+\S+", content, re.IGNORECASE | re.MULTILINE):
                            results["errors"].append(f"Invalid Dockerfile syntax in '{filepath.relative_to(project_path)}': Missing 'FROM' instruction.")
                    except Exception as e:
                        results["warnings"].append(f"Could not read Dockerfile '{filepath.relative_to(project_path)}': {e}")

    @classmethod
    def _validate_existing_compose(cls, project_path: Path, config: dict[str, Any], results: dict[str, list[str]]):
        compose_file = project_path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = project_path / "docker-compose.yaml"
        
        if compose_file.exists():
            try:
                with open(compose_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    results["errors"].append(f"Existing {compose_file.name} is not a valid YAML object.")
                elif "services" not in data:
                    results["warnings"].append(f"Existing {compose_file.name} does not contain any 'services' key.")
            except Exception as e:
                results["errors"].append(f"Existing {compose_file.name} has invalid YAML syntax: {e}")

    @classmethod
    def _validate_duplicate_services(cls, project_path: Path, config: dict[str, Any], results: dict[str, list[str]]):
        # If there's an existing compose file, check if service names conflict with plugins
        compose_file = project_path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = project_path / "docker-compose.yaml"

        if compose_file.exists():
            try:
                with open(compose_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                
                if isinstance(data, dict) and "services" in data:
                    existing_services = set(data["services"].keys())
                    plugins = set(config.get("plugins", []))
                    
                    duplicates = existing_services.intersection(plugins)
                    if duplicates:
                        results["warnings"].append(
                            f"Existing docker-compose.yml defines services that match active plugins: {', '.join(duplicates)}. "
                            "These services will be merged or replaced depending on your selection."
                        )
            except Exception:
                pass

    @classmethod
    def _validate_env_variables(cls, project_path: Path, config: dict[str, Any], results: dict[str, list[str]]):
        from engine.workspace import get_devforge_root
        
        plugins = config.get("plugins", [])
        plugins_dir = get_devforge_root() / "plugins"

        # Load current env vars from project's .env if it exists
        env_vars = {}
        env_file = project_path / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_vars[k.strip()] = v.strip()
            except Exception:
                pass

        # Check required env vars in plugin manifests
        for p_name in plugins:
            plugin_yaml = plugins_dir / p_name / "plugin.yaml"
            if plugin_yaml.exists():
                try:
                    with open(plugin_yaml, "r", encoding="utf-8") as f:
                        plugin_data = yaml.safe_load(f)
                    
                    req_vars = plugin_data.get("env", {})
                    # For databases, check if typical passwords/users are configured
                    for var_name, default_val in req_vars.items():
                        # If it's expected but not in env file, check if it's in the config's env overrides
                        if var_name not in env_vars and var_name not in config.get("env_vars", {}):
                            # Warn about missing env vars
                            results["warnings"].append(f"Missing required environment variable '{var_name}' for plugin '{p_name}'.")
                except Exception:
                    pass
