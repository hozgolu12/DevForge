from flask import Blueprint, jsonify, request
from datetime import datetime
import time

routes_bp = Blueprint("routes", __name__)
start_time = time.time()

@routes_bp.route("/health", methods=["GET"])
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

    return jsonify({
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": uptime,
        "memoryUsage": memory_usage,
    }), 200

@routes_bp.route("/api/info", methods=["GET"])
def get_info():
    return jsonify({
        "message": "Welcome to DevForge Flask Platform",
        "status": "operational",
        "databasesAvailable": ["PostgreSQL", "MongoDB", "Redis", "Neo4j"],
    }), 200
