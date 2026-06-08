import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict

# Context variables for tracking
trace_id_ctx_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
candidate_id_ctx_var: ContextVar[str | None] = ContextVar("candidate_id", default=None)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }
        
        # Add context variables if present
        trace_id = trace_id_ctx_var.get()
        if trace_id:
            log_data["trace_id"] = trace_id
            
        candidate_id = candidate_id_ctx_var.get()
        if candidate_id:
            log_data["candidate_id"] = candidate_id

        # Add exception info if present
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure structured logging for the application."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
        
    root_logger.addHandler(handler)
    
    # Configure uvicorn loggers to use the same formatter
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers = [handler]
        logger.propagate = False
