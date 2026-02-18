"""
Structured Logging Setup
JSON-formatted logs with level, timestamp, module, and trace context.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Outputs each log record as a single-line JSON object."""

    LEVEL_MAP = {
        logging.DEBUG:    "DEBUG",
        logging.INFO:     "INFO",
        logging.WARNING:  "WARNING",
        logging.ERROR:    "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "ts":      datetime.now(timezone.utc).isoformat(),
            "level":   self.LEVEL_MAP.get(record.levelno, "INFO"),
            "logger":  record.name,
            "msg":     record.getMessage(),
            "module":  record.module,
            "line":    record.lineno,
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log.update(record.extra)
        return json.dumps(log, default=str)


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: str | None = None,
) -> None:
    """
    Configure root logger for the sniper framework.

    Args:
        level:       Logging level (DEBUG/INFO/WARNING/ERROR)
        json_format: Use JSON structured logs (True for production)
        log_file:    Optional file path for log output
    """
    root = logging.getLogger("sniper")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    formatter = JSONFormatter() if json_format else logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # File handler (optional)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(formatter)
        root.addHandler(fh)

    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the sniper namespace."""
    return logging.getLogger(f"sniper.{name}" if not name.startswith("sniper") else name)
