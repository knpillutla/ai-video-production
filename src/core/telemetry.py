"""Structured JSON telemetry and contextual logging with in-memory streaming buffer."""

import asyncio
from collections import deque
from datetime import datetime, timezone
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from typing import Any, AsyncGenerator, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON lines with correlation tags."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("user_id", "project_id", "show_id", "episode_id", "channel_id", "step_name"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class MemoryLogBufferHandler(logging.Handler):
    """Circular in-memory buffer storing recent log entries and broadcasting to SSE queues."""

    def __init__(self, maxlen: int = 1000):
        super().__init__()
        self.buffer: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self.subscribers: set[asyncio.Queue] = set()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "time_str": datetime.now().strftime("%H:%M:%S"),
            }
            for key in ("episode_id", "channel_id", "step_name"):
                if hasattr(record, key):
                    entry[key] = getattr(record, key)
            self.buffer.append(entry)

            # Broadcast to active async queues
            dead_subscribers = set()
            for q in self.subscribers:
                try:
                    q.put_nowait(entry)
                except Exception:
                    dead_subscribers.add(q)
            self.subscribers.difference_update(dead_subscribers)
        except Exception:
            pass


log_buffer_handler = MemoryLogBufferHandler(maxlen=1000)


def get_recent_logs(limit: int = 200, level: Optional[str] = None) -> list[dict[str, Any]]:
    """Retrieve recent log entries from circular buffer with optional level filter."""
    logs = list(log_buffer_handler.buffer)
    if level:
        lvl_upper = level.upper()
        logs = [l for l in logs if l.get("level") == lvl_upper]
    return logs[-limit:]


def clear_log_buffer() -> None:
    """Clear memory log buffer."""
    log_buffer_handler.buffer.clear()


async def subscribe_logs() -> AsyncGenerator[dict[str, Any], None]:
    """Async generator yielding log events in real time to SSE streams."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    log_buffer_handler.subscribers.add(queue)
    try:
        while True:
            entry = await queue.get()
            yield entry
    finally:
        log_buffer_handler.subscribers.discard(queue)


def setup_logger(name: str = "video_studio", level: int = logging.INFO) -> logging.Logger:
    """Create a configured logger with standard JSON output, persistent file, and memory buffer."""
    l = logging.getLogger(name)
    l.setLevel(level)

    if not l.handlers:
        formatter = JSONFormatter()

        # Stream Handler for terminal / console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        l.addHandler(stream_handler)

        # In-Memory Buffer Handler for UI Console
        l.addHandler(log_buffer_handler)

        # Persistent File Handlers in logs/studio.log and logs/studio_server.log
        logs_dir = Path("logs")
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            for fname in ("studio.log", "studio_server.log"):
                file_handler = RotatingFileHandler(
                    logs_dir / fname,
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding="utf-8",
                )
                file_handler.setFormatter(formatter)
                l.addHandler(file_handler)
        except Exception:
            pass

    return l


logger = setup_logger()

__all__ = [
    "logger",
    "setup_logger",
    "JSONFormatter",
    "log_buffer_handler",
    "get_recent_logs",
    "clear_log_buffer",
    "subscribe_logs",
]

