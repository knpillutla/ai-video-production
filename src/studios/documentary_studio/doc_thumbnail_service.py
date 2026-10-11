"""Documentary High-CTR 4K Thumbnail Compositor & A/B Packager.

Composites bold high-contrast YouTube travel thumbnails featuring:
- Hero landmark background (Big Ben, Tower Bridge, etc.)
- Punchy high-impact title typography ("LONDON IN 1 DAY")
- Schedule & route badges ("9 AM – 6 PM FULL ROUTE • MAP INCLUDED")
- 4K Ultra HD badge
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _load_best_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    """Load high-impact sans-serif font or fallback cleanly."""
    font_names = (
        ["montserrat-black.ttf", "impact.ttf", "arialbd.ttf", "calibrib.ttf", "segoeuib.ttf"]
        if bold
        else ["montserrat-bold.ttf", "arial.ttf", "calibri.ttf"]
    )
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_high_ctr_tour_thumbnail(
    bg_image_path: Path,
    title: str,
    output_path: Path,
    schedule_text: str = "9:00 AM – 6:00 PM • FULL ROUTE",
    target_res: tuple[int, int] = (1920, 1080),
) -> Path:
    """Composites a broadcast 1920x1080 (or 4K) YouTube thumbnail with high CTR aesthetics."""
    out = output_path.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. Open background and resize/crop to 16:9
    if bg_image_path.is_file():
        bg = Image.open(bg_image_path).convert("RGBA")
    else:
        bg = Image.new("RGBA", target_res, (20, 24, 32, 255))

    bg = bg.resize(target_res, Image.Resampling.LANCZOS)

    # 2. Add cinematic subtle dark gradient on the bottom and left for text legibility
    gradient_overlay = Image.new("RGBA", target_res, (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient_overlay)

    w, h = target_res
    # Left vignette & bottom gradient
    for y in range(int(h * 0.45), h):
        alpha = int(((y - h * 0.45) / (h * 0.55)) * 190)
        g_draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    # Diagonal corner shadow for punchy contrast
    for x in range(int(w * 0.65)):
        alpha = int((1.0 - (x / (w * 0.65))) * 110)
        g_draw.line([(x, 0), (x, h)], fill=(0, 0, 0, alpha))

    bg = Image.alpha_composite(bg, gradient_overlay)

    draw = ImageDraw.Draw(bg)

    # 3. Format Short High-CTR Headline (e.g. "LONDON IN 1 DAY")
    clean_title = title.upper()
    if ":" in clean_title:
        clean_title = clean_title.split(":")[0].strip()
    if len(clean_title) > 28:
        clean_title = clean_title[:28]

    # Primary headline font & size
    font_title = _load_best_font(size=int(h * 0.088), bold=True)
    font_badge = _load_best_font(size=int(h * 0.038), bold=True)
    font_tag = _load_best_font(size=int(h * 0.032), bold=True)

    # 4. Draw Badges (Top right 4K HDR badge)
    tag_text = "4K UHD • ITINERARY"
    tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    tag_pad_x, tag_pad_y = int(w * 0.015), int(h * 0.008)
    tag_x1 = w - tag_w - int(w * 0.04) - tag_pad_x * 2
    tag_y1 = int(h * 0.04)
    tag_x2 = tag_x1 + tag_w + tag_pad_x * 2
    tag_y2 = tag_y1 + tag_h + tag_pad_y * 2

    # Draw rounded pill for top-right 4K tag
    draw.rounded_rectangle([tag_x1, tag_y1, tag_x2, tag_y2], radius=int(h * 0.012), fill=(180, 20, 20, 230))
    draw.text((tag_x1 + tag_pad_x, tag_y1 + tag_pad_y - 2), tag_text, fill=(255, 255, 255, 255), font=font_tag)

    # 5. Draw Lower-Third Glass HUD Card for Headline & Schedule
    pad_left = int(w * 0.045)
    base_bottom = int(h * 0.90)

    # Schedule pill badge (e.g. "🕒 9:00 AM – 6:00 PM • FULL ROUTE MAP")
    pill_text = f"🕒 {schedule_text}"
    pill_bbox = draw.textbbox((0, 0), pill_text, font=font_badge)
    pill_w = pill_bbox[2] - pill_bbox[0]
    pill_h = pill_bbox[3] - pill_bbox[1]
    pill_px, pill_py = int(w * 0.012), int(h * 0.007)

    pill_y2 = base_bottom
    pill_y1 = pill_y2 - pill_h - pill_py * 2
    pill_x1 = pad_left
    pill_x2 = pill_x1 + pill_w + pill_px * 2

    # Glass cyan pill
    draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=int(h * 0.012), fill=(16, 42, 68, 225), outline=(56, 189, 248, 220), width=3)
    draw.text((pill_x1 + pill_px, pill_y1 + pill_py - 2), pill_text, fill=(56, 189, 248, 255), font=font_badge)

    # Massive High-Contrast Yellow/White Headline
    title_bbox = draw.textbbox((0, 0), clean_title, font=font_title)
    title_h = title_bbox[3] - title_bbox[1]
    title_y = pill_y1 - title_h - int(h * 0.025)

    # High-impact drop shadow for maximum punch
    shadow_offset = int(h * 0.005)
    draw.text((pad_left + shadow_offset, title_y + shadow_offset), clean_title, fill=(0, 0, 0, 240), font=font_title)
    draw.text((pad_left, title_y), clean_title, fill=(255, 225, 53, 255), font=font_title)

    # Convert to RGB and save JPEG
    final_img = bg.convert("RGB")
    final_img.save(out, "JPEG", quality=95)
    return out


def generate_documentary_thumbnail_variants(
    sb: Any,
    ep_dir: Path,
    keyframe_paths: List[Path],
) -> Dict[str, Any]:
    """Generates primary thumbnail and 3 distinct high-CTR test variants."""
    hero_img = keyframe_paths[0] if keyframe_paths and keyframe_paths[0].is_file() else None
    if not hero_img:
        # Fallback to keyframe in ep_dir
        for cand in [ep_dir / "keyframe_p1.jpg", ep_dir / "keyframe_p4.jpg"]:
            if cand.is_file():
                hero_img = cand
                break

    if not hero_img or not hero_img.is_file():
        return {}

    thumb_primary = ep_dir / "thumbnail.jpg"
    thumb_var_a = ep_dir / "thumbnail_variant_a.jpg"
    thumb_var_b = ep_dir / "thumbnail_variant_b.jpg"

    # Variant A: Clean city title + 9 AM - 6 PM route
    title_a = sb.title if hasattr(sb, "title") else "LONDON IN 1 DAY"
    if "in a day" in title_a.lower() or "1 day" in title_a.lower():
        clean_headline = "LONDON IN 1 DAY"
    else:
        clean_headline = title_a.split(":")[0].strip().upper()

    render_high_ctr_tour_thumbnail(
        bg_image_path=hero_img,
        title=clean_headline,
        output_path=thumb_primary,
        schedule_text="9:00 AM – 6:00 PM • FULL ROUTE",
    )
    # Mirror as variant A
    import shutil
    shutil.copy2(thumb_primary, thumb_var_a)

    # Variant B: "PERFECT 24H ITINERARY" using second major landmark if available
    hero_b = keyframe_paths[3] if len(keyframe_paths) >= 4 and keyframe_paths[3].is_file() else hero_img
    render_high_ctr_tour_thumbnail(
        bg_image_path=hero_b,
        title="PERFECT 1-DAY ROUTE",
        output_path=thumb_var_b,
        schedule_text="MAP INCLUDED • EVERY STOP TIMED",
    )

    package = {
        "primary_thumbnail": str(thumb_primary),
        "variants": [
            {"id": "A", "label": "Hero Landmark + City In 1 Day", "path": str(thumb_var_a)},
            {"id": "B", "label": "Iconic River Vista + Timed Schedule Badge", "path": str(thumb_var_b)},
        ],
    }
    (ep_dir / "thumbnail_packaging.json").write_text(json.dumps(package, indent=2), encoding="utf-8")
    return package
