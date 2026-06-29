from django.http import JsonResponse
from datetime import datetime
import time

start_time = time.time()

def health_check(request):
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

    return JsonResponse({
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "memoryUsage": memory_usage,
    })

def get_info(request):
    return JsonResponse({
        "message": "Welcome to DevForge Django Platform",
        "status": "operational",
        "databasesAvailable": ["PostgreSQL", "MongoDB", "Redis", "Neo4j"],
    })
