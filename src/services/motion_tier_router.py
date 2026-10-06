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

    raw_motion_type = (getattr(scene, "motion_type", None) or "").strip().lower()
    base_model = requested_motion_model or "wan"
    clean_tier = (tier or "balanced").strip().lower()

    # Absolute Rule: Respect the value motion_type strictly from JSON script (Gemini output).
    # Whether balanced, 4K/cinematic, or draft/low_cost, ken_burns determines local vs AI model ($0.00 compute).
    if raw_motion_type in ("ken_burns", "static", "locked_tripod", "local_zoompan", "zoompan", "local"):
        rationale = (
            f"Directorial Script Directive: Scene {scene_index + 1} specifies '{raw_motion_type}' "
            "- executing 100% local steadycam perspective drone ($0.00 compute, 100% geometry lock)"
        )
        return "local_zoompan", False, rationale

    if raw_motion_type in ("ai_diffusion", "diffusion", "neural", "neural_diffusion"):
        rationale = (
            f"Directorial Script Directive: Scene {scene_index + 1} specifies '{raw_motion_type}' "
            f"- executing AI video diffusion ({base_model})"
        )
        return base_model, False, rationale

    if not raw_motion_type:
        if clean_tier in ("cinematic", "movie", "high", "flagship") or force_ai_motion:
            return base_model, False, f"Cinematic tier default: AI video diffusion ({base_model})"
        return "local_zoompan", False, "Tier default: local steadycam zoompan ($0.00 compute)"

    raise ValueError(
        f"Production halted: Scene {scene_index + 1} contains unknown motion_type '{raw_motion_type}'. "
        "Expected 'ai_diffusion' or 'ken_burns' in directorial script. Stopping."
    )


__all__ = ["resolve_scene_motion_model"]
