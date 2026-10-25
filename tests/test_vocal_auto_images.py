"""Offline Unit Tests for Autonomous Duration-Based Image Pacing.

Verifies:
1. Default autonomous scene calculation based on duration & musical tempo (Rule 14/15).
2. Override when manual --images is passed.
3. Fallback to len(scenes_list) in vocal_image_service.
"""

from pathlib import Path
import pytest

from src.compositor.genre_strategies import resolve_strategy
from src.compositor.vocal_image_service import synthesize_vocal_scenes


def test_vocal_strategy_autonomous_duration_pacing():
    """Verify autonomous duration-based scene pacing calculation by default."""
    strategy = resolve_strategy("vocal")

    # 1. 30s Mass song: 7-11s window -> ~3-4 scenes
    prompt_30s_mass = strategy.build_gemini_prompt(
        title="Charminar Mass",
        duration_seconds=30,
        language="te",
        theme="high-energy mass beats near Charminar",
        mass_song=True,
    )
    assert "AUTONOMOUS DURATION-BASED SCENE PACING (DEFAULT)" in prompt_30s_mass
    assert "7-11s (mass beats)" in prompt_30s_mass
    assert "recommended: 3 to 4 scenes" in prompt_30s_mass

    # 2. 180s Melody: 12-18s window -> 10 to 15 scenes
    prompt_180s_mel = strategy.build_gemini_prompt(
        title="Vennela Megham",
        duration_seconds=180,
        language="te",
        theme="soulful romantic melody in tea garden",
    )
    assert "AUTONOMOUS DURATION-BASED SCENE PACING (DEFAULT)" in prompt_180s_mel
    assert "12-18s (melody)" in prompt_180s_mel
    assert "recommended: 10 to 15 scenes" in prompt_180s_mel

    # 3. Explicit manual override (--images 4)
    prompt_override = strategy.build_gemini_prompt(
        title="Vennela Megham",
        duration_seconds=180,
        language="te",
        theme="soulful romantic melody in tea garden",
        num_images=4,
    )
    assert "MULTI-SCENE ROTATION (4 SCENES)" in prompt_override


@pytest.mark.asyncio
async def test_vocal_image_service_auto_defaults_to_scenes_list(tmp_path: Path):
    """Verify vocal_image_service synthesizes all scenes directed by Gemini when num_images is auto."""
    sb_data = {
        "prompts_by_model": {"z_image": "Hero in Charminar"},
        "scenes": [
            {"scene_index": 1, "visual_prompt": "Hero swagger walk Charminar"},
            {"scene_index": 2, "visual_prompt": "Hero mass hook step"},
            {"scene_index": 3, "visual_prompt": "Hero festival climax"},
        ],
        "characters": [{"seed": 999}],
    }
    scenes_dir = tmp_path / "scenes"

    # num_images="auto" should synthesize all 3 scenes from storyboard_data["scenes"]
    paths = await synthesize_vocal_scenes(
        storyboard_data=sb_data,
        scenes_dir=scenes_dir,
        num_images="auto",
        force_live=False,
    )
    assert len(paths) == 3
    assert (scenes_dir / "scene_01.jpg").is_file()
    assert (scenes_dir / "scene_02.jpg").is_file()
    assert (scenes_dir / "scene_03.jpg").is_file()
