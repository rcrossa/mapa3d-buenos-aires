"""
Structured logging configuration for the Mapa 3D pipeline.

Provides timestamped, leveled logging to both console and file.
Usage:
    from scripts.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Processing...")
"""
import logging
import os
import sys
from datetime import datetime


def setup(level=logging.INFO, log_dir=None):
    """Configure root logger with console + file handlers."""
    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-7s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # File handler (optional)
    if log_dir is None:
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "logs"
        )
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir,
        f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    return root


def get_logger(name):
    """Get a module-level logger (call after setup() if not auto-configured)."""
    return logging.getLogger(name)
