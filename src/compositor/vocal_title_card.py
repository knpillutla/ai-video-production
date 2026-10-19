"""Deterministic 4K Scene 0 Title Card Generator for Vocal Music Videos.

Generates a broadcast-grade opening title card (scene_00.jpg / scene_000_title.jpg) overlaying:
1. Native language song title (using regional fonts for Hindi, Telugu, Bengali, etc.)
2. English song title
3. Song type descriptor (Romantic Song, Kids Song, Soulful Ballad, etc.)
with high-CTR glassmorphic vignette backing, precision boundary padding, and drop shadows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from src.core.telemetry import logger
from src.scripts.local_thumbnail import _get_font


def resolve_song_mood_label(
    sub_genre: str | None = None,
    mood: str | None = None,
    theme: str | None = None,
    genre: str | None = None,
    music_style: str | None = None,
    idea: str | None = None,
    storyboard_data: dict[str, Any] | None = None,
    suno_tags: str | None = None,
    hook_thesis: str | None = None,
    song_type: str | None = None,
) -> str:
    """Derive a clean, culturally authentic audience-facing song type label from Gemini script data."""
    if storyboard_data:
        song_type = song_type or storyboard_data.get("song_type")
        mood = mood or storyboard_data.get("mood")
        suno_tags = suno_tags or storyboard_data.get("suno_tags")
        hook_thesis = hook_thesis or storyboard_data.get("hook_thesis")
        sub_genre = sub_genre or storyboard_data.get("sub_genre")

    if song_type and any(k in song_type.upper() for k in ("SOULFUL", "ROMANTIC", "FOLK", "KIDS", "DEVOTIONAL", "CLASSICAL", "POP", "LO-FI", "HEARTBREAK")):
        clean_st = song_type.strip().strip("•✦★-|").strip().upper()
        return f"•  {clean_st}  •"

    text = f"{sub_genre or ''} {mood or ''} {theme or ''} {genre or ''} {music_style or ''} {idea or ''} {suno_tags or ''} {hook_thesis or ''}".lower()
    if any(k in text for k in ("kid", "nursery", "rhyme", "child", "cartoon", "toddler", "animation")):
        return "•  KIDS FUN & RHYME  •"
    if any(k in text for k in ("soulful", "sad", "heartbreak", "emotional", "dard", "melancholy", "pathos", "acoustic ballad", "viraha", "separation")):
        return "•  SOULFUL MELODY  •"
    if any(k in text for k in ("romantic", "love", "romance", "prema", "pyaar", "ishq", "ballad", "crush", "sweet")):
        return "•  ROMANTIC SONG  •"
    if any(k in text for k in ("folk", "mass", "dance", "jathara", "teenmaar", "bhangra", "festive", "dappu", "kuthu")):
        return "•  ENERGETIC FOLK  •"
    if any(k in text for k in ("devotional", "bhajan", "spiritual", "puja", "stotram", "temple", "divine")):
        return "•  DEVOTIONAL SONG  •"
    if any(k in text for k in ("classical", "carnatic", "hindustani", "raga", "thumri")):
        return "•  CLASSICAL MELODY  •"
    if any(k in text for k in ("pop", "upbeat", "synth", "party", "club")):
        return "•  POP TRACK  •"
    if any(k in text for k in ("lofi", "lo-fi", "chill", "relaxing", "cozy")):
        return "•  LO-FI CHILL  •"
    if music_style:
        return f"•  {music_style.strip().upper()}  •"
    return "•  ROMANTIC SONG  •"


resolve_song_type_label = resolve_song_mood_label


def _load_title_font(size: int = 60, language: str = "en", preferred_font: str | None = None) -> ImageFont.ImageFont:
    """Load bold, premium broadcast-grade title font matching target language."""
    lang = (language or "en").lower().strip()

    # If a specific preferred font family is requested
    if preferred_font:
        for p in (Path(f"storage/fonts/en/{preferred_font}.ttf"), Path(f"storage/fonts/{lang}/{preferred_font}.ttf")):
            if p.is_file():
                try:
                    return ImageFont.truetype(str(p), size=size)
                except Exception:
                    pass

    # 1. Native Indic / Regional Fonts (Rozha One, Ramabhadra, Mandali, Rajdhani)
    if lang in ("te", "hi", "mr", "bn", "or", "gu", "pa", "ta", "kn", "ml"):
        lang_dir = Path("storage/fonts") / lang
        if lang_dir.is_dir():
            for pref in ("Rozha", "Ramabhadra", "Mandali", "Rajdhani", "NotoSans"):
                for ttf in lang_dir.glob(f"*{pref}*.ttf"):
                    try:
                        return ImageFont.truetype(str(ttf), size=size)
                    except Exception:
                        pass
            for ttf in lang_dir.glob("*.ttf"):
                try:
                    return ImageFont.truetype(str(ttf), size=size)
                except Exception:
                    continue
        for win_p in (Path("C:/Windows/Fonts/NirmalaB.ttf"), Path("C:/Windows/Fonts/Nirmala.ttc")):
            if win_p.is_file():
                try:
                    return ImageFont.truetype(str(win_p), size=size)
                except Exception:
                    continue

    # 2. Cinematic English Title fonts (Cinzel, Montserrat, Roboto)
    for latin_candidate in (
        Path("storage/fonts/en/Cinzel-Bold.ttf"),
        Path("storage/fonts/en/Montserrat-Bold.ttf"),
        Path("storage/fonts/en/Roboto.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ):
        if latin_candidate.is_file():
            try:
                return ImageFont.truetype(str(latin_candidate), size=size)
            except Exception:
                continue

    return _get_font(size=size, language=language)


def generate_vocal_title_card(
    base_image_path: Path | str,
    title_localized: str,
    title_en: str,
    song_type: str,
    language: str = "en",
    output_path: Path | str | None = None,
    target_res: tuple[int, int] = (3840, 2160),
) -> Path:
    """Create a 4K title card image (scene_00.jpg) overlaying native title, English title, and song type."""
    base_p = Path(base_image_path)
    out_p = Path(output_path) if output_path else base_p.parent / "scene_00.jpg"
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not base_p.is_file():
        raise FileNotFoundError(f"Base image not found for title card: {base_p}")

    with Image.open(base_p) as src_img:
        img = src_img.convert("RGBA")
        if img.size != target_res:
            img = img.resize(target_res, Image.Resampling.LANCZOS)

    w, h = target_res
    scale = h / 2160.0

    # 1. Cinematic Fonts Hierarchy
    f_loc_size = int(150 * scale)
    f_en_size = int(82 * scale)
    f_type_size = int(40 * scale)

    font_loc = _load_title_font(size=f_loc_size, language=language)
    font_en = _load_title_font(size=f_en_size, language="en", preferred_font="Cinzel-Bold")
    font_type = _load_title_font(size=f_type_size, language="en", preferred_font="Montserrat-Bold")

    line1 = (title_localized or title_en).strip()
    clean_en = (title_en or "").strip()
    line2 = "   ".join(clean_en.split()) if clean_en and clean_en.lower() != line1.lower() else ""

    # Clean Song Type text for pill
    raw_type = song_type.strip().strip("•✦★-|").strip().upper()
    line3 = f"•   {raw_type}   •"

    def _get_metrics(text: str, font: Any) -> tuple[int, int, int, int]:
        d = ImageDraw.Draw(img)
        bb = d.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]

    tw1, th1, ox1, oy1 = _get_metrics(line1, font_loc)
    tw2, th2, ox2, oy2 = _get_metrics(line2, font_en) if line2 else (0, 0, 0, 0)
    tw3, th3, ox3, oy3 = _get_metrics(line3, font_type)

    # Pill badge dimensions with generous boundary safety padding
    pad_pill_x = int(68 * scale)
    pad_pill_y = int(20 * scale)
    pill_w = tw3 + pad_pill_x * 2
    pill_h = th3 + pad_pill_y * 2

    spacing_1_2 = int(24 * scale) if line2 else 0
    spacing_2_3 = int(32 * scale)

    # 2. Atmospheric Lower-Third Vignette (Smooth gradient without intrusive card box)
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for y in range(int(h * 0.54), h):
        prog = (y - int(h * 0.54)) / (h * 0.46)
        alpha = int(210 * (prog ** 1.35))
        vdraw.line([(0, y), (w, y)], fill=(6, 10, 18, alpha))

    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img)

    # 3. Floating Cinematic Typography in Lower Third
    cx = w // 2
    curr_y = int(h * 0.74)

    def _draw_shadowed_text(pos: tuple[int, int], text: str, font: Any, fill_color: Any, shadow_color: Any = (0, 0, 0, 255), radius: int = 6) -> None:
        x, y = pos
        for dx in range(-radius, radius + 1, max(1, radius // 2)):
            for dy in range(-radius, radius + 1, max(1, radius // 2)):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=fill_color)

    # Line 1: Regional Hero Title (DirectWrite HarfBuzz for Indic; PIL for Latin)
    from src.compositor.indic_text_renderer import is_complex_indic_script, render_indic_text_directwrite
    indic_img = render_indic_text_directwrite(line1, font_size=f_loc_size, max_width=int(w * 0.88)) if is_complex_indic_script(line1) else None

    if indic_img:
        ix = cx - (indic_img.width // 2)
        iy = curr_y - int(10 * scale)
        img.alpha_composite(indic_img, (ix, iy))
        draw = ImageDraw.Draw(img)
        curr_y += indic_img.height + spacing_1_2
    else:
        _draw_shadowed_text((cx - (tw1 // 2) - ox1, curr_y - oy1), line1, font_loc, (255, 255, 255), radius=7)
        curr_y += th1 + spacing_1_2

    # Line 2: English Song Title (Cinzel tracked uppercase)
    if line2:
        _draw_shadowed_text((cx - (tw2 // 2) - ox2, curr_y - oy2), line2, font_en, (241, 245, 249), radius=5)
        curr_y += th2 + spacing_2_3

    # Line 3: Luxury Capsule Badge with Flanking Gold Hairlines
    px0 = cx - (pill_w // 2)
    py0 = curr_y
    px1 = px0 + pill_w
    py1 = py0 + pill_h

    # Flanking gold hairlines and accent dots
    flank_len = int(240 * scale)
    line_y = (py0 + py1) // 2
    draw.line([(px0 - flank_len, line_y), (px0 - int(24 * scale), line_y)], fill=(245, 158, 11, 160), width=max(1, int(2 * scale)))
    draw.line([(px1 + int(24 * scale), line_y), (px1 + flank_len, line_y)], fill=(245, 158, 11, 160), width=max(1, int(2 * scale)))
    draw.ellipse([px0 - flank_len - int(5 * scale), line_y - int(4 * scale), px0 - flank_len + int(3 * scale), line_y + int(4 * scale)], fill=(245, 158, 11, 200))
    draw.ellipse([px1 + flank_len - int(3 * scale), line_y - int(4 * scale), px1 + flank_len + int(5 * scale), line_y + int(4 * scale)], fill=(245, 158, 11, 200))

    # Pill Drop Shadow & Frosted Obsidian Body
    draw.rounded_rectangle([px0 + 4, py0 + 4, px1 + 4, py1 + 4], radius=pill_h // 2, fill=(0, 0, 0, 180))
    draw.rounded_rectangle([px0, py0, px1, py1], radius=pill_h // 2, fill=(12, 18, 32, 220), outline=(245, 158, 11, 240), width=max(2, int(2.5 * scale)))

    # Perfectly Centered Pill Text
    pill_cx = (px0 + px1) // 2
    pill_cy = (py0 + py1) // 2
    draw.text((pill_cx - (tw3 // 2) - ox3, pill_cy - (th3 // 2) - oy3), line3, font=font_type, fill=(253, 224, 71))

    final_rgb = img.convert("RGB")
    final_rgb.save(out_p, "JPEG", quality=95, optimize=True)
    logger.info(f"vocal_title_card_created: {out_p.name} ({final_rgb.size[0]}x{final_rgb.size[1]}, {out_p.stat().st_size} bytes)")
    return out_p


def create_vocal_title_card(
    base_image_path: Path | str,
    output_path: Path | str,
    title_localized: str,
    title_en: str,
    song_type: str,
    language: str = "en",
    target_res: tuple[int, int] = (3840, 2160),
) -> Path:
    """Positional output_path alias for generate_vocal_title_card."""
    return generate_vocal_title_card(
        base_image_path=base_image_path, title_localized=title_localized, title_en=title_en,
        song_type=song_type, language=language, output_path=output_path, target_res=target_res,
    )


def create_thumbnail_from_title_card(
    title_card_path: Path | str,
    output_path: Path | str,
    target_res: tuple[int, int] = (1280, 720),
) -> Path:
    """Downscale 4K title card to high-CTR 1280x720 thumbnail with subtle contrast pop."""
    src_p = Path(title_card_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src_p) as im:
        thumb = im.convert("RGB").resize(target_res, Image.Resampling.LANCZOS)
        thumb = ImageEnhance.Color(thumb).enhance(1.12)
        thumb = ImageEnhance.Contrast(thumb).enhance(1.10)
        thumb = ImageEnhance.Sharpness(thumb).enhance(1.20)
        thumb.save(out_p, "JPEG", quality=92, optimize=True)
    return out_p


__all__ = [
    "resolve_song_mood_label",
    "resolve_song_type_label",
    "generate_vocal_title_card",
    "create_vocal_title_card",
    "create_thumbnail_from_title_card",
]
