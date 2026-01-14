from logging import LogRecord
from core.context import request_id_ctx
from typing import Any, Literal
import logging.config
import os

class ContextFilter(logging.Filter):
    def filter(self, record: LogRecord) -> Literal[True]:
        record.request_id = request_id_ctx.get()
        return True

# Create a logs directory if it doesn't exist
if not os.path.exists("exc/logs"):
    os.makedirs("exc/logs")

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id_filter": {"()": ContextFilter}},
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s %(filename)s:%(lineno)d: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_id_filter"],
        },
        "file_handler": {
            "level": "WARNING",  # This saves WARNING, ERROR, and CRITICAL to the file
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "exc/logs/app_errors.log",
            "maxBytes": 5242880,  # 5MB per file
            "backupCount": 5,     # Keep the last 5 old log files
            "formatter": "detailed",
            "filters": ["request_id_filter"],
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file_handler"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)