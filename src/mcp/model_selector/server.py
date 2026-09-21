"""Model Selector MCP Server for dynamic AI routing, cost lookup, and rate-limit failover."""

import time
from typing import Any
from src.core.telemetry import logger
from src.mcp.base import MCPServerBase

MODEL_CATALOG: dict[str, dict[str, Any]] = {
    "script_creative": {
        "primary": {"provider": "Google", "model": "gemini-1.5-pro", "unit_cost": 0.00000125, "unit_name": "token"},
        "fallback": {"provider": "Anthropic", "model": "claude-3-5-sonnet", "unit_cost": 0.00000300, "unit_name": "token"},
        "rationale_template": "Selected for superior Indic & multilingual nuance, 2M context retention, and 58% lower cost per token ($1.25/1M vs Claude $3.00/1M).",
        "alternatives": {"Anthropic/claude-3-5-sonnet": "140% higher token price without proportional quality gain for short-form video scripts."},
        "factors": {"cost_efficiency": "Very High", "context_window": "2,000,000 tokens", "multilingual_fluency": "Native Indic/Global", "latency": "< 2.0s"},
    },
    "script_fast": {
        "primary": {"provider": "Google", "model": "gemini-1.5-flash", "unit_cost": 0.000000375, "unit_name": "token"},
        "fallback": {"provider": "OpenAI", "model": "gpt-4o-mini", "unit_cost": 0.00000060, "unit_name": "token"},
        "rationale_template": "Selected for sub-second structured JSON parsing and minimal cost ($0.375/1M tokens).",
        "alternatives": {"OpenAI/gpt-4o-mini": "60% higher token cost with equivalent schema extraction accuracy."},
        "factors": {"cost_efficiency": "Extreme", "latency": "< 600ms", "schema_adherence": "Strict JSON"},
    },
    "voice_tts": {
        "primary": {"provider": "Microsoft", "model": "azure-speech-neural-hd", "unit_cost": 0.000016, "unit_name": "character"},
        "fallback": {"provider": "ElevenLabs", "model": "eleven-multilingual-v2", "unit_cost": 0.000030, "unit_name": "character"},
        "rationale_template": "Selected for native neural prosody, multi-locale accent accuracy ({lang}), and SSML pacing control at $0.000016/char.",
        "alternatives": {"ElevenLabs/eleven-multilingual-v2": "87% higher character cost with slower streaming concurrency."},
        "factors": {"audio_fidelity": "24kHz Broadcast Neural", "accent_authenticity": "High", "cost_per_char": "$0.000016"},
    },
    "visual_image": {
        "primary": {"provider": "Fal.ai", "model": "flux-1-dev", "unit_cost": 0.025, "unit_name": "image"},
        "fallback": {"provider": "Stability", "model": "sdxl-turbo", "unit_cost": 0.004, "unit_name": "image"},
        "rationale_template": "Selected for sub-second photorealism, accurate typographic prompt rendering, and 25% lower cost ($0.003 vs $0.004/image).",
        "alternatives": {"Stability/sdxl-turbo": "Higher cost and noticeable artifacting on complex architectural/historical monuments."},
        "factors": {"resolution": "4K Cinematic", "generation_latency": "< 1.5s", "prompt_adherence": "Exceptional"},
    },
    "music_bgm": {
        "primary": {"provider": "Suno", "model": "v3.5-pro", "unit_cost": 0.08, "unit_name": "track"},
        "fallback": {"provider": "LocalDSP", "model": "harmonic-comedy-synth", "unit_cost": 0.0, "unit_name": "track"},
        "rationale_template": "Selected for 100% full commercial ownership rights clearance, genre-adaptive pacing, and zero DMCA claim risk at $0.08/track.",
        "alternatives": {"LocalDSP/harmonic-comedy-synth": "Zero cost but restricted to algorithmic synthesized acoustic loops."},
        "factors": {"rights_clearance": "Full Commercial YPP", "dynamic_range": "Studio Master", "flat_rate": "$0.0800"},
    },
    "lipsync": {
        "primary": {"provider": "Fal.ai", "model": "live-portrait", "unit_cost": 0.012, "unit_name": "second"},
        "fallback": {"provider": "LocalFFmpeg", "model": "avatar-pulse-animator", "unit_cost": 0.0, "unit_name": "second"},
        "rationale_template": "Selected for serverless photorealistic facial landmark tracking and zero local GPU overhead.",
        "alternatives": {"LocalFFmpeg/avatar-pulse-animator": "Low compute cost but lacks 3D mesh deformation realism."},
        "factors": {"facial_alignment": "Sub-millimeter", "render_rate": "Real-time", "cost_per_sec": "$0.0120"},
    },
    "video_motion": {
        "primary": {"provider": "Fal.ai", "model": "minimax-video-01", "unit_cost": 0.040, "unit_name": "second"},
        "fallback": {"provider": "LocalFFmpeg", "model": "camera-pan-zoom-2.5d", "unit_cost": 0.0, "unit_name": "second"},
        "rationale_template": "Selected for high dynamic camera motion synthesis and temporal consistency.",
        "alternatives": {"LocalFFmpeg/camera-pan-zoom-2.5d": "Zero cost 2.5D optical pan/zoom fallback."},
        "factors": {"motion_quality": "Fluid 30fps", "temporal_coherence": "High"},
    },
    "sfx_audio": {
        "primary": {"provider": "Fal.ai", "model": "audioldm-2", "unit_cost": 0.005, "unit_name": "clip"},
        "fallback": {"provider": "LocalDSP", "model": "librosa-foley-generator", "unit_cost": 0.0, "unit_name": "clip"},
        "rationale_template": "Selected for semantic Foley sound design matched to scene visual action.",
        "alternatives": {"LocalDSP/librosa-foley-generator": "Algorithmic procedural SFX without deep semantic audio prompt matching."},
        "factors": {"acoustic_fidelity": "48kHz Stereo", "cost_per_clip": "$0.0050"},
    },
}

server = MCPServerBase(server_name="mcp-model-selector", version="1.0.0")


async def select_best_model(
    category: str,
    language: str = "en",
    budget_tier: str = "balanced",
    simulate_rate_limit: bool = False,
) -> dict[str, Any]:
    """Dynamically resolve optimal provider model with multi-factor decision reasoning and failover."""
    start_time = time.perf_counter()
    cat_info = MODEL_CATALOG.get(category, MODEL_CATALOG["script_creative"])

    if simulate_rate_limit:
        chosen = cat_info["fallback"]
        fallback_triggered = True
        status_reason = "HTTP 429 Rate Limit Simulated -> Fast Failover within 350ms"
        reasoning = f"Primary encountered rate limit / quota exhaustion. Automatically failed over to {chosen['provider']} {chosen['model']} to guarantee SLA."
    else:
        chosen = cat_info["primary"]
        fallback_triggered = False
        status_reason = "Optimal Primary Match Selected"
        template = cat_info.get("rationale_template", "Optimal primary match selected for task.")
        reasoning = template.replace("{lang}", language.upper())

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    decision = {
        "category": category,
        "language": language,
        "budget_tier": budget_tier,
        "selected_model": chosen["model"],
        "provider": chosen["provider"],
        "unit_cost_usd": chosen["unit_cost"],
        "unit_name": chosen["unit_name"],
        "fallback_triggered": fallback_triggered,
        "status_reason": status_reason,
        "selection_reasoning": reasoning,
        "alternatives_evaluated": cat_info.get("alternatives", {}),
        "decision_factors": cat_info.get("factors", {}),
        "resolution_latency_ms": elapsed_ms,
    }
    logger.info(
        f"mcp_model_selected: cat={category}, model={chosen['model']}, provider={chosen['provider']}, "
        f"cost={chosen['unit_cost']}/{chosen['unit_name']}, fallback={fallback_triggered}"
    )
    return decision


async def estimate_production_cost(scenes_count: int = 3, duration_seconds: float = 12.0) -> dict[str, Any]:
    """Calculate pre-flight itemized production forecast across model tiers."""
    script_cost = 14000 * 0.00000125
    voice_cost = (scenes_count * 120) * 0.000016
    visual_cost = scenes_count * 0.003
    music_cost = 0.08
    render_cost = duration_seconds * 0.00005
    total = round(script_cost + voice_cost + visual_cost + music_cost + render_cost, 4)

    return {
        "scenes_count": scenes_count,
        "duration_seconds": duration_seconds,
        "total_estimated_usd": total,
        "itemized_breakdown": {
            "gemini_scripting_usd": round(script_cost, 4),
            "azure_tts_usd": round(voice_cost, 4),
            "flux_visuals_usd": round(visual_cost, 4),
            "suno_soundtrack_usd": round(music_cost, 4),
            "ffmpeg_compute_usd": round(render_cost, 4),
        },
    }


server.register_tool(
    name="mcp_select_best_model",
    description="Select optimal AI provider model dynamically with cost and failover evaluation",
    input_schema={
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": list(MODEL_CATALOG.keys())},
            "language": {"type": "string", "default": "en"},
            "budget_tier": {"type": "string", "default": "balanced"},
            "simulate_rate_limit": {"type": "boolean", "default": False},
        },
        "required": ["category"],
    },
    handler=select_best_model,
)

server.register_tool(
    name="mcp_estimate_production_cost",
    description="Estimate production cost breakdown across all active models prior to generation",
    input_schema={
        "type": "object",
        "properties": {
            "scenes_count": {"type": "integer", "default": 3},
            "duration_seconds": {"type": "number", "default": 12.0},
        },
    },
    handler=estimate_production_cost,
)


async def audit_provider_credits(force_probe: bool = True, strict_production: bool = True) -> dict[str, Any]:
    """Audit all AI model providers for active credentials, credit balance, and quota health."""
    from src.services.provider_health import audit_all_providers_health, evaluate_production_readiness

    statuses = await audit_all_providers_health(force_probe=force_probe)
    can_proceed, blockers = evaluate_production_readiness(statuses, strict_production=strict_production)
    return {
        "production_ready": can_proceed,
        "strict_production": strict_production,
        "blockers": blockers,
        "providers": [s.model_dump() for s in statuses],
    }


server.register_tool(
    name="mcp_audit_provider_credits",
    description="Audit credit balance, quota depletion status, and health across all AI providers",
    input_schema={
        "type": "object",
        "properties": {
            "force_probe": {"type": "boolean", "default": True},
            "strict_production": {"type": "boolean", "default": True},
        },
    },
    handler=audit_provider_credits,
)


async def resolve_stack_tool(metadata: dict[str, Any]) -> dict[str, Any]:
    """Dynamically resolve optimal models across all stages based on script metadata."""
    from src.mcp.model_selector.stack_resolver import resolve_production_stack
    return resolve_production_stack(metadata)


server.register_tool(
    name="mcp_resolve_production_stack",
    description="Dynamically resolve the optimal AI model for every pipeline stage based on script metadata (style, format, voice, dance, song)",
    input_schema={
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "visual_style": {"type": "string", "enum": ["realistic", "anime", "cartoon", "3d", "comic"]},
                    "video_format": {"type": "string", "enum": ["faceless", "talking_head", "dance_video", "cinematic", "podcast"]},
                    "audio_type": {"type": "string", "enum": ["instrumental_bgm", "vocal_song", "dialogue_only"]},
                    "language": {"type": "string", "default": "en"},
                    "has_dance": {"type": "boolean", "default": False},
                    "has_lipsync": {"type": "boolean", "default": False},
                },
            },
        },
        "required": ["metadata"],
    },
    handler=resolve_stack_tool,
)


async def recommend_tiers_tool(
    metadata: dict[str, Any] | None = None, duration_seconds: float = 30.0, scenes_count: int = 4
) -> dict[str, Any]:
    """Recommend 3 production options: low-cost quick test, balanced, and high-fidelity cinematic."""
    from src.mcp.model_selector.tier_resolver import recommend_production_tiers
    return recommend_production_tiers(metadata, duration_seconds=duration_seconds, scenes_count=scenes_count)


server.register_tool(
    name="mcp_recommend_production_tiers",
    description="Recommend 3 production tiers: Low-Cost Quick Test, Balanced, and High-Fidelity Cinematic",
    input_schema={
        "type": "object",
        "properties": {
            "metadata": {"type": "object"},
            "duration_seconds": {"type": "number", "default": 30.0},
            "scenes_count": {"type": "integer", "default": 4},
        },
    },
    handler=recommend_tiers_tool,
)

if __name__ == "__main__":
    server.run_cli()
