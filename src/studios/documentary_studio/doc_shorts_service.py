"""Auto-Generated 9:16 YouTube Shorts & Reels Teaser Engine ($0.00 Spend).

Generates high-retention 9:16 vertical teasers (1080x1920) from 16:9 master 4K
documentary videos with center-cropping, cold-open hook pacing, and CTA outro.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Optional

import cv2
import numpy as np

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_templates import DocStoryboard


def render_shorts_cta_card(
    output_path: Path,
    title: str = "WATCH FULL 4K DOCUMENTARY",
    channel_name: str = "SUBSCRIBE FOR MORE",
) -> Path:
    """Render 1080x1920 RGBA overlay card with bottom call-to-action pill."""
    card = np.zeros((1920, 1080, 4), dtype=np.uint8)

    # Lower-third container (y: 1540 to 1800)
    y1, y2, x1, x2 = 1540, 1800, 60, 1020
    card[y1:y2, x1:x2] = (12, 14, 22, 230)

    # Accent top border (Gold: #D4AF37)
    card[y1 : y1 + 6, x1:x2] = (55, 175, 212, 255)

    # Pill button background (y: 1690 to 1760)
    by1, by2, bx1, bx2 = 1690, 1765, 100, 980
    card[by1:by2, bx1:bx2] = (55, 175, 212, 255)  # Gold pill

    # Text overlays using OpenCV
    cv2.putText(
        card,
        title[:32].upper(),
        (100, 1620),
        cv2.FONT_HERSHEY_DUPLEX,
        0.95,
        (255, 255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        card,
        "CLICK LINK / VISIT CHANNEL ▶",
        (130, 1740),
        cv2.FONT_HERSHEY_DUPLEX,
        0.85,
        (15, 15, 15, 255),
        2,
        cv2.LINE_AA,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), card)
    return output_path


def generate_documentary_shorts_teaser(
    master_video_path: Path,
    storyboard: DocStoryboard,
    output_dir: Path,
    max_duration_seconds: float = 45.0,
) -> Optional[Path]:
    """Generate 9:16 vertical teaser video (1080x1920) for YouTube Shorts & Reels.

    Extracts cold open hook and first scenes up to max_duration_seconds, applies
    cinematic 9:16 center-crop, overlays CTA outro card on the final 4 seconds.
    """
    output_file = output_dir / "master_9x16_shorts_teaser.mp4"

    # Tier 1 Local Disk Cache Check (Rule 3)
    if output_file.is_file() and output_file.stat().st_size > 1000:
        logger.info(f"reusing_existing_shorts_teaser: {output_file}")
        return output_file

    if not master_video_path.is_file() or master_video_path.stat().st_size < 1000:
        logger.warning(f"master_video_missing_for_shorts: {master_video_path}")
        return None

    # Determine teaser cut duration from cold open + early scenes
    teaser_dur = 0.0
    for scene in storyboard.scenes:
        if teaser_dur + scene.duration_seconds <= max_duration_seconds:
            teaser_dur += scene.duration_seconds
        else:
            break
    if teaser_dur < 10.0:
        teaser_dur = min(max_duration_seconds, 30.0)

    cta_card_path = output_dir / "shorts_cta_overlay.png"
    render_shorts_cta_card(
        cta_card_path,
        title=f"WATCH FULL: {storyboard.title[:24]}",
    )

    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_exe = "ffmpeg"

    # Single-pass FFmpeg: 9:16 center-crop + CTA overlay on last 4s
    cta_start = max(0.0, teaser_dur - 4.5)
    filter_complex = (
        f"[0:v]trim=0:{teaser_dur:.2f},setpts=PTS-STARTPTS,"
        f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=30[base];"
        f"[1:v]format=rgba[cta];"
        f"[base][cta]overlay=0:0:enable='gte(t,{cta_start:.2f})'[vout];"
        f"[0:a]atrim=0:{teaser_dur:.2f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={teaser_dur - 1.5:.2f}:d=1.5[aout]"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-ss", "0",
        "-t", f"{teaser_dur:.2f}",
        "-i", str(master_video_path),
        "-loop", "1", "-i", str(cta_card_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_file),
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"documentary_shorts_teaser_generated: {output_file.name} ({teaser_dur}s)")
        return output_file
    except subprocess.CalledProcessError as exc:
        logger.error(f"shorts_teaser_render_failed: {exc.stderr[:400]}")
        return None
