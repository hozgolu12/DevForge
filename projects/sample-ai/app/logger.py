import logging
import sys
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logger():
    logger = logging.getLogger("ai_app")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = sys.stdout
        stream_handler = logging.StreamHandler(handler)
        stream_handler.setFormatter(JsonFormatter())
        logger.addHandler(stream_handler)
        
    return logger

logger = setup_logger()
