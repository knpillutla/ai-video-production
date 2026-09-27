"""Real-time production logs and SSE streaming API routes for the Web UI console."""

import asyncio
import json
from typing import Any, Optional
from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from src.core.telemetry import clear_log_buffer, get_recent_logs, subscribe_logs

router = APIRouter(prefix="/api/logs", tags=["Studio Logs & Console"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_recent_logs(
    limit: int = Query(200, ge=1, le=1000, description="Max number of logs to return"),
    level: Optional[str] = Query(None, description="Optional level filter (INFO, WARNING, ERROR)"),
):
    """Retrieve historical logs stored in memory buffer."""
    logs = get_recent_logs(limit=limit, level=level)
    return {"status": "ok", "count": len(logs), "logs": logs}


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_logs():
    """Clear memory log buffer."""
    clear_log_buffer()
    return {"status": "ok", "message": "Log buffer cleared"}


@router.get("/stream")
async def stream_logs_sse():
    """Stream real-time log lines via Server-Sent Events (SSE) to the Web UI terminal."""
    async def event_generator():
        # First send initial backlog
        backlog = get_recent_logs(limit=50)
        for item in backlog:
            yield f"data: {json.dumps(item)}\n\n"

        # Stream new incoming logs
        async for log_entry in subscribe_logs():
            yield f"data: {json.dumps(log_entry)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
