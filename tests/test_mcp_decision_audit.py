"""Tests for MCP Decision-Making Engine, Decision Auditor, and Telemetry File Logging."""

import json
from pathlib import Path
import pytest

from src.core.telemetry import logger
from src.mcp.model_selector.audit import MCPDecisionAuditor, audit_pipeline_models
from src.mcp.model_selector.server import select_best_model


@pytest.mark.asyncio
async def test_mcp_select_best_model_decision_reasoning():
    """Verify select_best_model returns selection_reasoning, alternatives, and factors."""
    decision = await select_best_model(category="script_creative", language="te")
    assert decision["selected_model"] == "gemini-1.5-pro"
    assert "selection_reasoning" in decision
    assert "Indic" in decision["selection_reasoning"] or "multilingual" in decision["selection_reasoning"]
    assert "alternatives_evaluated" in decision
    assert "decision_factors" in decision
    assert decision["fallback_triggered"] is False


@pytest.mark.asyncio
async def test_mcp_decision_auditor_persistence(tmp_path: Path):
    """Verify MCPDecisionAuditor saves structured mcp_decision_log.json to disk."""
    auditor = await audit_pipeline_models(
        language="en",
        budget_tier="balanced",
        output_dir=tmp_path,
        metadata={"title": "Test Title", "episode_id": "test-ep-01"},
    )
    assert len(auditor.decisions) == 4
    summary = auditor.get_summary()
    assert len(summary) == 4
    assert any(s["category"] == "script_creative" for s in summary)

    log_file = tmp_path / "mcp_decision_log.json"
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == "1.0.0"
    assert data["metadata"]["title"] == "Test Title"
    assert len(data["decisions"]) == 4


def test_telemetry_file_logging():
    """Verify that logger writes to disk in logs/studio.log."""
    log_path = Path("logs") / "studio.log"
    logger.info("telemetry_file_logging_verification_probe")
    assert log_path.exists()
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "telemetry_file_logging_verification_probe" in content


@pytest.mark.asyncio
async def test_mcp_resolve_production_stack_metadata():
    """Verify MCP resolves optimal models based on script metadata (anime, dance, faceless)."""
    from src.mcp.model_selector.server import server as model_selector_server

    # 1. Anime Dance Musical Video
    req_anime = {
        "jsonrpc": "2.0",
        "id": 90,
        "method": "tools/call",
        "params": {
            "name": "mcp_resolve_production_stack",
            "arguments": {
                "metadata": {
                    "visual_style": "anime",
                    "video_format": "dance_video",
                    "has_dance": True,
                    "audio_type": "vocal_song",
                    "language": "ja",
                }
            },
        },
    }
    res_anime = await model_selector_server.dispatch(req_anime)
    stack_anime = json.loads(res_anime["result"]["content"][0]["text"])
    assert stack_anime["visual_diffusion"]["model"] == "animagine-xl-3.1"
    assert stack_anime["motion_animation"]["model"] == "mimic-motion"
    assert stack_anime["soundtrack_music"]["music_type"] == "full_lyrical_song"

    # 2. Realistic Faceless Documentary Video
    req_faceless = {
        "jsonrpc": "2.0",
        "id": 91,
        "method": "tools/call",
        "params": {
            "name": "mcp_resolve_production_stack",
            "arguments": {
                "metadata": {
                    "visual_style": "realistic",
                    "video_format": "faceless",
                    "has_dance": False,
                    "has_lipsync": False,
                    "audio_type": "instrumental_bgm",
                    "language": "en",
                }
            },
        },
    }
    res_faceless = await model_selector_server.dispatch(req_faceless)
    stack_faceless = json.loads(res_faceless["result"]["content"][0]["text"])
    assert stack_faceless["visual_diffusion"]["model"] == "flux-1-schnell"
    assert stack_faceless["motion_animation"]["provider"] == "LocalFFmpeg"
    assert stack_faceless["motion_animation"]["unit_cost_usd"] == 0.0
    assert stack_faceless["soundtrack_music"]["music_type"] == "instrumental_bgm"


@pytest.mark.asyncio
async def test_mcp_recommend_production_tiers():
    """Verify MCP recommends 3 distinct production tiers with monotonic cost scaling."""
    from src.mcp.model_selector.server import server as model_selector_server

    req = {
        "jsonrpc": "2.0",
        "id": 92,
        "method": "tools/call",
        "params": {
            "name": "mcp_recommend_production_tiers",
            "arguments": {
                "metadata": {"visual_style": "realistic", "language": "te"},
                "duration_seconds": 30.0,
                "scenes_count": 4,
            },
        },
    }
    res = await model_selector_server.dispatch(req)
    data = json.loads(res["result"]["content"][0]["text"])
    tiers = data["tiers"]

    assert "low_cost" in tiers
    assert "balanced" in tiers
    assert "cinematic" in tiers

    low = tiers["low_cost"]
    bal = tiers["balanced"]
    cine = tiers["cinematic"]

    # Verify monotonic cost relationship
    assert low["total_cost_usd"] < bal["total_cost_usd"] < cine["total_cost_usd"]

    # Verify model selections per tier
    assert low["models"]["scriptwriting"]["model"] == "gemini-1.5-flash"
    assert bal["models"]["scriptwriting"]["model"] == "gemini-1.5-pro"
    assert cine["models"]["visuals"]["model"] == "flux-1-dev"
    assert cine["models"]["voiceover"]["provider"] == "ElevenLabs"


def test_preflight_gate_tier_normalization():
    """Verify tier input normalization for CLI shortcuts."""
    from src.scripts.preflight_gate import _normalize_tier_choice

    assert _normalize_tier_choice("1") == "low_cost"
    assert _normalize_tier_choice("low") == "low_cost"
    assert _normalize_tier_choice("2") == "balanced"
    assert _normalize_tier_choice("bal") == "balanced"
    assert _normalize_tier_choice("3") == "cinematic"
    assert _normalize_tier_choice("movie") == "cinematic"
    assert _normalize_tier_choice("4") == "local"
    assert _normalize_tier_choice("local") == "local"
    assert _normalize_tier_choice("unknown_value", default="balanced") == "balanced"

