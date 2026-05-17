# ════════════════════════════════════════════════════════════════
# InnAgent AI — Structured Logger
# ════════════════════════════════════════════════════════════════

import logging
import sys
import json
from datetime import datetime
from backend.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "hotel_id"):
            log_data["hotel_id"] = record.hotel_id
        if hasattr(record, "agent"):
            log_data["agent"] = record.agent
        if record.exc_info and record.exc_info[1]:
            log_data["error"] = str(record.exc_info[1])
            log_data["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        return json.dumps(log_data)


def get_logger(name: str = "innagent") -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if settings.ENVIRONMENT == "production":
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return logger


logger = get_logger()
