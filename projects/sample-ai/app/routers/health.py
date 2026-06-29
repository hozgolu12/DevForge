from fastapi import APIRouter
from datetime import datetime
import time
import httpx
from app.config import settings

router = APIRouter()
start_time = time.time()

@router.get("/health")
async def health_check():
    uptime = time.time() - start_time
    
    ollama_status = "DOWN"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_host}/", timeout=2.0)
            if response.status_code == 200:
                ollama_status = "UP"
    except Exception:
        pass

    chroma_status = "DOWN"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.chromadb_host}/heartbeat", timeout=2.0)
            if response.status_code == 200:
                chroma_status = "UP"
    except Exception:
        pass

    qdrant_status = "DOWN"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.qdrant_host}/healthz", timeout=2.0)
            if response.status_code == 200:
                qdrant_status = "UP"
    except Exception:
        pass

    return {
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "dependencies": {
            "ollama": ollama_status,
            "chromadb": chroma_status,
            "qdrant": qdrant_status,
        }
    }
