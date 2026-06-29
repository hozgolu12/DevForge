from fastapi import APIRouter
from datetime import datetime
import time
import os

router = APIRouter()
start_time = time.time()

@router.get("/health")
def health_check():
    uptime = time.time() - start_time
    memory_usage = {}
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    memory_usage["rss"] = int(line.split()[1]) * 1024  # bytes
                    break
    except Exception:
        pass

    return {
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "memoryUsage": memory_usage,
    }
