# Hardened Base Image for DevForge Services
FROM alpine:3.19

# Establish standard metadata
LABEL maintainer="DevForge Authors" \
      version="1.0.0" \
      description="Hardened Alpine base image containing standard dev utility binaries."

# Install critical system tools and utilities, then clean up cache
RUN apk update && \
    apk add --no-cache \
    curl \
    wget \
    ca-certificates \
    jq \
    bind-tools \
    iputils \
    tzdata && \
    rm -rf /var/cache/apk/*

# Create a non-privileged user and group
RUN addgroup -S devforge && adduser -S -G devforge devforge

# Default command
CMD ["/bin/sh"]
