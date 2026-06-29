FROM redis:7.2-alpine

# Copy custom configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Set permissions for configuration file and adjust ownership
RUN chown -R redis:redis /usr/local/etc/redis /data && \
    chmod 600 /usr/local/etc/redis/redis.conf

# Run as non-privileged redis user
USER redis

# Expose standard port
EXPOSE 6379

# Execute redis-server using our custom configuration
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
