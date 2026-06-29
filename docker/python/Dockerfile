# Production-grade Python Development Image for DevForge
FROM python:3.11-bookworm

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="Python development image containing uv, Poetry, JupyterLab, and standard linting/formatting tools."

# Install critical system tools, utility binaries, and database development packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    bash \
    zsh \
    zip \
    unzip \
    vim \
    nano \
    build-essential \
    ca-certificates \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install global python packages
RUN pip install --no-cache-dir \
    uv \
    poetry \
    pytest \
    ruff \
    black \
    mypy \
    jupyterlab \
    uvicorn \
    gunicorn

# Configure Zsh with Oh My Zsh for a friendly developer terminal environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true

# Set up standard working directory
WORKDIR /workspace

# Create a non-privileged user and group devforge (UID 1000) for security hardening
RUN groupadd -g 1000 devforge && \
    useradd -u 1000 -g devforge -m -s /bin/zsh devforge && \
    chown -R devforge:devforge /workspace

# Set default user to devforge for security hardening
USER devforge

# Set up environment variables
ENV PATH="/home/devforge/.local/bin:${PATH}"

# Default command
CMD ["python"]
