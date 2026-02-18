import logging
import sys
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Structured JSON Formatter for Enterprise Logging
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# Create Logger
logger = logging.getLogger("texthelper.backend")
logger.setLevel(logging.INFO)

# Console Handler
handler = logging.StreamHandler(sys.stdout)

# Use JSON Formatter for Production, Standard for Dev
is_dev = False # Toggled via Env var typically, defaulting to Structured for now as requested
if is_dev:
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
else:
    handler.setFormatter(JsonFormatter())

logger.addHandler(handler)

# Prevent propagation to root logger to avoid double logging
logger.propagate = False
