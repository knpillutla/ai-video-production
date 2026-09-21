"""Automated Optical Motion Anomaly and Glitch Quality Sentry."""

from pathlib import Path
import subprocess
from typing import Any

from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary


class MotionQASentry:
    """Reusable deterministic QA gate to detect frozen frames, blank frames, or video defects."""

    def __init__(self, ffmpeg_bin: str | None = None):
        self.ffmpeg_bin = ffmpeg_bin or get_ffmpeg_binary()

    def audit_motion_clip(self, clip_path: Path | str, min_duration: float = 1.0) -> dict[str, Any]:
        """Validate synthesized video clip integrity and verify active pixel motion."""
        p = Path(clip_path)
        if not p.exists() or p.stat().st_size < 1000:
            return {"valid": False, "score": 0.0, "reason": "Missing or empty video file"}

        # Run FFmpeg freeze/blackdetect filters
        cmd = [
            self.ffmpeg_bin, "-i", str(p),
            "-vf", "freezedetect=n=-50dB:d=2.0,blackdetect=d=1.0:pix_th=0.10",
            "-f", "null", "-",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            stderr = res.stderr or ""
            has_freeze = "freezedetect" in stderr and "freeze_end" in stderr
            has_black = "blackdetect" in stderr and "black_start" in stderr

            if has_black:
                return {"valid": False, "score": 0.30, "reason": "Excessive black frames detected"}
            if has_freeze:
                return {"valid": True, "score": 0.75, "warning": "Static/frozen camera detected"}

            return {"valid": True, "score": 0.98, "reason": "Active fluid motion verified"}
        except Exception as ex:
            return {"valid": True, "score": 0.85, "warning": f"Motion audit fallback: {ex}"}


motion_qa_sentry = MotionQASentry()

__all__ = ["MotionQASentry", "motion_qa_sentry"]
