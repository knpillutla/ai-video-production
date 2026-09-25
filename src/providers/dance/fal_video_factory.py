"""Dynamic Video Motion Adapter Factory driven by model_routing_matrix.json."""

from __future__ import annotations

from typing import Any
from src.core.config.artifact_models import get_scenario_config
from src.core.telemetry import logger
from src.providers.dance.fal_h3_max_turbo import FalH3MaxTurboAdapter
from src.providers.dance.fal_hunyuan import FalHunyuanAdapter
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.dance.fal_seedance import FalSeedanceAdapter


def resolve_video_motion_adapter(
    profile: str = "development",
    scenario: str = "general_default",
    model_override: str | None = None,
    endpoint_override: str | None = None,
) -> Any:
    """Dynamically resolve and instantiate the video motion adapter declared in JSON config.

    Allows switching video models (H3 Max, Seedance 2.5, Hunyuan Video v1.5, Kling 1.5 Pro, etc.)
    purely through model_selection_config.json without touching Python code.
    """
    sc_conf = get_scenario_config(scenario=scenario, profile=profile)
    is_dance = any(k in scenario.lower() for k in ("dance", "telugu", "south_indian", "folk", "mass", "jathara"))
    default_model = "Kling v3 Pro" if is_dance else "Tencent Hunyuan Video 1080p"
    model_name = str(model_override or vid_conf.get("model", default_model)).lower()
    endpoint = endpoint_override or vid_conf.get("endpoint")

    logger.info(f"resolving_video_motion_adapter: profile={profile}, scenario={scenario}, model={model_name}, endpoint={endpoint}")

    if any(k in model_name for k in ("kling", "dance", "choreography")):
        return FalKlingAdapter(endpoint=endpoint)

    if any(k in model_name for k in ("hunyuan", "tencent", "nature", "documentary")):
        return FalHunyuanAdapter(endpoint=endpoint)

    if any(k in model_name for k in ("h3", "minimax", "turbo", "prototype")):
        return FalH3MaxTurboAdapter(endpoint=endpoint)

    if any(k in model_name for k in ("seedance", "bytedance")):
        return FalSeedanceAdapter(endpoint=endpoint)

    return FalHunyuanAdapter(endpoint=endpoint)


__all__ = ["resolve_video_motion_adapter"]
