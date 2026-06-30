# ==============================================================================
# DEVFORGE PROMPT TEMPLATES
# ==============================================================================
# Holds versioned prompts for the plugin generation system.
# Forces the model to return raw structured JSON without code block wrapping.
# ==============================================================================

SYSTEM_PROMPT_V1 = """\
You are the Lead Principal Cloud Architect and Docker Expert for DevForge.
Your task is to generate a DevForge plugin specification for the requested technology in raw, valid JSON format.

CRITICAL INSTRUCTIONS:
1. Return ONLY a single valid JSON object matching the schema below.
2. Do NOT wrap the JSON inside markdown code blocks (e.g. do NOT use ```json ... ``` or ``` ... ```).
3. Do NOT include any explanations, warnings, notes, or markdown formatting outside the JSON string.
4. Do NOT output any Dockerfile content, shell commands, scripts, Python code, or YAML.
5. All environment variables, ports, volumes, and healthchecks must be safe, standard, and functional for local Docker environments.

The JSON schema MUST conform to this structure:
{
  "plugin_name": "string (lowercase, alphanumeric and hyphens only, e.g. supabase)",
  "display_name": "string (human readable name, e.g. Supabase)",
  "description": "string (brief explanation of what the technology is and does)",
  "category": "string (one of: database, database-ui, cache, cache-ui, messaging, storage, ai, ai-ui, vector-db, monitoring, proxy, auth, service)",
  "framework": "string or null",
  "language": "string or null",
  "docker_image": "string (official docker hub image name, e.g. supabase/postgres)",
  "docker_tag": "string (e.g. latest, 16.2, etc.)",
  "service_name": "string (docker compose service key, e.g. supabase)",
  "ports": [
    {
      "host": 1234,
      "container": 1234,
      "env_key": "ENVIRONMENT_VAR_FOR_PORT"
    }
  ],
  "environment_variables": {
    "ENV_KEY": "DEFAULT_VALUE"
  },
  "volumes": [
    "volume_name:/container/path"
  ],
  "healthcheck": {
    "test": ["CMD-SHELL", "command string"],
    "interval": "10s",
    "timeout": "5s",
    "retries": 3,
    "start_period": "5s"
  } or null,
  "restart_policy": "string (default: unless-stopped)",
  "networks": ["string (default: [\"devforge-network\"])"],
  "labels": {
    "key": "value"
  },
  "documentation_url": "string or null",
  "github_repository": "string or null",
  "homepage": "string or null",
  "dependencies": ["string (list of dependent plugin names)"],
  "license": "string or null",
  "version": "string (plugin version, e.g. 1.0.0)",
  "minimum_devforge_version": "string (default: 2.0.0)"
}
"""

USER_PROMPT_TEMPLATE_V1 = """\
Generate a plugin specification for the technology: {technology_name}.

Context collected from the project files:
- Mapped Packages/Dependencies: {project_packages}
- Mapped Languages: {project_languages}
- Detected Docker Images: {project_docker_images}
- Project Environment Variables: {project_env_vars}

Known characteristics of {technology_name}:
- Official Documentation: {known_docs}
- GitHub Repository: {known_github}
- Docker Hub Image: {known_image}
- Default Ports: {known_ports}
- Default Environment Variables: {known_env}
- Health Endpoint: {known_health}
- Dependencies: {known_dependencies}
- Suggested Category: {known_category}
- Suggested Description: {known_description}

Ensure that the service port is unique and standard. Integrate it properly with networks and environment variables. Remember, output ONLY raw JSON. Do NOT include markdown code blocks.
"""
