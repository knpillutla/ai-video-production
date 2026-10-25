"""Tier-0 Deterministic Episodic Thumbnail Generator with Top-Left Badges & VFX."""

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


@dataclass
class EpisodicBadgeConfig:
    """Configuration for serialized episode thumbnail badges."""

    episode_number: int = 1
    language: str = "en"  # "en", "te", "hi", "es"
    style: str = "pill"  # "pill", "box", "ribbon"
    position: str = "top_left"  # strictly top_left to avoid YouTube's bottom-right duration pill
    bg_color: tuple[int, int, int] = (245, 158, 11)  # Amber / Gold
    text_color: tuple[int, int, int] = (15, 23, 42)  # Charcoal
    border_color: tuple[int, int, int] = (255, 255, 255)
    custom_label: str | None = None


LOCALIZED_EPISODE_LABELS: dict[str, str] = {
    "en": "EP {num:02d}",
    "te": "భాగం {num:02d}",
    "hi": "भाग {num:02d}",
    "es": "EPISODIO {num:02d}",
}


def get_localized_badge_text(episode_number: int, language: str = "en") -> str:
    """Format the localized episode badge string."""
    fmt = LOCALIZED_EPISODE_LABELS.get(language, "EP {num:02d}")
    return fmt.format(num=max(1, episode_number))


def _get_font(size: int = 36, language: str = "en") -> ImageFont.ImageFont:
    """Load default truetype font or fallback to system font with Mandali as default for Telugu and Nirmala for Indic."""
    clean_lang = (language or "en").lower().strip()
    if clean_lang in ("te", "telugu"):
        for te_path in (
            Path("storage/fonts/te/Mandali-Regular.ttf"),
            Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Mandali-Regular.ttf",
            Path("C:/Windows/Fonts/Nirmala.ttc"),
        ):
            if te_path.is_file():
                try:
                    return ImageFont.truetype(str(te_path), size=size)
                except Exception:
                    continue

    # Instant native Windows Indic font check (covers Bengali, Odia, Devanagari/Marathi/Hindi, Gujarati, Gurmukhi, Tamil, Kannada, Malayalam)
    if clean_lang in ("hi", "mr", "bn", "or", "gu", "pa", "ta", "kn", "ml", "ks", "sd", "as", "ur", "kok"):
        for indic_path in (
            Path("C:/Windows/Fonts/Nirmala.ttc"),
            Path("C:/Windows/Fonts/NirmalaB.ttf"),
            Path("C:/Windows/Fonts/nirmala.ttf"),
        ):
            if indic_path.is_file():
                try:
                    return ImageFont.truetype(str(indic_path), size=size)
                except Exception:
                    continue

    try:
        from src.services.font_manager import ensure_language_font
        _, fonts_dir = ensure_language_font(language)
        for font_file in fonts_dir.glob("*.ttf"):
            try:
                return ImageFont.truetype(str(font_file), size=size)
            except Exception:
                continue
    except Exception:
        pass

    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def apply_cinematic_thumbnail_vfx(image: Image.Image) -> Image.Image:
    """Apply high-CTR cinematic color grading, contrast, and subtle warm flare VFX."""
    img = image.convert("RGB")
    # 1. Color vibrance, contrast & micro-sharpness boost
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    rgba = img.convert("RGBA")
    w, h = rgba.size

    # 2. Subtle warm golden top-right corner glow
    flare = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(flare)
    max_r = min(w, h) // 2
    for r in range(max_r, 0, -12):
        alpha = int(32 * (1.0 - (r / max_r)))
        fdraw.ellipse([w - r, -r // 2, w + r // 2, r], fill=(255, 215, 0, alpha))
    flare = flare.filter(ImageFilter.GaussianBlur(radius=25))
    rgba = Image.alpha_composite(rgba, flare)

    # 3. Smooth bottom vignette gradient for optimal text contrast
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    v_start = int(h * 0.65)
    for y in range(v_start, h):
        ratio = (y - v_start) / max(1, (h - v_start))
        alpha = int(170 * (ratio ** 1.5))
        vdraw.line([(0, y), (w, y)], fill=(10, 15, 30, alpha))
    rgba = Image.alpha_composite(rgba, vignette)

    return rgba.convert("RGB")


def render_top_left_badge(image: Image.Image, config: EpisodicBadgeConfig) -> Image.Image:
    """Render a prominent, high-contrast episode badge in the top-left corner."""
    img = image.convert("RGBA")
    badge_text = config.custom_label or get_localized_badge_text(config.episode_number, config.language)

    font = _get_font(size=32, language=config.language)
    dummy_draw = ImageDraw.Draw(img)
    bbox = dummy_draw.textbbox((0, 0), badge_text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x, pad_y = 20, 10
    badge_w, badge_h = text_w + (pad_x * 2), text_h + (pad_y * 2)
    x0, y0 = 36, 36
    x1, y1 = x0 + badge_w, y0 + badge_h

    # Drop shadow
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        [x0 + 6, y0 + 6, x1 + 6, y1 + 6],
        radius=12 if config.style == "pill" else 4,
        fill=(0, 0, 0, 180),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, overlay)

    # Badge container
    badge_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(badge_layer)
    if config.style == "pill":
        bdraw.rounded_rectangle([x0, y0, x1, y1], radius=badge_h // 2, fill=(*config.bg_color, 255), outline=(*config.border_color, 220), width=2)
    elif config.style == "box":
        bdraw.rectangle([x0, y0, x1, y1], fill=(220, 38, 38, 255), outline=(255, 255, 255, 255), width=3)
    else:
        bdraw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=(79, 70, 229, 240), outline=(165, 180, 252, 255), width=2)

    bdraw.text((x0 + pad_x, y0 + pad_y - 2), badge_text, font=font, fill=(*config.text_color, 255))
    return Image.alpha_composite(img, badge_layer).convert("RGB")


def render_bottom_headline(image: Image.Image, headline: str, font_size: int = 46, language: str = "en") -> Image.Image:
    """Render a sleek, high-CTR cinematic title ribbon with gold accent across the bottom."""
    if not headline:
        return image

    img = image.convert("RGBA")
    font = _get_font(size=font_size, language=language)
    dummy_draw = ImageDraw.Draw(img)
    bbox = dummy_draw.textbbox((0, 0), headline, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = 44
    y = img.height - text_h - 56
    pad_x, pad_y = 20, 12

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Dark glassmorphic backing with soft rounded corners
    rx0, ry0 = x - pad_x, y - pad_y
    rx1, ry1 = x + text_w + pad_x + 10, y + text_h + pad_y
    odraw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=8, fill=(10, 15, 26, 215), outline=(255, 215, 0, 160), width=2)
    # Vibrant vertical gold accent stripe on left edge
    odraw.rectangle([rx0, ry0, rx0 + 6, ry1], fill=(245, 158, 11, 255))

    # Text drop shadow + sharp white/gold text
    odraw.text((x + 2, y + 2), headline, font=font, fill=(0, 0, 0, 230))
    odraw.text((x, y), headline, font=font, fill=(255, 255, 255, 255))

    return Image.alpha_composite(img, overlay).convert("RGB")


def generate_episodic_thumbnail(
    output_path: Path | str,
    base_image_path: Path | str | None = None,
    badge_config: EpisodicBadgeConfig | None = None,
    headline: str = "",
    target_size: tuple[int, int] = (1280, 720),
    enable_vfx: bool = True,
    language: str | None = None,
) -> Path:
    """Generate and save an episodic thumbnail with cinematic grading, badge, and headline."""
    config = badge_config or EpisodicBadgeConfig()
    eff_lang = language or config.language or "en"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    base = None
    if base_image_path and Path(base_image_path).exists():
        p = Path(base_image_path)
        if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm", ".avi"):
            clean_stem = p.stem.replace("_motion", "").replace("_lipsync", "")
            for candidate in (p.with_suffix(".jpg"), p.parent / f"{clean_stem}.jpg"):
                if candidate.is_file() and candidate.stat().st_size > 1000:
                    try:
                        base = Image.open(candidate).resize(target_size, Image.Resampling.LANCZOS)
                        break
                    except Exception:
                        pass
            if base is None:
                import subprocess
                import imageio_ffmpeg
                extracted_jpg = p.parent / f"thumb_extracted_{p.stem}.jpg"
                try:
                    subprocess.run(
                        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-ss", "00:00:00.500", "-i", str(p), "-vframes", "1", "-q:v", "2", str(extracted_jpg)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                    )
                    base = Image.open(extracted_jpg).resize(target_size, Image.Resampling.LANCZOS)
                except Exception:
                    base = None
        else:
            try:
                base = Image.open(p).resize(target_size, Image.Resampling.LANCZOS)
            except Exception:
                base = None

    if base is None:
        base = Image.new("RGB", target_size, color=(15, 23, 42))
        draw = ImageDraw.Draw(base)
        for i in range(target_size[1]):
            r = int(15 + (40 * i / target_size[1]))
            g = int(23 + (20 * i / target_size[1]))
            b = int(42 + (60 * i / target_size[1]))
            draw.line([(0, i), (target_size[0], i)], fill=(r, g, b))

    if enable_vfx:
        base = apply_cinematic_thumbnail_vfx(base)

    img_with_badge = render_top_left_badge(base, config)
    final_img = render_bottom_headline(img_with_badge, headline, language=eff_lang)
    final_img.save(out, format="JPEG", quality=95)
    return out


get_language_font = _get_font

__all__ = [
    "EpisodicBadgeConfig",
    "get_localized_badge_text",
    "get_language_font",
    "render_top_left_badge",
    "render_bottom_headline",
    "apply_cinematic_thumbnail_vfx",
    "generate_episodic_thumbnail",
]
