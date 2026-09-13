"""Production Tier Resolver for the Model Selector MCP Server."""

from typing import Any
from pydantic import BaseModel, Field
from src.core.telemetry import logger


class TierSpecification(BaseModel):
    """Specification of models, costs, and capabilities for a production tier."""

    tier_key: str
    display_name: str
    total_cost_usd: float
    description: str
    target_use_case: str
    models: dict[str, dict[str, Any]]
    itemized_spend: dict[str, float]


def _build_tier(
    tier_key: str,
    name: str,
    desc: str,
    use_case: str,
    script_cfg: tuple[str, str, float, float],
    visual_cfg: tuple[str, str, float, int],
    voice_cfg: tuple[str, str, float, int],
    motion_cfg: tuple[str, str, float, float],
    music_cfg: tuple[str, str, float, int],
    sfx_cfg: tuple[str, str, float, int],
) -> TierSpecification:
    """Helper to assemble a typed TierSpecification and calculate itemized spend."""
    script_cost = round(script_cfg[2] * script_cfg[3], 4)
    visual_cost = round(visual_cfg[2] * visual_cfg[3], 4)
    voice_cost = round(voice_cfg[2] * voice_cfg[3], 4)
    motion_cost = round(motion_cfg[2] * motion_cfg[3], 4)
    music_cost = round(music_cfg[2] * music_cfg[3], 4)
    sfx_cost = round(sfx_cfg[2] * sfx_cfg[3], 4)
    total = round(script_cost + visual_cost + voice_cost + motion_cost + music_cost + sfx_cost, 4)

    return TierSpecification(
        tier_key=tier_key,
        display_name=name,
        total_cost_usd=total,
        description=desc,
        target_use_case=use_case,
        models={
            "scriptwriting": {"model": script_cfg[0], "provider": script_cfg[1], "unit_cost": script_cfg[2]},
            "visuals": {"model": visual_cfg[0], "provider": visual_cfg[1], "unit_cost": visual_cfg[2]},
            "voiceover": {"model": voice_cfg[0], "provider": voice_cfg[1], "unit_cost": voice_cfg[2]},
            "motion": {"model": motion_cfg[0], "provider": motion_cfg[1], "unit_cost": motion_cfg[2]},
            "music": {"model": music_cfg[0], "provider": music_cfg[1], "unit_cost": music_cfg[2]},
            "sfx": {"model": sfx_cfg[0], "provider": sfx_cfg[1], "unit_cost": sfx_cfg[2]},
        },
        itemized_spend={
            "scriptwriting_usd": script_cost,
            "visuals_usd": visual_cost,
            "voiceover_usd": voice_cost,
            "motion_usd": motion_cost,
            "music_usd": music_cost,
            "sfx_usd": sfx_cost,
        },
    )


def recommend_production_tiers(
    metadata: dict[str, Any] | None = None,
    duration_seconds: float = 30.0,
    scenes_count: int = 4,
) -> dict[str, Any]:
    """Calculate and return 3 distinct production tiers: Low-Cost, Balanced, and Cinematic."""
    meta = metadata or {}
    chars = scenes_count * 120
    is_dance = meta.get("has_dance", False) or "dance" in meta.get("video_format", "").lower()

    # 1. Tier 1: Low-Cost / Quick Test Tier
    tier_low = _build_tier(
        tier_key="low_cost",
        name="Low-Cost Quick Test",
        desc="Ultra-fast validation for script timing, comedic pacing, and visual framing with minimum API spend.",
        use_case="Quick test before selecting high-cost generation.",
        script_cfg=("gemini-1.5-flash", "Google", 0.000000375, 6000),
        visual_cfg=("flux-1-schnell", "TogetherAI", 0.003, scenes_count),
        voice_cfg=("edge-tts-neural", "EdgeTTS", 0.000000, chars),
        motion_cfg=("camera-pan-zoom-2.5d", "LocalFFmpeg", 0.0000, duration_seconds),
        music_cfg=("harmonic-synth-local", "LocalDSP", 0.0000, 1),
        sfx_cfg=("librosa-foley", "LocalDSP", 0.0000, scenes_count),
    )

    # 2. Tier 2: Balanced Creator Standard (Broadcast Default)
    tier_bal = _build_tier(
        tier_key="balanced",
        name="Balanced Creator Standard",
        desc="Commercial broadcast YouTube standard with studio neural voiceover and cleared soundtrack.",
        use_case="Default for public YouTube / Reels release with optimal ROI.",
        script_cfg=("gemini-1.5-pro", "Google", 0.00000125, 14000),
        visual_cfg=("flux-1-schnell", "TogetherAI", 0.003, scenes_count),
        voice_cfg=("azure-speech-neural-hd", "Microsoft", 0.000016, chars),
        motion_cfg=("camera-pan-zoom-2.5d", "LocalFFmpeg", 0.0000, duration_seconds),
        music_cfg=("suno-v3.5-instrumental", "Suno", 0.0800, 1),
        sfx_cfg=("librosa-foley", "LocalDSP", 0.0000, scenes_count),
    )

    # 3. Tier 3: High-Fidelity Cinematic Movie-Like
    motion_model = ("mimic-motion", "Fal.ai", 0.0400, 10.0) if is_dance else ("live-portrait", "Fal.ai", 0.0120, 10.0)
    tier_cine = _build_tier(
        tier_key="cinematic",
        name="High-Fidelity Cinematic Movie-Like",
        desc="Movie-grade visual fidelity, expressive emotional voice acting, neural motion, and vocal soundtrack.",
        use_case="Flagship production, high-budget campaigns, and premium cinematic showcase.",
        script_cfg=("claude-3-5-sonnet", "Anthropic", 0.00000300, 14000),
        visual_cfg=("flux-1-dev", "Fal.ai", 0.025, scenes_count),
        voice_cfg=("eleven-multilingual-v2", "ElevenLabs", 0.000030, chars),
        motion_cfg=motion_model,
        music_cfg=("suno-v3.5-vocal-pro", "Suno", 0.0800, 1),
        sfx_cfg=("audioldm-2", "Fal.ai", 0.0050, scenes_count),
    )

    result = {
        "recommended_default": "balanced",
        "quick_test_option": "low_cost",
        "tiers": {
            "low_cost": tier_low.model_dump(),
            "balanced": tier_bal.model_dump(),
            "cinematic": tier_cine.model_dump(),
        },
    }
    logger.info(
        f"tiers_recommended: low=${tier_low.total_cost_usd}, bal=${tier_bal.total_cost_usd}, "
        f"cine=${tier_cine.total_cost_usd}"
    )
    return result


__all__ = ["TierSpecification", "recommend_production_tiers"]
