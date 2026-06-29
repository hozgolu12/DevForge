# Production-grade Java Development Image for DevForge
FROM eclipse-temurin:21-jdk-jammy

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="Java development image containing OpenJDK 21, Maven, Gradle, and developer terminal utilities."

# Install critical system tools and utility binaries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    bash \
    zsh \
    zip \
    unzip \
    vim \
    nano \
    build-essential \
    ca-certificates \
    maven \
    && rm -rf /var/lib/apt/lists/*

# Install Gradle 8.7
RUN wget -q https://services.gradle.org/distributions/gradle-8.7-bin.zip -P /tmp && \
    unzip -d /opt/gradle /tmp/gradle-8.7-bin.zip && \
    ln -s /opt/gradle/gradle-8.7/bin/gradle /usr/bin/gradle && \
    rm /tmp/gradle-8.7-bin.zip

# Configure Zsh with Oh My Zsh for a friendly developer terminal environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true

# Set up standard working directory
WORKDIR /workspace

# Create a non-privileged user and group devforge (UID 1000) for security hardening
RUN groupadd -g 1000 devforge || true && \
    useradd -u 1000 -g devforge -m -s /bin/zsh devforge || true && \
    chown -R devforge:devforge /workspace || true

# Ensure Maven local repository directory exists and has proper permissions
RUN mkdir -p /home/devforge/.m2 && chown -R devforge:devforge /home/devforge/.m2

# Set default user to devforge for security hardening
USER devforge

# Set up environment variables
ENV PATH="/home/devforge/.local/bin:${PATH}"

# Default command
CMD ["java"]
