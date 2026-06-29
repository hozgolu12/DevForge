FROM mongo:7.0-jammy

# Copy the custom mongod configuration file
COPY mongod.conf /etc/mongod.conf

# Ensure configuration is owned by the correct non-root system user
RUN chown mongodb:mongodb /etc/mongod.conf && \
    chmod 600 /etc/mongod.conf

# Expose MongoDB port
EXPOSE 27017
