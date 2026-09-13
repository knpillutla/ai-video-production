"""Structured JSON telemetry and contextual logging."""

import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON lines with correlation tags."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach contextual telemetry metadata if present
        for key in ("user_id", "project_id", "show_id", "episode_id", "channel_id", "step_name"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str = "video_studio", level: int = logging.INFO) -> logging.Logger:
    """Create a configured logger with standard JSON output and persistent file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = JSONFormatter()

        # Stream Handler for terminal / console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Persistent File Handler in logs/studio.log
        logs_dir = Path("logs")
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            file_path = logs_dir / "studio.log"
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=10 * 1024 * 1024,  # 10 MB per log file
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # Non-blocking fallback if filesystem is read-only

    return logger


logger = setup_logger()

__all__ = ["logger", "setup_logger", "JSONFormatter"]

