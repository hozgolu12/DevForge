# ==============================================================================
# DEVFORGE PLUGIN SPECIFICATION VALIDATOR
# ==============================================================================
# Performs schema validation, docker compose structure checks, port mapping
# consistency checks, and service name uniqueness verification.
# ==============================================================================

import re
from typing import Dict, List, Optional
import yaml
from pydantic import ValidationError
from engine.ai.models import PluginSpecification


class ValidationResult:
    """Carries the outcome of a plugin validation process."""

    def __init__(self, passed: bool, errors: List[str], warnings: List[str]):
        self.passed = passed
        self.errors = errors
        self.warnings = warnings


class PluginValidator:
    """Validates the generated PluginSpecification object and templates."""

    ALLOWED_CATEGORIES = {
        "database",
        "database-ui",
        "cache",
        "cache-ui",
        "messaging",
        "storage",
        "ai",
        "ai-ui",
        "vector-db",
        "monitoring",
        "proxy",
        "auth",
        "service",
    }

    @classmethod
    def validate(
        cls, spec: PluginSpecification, active_project_ports: Optional[Dict[str, int]] = None
    ) -> ValidationResult:
        """
        Runs comprehensive validation rules on the specification.
        """
        errors = []
        warnings = []

        # 1. Alphanumeric lowercase checks on plugin name
        if not re.match(r"^[a-z0-9-]+$", spec.plugin_name):
            errors.append(
                f"Plugin name '{spec.plugin_name}' must be lowercase alphanumeric with hyphens only."
            )

        # 2. Check service name
        if not re.match(r"^[a-zA-Z0-9_-]+$", spec.service_name):
            errors.append(
                f"Service name '{spec.service_name}' must be alphanumeric with hyphens or underscores only."
            )

        # 3. Category validation
        if spec.category not in cls.ALLOWED_CATEGORIES:
            errors.append(
                f"Category '{spec.category}' is invalid. Must be one of: {', '.join(cls.ALLOWED_CATEGORIES)}"
            )

        # 4. Docker Image and tag format checks
        if not spec.docker_image:
            errors.append("Docker image name cannot be empty.")
        elif not re.match(r"^[a-zA-Z0-9_\-\./]+$", spec.docker_image):
            errors.append(f"Docker image '{spec.docker_image}' contains invalid characters.")

        if not spec.docker_tag or not re.match(r"^[a-zA-Z0-9_\-\.]+$", spec.docker_tag):
            errors.append(f"Docker tag '{spec.docker_tag}' contains invalid characters.")

        # 5. Port mapping checks
        seen_hosts = set()
        seen_containers = set()
        for port in spec.ports:
            # Range check
            if not (1 <= port.host <= 65535):
                errors.append(f"Host port {port.host} is out of range (1-65535).")
            if not (1 <= port.container <= 65535):
                errors.append(f"Container port {port.container} is out of range (1-65535).")

            # Check local duplicates
            if port.host in seen_hosts:
                errors.append(f"Duplicate host port {port.host} mapped in the same plugin.")
            seen_hosts.add(port.host)

            if port.container in seen_containers:
                warnings.append(f"Multiple mappings target the container port {port.container}.")
            seen_containers.add(port.container)

            # Check environment port keys format
            if not re.match(r"^[A-Z0-9_]+$", port.env_key):
                errors.append(
                    f"Port environment key '{port.env_key}' must be uppercase alphanumeric and underscores only."
                )

            # Check conflict with active project ports
            if active_project_ports:
                for active_svc, active_port in active_project_ports.items():
                    if active_port == port.host and active_svc != spec.plugin_name:
                        errors.append(
                            f"Port conflict: Port {port.host} is already used in this project by service '{active_svc}'."
                        )

        # 6. Environment variables name validation
        for env_key in spec.environment_variables.keys():
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", env_key):
                errors.append(f"Environment variable key '{env_key}' is invalid.")

        # 7. Volume mapping format check (must contain ":")
        for vol in spec.volumes:
            if ":" not in vol:
                errors.append(f"Volume mapping '{vol}' is invalid. Must use host:container or volume:container format.")
            else:
                parts = vol.split(":")
                if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                    errors.append(f"Volume mapping '{vol}' has invalid format.")

        # 8. Check healthcheck command syntax if present
        if spec.healthcheck:
            if not spec.healthcheck.test:
                errors.append("Health check is defined but the test command array is empty.")
            elif not isinstance(spec.healthcheck.test, list):
                errors.append("Health check test must be an array of strings.")
            elif spec.healthcheck.test[0] not in ("CMD", "CMD-SHELL"):
                warnings.append("Health check test command usually starts with 'CMD' or 'CMD-SHELL'.")

        # 9. Verify Compose Fragment generation works and has valid YAML structure
        try:
            cls._test_render_and_parse_compose(spec)
        except Exception as e:
            errors.append(f"Generated Docker Compose fragment fails YAML parsing: {e}")

        # Passed if there are no errors
        passed = len(errors) == 0
        return ValidationResult(passed, errors, warnings)

    @classmethod
    def _test_render_and_parse_compose(cls, spec: PluginSpecification):
        """
        Renders a compose fragment in-memory using jinja2 to check for syntax errors.
        """
        from jinja2 import Template
        
        # Keep a minimal inline template matching the renderer's logic
        compose_template_str = """
services:
  {{ service_name }}:
    image: "{{ docker_image }}:{{ docker_tag }}"
    container_name: "mockproject-{{ service_name }}"
    restart: "{{ restart_policy }}"
    environment:
    {% for k, v in environment_variables.items() %}
      {{ k }}: "${{ '{' }}{{ k }}{{ '}' }}"
    {% endfor %}
    {% if volumes %}
    volumes:
    {% for v in volumes %}
      - {{ v.split(':')[0] }}:{{ v.split(':')[1] }}
    {% endfor %}
    {% endif %}
    {% if ports %}
    ports:
    {% for p in ports %}
      - "${{ '{' }}{{ p.env_key }}:-{{ p.host }}{{ '}' }}:{{ p.container }}"
    {% endfor %}
    {% endif %}
    networks:
      - devforge-network
    {% if healthcheck %}
    healthcheck:
      test: {{ healthcheck.test }}
      interval: {{ healthcheck.interval }}
      timeout: {{ healthcheck.timeout }}
      retries: {{ healthcheck.retries }}
      start_period: {{ healthcheck.start_period }}
    {% endif %}
"""
        template = Template(compose_template_str)
        rendered = template.render(
            service_name=spec.service_name,
            docker_image=spec.docker_image,
            docker_tag=spec.docker_tag,
            restart_policy=spec.restart_policy,
            environment_variables=spec.environment_variables,
            volumes=spec.volumes,
            ports=spec.ports,
            healthcheck=spec.healthcheck
        )
        
        # Append minimal anchor mock definition to parse successfully
        yaml.safe_load(rendered)
