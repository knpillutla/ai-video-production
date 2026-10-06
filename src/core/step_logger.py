"""Structured Pipeline Step Logger for AI Video Producer Studio.

Enforces unified auditing format:
timestamp, process name: <name>, step: <step_name>, status: <status>, action: <action> [, metadata: [...]]
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from src.core.telemetry import logger


def log_pipeline_step(
    process_name: str,
    step: str,
    status: str,
    action: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> str:
    """Emit formatted step log to telemetry logger and stdout console."""
    ts = datetime.now(timezone.utc).isoformat()
    parts = [
        f"{ts}",
        f"process name: {process_name}",
        f"step: {step}",
        f"status: {status}",
    ]
    if action:
        parts.append(f"action: {action}")
    if metadata:
        meta_items = ", ".join(f"{k}: {v}" for k, v in metadata.items() if v is not None)
        if meta_items:
            parts.append(f"metadata: [{meta_items}]")

    line = ", ".join(parts)
    logger.info(line)
    print(line)
    return line


__all__ = ["log_pipeline_step"]
