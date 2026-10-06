"""Stream Copy Audio Muxer for Zero-Cost Dual 4K Video Masters."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("StreamCopyMuxer")


def mux_stream_copy_audio(
    source_video: Path,
    audio_stem: Path,
    output_video: Path,
    force_rerun: bool = False,
) -> Optional[Path]:
    """Mux alternative audio stem into 4K video using FFmpeg -c:v copy (1-2s, $0.00 cost)."""
    if not source_video.is_file() or source_video.stat().st_size < 1000:
        logger.warning(f"mux_stream_copy_skipped: Source video {source_video} not found or empty.")
        return None

    if not audio_stem.is_file() or audio_stem.stat().st_size < 1000:
        logger.warning(f"mux_stream_copy_skipped: Audio stem {audio_stem} not found or empty.")
        return None

    if (
        not force_rerun
        and output_video.is_file()
        and output_video.stat().st_size > 1000
        and output_video.stat().st_mtime >= source_video.stat().st_mtime
    ):
        logger.info(f"mux_stream_copy_cached: Reusing existing {output_video.name}")
        return output_video

    cmd = [
        "ffmpeg", "-y",
        "-i", str(source_video),
        "-i", str(audio_stem),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(output_video),
    ]

    try:
        logger.info(f"mux_stream_copy_executing: {source_video.name} + {audio_stem.name} -> {output_video.name}")
        proc = subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if output_video.is_file() and output_video.stat().st_size > 1000:
            logger.info(f"mux_stream_copy_success: Generated {output_video.name} ({output_video.stat().st_size / (1024*1024):.1f} MB)")
            return output_video
        return None
    except subprocess.CalledProcessError as err:
        err_msg = err.stderr.decode("utf-8", errors="replace") if err.stderr else str(err)
        logger.error(f"mux_stream_copy_failed: {err_msg[:400]}")
        return None
