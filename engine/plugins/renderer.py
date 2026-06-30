# ==============================================================================
# DEVFORGE PLUGIN FILES RENDERER
# ==============================================================================
# Renders PluginSpecification data into official DevForge YAML, Markdown, and
# shell scripts. The AI is strictly barred from generating files directly.
# ==============================================================================

import os
from pathlib import Path
from jinja2 import Environment, DictLoader
from engine.ai.models import PluginSpecification
from engine.workspace import get_devforge_root

# Internal file templates
TEMPLATES = {
    "plugin.yaml": """\
name: {{ plugin_name }}
display_name: "{{ display_name }}"
version: "{{ version }}"
versions: ["{{ version }}"]
category: {{ category }}
description: "{{ description }}"
depends_on: {{ dependencies }}
{% if ports %}
ports:
{% for p in ports %}
  - host: {{ p.host }}
    container: {{ p.container }}
    env_key: {{ p.env_key }}
{% endfor %}
{% endif %}
{% if volumes %}
volumes:
{% for v in volumes %}
  - {{ v }}
{% endfor %}
{% endif %}
env:
{% for k, v in environment_variables.items() %}
  {{ k }}: "{{ v }}"
{% endfor %}
image_base: {{ docker_image }}
""",
    "compose.fragment.yaml": """\
services:
  {{ service_name }}:
    image: "{{ docker_image }}:{{ docker_tag }}"
    container_name: "{{ '{{ project_name }}' }}-{{ service_name }}"
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
    logging: *default-logging
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    {% if healthcheck %}
    healthcheck:
      test: {{ healthcheck.test }}
      interval: {{ healthcheck.interval }}
      timeout: {{ healthcheck.timeout }}
      retries: {{ healthcheck.retries }}
      start_period: {{ healthcheck.start_period }}
    {% endif %}

{% if volumes %}
volumes:
{% for v in volumes %}
  {{ v.split(':')[0] }}:
{% endfor %}
{% endif %}
""",
    "README.md": """\
# {{ display_name }} DevForge Plugin

This plugin integrates **{{ display_name }}** into the DevForge v2 platform.

## Service Description
{{ description }}

## Port Mappings
{% if ports %}
The following port configurations are enabled:
{% for p in ports %}
- **Host Port**: `{{ p.host }}` mapped to container port `{{ p.container }}` (configurable via env var `{{ p.env_key }}`)
{% endfor %}
{% else %}
No default ports are exposed by this service.
{% endif %}

## Environment Variables
The following default configuration variables are automatically populated:

| Variable Name | Default Value | Description |
| --- | --- | --- |
{% for k, v in environment_variables.items() %}
| `{{ k }}` | `{{ v }}` | Configuration key |
{% endfor %}

{% if volumes %}
## Storage Volumes
Persistent volumes defined for this service:
{% for v in volumes %}
- `{{ v.split(':')[0] }}` mounted at `{{ v.split(':')[1] }}`
{% endfor %}
{% endif %}

{% if dependencies %}
## Service Dependencies
Required upstream plugins:
{% for dep in dependencies %}
- `{{ dep }}`
{% endfor %}
{% endif %}

## DevForge CLI Usage

Install the plugin to your active project:
```bash
devforge plugin install {{ plugin_name }}
```

Start the service container:
```bash
devforge start {{ service_name }}
```
""",
    "env.example": """\
# ==============================================================================
# {{ display_name }} ENVIRONMENT SETTINGS
# ==============================================================================
{% for k, v in environment_variables.items() %}
{{ k }}={{ v }}
{% endfor %}
""",
    "healthcheck.sh": """\
#!/bin/sh
# ==============================================================================
# DEVFORGE AUTOMATED SERVICE HEALTH CHECK
# ==============================================================================
# Generated for {{ display_name }}
# ==============================================================================

set -e

{% if healthcheck_cmd %}
echo "Running custom service check..."
{{ healthcheck_cmd }}
{% else %}
echo "Running default TCP port ping check..."
nc -z localhost {{ container_port }} || exit 1
{% endif %}
""",
}


class PluginRenderer:
    """Handles rendering of file structures from PluginSpecification models."""

    def __init__(self):
        self.jinja_env = Environment(
            loader=DictLoader(TEMPLATES),
            keep_trailing_newline=True,
        )

    def render(self, spec: PluginSpecification, output_dir: Path) -> Path:
        """
        Renders all plugin files inside the target directory.
        Creates directories if they do not exist.
        Returns the output directory path.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        context = {
            "plugin_name": spec.plugin_name,
            "display_name": spec.display_name,
            "description": spec.description,
            "category": spec.category,
            "version": spec.version,
            "docker_image": spec.docker_image,
            "docker_tag": spec.docker_tag,
            "service_name": spec.service_name,
            "ports": spec.ports,
            "environment_variables": spec.environment_variables,
            "volumes": spec.volumes,
            "healthcheck": spec.healthcheck,
            "restart_policy": spec.restart_policy,
            "dependencies": spec.dependencies,
        }

        # 1. Render YAML configurations
        plugin_yaml_content = self.jinja_env.get_template("plugin.yaml").render(**context)
        (output_dir / "plugin.yaml").write_text(plugin_yaml_content, encoding="utf-8")

        compose_fragment_content = self.jinja_env.get_template("compose.fragment.yaml").render(**context)
        (output_dir / "compose.fragment.yaml").write_text(compose_fragment_content, encoding="utf-8")

        # 2. Render documentation and env file
        readme_content = self.jinja_env.get_template("README.md").render(**context)
        (output_dir / "README.md").write_text(readme_content, encoding="utf-8")

        env_content = self.jinja_env.get_template("env.example").render(**context)
        (output_dir / "env.example").write_text(env_content, encoding="utf-8")

        # 3. Render healthcheck script from internal templates (strictly no AI scripts)
        healthcheck_cmd = ""
        container_port = 8080
        if spec.healthcheck and spec.healthcheck.test:
            # Reconstruct CMD/CMD-SHELL list to plain shell command if possible
            cmd_list = spec.healthcheck.test
            if cmd_list[0] in ("CMD", "CMD-SHELL"):
                healthcheck_cmd = " ".join(cmd_list[1:])
            else:
                healthcheck_cmd = " ".join(cmd_list)

        if spec.ports:
            container_port = spec.ports[0].container

        script_context = {
            "display_name": spec.display_name,
            "healthcheck_cmd": healthcheck_cmd,
            "container_port": container_port,
        }

        healthcheck_script = self.jinja_env.get_template("healthcheck.sh").render(**script_context)
        health_script_path = output_dir / "healthcheck.sh"
        health_script_path.write_text(healthcheck_script, encoding="utf-8")

        # Set executable permissions (chmod +x)
        try:
            os.chmod(health_script_path, 0o755)
        except Exception:
            # Fail silently on platforms that don't support chmod (Windows host, but CLI runs inside container)
            pass

        return output_dir

