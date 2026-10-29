"""Broadcast-grade 4K Lower-Third Documentary Attraction Overlay Service.

Renders cinema-grade frosted-glass lower-third location cards for educational documentaries,
featuring clean typography, golden accent borders, and safe-margin positioning.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
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


def create_documentary_lower_third_overlay(
    attraction_name: str,
    sub_location: Optional[str] = None,
    target_res: Tuple[int, int] = (3840, 2160),
    position: str = "bottom_left",
    theme: str = "gold_subtitle",
) -> np.ndarray:
    """Renders a prestigious 4K RGBA location overlay card with high-contrast typography."""
    w, h = target_res
    s = h / 2160.0  # Scale factor normalized to 4K

    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_title = _load_font(int(44 * s), bold=True)
    font_sub = _load_font(int(26 * s), bold=True)

    clean_title = (attraction_name or "Iconic Landmark").strip().upper()[:42]
    clean_sub = (sub_location or "").strip()[:54]

    t_bbox = draw.textbbox((0, 0), clean_title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]

    sub_w = 0
    if clean_sub:
        s_bbox = draw.textbbox((0, 0), clean_sub, font=font_sub)
        sub_w = s_bbox[2] - s_bbox[0]

    content_w = max(title_w, sub_w)
    card_w = max(int(480 * s), min(int(w * 0.45), content_w + int(70 * s)))
    card_h = int(120 * s) if clean_sub else int(85 * s)

    if position == "top_right":
        card_x = int(w * 0.945) - card_w
        card_y = int(h * 0.065)
    else:
        # Bottom-left safe zone: x=5.5% from left, y=82% from top (well above YouTube progress bar)
        card_x = int(w * 0.055)
        card_y = int(h * 0.82) - (card_h - int(85 * s))

    bar_w = max(4, int(5 * s))
    card_rgba = np.zeros((card_h, card_w, 4), dtype=np.uint8)

    if theme == "pearl_black":
        # Frosted Pearl Glass (light background with crisp black / slate font)
        card_rgba[:, :] = [250, 250, 252, 215]
        card_rgba[:, :bar_w] = [217, 119, 6, 255]
        card_rgba[0, :] = [255, 255, 255, 180]
        card_rgba[-1, :] = [200, 205, 215, 120]
        card_rgba[:, -1] = [200, 205, 215, 120]
        t_color, s_color = (15, 23, 42, 255), (71, 85, 105, 255)
    else:
        # Midnight Charcoal Glass with Gold Subtitle (highest contrast and visual luxury)
        card_rgba[:, :] = [10, 15, 26, 185]
        card_rgba[:, :bar_w] = [255, 196, 37, 255]
        card_rgba[0, :] = [255, 255, 255, 50]
        card_rgba[-1, :] = [255, 255, 255, 50]
        card_rgba[:, -1] = [255, 255, 255, 50]
        t_color, s_color = (255, 255, 255, 255), (255, 204, 51, 255)

    overlay[card_y : card_y + card_h, card_x : card_x + card_w] = card_rgba
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    # Text Rendering with subtle drop shadow
    text_x = card_x + bar_w + int(24 * s)
    title_y = card_y + int(14 * s)

    if theme != "pearl_black":
        draw.text((text_x + 2, title_y + 2), clean_title, fill=(0, 0, 0, 220), font=font_title)
    draw.text((text_x, title_y), clean_title, fill=t_color, font=font_title)

    if clean_sub:
        sub_y = title_y + int(52 * s)
        if theme != "pearl_black":
            draw.text((text_x + 2, sub_y + 2), clean_sub, fill=(0, 0, 0, 220), font=font_sub)
        draw.text((text_x, sub_y), clean_sub, fill=s_color, font=font_sub)

    return np.array(pil_overlay)


def create_documentary_chapter_title_card(
    chapter_title: str,
    chapter_subtitle: Optional[str] = None,
    key_stats: Optional[str] = None,
    target_res: Tuple[int, int] = (3840, 2160),
) -> np.ndarray:
    """Renders a prestigious centered 4K RGBA frosted-glass chapter slate."""
    w, h = target_res
    s = h / 2160.0

    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_badge = _load_font(int(24 * s), bold=True)
    font_title = _load_font(int(52 * s), bold=True)
    font_sub = _load_font(int(28 * s), bold=False)
    font_stats = _load_font(int(24 * s), bold=False)

    clean_title = (chapter_title or "CHAPTER").strip().upper()[:44]
    clean_sub = (chapter_subtitle or "").strip()[:64]
    clean_stats = (key_stats or "").strip()[:80]

    t_bbox = draw.textbbox((0, 0), clean_title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    sub_w = 0
    if clean_sub:
        s_bbox = draw.textbbox((0, 0), clean_sub, font=font_sub)
        sub_w = s_bbox[2] - s_bbox[0]
    stats_w = 0
    if clean_stats:
        st_bbox = draw.textbbox((0, 0), clean_stats, font=font_stats)
        stats_w = st_bbox[2] - st_bbox[0]

    content_w = max(title_w, sub_w, stats_w)
    card_w = max(int(780 * s), min(int(w * 0.72), content_w + int(140 * s)))

    num_lines = 1 + (1 if clean_sub else 0) + (1 if clean_stats else 0)
    card_h = int((125 + (num_lines * 40)) * s)

    card_x = (w - card_w) // 2
    card_y = int(h * 0.22)

    card_rgba = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    card_rgba[:, :] = [12, 16, 26, 220]

    bar_h = max(3, int(4 * s))
    card_rgba[:bar_h, :] = [255, 204, 51, 255]
    card_rgba[-1, :] = [255, 255, 255, 60]
    card_rgba[:, 0] = [255, 255, 255, 60]
    card_rgba[:, -1] = [255, 255, 255, 60]

    overlay[card_y : card_y + card_h, card_x : card_x + card_w] = card_rgba
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    cur_y = card_y + int(22 * s)
    tag_text = "✦ NATIONAL DOSSIER ✦"
    draw.text((w // 2, cur_y), tag_text, fill=(255, 215, 0, 230), font=font_badge, anchor="mt")
    cur_y += int(34 * s)

    draw.text((w // 2, cur_y), clean_title, fill=(255, 255, 255, 255), font=font_title, anchor="mt")
    cur_y += int(62 * s)

    if clean_sub:
        draw.text((w // 2, cur_y), clean_sub, fill=(240, 225, 185, 240), font=font_sub, anchor="mt")
        cur_y += int(40 * s)

    if clean_stats:
        div_w = int(card_w * 0.6)
        div_x1 = (w - div_w) // 2
        div_x2 = div_x1 + div_w
        draw.line([(div_x1, cur_y), (div_x2, cur_y)], fill=(255, 215, 0, 80), width=max(1, int(s)))
        cur_y += int(10 * s)
        draw.text((w // 2, cur_y), f"📊 {clean_stats}", fill=(220, 235, 255, 220), font=font_stats, anchor="mt")

    return np.array(pil_overlay)


def create_documentary_fact_badge_overlay(
    fact_text: str,
    target_res: Tuple[int, int] = (3840, 2160),
) -> np.ndarray:
    """Renders a prestigious 4K RGBA frosted-glass pill badge in the middle-right quadrant."""
    w, h = target_res
    s = h / 2160.0

    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_badge = _load_font(int(28 * s), bold=True)
    font_sub = _load_font(int(18 * s), bold=False)

    clean_fact = (fact_text or "").strip()[:52]
    if not clean_fact:
        return overlay

    bbox = draw.textbbox((0, 0), clean_fact, font=font_badge)
    text_w = bbox[2] - bbox[0]
    card_w = max(int(360 * s), text_w + int(60 * s))
    card_h = int(95 * s)

    # Position in safe middle-right quadrant (x=94% from right, y=38% from top)
    card_x = int(w * 0.94) - card_w
    card_y = int(h * 0.38)

    card_rgba = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    card_rgba[:, :] = [12, 18, 30, 215]  # Deep frosted obsidian

    # Golden left border accent & subtle glass borders
    l_w = max(3, int(4 * s))
    card_rgba[:, :l_w] = [255, 204, 51, 255]
    card_rgba[0, :] = [255, 255, 255, 60]
    card_rgba[-1, :] = [255, 255, 255, 60]
    card_rgba[:, -1] = [255, 255, 255, 60]

    overlay[card_y : card_y + card_h, card_x : card_x + card_w] = card_rgba
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    cur_x = card_x + int(24 * s)
    cur_y = card_y + int(14 * s)

    draw.text((cur_x, cur_y), "✦ VERIFIED DOSSIER FACT ✦", fill=(255, 215, 0, 230), font=font_sub)
    cur_y += int(28 * s)
    draw.text((cur_x, cur_y), clean_fact, fill=(255, 255, 255, 255), font=font_badge)

    return np.array(pil_overlay)


def build_shot_documentary_hud(sp_data: dict, ch: dict, shot: dict) -> Optional[dict]:
    """Build complete broadcast graphics HUD config for Shot 1 of a documentary chapter."""
    if int(shot.get("shot_index") or 1) != 1:
        return None
    return {
        "is_documentary": True,
        "attraction_name": ch.get("location_hub") or shot.get("location_hub") or ch.get("chapter_title") or "Landmark",
        "sub_location": ch.get("chapter_title") or "",
        "chapter_title": ch.get("chapter_title"),
        "chapter_subtitle": ch.get("chapter_subtitle"),
        "chapter_stats": ch.get("chapter_stats"),
        "fact_badge": ch.get("fact_badge"),
        "country_entity": sp_data.get("destination_entity") or (sp_data.get("title") or "").split(":")[0].strip(),
        "position": "bottom_left",
        "display_duration": 6.0,
    }


__all__ = [
    "create_documentary_lower_third_overlay",
    "create_documentary_chapter_title_card",
    "create_documentary_fact_badge_overlay",
    "build_shot_documentary_hud",
]

