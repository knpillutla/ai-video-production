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
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


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


def _compose_multi_cut_background(image_paths: List[Path], target_res: tuple[int, int] = (1920, 1080)) -> Image.Image:
    """Composites up to 3 complementary attraction cuts into a dynamic angled diagonal collage."""
    w, h = target_res
    valid = [Path(p) for p in image_paths if Path(p).is_file()][:3]
    if not valid:
        return Image.new("RGBA", target_res, (20, 24, 32, 255))
    if len(valid) == 1:
        img = Image.open(valid[0]).convert("RGBA").resize(target_res, Image.Resampling.LANCZOS)
        return ImageEnhance.Color(img).enhance(1.25)

    base = Image.new("RGBA", target_res, (0, 0, 0, 255))
    if len(valid) == 2:
        polys = [
            [(0, 0), (int(w * 0.54), 0), (int(w * 0.46), h), (0, h)],
            [(int(w * 0.54), 0), (w, 0), (w, h), (int(w * 0.46), h)],
        ]
        seams = [((int(w * 0.54), 0), (int(w * 0.46), h))]
    else:
        polys = [
            [(0, 0), (int(w * 0.38), 0), (int(w * 0.31), h), (0, h)],
            [(int(w * 0.38), 0), (int(w * 0.72), 0), (int(w * 0.65), h), (int(w * 0.31), h)],
            [(int(w * 0.72), 0), (w, 0), (w, h), (int(w * 0.65), h)],
        ]
        seams = [((int(w * 0.38), 0), (int(w * 0.31), h)), ((int(w * 0.72), 0), (int(w * 0.65), h))]

    for p, poly in zip(valid, polys):
        img = Image.open(p).convert("RGBA").resize(target_res, Image.Resampling.LANCZOS)
        img = ImageEnhance.Color(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.10)
        mask = Image.new("L", target_res, 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        base.paste(img, (0, 0), mask)

    draw = ImageDraw.Draw(base)
    for (x1, y1), (x2, y2) in seams:
        draw.line([(x1 - 2, y1), (x2 - 2, y2)], fill=(0, 0, 0, 180), width=6)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 240), width=3)
        draw.line([(x1 + 1, y1), (x2 + 1, y2)], fill=(255, 215, 0, 200), width=1)
    return base


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

    bg = Image.open(bg_image_path).convert("RGBA") if bg_image_path.is_file() else Image.new("RGBA", target_res, (20, 24, 32, 255))
    bg = bg.resize(target_res, Image.Resampling.LANCZOS)

    gradient_overlay = Image.new("RGBA", target_res, (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient_overlay)
    w, h = target_res
    for y in range(int(h * 0.45), h):
        g_draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(((y - h * 0.45) / (h * 0.55)) * 190)))
    for x in range(int(w * 0.65)):
        g_draw.line([(x, 0), (x, h)], fill=(0, 0, 0, int((1.0 - (x / (w * 0.65))) * 110)))

    bg = Image.alpha_composite(bg, gradient_overlay)
    draw = ImageDraw.Draw(bg)

    clean_title = title.upper().split(":")[0].strip()[:28]
    font_title = _load_best_font(size=int(h * 0.088), bold=True)
    font_badge = _load_best_font(size=int(h * 0.038), bold=True)
    font_tag = _load_best_font(size=int(h * 0.032), bold=True)

    tag_text = "4K UHD • ITINERARY"
    t_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w, tag_h = t_bbox[2] - t_bbox[0], t_bbox[3] - t_bbox[1]
    tag_px, tag_py = int(w * 0.015), int(h * 0.008)
    tx1, ty1 = w - tag_w - int(w * 0.04) - tag_px * 2, int(h * 0.04)
    draw.rounded_rectangle([tx1, ty1, tx1 + tag_w + tag_px * 2, ty1 + tag_h + tag_py * 2], radius=int(h * 0.012), fill=(180, 20, 20, 230))
    draw.text((tx1 + tag_px, ty1 + tag_py - 2), tag_text, fill=(255, 255, 255, 255), font=font_tag)

    pad_left = int(w * 0.045)
    pill_text = f"🕒 {schedule_text}"
    p_bbox = draw.textbbox((0, 0), pill_text, font=font_badge)
    pw, ph = p_bbox[2] - p_bbox[0], p_bbox[3] - p_bbox[1]
    px, py = int(w * 0.012), int(h * 0.007)
    py2, py1 = int(h * 0.90), int(h * 0.90) - ph - py * 2
    draw.rounded_rectangle([pad_left, py1, pad_left + pw + px * 2, py2], radius=int(h * 0.012), fill=(16, 42, 68, 225), outline=(56, 189, 248, 220), width=3)
    draw.text((pad_left + px, py1 + py - 2), pill_text, fill=(56, 189, 248, 255), font=font_badge)

    title_h = draw.textbbox((0, 0), clean_title, font=font_title)[3] - draw.textbbox((0, 0), clean_title, font=font_title)[1]
    title_y = py1 - title_h - int(h * 0.025)
    draw.text((pad_left + int(h * 0.005), title_y + int(h * 0.005)), clean_title, fill=(0, 0, 0, 240), font=font_title)
    draw.text((pad_left, title_y), clean_title, fill=(255, 225, 53, 255), font=font_title)

    final_img = bg.convert("RGB")
    final_img.save(out, "JPEG", quality=95)
    return out


def render_high_ctr_curiosity_thumbnail(
    bg_image_paths: List[Path] | Path,
    headline: str,
    output_path: Path,
    badge_text: str = "4K DOCUMENTARY",
    target_res: tuple[int, int] = (1920, 1080),
) -> Path:
    """Composites a single winning high-CTR curiosity thumbnail with dynamic multi-cut background and 3D typography."""
    out = output_path.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    paths = [bg_image_paths] if isinstance(bg_image_paths, (str, Path)) else list(bg_image_paths)
    bg = _compose_multi_cut_background(paths, target_res)
    w, h = target_res

    overlay = Image.new("RGBA", target_res, (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(overlay)
    for y in range(int(h * 0.40), h):
        g_draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(((y - h * 0.40) / (h * 0.60)) * 200)))
    for x in range(int(w * 0.70)):
        g_draw.line([(x, 0), (x, h)], fill=(0, 0, 0, int((1.0 - (x / (w * 0.70))) * 160)))

    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)

    font_badge = _load_best_font(size=int(h * 0.034), bold=True)
    t_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    tw, th = t_bbox[2] - t_bbox[0], t_bbox[3] - t_bbox[1]
    bx, by = int(w * 0.045), int(h * 0.05)
    draw.rounded_rectangle([bx, by, bx + tw + int(w * 0.024), by + th + int(h * 0.014)], radius=int(h * 0.01), fill=(185, 28, 28, 235))
    draw.text((bx + int(w * 0.012), by + int(h * 0.007) - 2), badge_text, fill=(255, 255, 255, 255), font=font_badge)

    clean_hl = (headline or "WHAT IS THIS PLACE BEST KNOWN FOR?").strip().upper()
    words = clean_hl.split()
    lines = [" ".join(words[:len(words)//2]), " ".join(words[len(words)//2:])] if len(words) > 3 else [clean_hl]

    font_title = _load_best_font(size=int(h * 0.092), bold=True)
    pad_left = int(w * 0.045)
    total_h = sum((draw.textbbox((0, 0), l, font=font_title)[3] - draw.textbbox((0, 0), l, font=font_title)[1] + int(h * 0.015)) for l in lines)
    cur_y = int(h * 0.88) - total_h

    for i, line in enumerate(lines):
        sh_off, str_w = int(h * 0.008), max(4, int(h * 0.006))
        draw.text((pad_left + sh_off, cur_y + sh_off), line, fill=(0, 0, 0, 255), font=font_title)
        color = (255, 225, 53, 255) if (i == 0 or len(lines) == 1) else (255, 255, 255, 255)
        draw.text((pad_left, cur_y), line, fill=color, font=font_title, stroke_width=str_w, stroke_fill=(0, 0, 0, 255))
        l_h = draw.textbbox((0, 0), line, font=font_title)[3] - draw.textbbox((0, 0), line, font=font_title)[1]
        cur_y += l_h + int(h * 0.015)

    final_img = bg.convert("RGB")
    final_img.save(out, "JPEG", quality=95)
    return out


def generate_documentary_thumbnail_variants(
    sb: Any,
    ep_dir: Path,
    keyframe_paths: List[Path],
) -> Dict[str, Any]:
    """Generates the single best high-CTR documentary thumbnail with dynamic 3-panel attraction cuts."""
    hero_idx = getattr(sb, "thumbnail_hero_scene_index", 1) or 1
    valid_kfs = [Path(p) for p in (keyframe_paths or []) if Path(p).is_file()]
    if not valid_kfs:
        for cand in [ep_dir / f"keyframe_p{hero_idx}.jpg", ep_dir / "keyframe_p1.jpg", ep_dir / "keyframe_p2.jpg"]:
            if cand.is_file():
                valid_kfs.append(cand)
    if not valid_kfs:
        return {}

    hero_img = valid_kfs[hero_idx - 1] if (1 <= hero_idx <= len(valid_kfs)) else valid_kfs[0]
    cuts = [hero_img]
    remaining = [k for k in valid_kfs if str(k) != str(hero_img)]
    if len(remaining) >= 2:
        cuts.append(remaining[0])
        cuts.append(remaining[-1])
    elif remaining:
        cuts.append(remaining[0])

    thumb_primary = ep_dir / "thumbnail.jpg"
    from src.studios.documentary_studio.doc_curiosity_title_service import derive_contextual_doc_titles
    dest_name = getattr(sb, "destination_entity", None) or getattr(sb, "title", "").split(":")[0].strip()
    _, auto_thumb, _ = derive_contextual_doc_titles(dest_name, getattr(sb, "title", None))
    thumb_hl = getattr(sb, "thumbnail_headline", None)
    headline = auto_thumb if (not thumb_hl or "BEST KNOWN FOR" in thumb_hl.upper()) else thumb_hl
    badge = f"4K UHD • {dest_name.upper()}" if dest_name else "4K UHD • DOCUMENTARY"

    render_high_ctr_curiosity_thumbnail(
        bg_image_paths=cuts,
        headline=headline,
        output_path=thumb_primary,
        badge_text=badge,
    )

    import json
    package = {
        "primary_thumbnail": str(thumb_primary),
        "thumbnail_headline": headline,
        "hero_image": str(hero_img),
        "attraction_cuts": [str(c) for c in cuts],
    }
    (ep_dir / "thumbnail_packaging.json").write_text(json.dumps(package, indent=2), encoding="utf-8")
    return package


__all__ = [
    "render_high_ctr_tour_thumbnail",
    "render_high_ctr_curiosity_thumbnail",
    "generate_documentary_thumbnail_variants",
]
