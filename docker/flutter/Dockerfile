# Production-grade Flutter Development Image for DevForge
FROM eclipse-temurin:17-jdk-jammy

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="Java/Android/Flutter development image containing Android SDK, Gradle cache, and Flutter SDK."

# Avoid prompt during installations
ENV DEBIAN_FRONTEND=noninteractive

# Install critical system tools, utility binaries, and build prerequisites
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
    xz-utils \
    libglu1-mesa \
    lib32stdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Setup Android SDK
ENV ANDROID_HOME=/opt/android-sdk
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -P /tmp && \
    unzip -d ${ANDROID_HOME}/cmdline-tools /tmp/commandlinetools-linux-11076708_latest.zip && \
    mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm /tmp/commandlinetools-linux-11076708_latest.zip

# Register Android Tools in PATH
ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/tools/bin:${PATH}"

# Auto-accept licenses and install required Android platform components
RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

# Setup Flutter SDK (stable release 3.19.6)
ENV FLUTTER_HOME=/opt/flutter
RUN wget -q https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.19.6-stable.tar.xz -P /tmp && \
    tar -xf /tmp/flutter_linux_3.19.6-stable.tar.xz -C /opt && \
    rm /tmp/flutter_linux_3.19.6-stable.tar.xz

# Register Flutter in PATH
ENV PATH="${FLUTTER_HOME}/bin:${PATH}"

# Configure Flutter and disable analytics
RUN flutter config --no-analytics

# Set up standard working directory
WORKDIR /workspace

# Create a non-privileged user and group devforge (UID 1000) for security hardening
RUN groupadd -g 1000 devforge || true && \
    useradd -u 1000 -g devforge -m -s /bin/zsh devforge || true && \
    chown -R devforge:devforge /opt/flutter && \
    chown -R devforge:devforge /opt/android-sdk && \
    chown -R devforge:devforge /workspace || true

# Ensure Gradle cache directory exists and has proper permissions
RUN mkdir -p /home/devforge/.gradle && chown -R devforge:devforge /home/devforge/.gradle

# Configure Zsh with Oh My Zsh for a friendly developer terminal environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended || true

# Set default user to devforge for security hardening
USER devforge

# Run diagnostic flutter doctor to verify integration
RUN flutter doctor

# Default command (runs standby for CLI worker task triggers)
CMD ["sleep", "infinity"]
