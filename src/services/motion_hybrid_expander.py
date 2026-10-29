"""Hybrid Motion Expander Engine: 5s AI Diffusion Living Plate + 4K Local Drone Multi-Angle Expansion.

Combines high-fidelity organic AI living motion (H3 Max/Wan/Kling) for establishing vistas
with Tier-0 4K Local Perspective Drone ($0.00) secondary detail glides to span full narration
audio durations seamlessly without cuts or audio desynchronization.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import subprocess
from typing import Optional

import imageio_ffmpeg
from src.core.telemetry import logger

try:
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


async def expand_motion_clip_if_needed(
    diff_clip: Path,
    target_duration: Optional[float],
    image_path: Path,
    output_path: Path,
    secondary_image_path: Optional[Path] = None,
    motion_prompt: str = "",
    visual_prompt: str = "",
    target_fps: int = 24,
    xfade_duration: float = 0.5,
) -> Path:
    """Seamlessly expands a 5-second living diffusion clip to match full audio duration."""
    from src.services.ambient_export_service import get_media_duration
    from src.services.video_4k_encoder import ensure_video_4k

    if not diff_clip.is_file() or diff_clip.stat().st_size < 1000:
        raise FileNotFoundError(f"Diffusion clip missing or empty: {diff_clip}")

    ensure_video_4k(diff_clip)
    actual_dur = get_media_duration(diff_clip)

    # If duration matches or exceeds target within margin, no expansion required
    if not target_duration or (target_duration - actual_dur) < 1.2:
        import shutil
        shutil.copy2(diff_clip, output_path)
        ensure_video_4k(output_path)
        logger.info(f"motion_hybrid_expander: No expansion required ({actual_dur:.2f}s vs target {target_duration}s)")
        return output_path

    # Determine secondary angle asset and camera choreography
    has_secondary = (
        secondary_image_path is not None
        and secondary_image_path.is_file()
        and secondary_image_path.stat().st_size > 1000
    )
    if not has_secondary:
        # Never loop or freeze the last frame of a 5s AI diffusion clip (which would freeze moving water/people/cars).
        # Instead, keep the AI diffusion clip at its native 5.0s living duration and let complementary local_drone shots cover the chapter.
        logger.info(f"motion_hybrid_expander: Retaining native {actual_dur:.2f}s AI diffusion clip without looping or freezing ({output_path.name})")
        import shutil
        shutil.copy2(diff_clip, output_path)
        ensure_video_4k(output_path)
        return output_path

    sec_img = secondary_image_path
    shortfall = float(target_duration) - actual_dur
    rem_dur = round(shortfall + xfade_duration, 2)
    xfade_offset = max(0.5, round(actual_dur - xfade_duration, 2))
    logger.info(
        f"motion_hybrid_expander: Expanding {actual_dur:.2f}s diffusion clip -> {target_duration:.2f}s "
        f"(rem_dur: {rem_dur:.2f}s, xfade_offset: {xfade_offset:.2f}s) for {output_path.name}"
    )

    start_zoom = "normal"

    # Select complementary secondary movement
    p_text = f"{visual_prompt} {motion_prompt}".lower()
    choreo = "crane_ascend" if any(k in p_text for k in ("crane", "tower", "church", "cathedral", "spire")) else "dollyin"

    rem_clip = output_path.parent / f"rem_drone_{output_path.stem}.mp4"
    try:
        from src.scripts.local_perspective_drone import render_perspective_drone_clip
        await render_perspective_drone_clip(
            image_path=sec_img,
            output_path=rem_clip,
            duration_seconds=rem_dur,
            fps=target_fps,
            target_res=(3840, 2160),
            choreography=choreo,
            start_pan="center",
            start_zoom=start_zoom,
            start_tilt="center",
            curve="cosine",
            force_rerun=True,
        )

        if not rem_clip.is_file() or rem_clip.stat().st_size < 1000:
            raise RuntimeError(f"Failed to render secondary local drone expansion clip: {rem_clip}")

        # Execute single-pass FFmpeg 4K xfade at target_fps
        filter_str = (
            f"[0:v]fps={target_fps},scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
            f"[1:v]fps={target_fps},scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
            f"[v0][v1]xfade=transition=fade:duration={xfade_duration}:offset={xfade_offset},format=yuv420p[outv]"
        )
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(diff_clip),
            "-i", str(rem_clip),
            "-filter_complex", filter_str,
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            str(output_path),
        ]
        def _run_xfade():
            return subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        res = await asyncio.to_thread(_run_xfade)
        if res.returncode != 0 or not output_path.is_file() or output_path.stat().st_size < 1000:
            err_msg = res.stderr.decode(errors="ignore")[:200]
            logger.warning(f"motion_hybrid_expander: FFmpeg xfade failed ({err_msg}), retaining raw diffusion 4K")
            import shutil
            shutil.copy2(diff_clip, output_path)
            ensure_video_4k(output_path)
            return output_path

        # Cleanup scratch secondary drone clip only (NEVER delete raw diff_clip)
        try:
            if rem_clip.exists():
                rem_clip.unlink()
        except Exception:
            pass

        logger.info(
            f"motion_hybrid_expander: Successfully created {target_duration:.2f}s master clip "
            f"({output_path.name}) via living plate + secondary sequential angle."
        )
        return output_path

    except Exception as e:
        logger.error(f"motion_hybrid_expander_error: {type(e).__name__}: {e}. Retaining raw diffusion 4K.")
        if diff_clip.is_file():
            import shutil
            shutil.copy2(diff_clip, output_path)
            ensure_video_4k(output_path)
        return output_path


__all__ = ["expand_motion_clip_if_needed"]
