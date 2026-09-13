"""Tests for Tier-0 Pillow Episodic Thumbnail Numbering Engine."""

from pathlib import Path
from PIL import Image
from src.scripts.local_thumbnail import (
    EpisodicBadgeConfig,
    generate_episodic_thumbnail,
    get_localized_badge_text,
)


def test_localized_badge_formatting():
    """Verify localized episode badge labels across Telugu, Hindi, English, and Spanish."""
    assert get_localized_badge_text(1, "en") == "EP 01"
    assert get_localized_badge_text(5, "en") == "EP 05"
    assert get_localized_badge_text(1, "te") == "భాగం 01"
    assert get_localized_badge_text(12, "te") == "భాగం 12"
    assert get_localized_badge_text(1, "hi") == "भाग 01"
    assert get_localized_badge_text(9, "hi") == "भाग 09"
    assert get_localized_badge_text(1, "es") == "EPISODIO 01"


def test_episodic_thumbnail_generation_output(tmp_path: Path):
    """Verify episodic thumbnail rendering, resolution, and output file existence."""
    out_file = tmp_path / "thumb_ep01_te.jpg"

    config = EpisodicBadgeConfig(
        episode_number=1,
        language="te",
        style="pill",
        position="top_left",
    )

    result_path = generate_episodic_thumbnail(
        output_path=out_file,
        badge_config=config,
        headline="వర్క్ ఫ్రమ్ హోమ్ గోల!",
        target_size=(1280, 720),
    )

    assert result_path.exists()
    assert result_path.stat().st_size > 5000  # Non-trivial image file

    with Image.open(result_path) as img:
        assert img.size == (1280, 720)
        assert img.format == "JPEG"


def test_episodic_badge_styles(tmp_path: Path):
    """Verify rendering of different badge styles (pill, box, ribbon)."""
    for style in ["pill", "box", "ribbon"]:
        out = tmp_path / f"thumb_{style}.jpg"
        cfg = EpisodicBadgeConfig(episode_number=3, language="en", style=style)
        res = generate_episodic_thumbnail(output_path=out, badge_config=cfg)
        assert res.exists()
