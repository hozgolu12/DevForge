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

# WORKDIR is set to /workspace to mount the project
WORKDIR /workspace

# Copy and install Python dependencies first (layer caching)
COPY requirements.engine.txt /tmp/requirements.engine.txt
RUN pip install --no-cache-dir -r /tmp/requirements.engine.txt && \
    find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test -o -name __pycache__ \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
        \) -exec rm -rf '{}' +

# Copy the engine source into the image
COPY engine/ /app/engine/

# Add engine to Python path
ENV PYTHONPATH=/app

# Default entrypoint delegates all arguments to the CLI
ENTRYPOINT ["python", "-m", "engine.cli"]

# Default command shows help when no arguments provided
CMD ["--help"]
