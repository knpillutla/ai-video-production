"""Targeted offline test for base directorial cadence, camera rig/movement, and 2s-12s range."""
import pytest
from src.studios.base_directorial_prompt import (
    build_base_directorial_prompt,
    build_default_image_model_configs,
    build_default_video_model_configs,
)


def test_balanced_mode_enforces_2s_to_12s_dynamic_range_across_all_genres():
    # Test for nature relaxing in balanced mode
    prompt_relax = build_base_directorial_prompt(
        genre="relax/mountain",
        sub_genre="alpine",
        archetype="mountain",
        cluster="Swiss Alps",
        custom_prompt="Matterhorn at sunrise",
        duration_seconds=60.0,
        num_shots=-1,
        tier="balanced",
    )
    assert "2s to 12s Dynamic Range" in prompt_relax
    assert "2.0 <= dur <= 12.0" in prompt_relax
    assert "CAMERA RIG VS. CAMERA MOVEMENT DIRECTORIAL CONTRACT" in prompt_relax
    assert "ANTI-MONOTONY GUARD" in prompt_relax

    # Test for travel in balanced mode
    prompt_travel = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="Metropolises",
        custom_prompt="Tokyo Skyline",
        duration_seconds=120.0,
        num_shots=-1,
        tier="balanced",
    )
    assert "2s to 12s Dynamic Range" in prompt_travel
    assert "2.0 <= dur <= 12.0" in prompt_travel


def test_user_choice_fixed_shots_for_nature_relaxing():
    # User explicitly selects 1 shot for 4K master living wallpaper
    prompt_single = build_base_directorial_prompt(
        genre="relax/mountain",
        sub_genre="alpine",
        archetype="mountain",
        cluster="Swiss Alps",
        custom_prompt="Tranquil alpine lake living wallpaper",
        duration_seconds=60.0,
        num_shots=1,
        tier="cinematic",  # 4K master mode with fixed shot selection
    )
    assert "Shot Count: 1 shots (60.0s per shot)" in prompt_single
    assert "4K Master Living Wallpaper Contract: Exactly 1 scene(s)" in prompt_single

    # User explicitly selects 3 shots for nature relaxing
    prompt_multi = build_base_directorial_prompt(
        genre="relax/ocean",
        sub_genre="coastal",
        archetype="ocean",
        cluster="Maldives",
        custom_prompt="Turquoise ocean waves",
        duration_seconds=30.0,
        num_shots=3,
        tier="cinematic",
    )
    assert "Shot Count: 3 shots (10.0s per shot)" in prompt_multi
    assert "Exactly 3 scene(s)" in prompt_multi


def test_camera_rig_and_movement_definitions():
    prompt = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="Metropolises",
        custom_prompt="Hyderabad Charminar",
        duration_seconds=60.0,
    )
    # Physical apparatus
    assert "heavy_lift_cine_drone" in prompt
    assert "technocrane_jib" in prompt
    assert "locked_tripod_telephoto" in prompt
    assert "motorized_cine_slider" in prompt

    # Kinetic 3D trajectory
    assert "dolly_pullback_reveal" in prompt
    assert "orbit_wrap_left" in prompt
    assert "tilt_up_monumental_reveal" in prompt
    assert "lateral_truck_right" in prompt


def test_directorial_configs_backward_compatibility():
    img_cfg = build_default_image_model_configs("Mountain Peak", "Matterhorn")
    assert "flux_dev" in img_cfg
    assert "flux_pro" in img_cfg
    assert "zimage" in img_cfg

    vid_cfg = build_default_video_model_configs("rushing stream")
    assert "wan_2_1" in vid_cfg
    assert "kling_v1_6_pro" in vid_cfg
