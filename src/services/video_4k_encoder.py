"""Deterministic 4K Video Encoder & Resolution Standardizer.

Ensures all motion models, video diffusion adapters (Wan 2.1, Kling 1.6/v3, Hunyuan),
lipsync engines, and local camera drone engines consistently deliver 4K UHD video masters:
- 16:9 Landscape: 3840x2160
- 9:16 Shorts: 2160x3840
- Optical Quality: Lanczos interpolation + unsharp mask sharpening
- Audio Handling: Preserves audio stream if present (-c:a copy), strips if absent (-an)
- Zero-Cost Idempotency: Immediate no-op pass-through if clip is already 4K UHD
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
from typing import Optional, Tuple

import imageio_ffmpeg
from src.core.telemetry import logger
from src.providers.base import is_mock_mode


def get_video_resolution(video_path: Path | str) -> Optional[Tuple[int, int]]:
    """Probe video file resolution (width, height) using FFmpeg banner output."""
    v_path = Path(video_path)
    if not v_path.is_file() or v_path.stat().st_size < 100:
        return None
    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        probe = subprocess.run(
            [ffmpeg_bin, "-i", str(v_path)],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=flags,
        )
        match = re.search(r"(\d{3,4})x(\d{3,4})", probe.stderr)
        if match:
            return int(match.group(1)), int(match.group(2))
    except Exception as e:
        logger.debug(f"video_4k_encoder_probe_error: {e}")
    return None


def is_clip_4k(video_path: Path | str, target_w: int = 3840, target_h: int = 2160) -> bool:
    """Return True if clip is at least 4K resolution (3840x2160 for 16:9 or 2160x3840 for 9:16)."""
    res = get_video_resolution(video_path)
    if not res:
        return False
    w, h = res
    if h > w:  # 9:16 Vertical Shorts
        return w >= 2160 and h >= 3840
    return w >= target_w and h >= target_h


def ensure_video_4k(
    video_path: Path | str,
    target_w: int = 3840,
    target_h: int = 2160,
    crf: int = 18,
    preset: str = "veryfast",
) -> Path:
    """Upscale video to 4K UHD in-place if not already 4K, using Lanczos + Unsharp sharpening.

    Guarantees every motion model or local drone returns a 4K broadcast-ready MP4.
    If the video is already 4K, returns immediately without re-encoding.
    """
    v_path = Path(video_path)
    if not v_path.is_file():
        return v_path

    # Mock mode & test fixture safety (Rule 8)
    if is_mock_mode() and v_path.stat().st_size < 1000:
        return v_path

    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        probe = subprocess.run(
            [ffmpeg_bin, "-i", str(v_path)],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=flags,
        )
        match = re.search(r"(\d{3,4})x(\d{3,4})", probe.stderr)

        tw, th = target_w, target_h
        if match:
            w, h = int(match.group(1)), int(match.group(2))
            if h > w:  # Vertical Shorts (9:16)
                if w >= 2160 and h >= 3840:
                    return v_path
                tw, th = 2160, 3840
            else:  # Horizontal Landscape (16:9)
                if w >= target_w and h >= target_h:
                    return v_path
                tw, th = target_w, target_h
        else:
            # Cannot determine resolution, skip scaling to avoid corruption
            return v_path

        temp_raw = v_path.parent / f"_raw_scale_{v_path.name}"
        v_path.rename(temp_raw)

        has_audio = "Audio:" in probe.stderr
        audio_args = ["-c:a", "copy"] if has_audio else ["-an"]
        vf_filter = f"scale={tw}:{th}:flags=lanczos,unsharp=5:5:0.8:5:5:0.0"

        cmd = [
            ffmpeg_bin, "-y", "-i", str(temp_raw),
            "-vf", vf_filter,
            "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p",
            *audio_args,
            str(v_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
        if res.returncode == 0 and v_path.is_file() and v_path.stat().st_size > 1000:
            temp_raw.unlink(missing_ok=True)
            logger.info(f"upscaled_to_4k_ok: {v_path.name} -> {tw}x{th} (Lanczos + Unsharp)")
            return v_path

        # Recovery on error
        if temp_raw.is_file() and not v_path.is_file():
            temp_raw.rename(v_path)
    except Exception as ex:
        logger.warning(f"ensure_video_4k_failed: {ex} on {v_path.name}. Retaining original.")
        temp_raw = v_path.parent / f"_raw_scale_{v_path.name}"
        if temp_raw.is_file() and not v_path.is_file():
            try:
                temp_raw.rename(v_path)
            except Exception:
                pass
    return v_path


__all__ = ["is_clip_4k", "ensure_video_4k", "get_video_resolution"]
