"""Single-Pass 4K Vocal Video FFmpeg Assembly.

Extracts Stage 1 base crossfades and Stage 2 atmospheric VFX overlays.
Preserves Rule 4 (< 300 lines limit) and provides sub-second duration probing.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import re
import subprocess
from typing import Any

import imageio_ffmpeg

from src.core.telemetry import logger


def probe_audio_duration(audio_path: Path | str) -> float:
    """Probe exact duration in seconds of any audio file."""
    path = Path(audio_path)
    if not path.is_file():
        return 60.0
    if path.suffix.lower() == ".wav":
        try:
            import wave
            with wave.open(str(path), "rb") as w:
                return float(w.getnframes()) / float(w.getframerate())
        except Exception:
            pass
    try:
        proc = subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stderr)
        if m:
            return round(
                float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3)),
                2,
            )
    except Exception as e:
        logger.warning(f"probe_audio_duration_failed: {e}")
    return 60.0


async def assemble_vocal_video(
    image_paths: list[Path] | Path,
    song_path: Path,
    sub_path: Path | None,
    out_video_path: Path,
    duration: float,
    fps: int = 30,
    timeline_cues: list[dict[str, Any]] | None = None,
    fonts_dir: Path | str | None = None,
    static_canvas: bool = True,
    enable_vfx: bool = True,
    theme: str | None = None,
    episode_seed: int = 0,
    segment_durations: list[float] | None = None,
    enable_movement: bool = False,
    scene_movements: list[str] | None = None,
    is_mass: bool = False,
    scene_speeds: list[str] | None = None,
) -> Path:
    """Fast 2-Stage Assembly: Stage 1 Base Assembly (Static/2.5D Movement + xfade + Audio) -> Stage 2 Scene VFX."""
    imgs = [image_paths] if isinstance(image_paths, Path) else list(image_paths)
    if out_video_path.is_file() and out_video_path.stat().st_size > 1000:
        out_mt = out_video_path.stat().st_mtime
        stale = any(p.is_file() and p.stat().st_mtime > out_mt for p in imgs) or (
            song_path.is_file() and song_path.stat().st_mtime > out_mt
        )
        if not stale:
            logger.info(f"vocal_master_cached: reusing existing render {out_video_path.name}")
            return out_video_path
        logger.info(f"vocal_master_stale: re-rendering {out_video_path.name} due to updated source inputs")
    out_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    from src.compositor.vocal_fx import (
        compile_vocal_base_filter_complex,
        ensure_fx_overlay,
        resolve_scene_vfx_type,
    )

    base_target = out_video_path.parent / f"_temp_base_{out_video_path.name}" if enable_vfx else out_video_path

    # Stage 1: Fast Base Assembly (Images/Video clips + xfade + Audio + Subtitles + optional mass movement)
    base_filter = compile_vocal_base_filter_complex(
        len(imgs),
        duration,
        sub_path=sub_path,
        fonts_dir=fonts_dir,
        fps=fps,
        segment_durations=segment_durations,
        enable_movement=enable_movement,
        scene_movements=scene_movements,
        is_mass=is_mass,
        scene_speeds=scene_speeds,
    )
    img_args = [
        arg
        for p in imgs
        for arg in (
            ("-stream_loop", "-1", "-t", f"{duration:.2f}", "-i", str(p))
            if p.suffix.lower() == ".mp4"
            else ("-loop", "1", "-t", f"{duration:.2f}", "-i", str(p))
        )
    ]
    cmd_base = [
        ffmpeg, "-y", *img_args, "-i", str(song_path), "-t", f"{duration:.2f}",
        "-filter_complex", base_filter, "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-threads", "8", "-shortest", str(base_target),
    ]
    proc = await asyncio.create_subprocess_exec(*cmd_base, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr.decode(errors="replace")
        logger.error(f"ffmpeg_base_render_failed: {err_msg[-1200:]}")
        raise RuntimeError(f"FFmpeg base render error:\n{err_msg[-1200:]}")

    if not enable_vfx:
        return out_video_path

    # Stage 2: Fast Single-Overlay VFX Pass across Timeline (Scene-Matched & Seed-Randomized)
    fx_type = resolve_scene_vfx_type(theme=theme, timeline_cues=timeline_cues)
    vfx_clip = ensure_fx_overlay(fx_type, seed=episode_seed)
    logger.info(f"vocal_vfx_applied: fx_type={fx_type}, seed={episode_seed % 30}, clip={vfx_clip.name}")
    vfx_filter = (
        "[1:v]colorkey=0x000000:0.04:0.12,format=yuva420p,scale=3840:2160:flags=fast_bilinear[ov];"
        "[0:v][ov]overlay=x=0:y=0:format=auto[v_out]"
    )
    cmd_vfx = [
        ffmpeg, "-y", "-i", str(base_target), "-stream_loop", "-1", "-i", str(vfx_clip),
        "-filter_complex", vfx_filter, "-map", "[v_out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "copy",
        "-t", f"{duration:.2f}", "-threads", "8", str(out_video_path),
    ]
    proc_vfx = await asyncio.create_subprocess_exec(*cmd_vfx, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr_vfx = await proc_vfx.communicate()
    base_target.unlink(missing_ok=True)
    if proc_vfx.returncode != 0:
        err_msg = stderr_vfx.decode(errors="replace")
        logger.error(f"ffmpeg_vfx_render_failed: {err_msg[-1200:]}")
        raise RuntimeError(f"FFmpeg VFX overlay error:\n{err_msg[-1200:]}")
    return out_video_path


__all__ = ["probe_audio_duration", "assemble_vocal_video"]
