"""Unit tests for Contextual Directorial Prompt MCP Server & Router."""

import json
import pytest
from src.mcp.prompt_director.directorial_router import (
    classify_directorial_mode,
    build_directorial_prompt,
)
from src.mcp.prompt_director.server import get_directorial_prompt, prompt_director_server
from src.agents.script_agent import ScriptAgent
from src.providers.llm.mock_storyboards import resolve_mock_storyboard


def test_telangana_folk_dance_intent_is_preserved():
    """Folk dance requests must not auto-flip into comedy or Bathukamma-song territory."""
    plan = resolve_mock_storyboard("telangana folk dance in village setting")

    title = (plan.get("title") or "").lower()
    hook = (plan.get("hook_thesis") or "").lower()
    assert "dance" in title or "dance" in hook
    assert "comedy" not in title.lower()
    assert "bathukamma" not in title.lower()
    assert "comedy" not in hook.lower()
    assert "bathukamma" not in hook.lower()


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
async def test_cinematic_lighting_and_context_lock():
    """Prompts must default to readable daylight for village scenes and bright premium light for hotel events."""
    village = await get_directorial_prompt(
        topic="Telangana folk dance in village setting",
        genre="music",
        video_format="Dance Video",
        target_duration_seconds=10,
        language="te",
    )
    hotel = await get_directorial_prompt(
        topic="Hindi family party dance in hotel setting",
        genre="music",
        video_format="Dance Video",
        target_duration_seconds=10,
        language="te",
    )

    village_prompt = village["prompt"]
    hotel_prompt = hotel["prompt"]

    assert "5400K–5600K" in village_prompt or "5400K-5600K" in village_prompt
    assert "visible faces" in village_prompt.lower() or "visible facial detail" in village_prompt.lower()
    assert "bright polished event lighting" in hotel_prompt.lower() or "well-lit event lighting" in hotel_prompt.lower()
    assert "no dark under-lit" in hotel_prompt.lower() or "no muddy dark frames" in hotel_prompt.lower()


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
    assert "WALKING CADENCE" in prompt and ("1.5" in prompt or "3 km/h" in prompt)
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
