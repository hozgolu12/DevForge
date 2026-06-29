# ==============================================================================
# DEVFORGE CLI IMAGE
# ==============================================================================
# Builds the ephemeral devforge-cli:2.0 container.
# This image is invoked by devforge.ps1 / devforge wrappers via:
#   docker run --rm -it -v ${PWD}:/workspace devforge-cli:2.0 <command>
#
# Host requirements: Docker Desktop + Git + VS Code only.
# No Python, Node.js, or any runtime needed on the host machine.
# ==============================================================================

FROM python:3.12-slim

LABEL maintainer="DevForge"
LABEL version="2.0.0"
LABEL description="DevForge CLI — ephemeral project generator and platform manager"

# Install system dependencies required by the CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the workspace directory — matches the host volume mount point
WORKDIR /workspace

# Copy and install Python dependencies first (layer caching)
COPY requirements.engine.txt /tmp/requirements.engine.txt
RUN pip install --no-cache-dir -r /tmp/requirements.engine.txt

# Copy the engine source into the image
COPY engine/ /app/engine/

# Add engine to Python path
ENV PYTHONPATH=/app

# Default entrypoint delegates all arguments to the CLI
ENTRYPOINT ["python", "-m", "engine.cli"]

# Default command shows help when no arguments provided
CMD ["--help"]
