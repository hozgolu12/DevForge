# DevForge Observability & Infrastructure Operations Guide

This guide details active configurations, connections, credentials, administrative web dashboards, and instrumentation protocols for the DevForge observability and message broker stack.

---

## 1. Service Connections & Dashboards

All services run inside the container network `devforge-network`. For local development convenience, they are exposed through the Nginx Ingress gateway on host port `8080` (or `8080/secure` / `8443` secure SSL route).

### Observability Services

| Service | Proxy Access Path | Host Direct Port | Default Credentials |
| :--- | :--- | :--- | :--- |
| **Prometheus** | `http://localhost:8080/prometheus/` | `9090` | None |
| **Grafana** | `http://localhost:8080/grafana/` | `3002` | User: `admin` / Pass: `admin` |
| **cAdvisor** | None | `8089` | None |
| **Loki** | None | `3100` (API) | None |

### Middleware & Storage UIs

| Service | Proxy Access Path | Host Direct Port | Default Credentials |
| :--- | :--- | :--- | :--- |
| **MinIO Console** | `http://localhost:8080/minio/` | `9001` (Console) / `9000` (API) | User: `admin` / Pass: `minioadmin` |
| **RabbitMQ Admin** | `http://localhost:8080/rabbitmq/` | `15672` (Admin) / `5672` (AMQP) | User: `admin` / Pass: `admin` |

---

## 2. Grafana Dashboards

Grafana is pre-configured with **automatic provisioning**:
- **Data Sources**: Prometheus and Loki are pre-configured out of the box.
- **Dashboards**: A default dashboard `DevForge Container Observability` is pre-loaded. It displays container CPU and Memory usage statistics sourced directly from cAdvisor.

To access:
1. Navigate to `http://localhost:8080/grafana/`.
2. Login with `admin` / `admin`.
3. Open **Dashboards** to view `DevForge Container Observability`.

---

## 3. How to Instrument Your Code (Prometheus Metrics)

To scrape application-level metrics, update `docker/prometheus/prometheus.yml` under `scrape_configs` to point to your new service container:

### FastAPI (Python)
Install `prometheus-fastapi-instrumentator`:
```python
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```
Add to Prometheus scrape config:
```yaml
  - job_name: 'fastapi-app'
    static_configs:
      - targets: ['fastapi:8000']
```

### Spring Boot (Java)
Add dependencies for actuator and micrometer-registry-prometheus in `pom.xml`:
```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```
Expose prometheus endpoint in `application.yml`:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
```
Add to Prometheus scrape config:
```yaml
  - job_name: 'springboot-app'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['springboot:8080']
```

### Node.js (Express)
Install `prom-client`:
```javascript
const client = require('prom-client');
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics();

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```
Add to Prometheus scrape config:
```yaml
  - job_name: 'express-app'
    static_configs:
      - targets: ['express:5000']
```
