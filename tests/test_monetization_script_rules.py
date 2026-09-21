"""Tests for genre-aware YPP monetization prompt injection and safety auditing."""

import pytest
from src.agents.script_agent import script_agent


@pytest.mark.asyncio
async def test_scenic_monetization_prompt_injection():
    """Verify that scenic and walking tour scripts enforce voiceover narration to prevent YPP demonetization."""
    prompt, mode = script_agent._build_genre_monetization_prompt(
        topic="Appenzell Rainy Alpine Walk",
        genre="scenic",
        video_format="walking_tour",
        style_name="Swiss Alpine Rainy Village & Walking Tour",
        decorations="Glistening rain on timber chalets",
        lighting="Soft overcast mountain light",
        palette="Emerald green, slate grey",
        guidance="Slow steady tracking",
        target_duration_seconds=30,
        language="en",
    )
    assert mode == "scenic_narrative"
    assert "CRITICAL YPP MONETIZATION MANDATE" in prompt
    assert "Repetitive / Reused Content" in prompt
    assert "educational trail guidance" in prompt
    assert "Never leave dialogue blank" in prompt


@pytest.mark.asyncio
async def test_music_dance_monetization_prompt_injection():
    """Verify that music and folk dance scripts enforce rhythmic lyrics, choreo staging, and Green Dollar safety."""
    prompt, mode = script_agent._build_genre_monetization_prompt(
        topic="Village Festive Celebration",
        genre="tollywood_mass",
        video_format="folk_dance_music_video",
        style_name="Vibrant Village Mass Folk",
        decorations="Festive marigolds, rustic village square",
        lighting="Warm golden hour",
        palette="Vibrant yellow, crimson red",
        guidance="Fast rhythmic cutting",
        target_duration_seconds=30,
        language="te",
    )
    assert mode == "music_dance"
    assert "CRITICAL YPP MONETIZATION & ADSENSE SAFETY MANDATE" in prompt
    assert "rhyming couplets (prasa)" in prompt
    assert "CHOREOGRAPHY STAGING" in prompt
    assert "GREEN DOLLAR GUARANTEE" in prompt


@pytest.mark.asyncio
async def test_narrative_retention_monetization_prompt_injection():
    """Verify that narrative/comedy scripts enforce 5-second hooks and AdSense 11 category safety."""
    prompt, mode = script_agent._build_genre_monetization_prompt(
        topic="Tech Startup Moonlighting",
        genre="comedy",
        video_format="satire",
        style_name="Modern Satire",
        decorations="Dual laptop screens",
        lighting="Cool office blue",
        palette="Steel grey, electric blue",
        guidance="Fast comic timing",
        target_duration_seconds=30,
        language="en",
    )
    assert mode == "narrative_retention"
    assert "RETENTION HOOK" in prompt
    assert "ADSENSE SAFETY" in prompt


@pytest.mark.asyncio
async def test_draft_episode_storyboard_includes_monetization_audit():
    """Verify draft_episode_storyboard attaches automated YPP monetization safety audit."""
    storyboard = await script_agent.draft_episode_storyboard(
        topic="Seealpsee Mountain Lake Walk",
        genre="scenic",
        video_format="walking_tour",
        target_duration_seconds=15,
    )
    assert storyboard["production_mode"] == "scenic_narrative"
    assert "ypp_monetization_safety" in storyboard
    audit = storyboard["ypp_monetization_safety"]
    assert "is_monetization_safe" in audit
    assert "risk_level" in audit
    assert "adsense_violations" in audit
