"""Broadcast-grade 4K Documentary Overlay Service.

Renders pure white typographic location overlay on the bottom-left corner
fading in for 6 seconds and fading out smoothly (BBC / National Geographic standard).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Loads modern sans-serif font from Windows / Linux system locations."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).is_file():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_documentary_location_lower_third(
    location_name: str,
    target_res: Tuple[int, int] = (3840, 2160),
) -> np.ndarray:
    """Renders a prestigious, clean white typographic location overlay on the bottom-left corner."""
    w, h = target_res
    s = h / 2160.0

    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    clean_loc = (location_name or "").strip()
    if not clean_loc:
        return overlay

    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_main = _load_font(int(46 * s), bold=True)

    # Bottom-left placement with television broadcast safe margins
    x = int(w * 0.055)
    y = int(h * 0.88)

    # Soft dark drop shadow for 100% legibility on light/snow/sky backgrounds
    shadow_offset = max(2, int(3 * s))
    draw.text((x + shadow_offset, y + shadow_offset), clean_loc, fill=(0, 0, 0, 220), font=font_main)
    # Pure white typography
    draw.text((x, y), clean_loc, fill=(255, 255, 255, 255), font=font_main)

    return np.array(pil_overlay)


def apply_location_fade_overlay_to_mp4(
    mp4_path: Path,
    location_name: str,
    duration_sec: float = 5.0,
    display_sec: float = 6.0,
) -> bool:
    """Applies clean white bottom-left location typography fading in and out for up to 6s using FFmpeg."""
    if not mp4_path.is_file() or not location_name or not location_name.strip():
        return False

    real_dur = duration_sec
    try:
        from src.services.ambient_export_service import get_media_duration
        d = get_media_duration(mp4_path)
        if d and d > 0.5:
            real_dur = d
    except Exception:
        pass

    eff_display = min(display_sec, real_dur)
    fade_in_d = min(0.8, eff_display * 0.2)
    fade_out_st = max(0.5, eff_display - fade_in_d)

    rgba = create_documentary_location_lower_third(location_name=location_name)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as png_tmp, \
         tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out_tmp:
        png_p = Path(png_tmp.name)
        out_p = Path(out_tmp.name)

    try:
        Image.fromarray(rgba).save(png_p, format="PNG")
        filt = (
            f"[1:v]format=rgba,fade=t=in:st=0:d={fade_in_d:.2f}:alpha=1,"
            f"fade=t=out:st={fade_out_st:.2f}:d={fade_in_d:.2f}:alpha=1[ov];"
            f"[0:v][ov]overlay=0:0:shortest=1"
        )
        cmd = [
            "ffmpeg", "-y", "-i", str(mp4_path), "-loop", "1", "-i", str(png_p),
            "-filter_complex", filt, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "copy", str(out_p)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_p.is_file() and out_p.stat().st_size > 1000:
            out_p.replace(mp4_path)
            return True
        return False
    except Exception as e:
        logger.warning(f"failed_to_apply_location_overlay_to_mp4: {e}")
        return False
    finally:
        png_p.unlink(missing_ok=True)
        out_p.unlink(missing_ok=True)


__all__ = [
    "_load_font",
    "create_documentary_location_lower_third",
    "apply_location_fade_overlay_to_mp4",
]
