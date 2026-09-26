"""Automated 9:16 Vertical Shorts & TikTok Teaser Generator for Ambient Productions."""

from pathlib import Path
import subprocess
from typing import Optional
import imageio_ffmpeg

from src.core.telemetry import logger


def generate_ambient_short(
    source_4k_video: Path | str,
    output_short_path: Path | str,
    duration_seconds: float = 20.0,
    hook_text: str = "Put on headphones if you need to sleep tonight... 🎧",
    aspect_ratio: str = "1080:1920",
) -> Path:
    """Generate a 9:16 vertical Short from the 4K horizontal master."""
    src = Path(source_4k_video).resolve()
    out = Path(output_short_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not src.is_file():
        raise FileNotFoundError(f"Source master video not found: {src}")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    logger.info(f"generating_ambient_short: {src.name} -> {out.name} ({duration_seconds}s)")

    # 9:16 Center Crop + Lanczos Scale + Smooth 0.5s In/Out Loop Fades
    fade_out_start = max(1.0, duration_seconds - 0.5)
    vf_filters = [
        "crop=ih*9/16:ih:iw/2-(ih*9/16)/2:0",
        f"scale={aspect_ratio.replace(':', 'x')}:flags=lanczos",
        "fade=t=in:st=0:d=0.5",
        f"fade=t=out:st={fade_out_start:.2f}:d=0.5",
    ]
    af_filters = [
        "afade=t=in:st=0:d=0.5",
        f"afade=t=out:st={fade_out_start:.2f}:d=0.5",
    ]

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", "0",
        "-i", str(src),
        "-t", str(duration_seconds),
        "-vf", ",".join(vf_filters),
        "-af", ",".join(af_filters),
        "-c:v", "libx264", "-preset", "veryfast", "-threads", "4", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out)
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"ambient_short_generated: {out.name}")
    except subprocess.CalledProcessError as err:
        logger.error(f"failed_to_generate_short: {err}")
        raise

    return out
