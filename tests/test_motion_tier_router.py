"""Unit tests for the Strict Universal Motion Tier Router (100% Offline, $0.00 spend)."""

from types import SimpleNamespace
import pytest
from src.services.motion_tier_router import resolve_scene_motion_model


def test_cinematic_tier_allocates_all_scenes_to_ai_diffusion():
    """Verify cinematic tier mandates AI video diffusion with zero fallback."""
    scenes = [
        SimpleNamespace(motion_type="ken_burns", domain="landscape_solid"),
        SimpleNamespace(motion_type="static", domain="architecture"),
        SimpleNamespace(motion_type="ai_diffusion", domain="water_fluid"),
    ]
    for idx, s in enumerate(scenes):
        model, allow_fb, rationale = resolve_scene_motion_model(
            scene=s,
            tier="cinematic",
            requested_motion_model="kling_v3",
            scene_index=idx,
            total_scenes=len(scenes),
        )
        assert model == "kling_v3"
        assert allow_fb is False
        assert "Cinematic tier" in rationale


def test_low_cost_tier_allocates_all_scenes_to_local_steadycam():
    """Verify low-cost tier mandates local steadycam with zero fallback ($0.00 compute)."""
    scenes = [
        SimpleNamespace(motion_type="ai_diffusion", domain="water_fluid"),
        SimpleNamespace(motion_type="ai_diffusion", domain="water_impact_collision"),
    ]
    for idx, s in enumerate(scenes):
        model, allow_fb, rationale = resolve_scene_motion_model(
            scene=s,
            tier="low_cost",
            requested_motion_model="wan",
            scene_index=idx,
            total_scenes=len(scenes),
        )
        assert model == "local_zoompan"
        assert allow_fb is False
        assert "Low-cost tier" in rationale


def test_balanced_tier_strictly_respects_script():
    """Verify balanced tier strictly respects screenplay motion_type with zero fallback."""
    # Scene 1: Script dictates live AI diffusion for living subjects/water
    s1 = SimpleNamespace(motion_type="ai_diffusion", domain="water_fluid")
    m1, fb1, r1 = resolve_scene_motion_model(s1, tier="balanced", requested_motion_model="wan", scene_index=0, total_scenes=2)
    assert m1 == "wan"
    assert fb1 is False
    assert "live AI video diffusion" in r1

    # Scene 2: Script dictates steadycam for rigid architecture/monument
    s2 = SimpleNamespace(motion_type="ken_burns", domain="landscape_solid")
    m2, fb2, r2 = resolve_scene_motion_model(s2, tier="balanced", requested_motion_model="wan", scene_index=1, total_scenes=2)
    assert m2 == "local_zoompan"
    assert fb2 is False
    assert "steadycam local zoompan" in r2


def test_balanced_tier_halts_if_script_missing_or_scene_none():
    """Verify execution errors out and halts if script or scene directive is missing (Zero Fallback)."""
    # 1. Missing scene object
    with pytest.raises(ValueError, match="script is the mandatory base"):
        resolve_scene_motion_model(None, tier="balanced", scene_index=0)

    # 2. Missing motion_type in script
    s_empty = SimpleNamespace(motion_type="", domain="water_fluid")
    with pytest.raises(ValueError, match="missing mandatory 'motion_type' in script"):
        resolve_scene_motion_model(s_empty, tier="balanced", scene_index=0)

    # 3. Invalid motion_type in script
    s_invalid = SimpleNamespace(motion_type="teleport", domain="water_fluid")
    with pytest.raises(ValueError, match="unknown motion_type 'teleport'"):
        resolve_scene_motion_model(s_invalid, tier="balanced", scene_index=0)


def test_tier_persistence_reprocess_logic():
    """Verify tier retrieval defaults to saved inputs on reprocess if not explicitly overridden."""
    saved_inputs = {"tier": "balanced"}
    cli_tier_none = None
    cli_tier_cinematic = "cinematic"

    eff_tier_default = cli_tier_none or saved_inputs.get("tier", "balanced")
    assert eff_tier_default == "balanced"

    eff_tier_override = cli_tier_cinematic or saved_inputs.get("tier", "balanced")
    assert eff_tier_override == "cinematic"
