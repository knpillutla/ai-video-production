"""Tier-0 Deterministic Episodic Thumbnail Generator with Top-Left Numbering Badges."""

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


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


def _get_font(size: int = 36) -> ImageFont.ImageFont:
    """Load default truetype font or fallback to system font."""
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
        except Exception:
            return ImageFont.load_default()


def render_top_left_badge(
    image: Image.Image,
    config: EpisodicBadgeConfig,
) -> Image.Image:
    """Render a prominent, high-contrast episode badge in the top-left corner."""
    img = image.convert("RGBA")
    badge_text = config.custom_label or get_localized_badge_text(config.episode_number, config.language)

    font = _get_font(size=32)
    dummy_draw = ImageDraw.Draw(img)
    bbox = dummy_draw.textbbox((0, 0), badge_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Calculate badge dimensions with padding
    pad_x, pad_y = 20, 10
    badge_w = text_w + (pad_x * 2)
    badge_h = text_h + (pad_y * 2)

    # Standard non-obscured top-left placement (36px margin)
    x0, y0 = 36, 36
    x1, y1 = x0 + badge_w, y0 + badge_h

    # Create overlay for shadow and rounded geometry
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Heavy drop shadow for contrast against any background
    shadow_offset = 6
    draw.rounded_rectangle(
        [x0 + shadow_offset, y0 + shadow_offset, x1 + shadow_offset, y1 + shadow_offset],
        radius=12 if config.style == "pill" else 4,
        fill=(0, 0, 0, 180),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, overlay)

    # 2. Draw badge container
    badge_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(badge_layer)

    if config.style == "pill":
        radius = badge_h // 2
        bdraw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=radius,
            fill=(*config.bg_color, 255),
            outline=(*config.border_color, 220),
            width=2,
        )
    elif config.style == "box":
        bdraw.rectangle(
            [x0, y0, x1, y1],
            fill=(220, 38, 38, 255),  # Crimson Red
            outline=(255, 255, 255, 255),
            width=3,
        )
    else:  # Ribbon style
        bdraw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=6,
            fill=(79, 70, 229, 240),  # Indigo
            outline=(165, 180, 252, 255),
            width=2,
        )

    # 3. Draw high-contrast text centered in the badge
    text_x = x0 + pad_x
    text_y = y0 + pad_y - 2
    bdraw.text((text_x, text_y), badge_text, font=font, fill=(*config.text_color, 255))

    return Image.alpha_composite(img, badge_layer).convert("RGB")


def render_bottom_headline(
    image: Image.Image,
    headline: str,
    font_size: int = 48,
) -> Image.Image:
    """Render a high-CTR headline banner across the bottom."""
    if not headline:
        return image

    img = image.convert("RGBA")
    font = _get_font(size=font_size)
    dummy_draw = ImageDraw.Draw(img)
    bbox = dummy_draw.textbbox((0, 0), headline, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Position at bottom-left with safe margins
    x = 40
    y = img.height - text_h - 60

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Draw dark backing ribbon
    pad = 16
    odraw.rectangle(
        [x - pad, y - pad, x + text_w + pad, y + text_h + pad],
        fill=(0, 0, 0, 210),
    )
    # Draw vibrant headline text
    odraw.text((x, y), headline, font=font, fill=(255, 255, 255, 255))

    return Image.alpha_composite(img, overlay).convert("RGB")


def generate_episodic_thumbnail(
    output_path: Path | str,
    base_image_path: Path | str | None = None,
    badge_config: EpisodicBadgeConfig | None = None,
    headline: str = "",
    target_size: tuple[int, int] = (1280, 720),
) -> Path:
    """Generate and save an episodic thumbnail with top-left badge and headline."""
    config = badge_config or EpisodicBadgeConfig()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Load base image or generate default high-tech gradient canvas
    if base_image_path and Path(base_image_path).exists():
        base = Image.open(base_image_path).resize(target_size, Image.Resampling.LANCZOS)
    else:
        # Create rich cinematic canvas
        base = Image.new("RGB", target_size, color=(15, 23, 42))
        draw = ImageDraw.Draw(base)
        for i in range(target_size[1]):
            r = int(15 + (40 * i / target_size[1]))
            g = int(23 + (20 * i / target_size[1]))
            b = int(42 + (60 * i / target_size[1]))
            draw.line([(0, i), (target_size[0], i)], fill=(r, g, b))

    # 1. Render Top-Left Episode Badge (Never obscured by YouTube time pill)
    img_with_badge = render_top_left_badge(base, config)

    # 2. Render Headline Text
    final_img = render_bottom_headline(img_with_badge, headline)

    final_img.save(out, format="JPEG", quality=92)
    return out


__all__ = [
    "EpisodicBadgeConfig",
    "get_localized_badge_text",
    "render_top_left_badge",
    "render_bottom_headline",
    "generate_episodic_thumbnail",
]
