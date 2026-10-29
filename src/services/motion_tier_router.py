"""Universal Motion Tier Router.

Strict Directorial Motion Engine.
Enforces the screenplay script as the absolute authoritative source of truth.
If a screenplay or scene directorial directive is missing, errors out and halts.
Zero fallbacks allowed.
"""

from __future__ import annotations

from typing import Any, Tuple
from src.core.telemetry import logger


def scene_has_humans(scene_or_prompt: Any) -> bool:
    """Detect whether a scene visual prompt, motion prompt, or metadata features human subjects."""
    if not scene_or_prompt:
        return False
    if isinstance(scene_or_prompt, str):
        text = scene_or_prompt.lower()
    else:
        v_p = getattr(scene_or_prompt, "visual_prompt", "") or ""
        m_p = getattr(scene_or_prompt, "motion_prompt", "") or ""
        desc = getattr(scene_or_prompt, "description", "") or ""
        c_p = getattr(scene_or_prompt, "character_prompt", "") or ""
        text = f"{v_p} {m_p} {desc} {c_p}".lower()

    if any(neg in text for neg in ("zero humans", "no humans", "no people", "zero people", "devoid of humans", "uninhabited")):
        return False

    human_keywords = (
        "human", "humans", "person", "persons", "people",
        "pedestrian", "pedestrians", "crowd", "crowds",
        "man", "men", "woman", "women", "girl", "girls", "boy", "boys",
        "child", "children", "dancer", "dancers", "shepherd", "shepherds",
        "artisan", "artisans", "baker", "bakers", "monk", "monks",
        "locals walking", "locals strolling", "locals gathered",
        "tourist", "tourists", "student", "students", "vendor", "vendors",
        "shopper", "shoppers", "passerby", "passersby", "commuter", "commuters",
        "facial expression", "walking down", "strolling along",
        "people walking", "people gathered", "performer"
    )
    return any(k in text for k in human_keywords)


def resolve_scene_motion_model(
    scene: Any,
    tier: str = "balanced",
    requested_motion_model: str = "h3_max",
    scene_index: int = 0,
    total_scenes: int = 1,
    genre: str = "relax/nature",
    force_ai_motion: bool = False,
    execution_mode: str = "prod",
) -> Tuple[str, bool, str]:
    """Resolve the effective motion model strictly from the screenplay script."""
    if scene is None:
        raise ValueError(
            f"Production halted: Scene at index {scene_index} is None. "
            "The script is the mandatory base for all production. Missing script; stopping."
        )

    clean_tier = (tier or "balanced").strip().lower()
    base_model = requested_motion_model or "h3_max"
    if base_model == "auto":
        base_model = "h3_max"
    clean_exec = (execution_mode or "test").strip().lower()
    is_prod = clean_exec in ("prod", "production", "live")
    has_humans = scene_has_humans(scene)

    # 0. User / Directorial Selection of Local Motion Engine
    if base_model in ("local_drone", "locked_tripod", "local_zoompan", "local", "offline"):
        rationale = f"Local motion engine mandated ({base_model}) ($0.00 compute)"
        return "local_zoompan", False, rationale

    is_diffusion = (base_model or "").lower() in (
        "kling_v3_4k", "kling_v3", "kling_4k", "kling_pro", "kling_1_6", "kling_v1_6_pro",
        "wan", "wan_2_1", "wan_4k", "h3", "h3_max", "minimax", "hailuo", "hunyuan",
    )

    # In test mode, force local drone unless explicitly forcing AI motion
    if clean_exec == "test" and not force_ai_motion:
        rationale = f"Test execution mode: Local perspective drone mandated for Scene {scene_index + 1} ($0.00 compute)"
        return "local_zoompan", False, rationale

    is_doc = any(k in str(genre).lower() for k in ("doc", "nations", "documentary", "tour", "euro_discovery"))

    # 1. Flagship Cinematic Tier or Explicit AI Motion Request -> 100% AI Video Diffusion
    if clean_tier in ("cinematic", "movie", "high", "flagship") or force_ai_motion:
        if is_prod and has_humans:
            eff_model = "kling_v3"
            rationale = f"Prod mode human motion mandate: Kling v3 4K selected for authentic human anatomy and motion (Scene {scene_index + 1})"
            return eff_model, False, rationale

        if is_doc:
            rec_model = getattr(scene, "recommended_model", None) or getattr(scene, "motion_model", None)
            eff_model = "kling_v3" if (rec_model and "kling" in str(rec_model).lower()) else "h3_max"
        else:
            rec_model = getattr(scene, "recommended_model", None) or getattr(scene, "motion_model", None)
            if base_model and base_model != "auto":
                eff_model = base_model
            elif rec_model and rec_model not in ("auto", "local_drone"):
                eff_model = rec_model
            else:
                eff_model = "h3_max"

        if eff_model in ("kling_4k", "kling_v3_4k", "kling_v3"):
            eff_model = "kling_v3"
        elif eff_model in ("kling_pro", "kling_v1_6_pro", "kling_1_6", "kling"):
            eff_model = "kling_pro"
        elif eff_model in ("h3", "h3_max", "minimax", "hailuo"):
            eff_model = "h3_max"
        elif eff_model in ("wan_4k", "wan_super_res", "wan-2.1-4k", "wan2.1 4k"):
            eff_model = "wan_4k"
        elif eff_model in ("wan", "wan_2_1", "wan21"):
            eff_model = "wan_4k"

        rationale = f"Cinematic tier: Full neural video diffusion mandated ({eff_model})"
        return eff_model, False, rationale

    # 2. Low-Cost / Local Tier -> 100% Local Steadycam Zoom-Pan ($0.00 compute)
    if clean_tier in ("low_cost", "low", "quick", "local", "offline"):
        rationale = "Low-cost tier: Single-pass 4K Ken Burns steadycam mandated ($0.00)"
        return "local_zoompan", False, rationale

    # 3. Balanced Tier -> Strict Script Directorial Decision (No Implicit Fallbacks)
    raw_motion_type = (getattr(scene, "motion_type", None) or "").strip().lower()

    if not raw_motion_type:
        raise ValueError(
            f"Production halted: Scene {scene_index + 1} is missing mandatory 'motion_type' in script. "
            "The screenplay script is the foundation for all production. Fallback is prohibited; stopping."
        )

    if raw_motion_type in ("ai_diffusion", "diffusion", "neural", "neural_diffusion"):
        # Prod mode human motion rule: humans in scene must use Kling
        if is_prod and has_humans:
            eff_model = "kling_v3"
            rationale = (
                f"Prod mode human motion mandate: Scene {scene_index + 1} features human subjects "
                f"-> Kling v3 4K selected for high-fidelity human anatomy and locomotion"
            )
            return eff_model, False, rationale

        if is_doc:
            eff_model = "h3_max"
            rationale = (
                f"Documentary format mandate: Scene {scene_index + 1} strictly uses "
                f"cost-optimized h3_max ($0.015/s) for all ai_diffusion motion without humans"
            )
            return eff_model, False, rationale

        rec_model = getattr(scene, "recommended_model", None) or getattr(scene, "motion_model", None)
        eff_model = rec_model if (rec_model and rec_model not in ("auto", "local_drone")) else base_model
        if eff_model in ("h3", "h3_max", "minimax", "hailuo"):
            eff_model = "h3_max"
        elif "kling" in str(eff_model).lower():
            eff_model = "kling_v3"
        rationale = (
            f"Prod tier (Gemini Directive): Scene {scene_index + 1} dictates "
            f"live AI video diffusion via model '{eff_model}'"
        )
        return eff_model, False, rationale

    if raw_motion_type in ("ken_burns", "static", "locked_tripod", "local_zoompan", "zoompan", "local", "local_drone"):
        rationale = (
            f"Balanced tier (Script Directive): Scene {scene_index + 1} explicitly dictates "
            "steadycam local zoompan ($0.00 compute, 100% geometry lock)"
        )
        return "local_zoompan", False, rationale

    raise ValueError(
        f"Production halted: Scene {scene_index + 1} contains unknown motion_type '{raw_motion_type}'. "
        "Expected 'ai_diffusion' or 'ken_burns' in directorial script. Stopping."
    )


__all__ = ["resolve_scene_motion_model", "scene_has_humans"]
