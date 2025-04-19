import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level: str = "INFO", log_file: str = None):
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []  # Remove default handlers
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    if log_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Usage: from app.logging_config import setup_logging; setup_logging()
