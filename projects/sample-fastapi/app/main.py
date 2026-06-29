from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from app.config import settings
from app.logger import logger
from app.routers import health

app = FastAPI(
    title="DevForge FastAPI Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_hosts],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging request middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} {response.status_code}",
        extra={
            "ip": request.client.host if request.client else "unknown",
            "duration": duration,
        }
    )
    return response

# Register routers
app.include_router(health.router)

# Sample api endpoint
@app.get("/api/info")
def get_info():
    return {
        "message": "Welcome to DevForge FastAPI Platform",
        "status": "operational",
        "databasesAvailable": ["PostgreSQL", "MongoDB", "Redis", "Neo4j"],
    }
