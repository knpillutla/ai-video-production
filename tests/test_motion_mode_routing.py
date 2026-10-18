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


def test_local_perspective_drone_pan_and_tilt_motion_non_zero():
    """Verify that pan, tilt, and orbit motions produce non-zero camera movement even when start_zoom is normal."""
    import numpy as np
    from src.scripts.local_perspective_drone import precompute_sequence_matrices

    # 1. Pan-Right: Must produce non-zero horizontal camera translation
    m_pan, _ = precompute_sequence_matrices((2160, 3840, 3), [("pan-right", 5.0)], fps=24, output_size=(3840, 2160), start_pan="left", start_zoom="normal")
    pan_diff = np.max(np.abs(m_pan[-1] - m_pan[0]))
    assert pan_diff > 500.0, f"pan-right matrix diff should be > 500, got {pan_diff}"

    # 2. Tilt-Up: Must produce non-zero vertical camera translation
    m_tilt, _ = precompute_sequence_matrices((2160, 3840, 3), [("tilt-up", 5.0)], fps=24, output_size=(3840, 2160), start_pan="center", start_zoom="normal")
    tilt_diff = np.max(np.abs(m_tilt[-1] - m_tilt[0]))
    assert tilt_diff > 300.0, f"tilt-up matrix diff should be > 300, got {tilt_diff}"

    # 3. Orbit-Left: Must produce non-zero arc glide
    m_orbit, _ = precompute_sequence_matrices((2160, 3840, 3), [("orbit-left", 5.0)], fps=24, output_size=(3840, 2160), start_pan="right", start_zoom="normal")
    orbit_diff = np.max(np.abs(m_orbit[-1] - m_orbit[0]))
    assert orbit_diff > 500.0, f"orbit-left matrix diff should be > 500, got {orbit_diff}"

    # 4. Stay: Must produce zero camera movement (static locked frame)
    m_stay, _ = precompute_sequence_matrices((2160, 3840, 3), [("stay", 5.0)], fps=24, output_size=(3840, 2160), start_pan="center", start_zoom="normal")
    stay_diff = np.max(np.abs(m_stay[-1] - m_stay[0]))
    assert stay_diff == 0.0, f"stay matrix diff should be 0.0, got {stay_diff}"


def test_water_shimmer_generates_active_plates():
    """Verify that SpecularWaterShimmerEngine detects water and generates shimmering cyclic plates."""
    import cv2
    import numpy as np
    from src.scripts.drone_living_dynamics import SpecularWaterShimmerEngine

    # Create a 1920x1080 synthetic image: top is sky/mountain, bottom is blue lake water
    synth = np.zeros((1080, 1920, 3), dtype=np.uint8)
    synth[:300, :] = [220, 180, 140]  # Sky (light blue/grey in BGR)
    synth[300:500, :] = [80, 90, 80]   # Mountain terrain
    synth[500:, :] = [180, 120, 30]    # Blue lake water in BGR (Hue ~105 in HSV)

    eng = SpecularWaterShimmerEngine(synth, 1920, 1080, num_frames=12)
    assert eng.has_water is True
    assert len(eng.plates) == 12

    # Verify difference between opposite phase plates
    diff = np.max(np.abs(eng.plates[6].astype(float) - eng.plates[0].astype(float)))
    assert diff > 20.0, f"Water shimmer diff should be > 20, got {diff}"
