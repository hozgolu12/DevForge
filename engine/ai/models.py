# ==============================================================================
# DEVFORGE AI PLUGIN SPECIFICATION MODELS
# ==============================================================================
# Defines the Pydantic schemas that validate and structure the AI's output.
# ==============================================================================

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PortSpecification(BaseModel):
    """Port mappings for the container and environment variable."""
    host: int = Field(description="Default host port mapping, e.g. 5432")
    container: int = Field(description="Internal container port, e.g. 5432")
    env_key: str = Field(description="Environment variable key naming this port, e.g. POSTGRES_PORT")


class HealthCheckSpecification(BaseModel):
    """Container health check parameters."""
    test: List[str] = Field(description="Command-shell array to run, e.g. ['CMD-SHELL', 'pg_isready']")
    interval: str = Field(default="10s", description="Frequency of checks, e.g. 10s")
    timeout: str = Field(default="5s", description="Timeout of each check, e.g. 5s")
    retries: int = Field(default=3, description="Failure threshold count before reporting unhealthy")
    start_period: str = Field(default="5s", description="Initial startup delay before checking")


class PluginSpecification(BaseModel):
    """Complete schema for a generated DevForge service plugin."""
    plugin_name: str = Field(description="Alphanumeric lowercase name with hyphens only, e.g. supabase")
    display_name: str = Field(description="Human readable name, e.g. Supabase")
    description: str = Field(description="Short sentence describing what the service does")
    category: str = Field(description="Category of the plugin, e.g. database, cache, messaging, storage, ai, vector-db, auth, monitoring")
    framework: Optional[str] = Field(default=None, description="Associated software framework if any")
    language: Optional[str] = Field(default=None, description="Programming language primarily used")
    docker_image: str = Field(description="Official Docker image name on Docker Hub, e.g. supabase/postgres")
    docker_tag: str = Field(default="latest", description="Default tag for the Docker image")
    service_name: str = Field(description="Default service key for docker-compose, e.g. supabase")
    ports: List[PortSpecification] = Field(default_factory=list, description="List of ports exposed by this service")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables needed by the container")
    volumes: List[str] = Field(default_factory=list, description="Volume mounts defined as volume_name:container_path")
    healthcheck: Optional[HealthCheckSpecification] = Field(default=None, description="Optional service health check settings")
    restart_policy: str = Field(default="unless-stopped", description="Container restart behavior")
    networks: List[str] = Field(default_factory=lambda: ["devforge-network"], description="Associated compose networks")
    labels: Dict[str, str] = Field(default_factory=dict, description="Docker metadata labels")
    documentation_url: Optional[str] = Field(default=None, description="Link to official documentation")
    github_repository: Optional[str] = Field(default=None, description="Link to source code repository")
    homepage: Optional[str] = Field(default=None, description="Link to project homepage")
    dependencies: List[str] = Field(default_factory=list, description="Other plugins required by this plugin")
    license: Optional[str] = Field(default="MIT", description="Software license code")
    version: str = Field(default="1.0.0", description="Plugin version string")
    minimum_devforge_version: str = Field(default="2.0.0", description="Minimum DevForge platform version required")
