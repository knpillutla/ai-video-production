"""Broadcast-Grade 4K Lower-Third Dossier Card Service (Option A).

Renders prestigious BBC/CNBC International frosted-glass educational cards
in the bottom-left safe zone (x=5.5%, y=78%) featuring:
1. Gold/Amber Kicker Badge (Category / Fact)
2. Bold Crisp White Chapter Title
3. Warm Ivory Subtitle
4. Quantitative Stats Bar with Hairline Divider
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Loads modern sans-serif font from system font candidates."""
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


def parse_dossier_kv_pairs(
    chapter_title: str,
    chapter_subtitle: Optional[str] = None,
    badge: Optional[str] = None,
    stats: Optional[str] = None,
) -> list[Tuple[str, str]]:
    """Extracts structured KEY-VALUE pairs from chapter metadata for broadcast display."""
    import re

    def _strip(txt: str) -> str:
        if not txt:
            return ""
        clean = re.sub(r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]", "", txt)
        return clean.replace("✦", "").replace("📊", "").replace("📍", "").strip()

    pairs: list[Tuple[str, str]] = []
    c_title = _strip(chapter_title or "")
    if c_title:
        pairs.append(("CHAPTER", c_title.upper()))

    if badge:
        c_badge = _strip(badge)
        if ":" in c_badge:
            k, v = c_badge.split(":", 1)
            pairs.append((k.strip().upper(), v.strip()))
        elif c_badge:
            pairs.append(("KEY FACT", c_badge))

    if stats:
        c_stats = _strip(stats)
        parts = [p.strip() for p in re.split(r"[•|]", c_stats) if p.strip()]
        for p in parts:
            if ":" in p:
                k, v = p.split(":", 1)
                pairs.append((k.strip().upper(), v.strip()))
            else:
                pairs.append(("STAT", p))

    if chapter_subtitle and len(pairs) < 5:
        c_sub = _strip(chapter_subtitle)
        if c_sub:
            pairs.insert(1, ("THEME", c_sub))

    return pairs[:5]


def create_documentary_dossier_card(
    chapter_title: str,
    chapter_subtitle: Optional[str] = None,
    stats: Optional[str] = None,
    badge: Optional[str] = None,
    target_res: Tuple[int, int] = (3840, 2160),
    position: str = "bottom_left",
) -> np.ndarray:
    """Renders a 4K RGBA key-value educational dossier overlay (defaults to bottom-left corner)."""
    w, h = target_res
    s = h / 2160.0

    pairs = parse_dossier_kv_pairs(
        chapter_title=chapter_title,
        chapter_subtitle=chapter_subtitle,
        badge=badge,
        stats=stats,
    )
    if not pairs:
        return np.zeros((h, w, 4), dtype=np.uint8)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_key = _load_font(int(34 * s), bold=True)
    font_val = _load_font(int(36 * s), bold=True)

    line_h = int(56 * s)
    total_h = len(pairs) * line_h + int(20 * s)

    if position == "top_right":
        key_widths = [draw.textbbox((0, 0), k, font=font_key)[2] - draw.textbbox((0, 0), k, font=font_key)[0] for k, _ in pairs]
        val_widths = [draw.textbbox((0, 0), v, font=font_val)[2] - draw.textbbox((0, 0), v, font=font_val)[0] for _, v in pairs]
        max_kw = max(key_widths) if key_widths else int(160 * s)
        max_vw = max(val_widths) if val_widths else int(340 * s)
        box_w = max_kw + max_vw + int(100 * s)
        start_x = int(w * 0.945) - box_w
        start_y = int(h * 0.065)
    else:
        start_x = int(w * 0.055)
        start_y = int(h * 0.82) - total_h

    bar_w = max(4, int(6 * s))

    # Ultra-sheer high-contrast backdrop (ensuring 100% legibility on mobile & desktop)
    scrim = Image.new("RGBA", (int(1120 * s), total_h + int(28 * s)), (8, 12, 20, 110))
    overlay.paste(scrim, (start_x, start_y - int(14 * s)), scrim)
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([start_x, start_y, start_x + bar_w, start_y + total_h], fill=(255, 196, 37, 255))

    cur_y = start_y + int(10 * s)
    text_pad = start_x + bar_w + int(26 * s)

    key_widths = [draw.textbbox((0, 0), k, font=font_key)[2] - draw.textbbox((0, 0), k, font=font_key)[0] for k, _ in pairs]
    max_kw = max(key_widths) if key_widths else int(160 * s)
    col_x = text_pad + max_kw + int(20 * s)
    val_x = col_x + int(24 * s)

    for k, v in pairs:
        for dx, dy in [(2, 2), (3, 3)]:
            draw.text((text_pad + dx, cur_y + dy), k, fill=(0, 0, 0, 220), font=font_key)
            draw.text((col_x + dx, cur_y + dy), ":", fill=(0, 0, 0, 220), font=font_key)
            draw.text((val_x + dx, cur_y + dy), v, fill=(0, 0, 0, 220), font=font_val)

        draw.text((text_pad, cur_y), k, fill=(255, 204, 51, 255), font=font_key)
        draw.text((col_x, cur_y), ":", fill=(240, 220, 180, 240), font=font_key)
        draw.text((val_x, cur_y), v, fill=(255, 255, 255, 255), font=font_val)
        cur_y += line_h

    return np.array(overlay)


def save_dossier_card_png(
    output_path: Path,
    chapter_title: str,
    chapter_subtitle: Optional[str] = None,
    stats: Optional[str] = None,
    badge: Optional[str] = None,
    target_res: Tuple[int, int] = (3840, 2160),
    position: str = "bottom_left",
) -> Path:
    """Renders and saves 4K RGBA key-value dossier overlay PNG card."""
    rgba = create_documentary_dossier_card(
        chapter_title=chapter_title,
        chapter_subtitle=chapter_subtitle,
        stats=stats,
        badge=badge,
        target_res=target_res,
        position=position,
    )
    img = Image.fromarray(rgba)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), format="PNG")
    logger.info(f"saved_dossier_card_png: {output_path.name} -> {target_res[0]}x{target_res[1]} at {position}")
    return output_path


__all__ = ["create_documentary_dossier_card", "save_dossier_card_png", "parse_dossier_kv_pairs"]
