"""Unit tests for Channel Profile Registry and Directorial Guardrails."""

import json
from pathlib import Path
from src.config.channel_registry import (
    ChannelProfile,
    load_channel_profiles,
    get_channel_profile,
    save_channel_profile,
)


def test_channel_registry_loading():
    """Verify that all default channel JSON profiles are loaded correctly."""
    profiles = load_channel_profiles(force_reload=True)
    assert len(profiles) >= 4
    assert "earth_serenade" in profiles
    assert "silent_hearth" in profiles
    assert "cineai_docs" in profiles
    assert "telugu_comedy" in profiles


def test_earth_serenade_profile_and_guardrails():
    """Verify Earth Serenade profile metadata and directorial prompt formatting."""
    profile = get_channel_profile("earth_serenade")
    assert profile is not None
    assert profile.channel_name == "Earth Serenade"
    assert "🌿" in profile.tag
    assert "relax/nature" in profile.allowed_genres
    assert "relax/healing" in profile.allowed_genres
    assert "relax/zen" in profile.allowed_genres

    guardrails_text = profile.format_directorial_guardrails_block()
    assert "ACTIVE CHANNEL BRANDING" in guardrails_text
    assert "Earth Serenade" in guardrails_text
    assert "Solfeggio" in guardrails_text or "432Hz" in guardrails_text or "Harmonic" in guardrails_text


def test_silent_hearth_profile_and_guardrails():
    """Verify Silent Hearth profile metadata and pure ASMR policy."""
    profile = get_channel_profile("silent_hearth")
    assert profile is not None
    assert profile.channel_name == "Silent Hearth"
    assert "🔥" in profile.tag
    assert "relax/hearth" in profile.allowed_genres
    assert "relax/cozy" in profile.allowed_genres
    assert profile.audio_profile.bgm_enabled_by_default is False

    guardrails_text = profile.format_directorial_guardrails_block()
    assert "DISABLED (Pure Natural Foley / ASMR)" in guardrails_text
    assert "Amber firelight" in guardrails_text or "firelight" in guardrails_text.lower()


def test_save_and_reload_channel_profile(tmp_path, monkeypatch):
    """Verify saving and re-reading channel profiles."""
    test_channels_dir = tmp_path / "channels"
    test_channels_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("src.config.channel_registry.CHANNELS_DIR", test_channels_dir)

    new_profile = ChannelProfile(
        channel_id="nordic_aurora",
        channel_name="Nordic Aurora",
        handle="@NordicAurora",
        niche_category="Arctic Chill & Solitude",
        target_audience="Deep sleep & insomnia relief",
        tag="❄️ Arctic Solitude",
        comments="Focus on Finnish Lapland and snowy pine forests",
        allowed_genres=["relax/nature", "relax/ambient"],
    )
    saved_file = save_channel_profile(new_profile)
    assert saved_file.exists()

    loaded = get_channel_profile("nordic_aurora")
    assert loaded is not None
    assert loaded.channel_name == "Nordic Aurora"
    assert loaded.tag == "❄️ Arctic Solitude"
    assert loaded.comments == "Focus on Finnish Lapland and snowy pine forests"


def test_api_list_channels_endpoint():
    """Verify that GET /api/channels returns seeded channels with tags and allowed genres."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    from src.config.channel_registry import load_channel_profiles

    load_channel_profiles(force_reload=True)
    client = TestClient(app)
    response = client.get("/api/channels")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    slugs = [c["channel_slug"] for c in data]
    assert "earth_serenade" in slugs
    assert "silent_hearth" in slugs

