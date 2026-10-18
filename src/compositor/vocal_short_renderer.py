"""Vocal 9:16 Vertical Short Video Renderer.

Intelligently selects the keyframe featuring full character poses and renders a high-CTR
9:16 vertical YouTube Short with singing audio beginning on the vocal onset.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger
from src.services.font_manager import ensure_language_font


def select_full_pose_image(ep_dir: Path, sb_data: dict[str, Any], fallback: Path) -> Path:
    """Intelligently pick the image showing full character poses, avoiding cropped or tight vehicle/table shots."""
    scenes_dir = ep_dir / "scenes"
    scene_files = sorted(scenes_dir.glob("scene_*.jpg"))
    if not scene_files:
        scene_files = sorted(ep_dir.glob("scene_*.jpg"))
    if not scene_files:
        return fallback if fallback.is_file() else (ep_dir / "keyframe_p1.jpg")

    scenes_meta = sb_data.get("scenes", [])
    best_file = scene_files[-1]
    best_score = -100

    full_pose_kw = {"full", "lawn", "garden", "back-to-back", "standing", "skirt", "trousers", "anklet", "pose", "poses", "side-by-side"}
    partial_kw = {"car", "convertible", "table", "bistro", "close_up", "close-up", "portrait"}

    for img_path in scene_files:
        score = 0
        try:
            idx = int(img_path.stem.split("_")[-1])
        except Exception:
            idx = -1
        desc, shot_type = "", ""
        if 1 <= idx <= len(scenes_meta):
            m = scenes_meta[idx - 1]
            desc = f"{m.get('character_pose', '')} {m.get('visual_prompt', '')}".lower()
            shot_type = m.get("camera_shot_type", "").lower()

        for kw in full_pose_kw:
            if kw in desc or kw in shot_type:
                score += 3
        for pkw in partial_kw:
            if pkw in desc or pkw in shot_type:
                score -= 4
        score += idx
        if score > best_score:
            best_score = score
            best_file = img_path

    logger.info(f"selected_full_pose_image: {best_file.name} (score={best_score})")
    return best_file


def render_vocal_short_video(
    full_pose_img: Path,
    audio_path: Path,
    output_path: Path,
    sb_data: dict[str, Any],
    language: str,
    vocal_start: float,
    duration: float = 30.0,
) -> None:
    """Render a 9:16 vertical Short showing full character poses with blurred backdrop, title banner, and singing audio."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ov = output_path.parent / f"_temp_overlay_{output_path.stem}.png"
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_name, fonts_dir = ensure_language_font(language)
    font_file = fonts_dir / font_name if (fonts_dir / font_name).is_file() else Path(f"storage/fonts/{language}/Mandali-Regular.ttf")

    try:
        font_lg = ImageFont.truetype(str(font_file), 50)
        font_sm = ImageFont.truetype(str(font_file), 32)
    except Exception:
        font_lg = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    title_loc = sb_data.get("title_localized") or sb_data.get("title_en", "")
    sub_title = "Soulful Romantic Melody"

    draw.rounded_rectangle([100, 130, 980, 270], radius=40, fill=(15, 23, 42, 220), outline=(255, 255, 255, 70), width=2)
    draw.text((540, 178), title_loc, font=font_lg, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((540, 228), sub_title, font=font_sm, fill=(226, 232, 240, 230), anchor="mm")

    draw.rounded_rectangle([200, 1680, 880, 1770], radius=35, fill=(15, 23, 42, 220), outline=(255, 215, 0, 120), width=2)
    draw.text((540, 1725), "Watch Full 4K Video On Channel", font=font_sm, fill=(255, 215, 0, 255), anchor="mm")
    overlay.save(ov)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    fade_out_st = max(1.0, duration - 0.5)
    v_filter = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.15[bg];"
        "[0:v]scale=1080:-1[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
        f"[base][1:v]overlay=0:0,fade=t=in:st=0:d=0.5,fade=t=out:st={fade_out_st:.2f}:d=0.5[v]"
    )
    a_filter = f"afade=t=in:st=0:d=0.5,afade=t=out:st={fade_out_st:.2f}:d=0.5"

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-t", f"{duration:.2f}", "-i", str(full_pose_img),
        "-loop", "1", "-t", f"{duration:.2f}", "-i", str(ov),
        "-ss", f"{vocal_start:.2f}", "-t", f"{duration:.2f}", "-i", str(audio_path),
        "-filter_complex", v_filter,
        "-map", "[v]", "-map", "2:a",
        "-af", a_filter,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    try:
        ov.unlink(missing_ok=True)
    except Exception:
        pass


__all__ = ["select_full_pose_image", "render_vocal_short_video"]
