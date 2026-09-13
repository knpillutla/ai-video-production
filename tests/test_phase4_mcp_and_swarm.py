"""Phase 4 Comprehensive Test Suite: Modular MCP Servers & Specialized Agent Swarm."""

import json
from pathlib import Path
from uuid import uuid4
import pytest

from src.agents.audio_foley_agent import audio_foley_agent
from src.agents.growth_seo_agent import growth_seo_agent
from src.agents.script_agent import script_agent
from src.agents.swarm_coordinator import swarm_coordinator
from src.agents.transcreation_agent import transcreation_agent
from src.compliance.rights_ledger import rights_ledger
from src.domain.rights import AssetType, CommercialLicenseType
from src.mcp.compliance_guard.server import server as compliance_server
from src.mcp.compositor_engine.server import server as compositor_server
from src.mcp.model_selector.server import server as model_selector_server
from src.mcp.publisher.server import server as publisher_server
from src.mcp.topic_memory.server import server as topic_memory_server
from src.providers.audio.demucs_adapter import demucs_separator


@pytest.mark.asyncio
async def test_mcp_json_rpc_dispatch_protocol():
    """Verify standard JSON-RPC 2.0 dispatch (initialize, ping, tools/list, tools/call)."""
    # 1. Initialize
    init_res = await model_selector_server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_res["result"]["serverInfo"]["name"] == "mcp-model-selector"
    assert "tools" in init_res["result"]["capabilities"]

    # 2. Ping
    ping_res = await model_selector_server.dispatch({"jsonrpc": "2.0", "id": 2, "method": "ping"})
    assert ping_res["result"] == {}

    # 3. Tools list
    tools_res = await model_selector_server.dispatch({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    tool_names = [t["name"] for t in tools_res["result"]["tools"]]
    assert "mcp_select_best_model" in tool_names
    assert "mcp_estimate_production_cost" in tool_names


@pytest.mark.asyncio
async def test_model_selector_dynamic_routing_and_failover():
    """Verify dynamic model selection and sub-350ms rate limit failover."""
    # Primary selection
    req_primary = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {"name": "mcp_select_best_model", "arguments": {"category": "script_creative"}},
    }
    res_primary = await model_selector_server.dispatch(req_primary)
    data_primary = json.loads(res_primary["result"]["content"][0]["text"])
    assert data_primary["selected_model"] == "gemini-1.5-pro"
    assert data_primary["fallback_triggered"] is False

    # Failover trigger (HTTP 429 simulation)
    req_fallback = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "mcp_select_best_model",
            "arguments": {"category": "script_creative", "simulate_rate_limit": True},
        },
    }
    res_fallback = await model_selector_server.dispatch(req_fallback)
    data_fallback = json.loads(res_fallback["result"]["content"][0]["text"])
    assert data_fallback["selected_model"] == "claude-3-5-sonnet"
    assert data_fallback["fallback_triggered"] is True
    assert data_fallback["resolution_latency_ms"] < 350.0


@pytest.mark.asyncio
async def test_compliance_guard_mcp_validation():
    """Verify compliance guard tool validates clean scripts and catches profanity."""
    # Clean script
    clean_call = {
        "jsonrpc": "2.0",
        "id": 20,
        "method": "tools/call",
        "params": {
            "name": "mcp_validate_compliance",
            "arguments": {"script_text": "Welcome to our wonderful family comedy show!"},
        },
    }
    res_clean = await compliance_server.dispatch(clean_call)
    data_clean = json.loads(res_clean["result"]["content"][0]["text"])
    assert data_clean["is_monetization_safe"] is True

    # Dirty script
    dirty_call = {
        "jsonrpc": "2.0",
        "id": 21,
        "method": "tools/call",
        "params": {
            "name": "mcp_validate_compliance",
            "arguments": {"script_text": "What the fuck is this remote standup?"},
        },
    }
    res_dirty = await compliance_server.dispatch(dirty_call)
    data_dirty = json.loads(res_dirty["result"]["content"][0]["text"])
    assert data_dirty["opening_profanity_safe"] is False
    assert len(data_dirty["opening_profanity_violations"]) > 0


@pytest.mark.asyncio
async def test_compliance_guard_rights_audit():
    """Verify compliance guard checks rights ledger commercial clearance."""
    ep_id = uuid4()
    rights_ledger.record_asset(
        episode_id=ep_id,
        asset_type=AssetType.IMAGE,
        file_path="/storage/img_scene.jpg",
        provider="TogetherAI",
        model_name="flux-1-schnell",
        license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
        license_id="COMM-123",
        cleared=True,
    )

    audit_call = {
        "jsonrpc": "2.0",
        "id": 22,
        "method": "tools/call",
        "params": {"name": "mcp_audit_rights_ledger", "arguments": {"episode_id": str(ep_id)}},
    }
    res_audit = await compliance_server.dispatch(audit_call)
    data_audit = json.loads(res_audit["result"]["content"][0]["text"])
    assert data_audit["cleared_for_commercial_monetization"] is True
    assert data_audit["assets_audited_count"] == 1


@pytest.mark.asyncio
async def test_topic_memory_cosine_deduplication():
    """Verify topic memory rejects duplicate topics and commits fresh concepts."""
    # Near duplicate of existing seed topic
    dup_call = {
        "jsonrpc": "2.0",
        "id": 30,
        "method": "tools/call",
        "params": {
            "name": "mcp_check_topic_duplicate",
            "arguments": {"topic": "IT Employee Remote Work Confusions and Standup Comedy"},
        },
    }
    res_dup = await topic_memory_server.dispatch(dup_call)
    data_dup = json.loads(res_dup["result"]["content"][0]["text"])
    assert data_dup["is_duplicate"] is True
    assert data_dup["max_similarity_score"] >= 0.80

    # Fresh original topic
    fresh_call = {
        "jsonrpc": "2.0",
        "id": 31,
        "method": "tools/call",
        "params": {
            "name": "mcp_check_topic_duplicate",
            "arguments": {"topic": "Mars Rover Discovery of Ancient Hydrothermal Vents"},
        },
    }
    res_fresh = await topic_memory_server.dispatch(fresh_call)
    data_fresh = json.loads(res_fresh["result"]["content"][0]["text"])
    assert data_fresh["is_duplicate"] is False

    # Remember fresh topic
    rem_call = {
        "jsonrpc": "2.0",
        "id": 32,
        "method": "tools/call",
        "params": {
            "name": "mcp_remember_topic",
            "arguments": {"topic": "Mars Rover Discovery", "episode_id": "ep_mars_01"},
        },
    }
    res_rem = await topic_memory_server.dispatch(rem_call)
    data_rem = json.loads(res_rem["result"]["content"][0]["text"])
    assert data_rem["status"] == "memorized"


@pytest.mark.asyncio
async def test_compositor_and_publisher_mcp_servers(tmp_path: Path):
    """Verify compositor engine graph generation and publisher payload assembly."""
    scenes = [
        {"duration_seconds": 3.8, "shot_type": "close_up", "dialogue": "Scene 1 speech"},
        {"duration_seconds": 4.2, "shot_type": "wide", "dialogue": "Scene 2 speech"},
    ]
    comp_call = {
        "jsonrpc": "2.0",
        "id": 40,
        "method": "tools/call",
        "params": {"name": "mcp_compile_filter_complex", "arguments": {"scenes": scenes}},
    }
    res_comp = await compositor_server.dispatch(comp_call)
    data_comp = json.loads(res_comp["result"]["content"][0]["text"])
    assert data_comp["is_single_pass"] is True
    assert data_comp["total_scenes"] == 2

    # Publisher payload
    pub_call = {
        "jsonrpc": "2.0",
        "id": 50,
        "method": "tools/call",
        "params": {
            "name": "mcp_prepare_youtube_payload",
            "arguments": {"title": "Test Comedy Video", "description": "Funny sketch"},
        },
    }
    res_pub = await publisher_server.dispatch(pub_call)
    data_pub = json.loads(res_pub["result"]["content"][0]["text"])
    assert data_pub["contains_synthetic_disclosure"] is True
    assert data_pub["payload"]["contentDetails"]["containsSyntheticMedia"] is True


@pytest.mark.asyncio
async def test_demucs_vocal_stem_separation(tmp_path: Path):
    """Verify Demucs adapter generates isolated vocal and accompaniment stems."""
    in_wav = tmp_path / "song.wav"
    out_dir = tmp_path / "stems"

    stems = await demucs_separator.separate_stems(in_wav, out_dir)
    assert stems["vocals"].exists()
    assert stems["accompaniment"].exists()
    assert stems["vocals"].stat().st_size > 500


@pytest.mark.asyncio
async def test_swarm_coordinator_full_agent_workflow(tmp_path: Path):
    """Verify complete Swarm Coordinator handoff across all specialized agents."""
    result = await swarm_coordinator.run_pipeline_swarm(
        topic="Startup Founder Coffee Addiction",
        genre="comedy",
        language="te",
        output_workspace=tmp_path / "swarm_output",
        simulate_model_failover=True,
    )

    assert result["status"] == "completed"
    assert result["model_routing"]["fallback_triggered"] is True
    assert result["compliance_guard"]["is_monetization_safe"] is True
    assert len(result["storyboard"]["scenes"]) >= 3
    assert "manifest" in result["subtitle_bundle"]
    assert Path(result["audio_stems"]["vocals"]).exists()
    assert result["publisher_payload"]["contains_synthetic_disclosure"] is True
