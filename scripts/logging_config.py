"""
Structured logging configuration for the Mapa 3D pipeline.

Provides timestamped, leveled logging to both console and file.
Handlers are added only once — safe to call setup() multiple times.
Oldest log files are rotated out (keeps last 10).

Usage:
    from scripts.logging_config import setup, get_logger
    setup()
    logger = get_logger(__name__)
    logger.info("Processing...")
"""
import glob
import logging
import os
import sys
from datetime import datetime

_MAX_LOG_FILES = 10


def setup(level=logging.INFO, log_dir=None):
    """Configure root logger with console + file handlers.

    Idempotent: skips handler setup if already configured.
    """
    root = logging.getLogger()

    # Avoid duplicate handlers on repeated calls.
    # Use sentinel attribute to distinguish our handlers from foreign ones
    # (third-party libraries may add root handlers before setup() is called).
    if getattr(root, '_pipeline_logging_configured', False):
        return root

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

    # File handler with rotation (keep last N logs)
    if log_dir is None:
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "logs"
        )
    os.makedirs(log_dir, mode=0o755, exist_ok=True)

    # Rotate: remove oldest logs beyond _MAX_LOG_FILES
    existing = sorted(
        glob.glob(os.path.join(log_dir, "pipeline_*.log")),
        key=lambda p: os.path.getmtime(p)
    )
    while len(existing) >= _MAX_LOG_FILES:
        os.unlink(existing.pop(0))

    log_file = os.path.join(
        log_dir,
        f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    root._pipeline_logging_configured = True
    return root


def get_logger(name):
    """Get a module-level logger (call after setup() if not auto-configured)."""
    return logging.getLogger(name)
