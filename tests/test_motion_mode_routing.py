"""Targeted unit tests verifying motion model routing in Test vs Prod modes."""

import pytest
from src.studios.screenplay_models import RelaxSceneDirective
from src.services.motion_tier_router import resolve_scene_motion_model


def test_test_mode_always_forces_local_drone_even_if_diffusion():
    """In test mode, all motions must route to local drone to ensure $0.00 compute."""
    scene = RelaxSceneDirective(
        visual_prompt="Dramatic waterfall crashing into river",
        motion_prompt="Heavy turbulent water cascading down granite cliff",
        motion_type="ai_diffusion",
        recommended_model="kling_v3",
    )

    chosen_model, allow_fallback, rationale = resolve_scene_motion_model(
        scene=scene,
        tier="balanced",
        requested_motion_model="kling_v3",
        scene_index=0,
        total_scenes=1,
        execution_mode="test",
    )

    assert chosen_model == "local_zoompan"
    assert allow_fallback is False
    assert "$0.00 compute" in rationale
    assert "Test execution mode" in rationale


def test_prod_mode_uses_gemini_recommended_model():
    """In prod mode, AI diffusion must use the exact model recommended by Gemini."""
    scene_kling = RelaxSceneDirective(
        visual_prompt="Violent rapids crashing through gorge",
        motion_prompt="Fast fluid water dynamics with mist plumes",
        motion_type="ai_diffusion",
        recommended_model="kling_v3",
    )

    chosen_model, allow_fallback, rationale = resolve_scene_motion_model(
        scene=scene_kling,
        tier="balanced",
        requested_motion_model="wan",
        scene_index=0,
        total_scenes=2,
        execution_mode="prod",
    )

    assert chosen_model == "kling_v3"
    assert "Gemini Directive" in rationale

    scene_wan = RelaxSceneDirective(
        visual_prompt="Tranquil alpine lake at dawn",
        motion_prompt="Gentle laminar ripples across glassy water reflection",
        motion_type="ai_diffusion",
        recommended_model="wan_2_1",
    )

    chosen_model_wan, _, rationale_wan = resolve_scene_motion_model(
        scene=scene_wan,
        tier="balanced",
        requested_motion_model="kling_v3",
        scene_index=1,
        total_scenes=2,
        execution_mode="prod",
    )

    assert chosen_model_wan == "wan_2_1"
    assert "Gemini Directive" in rationale_wan


def test_prod_mode_preserves_local_drone_when_script_specifies_ken_burns():
    """In prod mode, if scene dictates ken_burns, local drone is preserved."""
    scene_local = RelaxSceneDirective(
        visual_prompt="Static mountain peak panorama",
        motion_prompt="Slow steady camera flight across ridge",
        motion_type="ken_burns",
        recommended_model="local_drone",
    )

    chosen_model, _, rationale = resolve_scene_motion_model(
        scene=scene_local,
        tier="balanced",
        requested_motion_model="wan",
        scene_index=0,
        total_scenes=1,
        execution_mode="prod",
    )

    assert chosen_model == "local_zoompan"
    assert "$0.00 compute" in rationale


def test_render_perspective_drone_clip_accepts_lower_third_hud():
    """Verify render_perspective_drone_clip signature accepts lower_third_hud parameter."""
    import inspect
    from src.scripts.local_perspective_drone import render_perspective_drone_clip
    sig = inspect.signature(render_perspective_drone_clip)
    assert "lower_third_hud" in sig.parameters
    assert sig.parameters["lower_third_hud"].default is None
