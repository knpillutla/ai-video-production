"""In-memory Job State & SSE Streaming Manager for Video Production."""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, Optional

from src.core.telemetry import logger


class ProductionJobManager:
    """Manages asynchronous production job lifecycle and Server-Sent Events (SSE)."""

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._events: Dict[str, asyncio.Event] = {}

    def create_job(self, job_id: str, episode_id: str, title: str, channel_id: str, user_id: str = "user_krishna_01") -> Dict[str, Any]:
        """Register a new production job with initial stage state and user isolation."""
        state = {
            "job_id": job_id,
            "user_id": user_id,
            "episode_id": episode_id,
            "title": title,
            "channel_id": channel_id,
            "stage": 1,
            "progress": 5,
            "status": "processing",
            "keyframes": [],
            "motion_clips": [],
            "audio_stems": [],
            "video_url": None,
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self._jobs[job_id] = state
        self._events[job_id] = asyncio.Event()
        return state

    def update_job(
        self,
        job_id: str,
        stage: Optional[int] = None,
        progress: Optional[int] = None,
        status: Optional[str] = None,
        keyframes: Optional[list] = None,
        motion_clips: Optional[list] = None,
        audio_stems: Optional[list] = None,
        video_url: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update job stage, artifacts, and notify SSE event listeners."""
        job = self._jobs.get(job_id)
        if not job:
            return None

        if stage is not None:
            job["stage"] = stage
        if progress is not None:
            job["progress"] = progress
        if status is not None:
            job["status"] = status
        if keyframes is not None:
            job["keyframes"] = keyframes
        if motion_clips is not None:
            job["motion_clips"] = motion_clips
        if audio_stems is not None:
            job["audio_stems"] = audio_stems
        if video_url is not None:
            job["video_url"] = video_url
        if error is not None:
            job["error"] = error
            job["status"] = "failed"

        job["updated_at"] = time.time()

        # Signal SSE listener
        ev = self._events.get(job_id)
        if ev:
            ev.set()

        return job

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve current job state."""
        return self._jobs.get(job_id)

    async def stream_job(self, job_id: str) -> AsyncGenerator[str, None]:
        """Stream SSE chunks as the job transitions through stages."""
        last_progress = -1
        while True:
            job = self._jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'job_not_found', 'status': 'failed'})}\n\n"
                break

            if job["progress"] != last_progress:
                last_progress = job["progress"]
                yield f"data: {json.dumps(job)}\n\n"

            if job.get("status") in ("completed", "failed"):
                break

            ev = self._events.get(job_id)
            if ev:
                try:
                    await asyncio.wait_for(ev.wait(), timeout=1.0)
                    ev.clear()
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(0.5)


job_manager = ProductionJobManager()
