"""Targeted Unit Test for FLUX 1.1 Pro Ultra Routing and Dynamic Wardrobe Directives ($0.00 spend, Rule 8)."""

from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.compositor.genre_strategies.virtual_artist_directives import (
    build_virtual_artist_directives,
)
from src.compositor.vocal_image_service import synthesize_vocal_scenes
from src.compositor.vocal_lora_resolver import resolve_vocal_loras
from src.compositor.vocal_prompt_service import (
    build_vocal_scene_prompt,
    get_canonical_concert_outfit,
)


def test_virtual_artist_directives_dynamic_wardrobe_gemini_derivation():
    """Verify Gemini is mandated to dynamically derive fully covered, colorful, elegant wardrobe with zero hardcoding."""
    directives = build_virtual_artist_directives(
        gender="female",
        artist_mode="concert",
        instrument="acoustic_guitar",
        scenic_archetype="meadows",
        landmark="taj_mahal",
    )
    # Check that Gemini dynamic derivation is mandated
    assert "GEMINI DYNAMIC DERIVATION - ZERO HARDCODING" in directives
    assert "Gemini MUST autonomously derive the clothing, outfit, and accessories dynamically based on the exact background context" in directives
    # Check full coverage and modesty
    assert "FULLY COVERED & STRICT MODESTY" in directives
    assert "zero bare midriff" in directives
    assert "fitted 3/4 length sleeves or long tailored sleeves" in directives
    assert "high closed boat neckline or mandarin collar" in directives
    # Check elegant, colorful & decorative
    assert "ELEGANT, COLORFUL & DECORATIVE" in directives
    assert "rich saturated jewel tones or radiant vivid pastels" in directives
    # Check 4-zone accessories
    assert "CURATED 4-ZONE ACCESSORIES" in directives
    # Check concert continuity
    assert "MANDATORY CONCERT WARDROBE & SETTING CONTINUITY" in directives


def test_canonical_concert_outfit_derives_from_gemini_without_hardcoded_colors():
    """Verify canonical concert outfit dynamically derives from Gemini's storyboard output."""
    # When Gemini specifies an emerald-cyan designer anarkali
    sb1 = {
        "theme": "twilight acoustic concert",
        "characters": [{
            "name": "Sita",
            "outfit_description": "vibrant peacock-blue and emerald floor-length anarkali gown with silver zari embroidery",
        }],
        "scenes": [],
    }
    outfit1 = get_canonical_concert_outfit(sb1)
    assert "peacock-blue" in outfit1
    assert "emerald" in outfit1
    assert "continuous one-piece" in outfit1
    assert "zero bare midriff" in outfit1

    # When Gemini specifies an outfit in scene 1
    sb2 = {
        "theme": "royal heritage concert",
        "characters": [],
        "scenes": [{
            "visual_prompt": "Lead singer performing on stage wearing royal amethyst purple designer gown with gold borders",
        }],
    }
    outfit2 = get_canonical_concert_outfit(sb2)
    assert "royal amethyst purple designer gown" in outfit2
    assert "continuous one-piece" in outfit2
    assert "zero bare midriff" in outfit2


@pytest.mark.asyncio
async def test_resolve_vocal_loras_flux_ultra_bypasses_loras():
    """Verify resolve_vocal_loras returns empty LoRAs and empty trigger words for flux-ultra."""
    sb = {"characters": [{"name": "Radha", "gender": "female"}]}
    for model_str in ("flux ultra", "flux-ultra", "flux_ultra", "flux-pro-ultra"):
        loras, triggers = await resolve_vocal_loras(
            storyboard_data=sb,
            char_names=["Radha"],
            chars=None,
            explicit_loras=None,
            user_id="user_test",
            network="test_net",
            use_loras=True,
            force_live=False,
            lora_model=model_str,
        )
        assert loras == []
        assert triggers == ""


@pytest.mark.asyncio
async def test_synthesize_vocal_scenes_routes_to_flux_ultra(tmp_path: Path):
    """Verify synthesize_vocal_scenes dispatches to FalFluxProUltraAdapter when lora_model is flux-ultra."""
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    sb = {
        "artist_mode": "concert",
        "theme": "live amphitheater concert",
        "characters": [{"name": "Radha", "gender": "female", "outfit_description": "ruby red designer gown"}],
        "scenes": [
            {"scene_index": 1, "visual_prompt": "Radha singing at vintage chrome microphone on live concert stage"},
        ],
    }

    with patch("src.providers.visual.fal_flux_pro_ultra.FalFluxProUltraAdapter.generate_to_file", new_callable=AsyncMock) as mock_ultra:
        async def fake_generate(prompt, output_path, **kwargs):
            out = Path(output_path)
            out.write_bytes(b"FLUX_ULTRA_MOCK_IMAGE_DATA_" + b"0" * 2000)
            return "https://fal.media/files/mock_flux_ultra.jpg", out

        mock_ultra.side_effect = fake_generate

        res = await synthesize_vocal_scenes(
            storyboard_data=sb,
            scenes_dir=scenes_dir,
            num_images=1,
            user_id="test_user",
            network="telugu_rhythms",
            force_live=False,
            use_loras=False,
            lora_model="flux-ultra",
        )

        assert len(res) == 1
        assert res[0].is_file()
        assert mock_ultra.called
        call_kwargs = mock_ultra.call_args[1]
        assert "ruby red designer gown" in call_kwargs["prompt"]
        assert "strictly identical stage outfit" in call_kwargs["prompt"]


def test_generate_episodic_thumbnail_with_video_input(tmp_path: Path):
    """Verify generate_episodic_thumbnail gracefully resolves keyframe image when given an MP4 path."""
    from PIL import Image
    from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail

    # Create dummy scene_06.jpg
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    img_path = scenes_dir / "scene_06.jpg"
    img = Image.new("RGB", (1280, 720), color=(200, 50, 50))
    img.save(img_path)

    # Fake scene_06_motion.mp4
    video_path = scenes_dir / "scene_06_motion.mp4"
    video_path.write_bytes(b"FAKE_MP4_CONTENT")

    thumb_out = tmp_path / "thumb_test.jpg"

    # Call with the .mp4 path — should resolve to scene_06.jpg and not raise UnidentifiedImageError
    res = generate_episodic_thumbnail(
        output_path=thumb_out,
        base_image_path=video_path,
        badge_config=EpisodicBadgeConfig(episode_number=12, language="te", style="pill"),
        headline="Echoes In The Spotlight",
        enable_vfx=False,
    )
    assert res.is_file()
    assert res.stat().st_size > 1000
