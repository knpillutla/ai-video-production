"""Single-Pass Long-Play Master Video Stretcher with Circadian Fade-to-Black.

Stretches 60s 4K video masters into 1-Hour, 3-Hour, or 8-Hour sleep broadcasts
with optional Circadian OLED Black Screen dimming for bedroom TV/monitor comfort.
"""

from pathlib import Path
import subprocess
from typing import Optional
import imageio_ffmpeg

from src.core.telemetry import logger


def export_long_play_broadcast(
    source_4k_video: Path | str,
    output_long_play: Path | str,
    target_duration_seconds: float = 3600.0,  # default 1 hour
    fade_to_black_hours: Optional[float] = None,
    target_resolution: str = "3840x2160",
) -> Path:
    """Export long-play 4K video with optional Circadian Fade-to-Black."""
    src = Path(source_4k_video).resolve()
    out = Path(output_long_play).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not src.is_file():
        raise FileNotFoundError(f"Source video master not found: {src}")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    logger.info(f"stretching_long_play_video: {src.name} -> {out.name} ({target_duration_seconds}s, fade_to_black={fade_to_black_hours}h)")

    if fade_to_black_hours and (fade_to_black_hours * 3600.0) < target_duration_seconds:
        fade_start_sec = fade_to_black_hours * 3600.0
        # Visual fades to black at fade_start_sec while audio continues uninterrupted
        vf_filter = (
            f"[0:v]fade=t=out:st={int(fade_start_sec)}:d=30:color=black,"
            f"drawbox=y=0:color=black@1.0:t=fill:enable='gte(t,{int(fade_start_sec + 30)})'[v]"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-stream_loop", "-1", "-i", str(src),
            "-filter_complex", vf_filter,
            "-map", "[v]", "-map", "0:a",
            "-t", str(target_duration_seconds),
            "-c:v", "libx264", "-preset", "ultrafast", "-threads", "4", "-crf", "18",
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(out)
        ]
    else:
        # Visually lossless 0-CPU-cost stream copy
        cmd = [
            ffmpeg_bin, "-y",
            "-stream_loop", "-1",
            "-i", str(src),
            "-t", str(target_duration_seconds),
            "-c", "copy",
            "-movflags", "+faststart",
            str(out)
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"long_play_export_complete: {out.name} ({round(out.stat().st_size / (1024*1024), 2)} MB)")
    except subprocess.CalledProcessError as err:
        logger.warning(f"stream_copy_failed_fallback_reencode: {err}")
        cmd_fallback = [
            ffmpeg_bin, "-y",
            "-stream_loop", "-1",
            "-i", str(src),
            "-t", str(target_duration_seconds),
            "-c:v", "libx264", "-preset", "ultrafast", "-threads", "4", "-crf", "18",
            "-c:a", "aac", "-b:a", "320k",
            "-movflags", "+faststart",
            str(out)
        ]
        subprocess.run(cmd_fallback, capture_output=True, check=True)

    return out


def stretch_channel_episode_background(channel_name: str, episode_id: str) -> Path:
    """Find channel episode directory on disk and stretch master video to target long-play duration."""
    import json
    channel_slug = "earth_serenade" if "earth" in channel_name.lower() else ("silent_hearth" if "silent" in channel_name.lower() or "sleep" in channel_name.lower() else "rain_and_quill")
    ep_dir = Path("storage/channels") / channel_slug / episode_id
    if not ep_dir.is_dir():
        # Search all channels for the episode ID
        for ch in Path("storage/channels").iterdir():
            if ch.is_dir() and (ch / episode_id).is_dir():
                ep_dir = ch / episode_id
                break

    master_path = ep_dir / "master_4k_ambient.mp4"
    if not master_path.is_file():
        raise FileNotFoundError(f"Cannot find master_4k_ambient.mp4 in {ep_dir}")

    # Read target hours from youtube_packaging.json if present
    pkg_file = ep_dir / "youtube_packaging.json"
    hours, fade_h = 3.0, None
    if "silent" in channel_slug or "sleep" in channel_slug:
        hours, fade_h = 8.0, 2.0
    if pkg_file.is_file():
        try:
            pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
            hours = pkg.get("long_play_hours", hours)
            fade_h = pkg.get("fade_to_black_hours", fade_h)
        except Exception:
            pass

    suffix = f"_{int(fade_h)}h_black" if fade_h else ""
    hour_label = int(hours) if hours.is_integer() else hours
    out_lp = ep_dir / f"master_4k_{hour_label}hour{suffix}_sleep.mp4"
    return export_long_play_broadcast(source_4k_video=master_path, output_long_play=out_lp, target_duration_seconds=hours * 3600.0, fade_to_black_hours=fade_h)
