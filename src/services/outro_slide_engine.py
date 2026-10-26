"""4K Cinematic End-of-Video Outro Slide & Video Clip Generator.

Produces broadcast-grade 4K closing slides and video cards for documentaries and tour itineraries,
providing an elegant narrative conclusion with fade-to-black instead of repetitive clip looping.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional, Tuple
import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger


def is_documentary_or_tour(genre: str, sub_genre: str = "", archetype: str = "") -> bool:
    """Return True if genre/format is narrative documentary or tour itinerary."""
    combined = f"{genre} {sub_genre} {archetype}".lower()
    doc_tokens = ("documentary", "doc", "historical_epic", "blue_chip", "nature_doc")
    tour_tokens = ("travel", "tour", "walking", "itinerary", "vacation_planner", "scenic_tour")
    return any(t in combined for t in doc_tokens) or any(t in combined for t in tour_tokens)


def render_4k_outro_slide(
    output_image_path: Path,
    title: str,
    channel_name: str = "Euro Discovery",
    is_tour: bool = False,
    tour_stops: Optional[List[Dict[str, Any]]] = None,
    base_keyframe_path: Optional[Path] = None,
    target_res: Tuple[int, int] = (3840, 2160),
) -> Path:
    """Renders a prestigious 4K cinematic closing slide with frosted glass slate and elegant typography."""
    out = Path(output_image_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    w, h = target_res

    # 1. Background Generation: Frosted Blurred Final Keyframe or Midnight Slate Gradient
    if base_keyframe_path and Path(base_keyframe_path).is_file():
        try:
            raw_bg = cv2.imread(str(base_keyframe_path))
            if raw_bg is not None:
                resized_bg = cv2.resize(raw_bg, (w, h), interpolation=cv2.INTER_LANCZOS4)
                # Fast downsample optical blur for creamy cinematic depth of field
                small = cv2.resize(resized_bg, (960, 540), interpolation=cv2.INTER_LINEAR)
                blurred_sm = cv2.GaussianBlur(small, (35, 35), 18)
                bg = cv2.resize(blurred_sm, (w, h), interpolation=cv2.INTER_CUBIC)
                # Darken background to 35% for contrast
                bg = np.clip(bg.astype(np.float32) * 0.35, 0, 255).astype(np.uint8)
            else:
                bg = _create_slate_gradient(w, h)
        except Exception as bg_err:
            logger.warning(f"outro_keyframe_blur_fallback: {bg_err}")
            bg = _create_slate_gradient(w, h)
    else:
        bg = _create_slate_gradient(w, h)

    # 2. Add subtle vignette
    vignette = _create_radial_vignette(w, h)
    bg = (bg.astype(np.float32) * vignette[:, :, None]).astype(np.uint8)

    # Convert to PIL for anti-aliased typography
    pil_img = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img, "RGBA")

    # Font setup
    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 36)
        font_title = ImageFont.truetype("arialbd.ttf", 68)
        font_sub = ImageFont.truetype("arial.ttf", 38)
        font_body = ImageFont.truetype("arial.ttf", 32)
        font_callout = ImageFont.truetype("arialbd.ttf", 44)
    except Exception:
        font_badge = font_title = font_sub = font_body = font_callout = ImageFont.load_default()

    # 3. Center Glassmorphism Slate
    cw, ch = 2800, 1360
    cx0 = (w - cw) // 2
    cy0 = (h - ch) // 2
    cx1 = cx0 + cw
    cy1 = cy0 + ch

    # Semi-transparent dark glass backing
    glass_rect = [cx0, cy0, cx1, cy1]
    draw.rounded_rectangle(glass_rect, radius=28, fill=(14, 18, 26, 215), outline=(65, 110, 160, 180), width=3)

    # Top accent cyan/gold brand band
    band_h = 10
    draw.rounded_rectangle([cx0 + 20, cy0 + 4, cx1 - 20, cy0 + 4 + band_h], radius=5, fill=(0, 210, 255, 230))

    # Channel & Category Badge
    badge_label = f"TRAVEL EXPEDITION CONCLUDED • {channel_name.upper()}" if is_tour else f"DOCUMENTARY ODYSSEY CONCLUDED • {channel_name.upper()}"
    draw.text((cx0 + 100, cy0 + 90), badge_label, fill=(0, 210, 255), font=font_badge)

    # Main Title (wrapped to fit)
    wrapped_title = _wrap_text(title, max_chars=48)
    cur_y = cy0 + 160
    for line in wrapped_title[:2]:
        draw.text((cx0 + 100, cur_y), line, fill=(255, 255, 255), font=font_title)
        cur_y += 85

    # Decorative Divider Line
    cur_y += 30
    draw.line([cx0 + 100, cur_y, cx1 - 100, cur_y], fill=(70, 95, 125, 180), width=2)
    cur_y += 60

    # Content Area based on Type
    if is_tour and tour_stops:
        num_stops = len(tour_stops)
        draw.text((cx0 + 100, cur_y), "COMPLETE ITINERARY SUMMARY", fill=(180, 210, 240), font=font_sub)
        cur_y += 55

        # Horizontal Pill Badges for Tour Metrics
        badges = [
            f"🏛️ {num_stops} Stops Explored",
            "🚶 Guided Walking Legs",
            "🗺️ Circuit Concluded",
            "⭐ Certified Experience",
        ]
        badge_x = cx0 + 100
        for b_text in badges:
            bbox = draw.textbbox((badge_x, cur_y), b_text, font=font_body)
            bw = (bbox[2] - bbox[0]) + 40
            draw.rounded_rectangle([badge_x, cur_y - 6, badge_x + bw, cur_y + 44], radius=12, fill=(28, 42, 60, 240), outline=(0, 210, 255, 150), width=2)
            draw.text((badge_x + 20, cur_y), b_text, fill=(240, 248, 255), font=font_body)
            badge_x += bw + 30
        cur_y += 120

        draw.text((cx0 + 100, cur_y), "Thank You For Travelling With Us", fill=(0, 210, 255), font=font_callout)
        cur_y += 60
        draw.text((cx0 + 100, cur_y), "Safe travels and continuous discovery on your next adventure.", fill=(200, 210, 225), font=font_sub)
    else:
        # Standard Documentary Outro
        draw.text((cx0 + 100, cur_y), "A CINEMATIC EXPLORATION OF OUR LIVING WORLD", fill=(180, 210, 240), font=font_sub)
        cur_y += 80

        # Elegant Callouts
        draw.text((cx0 + 100, cur_y), "Thank You For Watching", fill=(0, 210, 255), font=font_callout)
        cur_y += 75
        draw.text((cx0 + 100, cur_y), "Subscribe and join us as we uncover timeless landscapes and cultural wonders.", fill=(225, 235, 245), font=font_sub)
        cur_y += 60
        draw.text((cx0 + 100, cur_y), "Mastered in 4K UHD 24fps • Broadcast Edition", fill=(130, 155, 185), font=font_body)

    # Save to disk
    pil_img.convert("RGB").save(str(out), "JPEG", quality=96)
    logger.info(f"outro_slide_rendered: {out.name}")
    return out


def render_4k_outro_video(
    output_video_path: Path,
    outro_image_path: Path,
    duration_seconds: float = 4.5,
    fade_duration: float = 1.5,
    fps: int = 24,
    crf: int = 22,
) -> Path:
    """Renders 4K 24fps MP4 video clip of the outro slide with a smooth 1.5s fade-to-black."""
    out = Path(output_video_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file() and out.stat().st_size > 1000:
        return out

    in_img = Path(outro_image_path).resolve()
    if not in_img.is_file() or in_img.stat().st_size < 100:
        logger.warning(f"outro_image_missing_or_empty: {in_img}")
        return out

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    fade_start = max(0.5, duration_seconds - fade_duration)
    vf_filter = f"scale=3840:2160,fps={fps},fade=t=out:st={fade_start:.2f}:d={fade_duration:.2f}"

    cmd = [
        ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
        "-loop", "1", "-i", str(in_img),
        "-vf", vf_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4",
        "-crf", str(crf), "-t", f"{duration_seconds:.2f}",
        "-movflags", "+faststart", str(out),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as err:
        logger.error(f"render_4k_outro_video primary failed: {err.stderr or err.stdout}")
        try:
            cmd_fallback = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-loop", "1", "-i", str(in_img),
                "-t", f"{duration_seconds:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "ultrafast", str(out),
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True, text=True)
        except Exception as fb_err:
            logger.error(f"render_4k_outro_video fallback failed: {fb_err}")
            return out

    logger.info(f"outro_video_clip_rendered: {out.name} ({duration_seconds}s)")
    return out


def _create_slate_gradient(w: int, h: int) -> np.ndarray:
    """Generate subtle dark midnight slate gradient."""
    bg = np.zeros((h, w, 3), dtype=np.uint8)
    for y_idx in range(h):
        blend = y_idx / float(h)
        bg[y_idx, :] = [int(22 * (1 - blend) + 10 * blend), int(18 * (1 - blend) + 8 * blend), int(14 * (1 - blend) + 6 * blend)]
    return bg


def _create_radial_vignette(w: int, h: int) -> np.ndarray:
    """Create radial vignette matrix for edge darkening."""
    x = np.linspace(-1, 1, w, dtype=np.float32)
    y = np.linspace(-1, 1, h, dtype=np.float32)
    gx, gy = np.meshgrid(x, y)
    r = np.sqrt(gx**2 + gy**2)
    vignette = np.clip(1.0 - (r * 0.45), 0.35, 1.0)
    return vignette


def _wrap_text(text: str, max_chars: int = 48) -> List[str]:
    """Wrap string into lines respecting word boundaries."""
    words = text.split()
    lines: List[str] = []
    current: List[str] = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > max_chars and current:
            lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines
