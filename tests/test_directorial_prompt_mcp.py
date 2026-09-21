"""Unit tests for Contextual Directorial Prompt MCP Server & Router."""

import json
import pytest
from src.mcp.prompt_director.directorial_router import (
    classify_directorial_mode,
    build_directorial_prompt,
)
from src.mcp.prompt_director.server import get_directorial_prompt, prompt_director_server
from src.agents.script_agent import ScriptAgent


def test_classifier_modes():
    """Verify deterministic Tier 0 classification for diverse prompts."""
    # Music / Dance
    assert classify_directorial_mode("Telugu folk dance celebration", "music") == "music_dance"
    assert classify_directorial_mode("High energy mass song", "tollywood_mass") == "music_dance"

    # Scenic Walking Tour
    assert classify_directorial_mode("Swiss Alps 4K scenic walking tour", "travel") == "scenic_narrative"
    assert classify_directorial_mode("Rainy forest relaxation stroll", "nature") == "scenic_narrative"

    # Tech Explainer
    assert classify_directorial_mode("Explaining distributed consensus in Python", "tech") == "tech_explainer"
    assert classify_directorial_mode("Software architecture tutorial", "education") == "tech_explainer"

    # Nature Documentary
    assert classify_directorial_mode("Wild Canada Nature's Untamed Beauty", "documentary") == "nature_documentary"
    assert classify_directorial_mode("Arctic Wildlife Planet Earth", "nature") == "nature_documentary"

    # Mountain Survival Documentary
    assert classify_directorial_mode("Trapped in Afghanistan's Deadliest Blizzard: Shepherd's Survival Story", "documentary") == "mountain_survival"
    assert classify_directorial_mode("Pamir Mountain nomadic blizzard survival", "survival") == "mountain_survival"

    # Narrative Satire
    assert classify_directorial_mode("Silicon Valley corporate satire", "comedy") == "narrative_retention"


@pytest.mark.asyncio
async def test_dance_directorial_prompt_injection():
    """Verify dance prompt includes 3-phase choreo, optical bokeh depth, and Directive 12 contract."""
    res = await get_directorial_prompt(
        topic="Village jathara mass dance with female lead",
        genre="music",
        video_format="Music Video",
        target_duration_seconds=180,
    )
    prompt = res["prompt"]
    assert res["mode"] == "music_dance"

    # Must contain Directive 15 & 16 dance specifics
    assert "DYNAMIC CHOREOGRAPHY PER BEAT" in prompt
    assert "MULTI-LOCATION PROGRESSION" in prompt
    assert "optical bokeh" in prompt

    # Must contain Universal Baseline Contract (Directive 12 & 14)
    assert "MANDATORY CAST & CHARACTER PHYSICALITY DIRECTIVE" in prompt
    assert "balanced, naturally fit, healthy medium-slender build" in prompt
    assert "ages 23–27" in prompt
    assert "48000 Hz 24-bit" in prompt

    # Must NOT contain irrelevant walking tour or tech explainer directives
    assert "walking cadence (~1 m/s / 3 km/h)" not in prompt
    assert "PROBLEM THESIS HOOK" not in prompt


@pytest.mark.asyncio
async def test_scenic_walk_directorial_prompt_injection():
    """Verify walking tour prompt includes 3km/h pacing, 5600K daylight, and narrative lore."""
    res = await get_directorial_prompt(
        topic="Alpine mountain walking trail in Switzerland",
        genre="travel",
        video_format="Walking Tour",
    )
    prompt = res["prompt"]
    assert res["mode"] == "scenic_narrative"

    # Must contain Directive 11 & 13 specifics
    assert "LEISURELY WALKING CADENCE (3 km/h)" in prompt
    assert "NATURAL DAYLIGHT OVER ARTIFICIAL FLARES" in prompt
    assert "CRITICAL YPP MONETIZATION & NARRATIVE GUARD" in prompt

    # Must NOT contain dance hook steps
    assert "spinning chakkars" not in prompt


@pytest.mark.asyncio
async def test_mcp_server_protocol_dispatch():
    """Verify JSON-RPC 2.0 dispatch for mcp_get_directorial_prompt."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "mcp_get_directorial_prompt",
            "arguments": {
                "topic": "Fast-paced tech explainer on LLMs",
                "genre": "tech",
            },
        },
    }
    response = await prompt_director_server.dispatch(request)
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["mode"] == "tech_explainer"
    assert "PROBLEM THESIS HOOK" in payload["prompt"]


@pytest.mark.asyncio
async def test_script_agent_integration(monkeypatch):
    """Verify ScriptAgent properly delegates to MCP and returns complete storyboard metadata."""
    agent = ScriptAgent()

    # Mock the LLM call to verify agent pipeline end-to-end deterministically
    async def mock_generate_structured(prompt):
        assert "DYNAMIC CHOREOGRAPHY PER BEAT" in prompt
        return {
            "title": "Jathara Beat",
            "hook_thesis": "The dance begins",
            "scenes": [{"scene_id": 1, "dialogue": "Dhim dhim taka taka"}],
            "vocal_gender": "female",
            "vocal_delivery_type": "lead_lip_sync",
            "recommended_fps": 30,
        }

    monkeypatch.setattr(agent.llm, "generate_structured", mock_generate_structured)

    result = await agent.draft_episode_storyboard(
        topic="Jathara mass folk song with female dancer",
        genre="music",
    )

    assert result["production_mode"] == "music_dance"
    assert result["vocal_gender"] == "female"
    assert result["vocal_delivery_type"] == "lead_lip_sync"
    assert result["recommended_fps"] == 30
