# Production-grade Node.js Development Image for DevForge
FROM node:22-bookworm

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="Node.js development image containing core runtime, package managers, and development CLIs."

# Install critical system tools and utilities
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
    && rm -rf /var/lib/apt/lists/*

# Install global node packages
RUN npm install -g typescript tsx nodemon @nestjs/cli vite eslint prettier pnpm yarn

# Configure Zsh with Oh My Zsh for a friendly developer terminal environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true

# Set up standard working directory
WORKDIR /workspace

# Set default user to node (UID 1000) for security hardening
USER node

# Default command
CMD ["node"]
