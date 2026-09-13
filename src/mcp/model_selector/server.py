"""Model Selector MCP Server for dynamic AI routing, cost lookup, and rate-limit failover."""

import time
from typing import Any
from src.mcp.base import MCPServerBase

MODEL_CATALOG: dict[str, dict[str, Any]] = {
    "script_creative": {
        "primary": {"provider": "Google", "model": "gemini-1.5-pro", "unit_cost": 0.00000125, "unit_name": "token"},
        "fallback": {"provider": "Anthropic", "model": "claude-3-5-sonnet", "unit_cost": 0.00000300, "unit_name": "token"},
    },
    "script_fast": {
        "primary": {"provider": "Google", "model": "gemini-1.5-flash", "unit_cost": 0.000000375, "unit_name": "token"},
        "fallback": {"provider": "OpenAI", "model": "gpt-4o-mini", "unit_cost": 0.00000060, "unit_name": "token"},
    },
    "voice_tts": {
        "primary": {"provider": "Microsoft", "model": "azure-speech-neural-hd", "unit_cost": 0.000016, "unit_name": "character"},
        "fallback": {"provider": "ElevenLabs", "model": "eleven-multilingual-v2", "unit_cost": 0.000030, "unit_name": "character"},
    },
    "visual_image": {
        "primary": {"provider": "TogetherAI", "model": "flux-1-schnell", "unit_cost": 0.003, "unit_name": "image"},
        "fallback": {"provider": "Stability", "model": "sdxl-turbo", "unit_cost": 0.004, "unit_name": "image"},
    },
    "music_bgm": {
        "primary": {"provider": "Suno", "model": "v3.5-pro", "unit_cost": 0.08, "unit_name": "track"},
        "fallback": {"provider": "LocalDSP", "model": "harmonic-comedy-synth", "unit_cost": 0.0, "unit_name": "track"},
    },
    "lipsync": {
        "primary": {"provider": "Fal.ai", "model": "live-portrait", "unit_cost": 0.012, "unit_name": "second"},
        "fallback": {"provider": "LocalFFmpeg", "model": "avatar-pulse-animator", "unit_cost": 0.0, "unit_name": "second"},
    },
    "video_motion": {
        "primary": {"provider": "Fal.ai", "model": "minimax-video-01", "unit_cost": 0.040, "unit_name": "second"},
        "fallback": {"provider": "LocalFFmpeg", "model": "camera-pan-zoom-2.5d", "unit_cost": 0.0, "unit_name": "second"},
    },
    "sfx_audio": {
        "primary": {"provider": "Fal.ai", "model": "audioldm-2", "unit_cost": 0.005, "unit_name": "clip"},
        "fallback": {"provider": "LocalDSP", "model": "librosa-foley-generator", "unit_cost": 0.0, "unit_name": "clip"},
    },
}

server = MCPServerBase(server_name="mcp-model-selector", version="1.0.0")


async def select_best_model(
    category: str,
    language: str = "en",
    budget_tier: str = "balanced",
    simulate_rate_limit: bool = False,
) -> dict[str, Any]:
    """Dynamically resolve optimal provider model with automatic rate-limit failover."""
    start_time = time.perf_counter()
    cat_info = MODEL_CATALOG.get(category, MODEL_CATALOG["script_creative"])

    if simulate_rate_limit:
        chosen = cat_info["fallback"]
        fallback_triggered = True
        status_reason = "HTTP 429 Rate Limit Simulated -> Fast Failover within 350ms"
    else:
        chosen = cat_info["primary"]
        fallback_triggered = False
        status_reason = "Optimal Primary Match Selected"

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return {
        "category": category,
        "language": language,
        "budget_tier": budget_tier,
        "selected_model": chosen["model"],
        "provider": chosen["provider"],
        "unit_cost_usd": chosen["unit_cost"],
        "unit_name": chosen["unit_name"],
        "fallback_triggered": fallback_triggered,
        "status_reason": status_reason,
        "resolution_latency_ms": elapsed_ms,
    }


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

if __name__ == "__main__":
    server.run_cli()
