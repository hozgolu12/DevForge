FROM alpine:3.19

# Install Nginx and update packages
RUN apk update && \
    apk add --no-cache nginx tzdata && \
    rm -rf /var/cache/apk/*

# Copy configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY html/ /usr/share/nginx/html/

# Create Nginx execution paths and adjust permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/lib/nginx /tmp/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /var/lib/nginx /usr/share/nginx/html /tmp/nginx /etc/nginx

# Configure Nginx logs to redirect to container stdout/stderr
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Switch to the non-privileged nginx user
USER nginx

# Expose non-privileged HTTP port
EXPOSE 8080

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
