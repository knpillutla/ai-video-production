"""Tests for Content Style & Format Intelligence Classifier Agent with User Override."""

import pytest
from httpx import ASGITransport, AsyncClient
from src.agents.classifier_agent import classifier_agent
from src.api.main import app
from src.domain.generation import MediaFormat, ThemeGenre, VisualStyle
from src.domain.repo import repo


def test_deterministic_classification_telugu_comedy():
    """Verify IT WFH comedy scripts are detected as web series, realistic, telugu comedy."""
    result = classifier_agent.detect(
        text="IT employee remote work standup comedy confusions in Hyderabad with funny WiFi excuses.",
        title="WFH Confusions",
    )
    assert result.media_format == MediaFormat.WEB_SERIES
    assert result.visual_style == VisualStyle.REALISTIC
    assert result.theme == ThemeGenre.TELUGU_COMEDY
    assert result.is_auto_detected is True
    assert result.confidence >= 0.80


def test_deterministic_classification_epic_action():
    """Verify epic warrior battles are detected as cinematic movie with epic action theme."""
    result = classifier_agent.detect(
        text="A fierce dynasty warrior interval elevation clash with swords and mass battle scenes.",
        title="Rebel Commander",
    )
    assert result.media_format == MediaFormat.MOVIE_CINEMATIC
    assert result.visual_style == VisualStyle.REALISTIC
    assert result.theme == ThemeGenre.EPIC_ACTION
    assert result.is_auto_detected is True


def test_deterministic_classification_bollywood_dance():
    """Verify high-energy dance steps are detected as dance video with bollywood dance theme."""
    result = classifier_agent.detect(
        text="High-energy sangeet choreography with synchronized hook step and beat drop celebration.",
        title="Desi Beat Drop",
    )
    assert result.media_format == MediaFormat.DANCE_VIDEO
    assert result.visual_style == VisualStyle.REALISTIC
    assert result.theme == ThemeGenre.BOLLYWOOD_DANCE
    assert result.is_auto_detected is True


def test_deterministic_classification_nature_and_wildlife():
    """Verify wildlife safari prompts are detected as cinematic nature documentary."""
    result = classifier_agent.detect(
        text="Snow leopard hunting in Himalayan rocky mountains with pristine wilderness footage.",
        title="Himalayan Predators",
    )
    assert result.media_format == MediaFormat.MOVIE_CINEMATIC
    assert result.visual_style == VisualStyle.REALISTIC
    assert result.theme == ThemeGenre.NATURE_WILDLIFE
    assert result.is_auto_detected is True


def test_deterministic_classification_anime_visual_style():
    """Verify anime keywords trigger VisualStyle.ANIME."""
    result = classifier_agent.detect(
        text="A shonen anime tournament duel with cel shaded manga aesthetics.",
        title="Tokyo Ninja Saga",
    )
    assert result.visual_style == VisualStyle.ANIME


def test_deterministic_classification_3d_animation_style():
    """Verify 3D CGI keywords trigger VisualStyle.ANIMATION_3D."""
    result = classifier_agent.detect(
        text="A friendly talking robot puppy rendered in stylized 3d cgi pixar style.",
        title="Robot Pup Adventures",
    )
    assert result.visual_style == VisualStyle.ANIMATION_3D


def test_user_override_precedence():
    """Verify that user explicit choice overrides AI inference while preserving un-overridden values."""
    # User forces Anime visual style for an IT Comedy script
    res = classifier_agent.resolve_classification(
        text="IT employee WFH comedy",
        user_format=MediaFormat.AUTO,
        user_style=VisualStyle.ANIME,
        user_theme=ThemeGenre.AUTO,
    )
    assert res.visual_style == VisualStyle.ANIME  # Overridden
    assert res.theme == ThemeGenre.TELUGU_COMEDY   # Inferred
    assert res.media_format == MediaFormat.WEB_SERIES  # Inferred
    assert res.is_auto_detected is False
    assert "User Overrides Applied" in res.explanation

    # User leaves everything on AUTO
    res_auto = classifier_agent.resolve_classification(
        text="IT employee WFH comedy",
        user_format=MediaFormat.AUTO,
        user_style=VisualStyle.AUTO,
        user_theme=ThemeGenre.AUTO,
    )
    assert res_auto.is_auto_detected is True


@pytest.mark.asyncio
async def test_api_classify_content_endpoint():
    """Test POST /api/projects/classify-content API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Issue test token
        auth_res = await client.post(
            "/api/auth/test-token",
            json={"email": "director_style@studio.com", "display_name": "Studio Director"},
        )
        token = auth_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test auto detection
        classify_res = await client.post(
            "/api/projects/classify-content",
            headers=headers,
            json={
                "title": "Himalayan Safari",
                "text": "Wild tiger tracking in the thick jungle forest.",
                "user_format": "auto",
                "user_style": "auto",
                "user_theme": "auto",
            },
        )
        assert classify_res.status_code == 200
        data = classify_res.json()
        assert data["theme"] == "nature_wildlife"
        assert data["media_format"] == "movie_cinematic"
        assert data["is_auto_detected"] is True

        # 2. Test user override via API
        override_res = await client.post(
            "/api/projects/classify-content",
            headers=headers,
            json={
                "title": "Himalayan Safari",
                "text": "Wild tiger tracking in the thick jungle forest.",
                "user_format": "web_series",
                "user_style": "anime",
                "user_theme": "auto",
            },
        )
        assert override_res.status_code == 200
        ov_data = override_res.json()
        assert ov_data["media_format"] == "web_series"
        assert ov_data["visual_style"] == "anime"
        assert ov_data["theme"] == "nature_wildlife"
        assert ov_data["is_auto_detected"] is False
