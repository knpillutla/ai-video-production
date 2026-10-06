"""Universal Motion Tier Router.

Strict Directorial Motion Engine.
Enforces the screenplay script as the absolute authoritative source of truth.
If a screenplay or scene directorial directive is missing, errors out and halts.
Zero fallbacks allowed.
"""

from __future__ import annotations

from typing import Any, Tuple
from src.core.telemetry import logger


def resolve_scene_motion_model(
    scene: Any,
    tier: str = "balanced",
    requested_motion_model: str = "wan",
    scene_index: int = 0,
    total_scenes: int = 1,
    genre: str = "relax/nature",
    force_ai_motion: bool = False,
) -> Tuple[str, bool, str]:
    """Resolve the effective motion model strictly from the screenplay script.

    Args:
        scene: Scene object with mandatory `motion_type` from the director script.
        tier: Production tier ('cinematic', 'balanced', 'low_cost', 'local').
        requested_motion_model: Default AI diffusion model requested (e.g. 'wan', 'kling').
        scene_index: 0-indexed position of scene in storyboard.
        total_scenes: Total count of scenes in storyboard.
        genre: Channel/story genre category.
        force_ai_motion: Overriding flag to mandate AI diffusion.

    Returns:
        Tuple[str, bool, str]: (chosen_model, allow_fallback, rationale)

    Raises:
        ValueError: If scene is missing or motion_type is undefined in the script.
    """
    if scene is None:
        raise ValueError(
            f"Production halted: Scene at index {scene_index} is None. "
            "The script is the mandatory base for all production. Missing script; stopping."
        )

    clean_tier = (tier or "balanced").strip().lower()
    base_model = requested_motion_model or "wan"

    # 1. Flagship Cinematic Tier -> 100% AI Video Diffusion
    if clean_tier in ("cinematic", "movie", "high", "flagship") or force_ai_motion:
        rationale = f"Cinematic tier: Full neural video diffusion mandated ({base_model})"
        return base_model, False, rationale

    # 2. Low-Cost / Local Tier -> 100% Local Steadycam Zoom-Pan ($0.00 compute)
    if clean_tier in ("low_cost", "low", "quick", "test", "local", "offline"):
        rationale = "Low-cost tier: Single-pass 4K Ken Burns steadycam mandated ($0.00)"
        return "local_zoompan", False, rationale

    # 3. Balanced Tier -> Strict Script Directorial Decision (No Implicit Fallbacks)
    raw_motion_type = (getattr(scene, "motion_type", None) or "").strip().lower()

    if not raw_motion_type:
        raise ValueError(
            f"Production halted: Scene {scene_index + 1} is missing mandatory 'motion_type' in script. "
            "The screenplay script is the foundation for all production. Fallback is prohibited; stopping."
        )

    if raw_motion_type == "ai_diffusion":
        rationale = (
            f"Balanced tier (Script Directive): Scene {scene_index + 1} explicitly dictates "
            f"live AI video diffusion ({base_model})"
        )
        return base_model, False, rationale

    if raw_motion_type in ("ken_burns", "static", "locked_tripod"):
        rationale = (
            f"Balanced tier (Script Directive): Scene {scene_index + 1} explicitly dictates "
            "steadycam local zoompan ($0.00 compute, 100% geometry lock)"
        )
        return "local_zoompan", False, rationale

    raise ValueError(
        f"Production halted: Scene {scene_index + 1} contains unknown motion_type '{raw_motion_type}'. "
        "Expected 'ai_diffusion' or 'ken_burns' in directorial script. Stopping."
    )


__all__ = ["resolve_scene_motion_model"]
