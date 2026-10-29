"""Targeted unit tests for format decoupling, 21 chapters, and separate APIs.

Verifies:
1. All 21 sovereign chapters (including art, movies/music) are generated.
2. Format-specific artifact models instantiate correctly.
3. Documentary create-episode auto-generates 21-chapter raw story and extracts title.
4. Relaxation create-episode initializes decoupled relaxation artifacts.
Strictly offline, $0.00 API expenditure (Rule 8).
"""

import pytest
from pathlib import Path

from src.domain.format_artifacts import (
    DocumentaryArtifacts,
    DocumentaryStoryArtifact,
    RelaxationArtifacts,
    MusicVideoArtifacts,
)
from src.studios.documentary_studio.doc_country_syllabus import ALL_21_KEYS
from src.studios.documentary_studio.doc_story_service import (
    generate_sovereign_21_chapters,
    build_raw_documentary_story,
)


def test_21_chapters_completeness_and_mandates():
    """Confirms all 21 chapters exist and include art, music/movies, and clean energy."""
    chapters = generate_sovereign_21_chapters(destination="Iceland")
    assert len(chapters) == 21

    # Verify keys
    keys = [ch["chapter_key"] for ch in chapters]
    assert keys == ALL_21_KEYS

    # Verify art and music/entertainment specifically
    assert "arts_crafts" in keys
    assert "music_entertainment" in keys

    art_ch = next(c for c in chapters if c["chapter_key"] == "arts_crafts")
    assert "Art" in art_ch["chapter_subtitle"] or "Craftsmanship" in art_ch["chapter_subtitle"]
    assert "🎨" in art_ch["fact_badge"]

    music_ch = next(c for c in chapters if c["chapter_key"] == "music_entertainment")
    assert "Musical" in music_ch["chapter_subtitle"] or "Music" in music_ch["chapter_subtitle"]
    assert "🎵" in music_ch["fact_badge"]


def test_raw_story_metadata_extraction():
    """Confirms raw documentary story extracts title, synopsis, and 21 chapters."""
    story = build_raw_documentary_story(destination="Norway", channel_id="euro_discovery")
    assert story["destination_entity"] == "Norway"
    assert "Norway:" in story["title"]
    assert story["total_chapters"] == 21
    assert len(story["chapters"]) == 21
    assert "suno_prompt" in story["audio_master"]


def test_format_artifacts_models():
    """Validates strongly-typed decoupled artifact domain models for each format."""
    story_art = DocumentaryStoryArtifact(
        title="Iceland Documentary",
        destination_entity="Iceland",
        synopsis="Full 21-chapter exploration",
        total_chapters=21,
        chapters=[],
    )
    doc_art = DocumentaryArtifacts(
        episode_id="EP-001",
        channel_id="euro_discovery",
        title="Iceland Documentary",
        story=story_art,
    )
    assert doc_art.format == "documentary"
    assert doc_art.story.total_chapters == 21

    rel_art = RelaxationArtifacts(
        episode_id="EP-002",
        channel_id="earth_serenade",
        title="Alpine Sanctuary",
        storyboard={"theme": "alpine"},
    )
    assert rel_art.format == "relaxation"
    assert rel_art.storyboard["theme"] == "alpine"

    mv_art = MusicVideoArtifacts(
        episode_id="EP-003",
        channel_id="default_channel",
        title="Dance Track",
    )
    assert mv_art.format == "music_video"


def test_api_documentary_create_episode_auto_story():
    """Verifies POST /api/documentary/create-episode auto-generates 21 chapters and metadata."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)
    res = client.post(
        "/api/documentary/create-episode",
        json={"channel_id": "euro_discovery", "destination": "Switzerland", "user_id": "test_user_krishna"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["destination_entity"] == "Switzerland"
    assert data["total_chapters"] == 21
    assert "Switzerland:" in data["title"]
    assert len(data["story"]["chapters"]) == 21
    # Check that art and music/entertainment are present
    keys = [c["chapter_key"] for c in data["story"]["chapters"]]
    assert "arts_crafts" in keys
    assert "music_entertainment" in keys


def test_api_relaxation_create_episode():
    """Verifies POST /api/relaxation/create-episode initializes independent relaxation artifacts."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)
    res = client.post(
        "/api/relaxation/create-episode",
        json={"channel_id": "earth_serenade", "genre": "relax/nature", "archetype": "alpine_streams"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["format"] == "relaxation"
    assert data["archetype"] == "alpine_streams"


def test_api_documentary_produce_stage1_and_poll_artifacts():
    """Verifies POST /api/documentary/produce generates Stage 1 Raw Story without screenplay and poll-artifacts returns it."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)
    # Produce stage 1
    res = client.post(
        "/api/documentary/produce",
        json={
            "channel_id": "euro_discovery",
            "episode_id": "EP-999",
            "production_name": "Iceland",
            "prompt": "Discover Iceland",
            "format": "documentary",
            "format_slug": "documentary",
            "script_only": True,
            "user_id": "test_doc_poll_user",
        }
    )
    assert res.status_code == 200
    p_data = res.json()
    assert p_data["success"] is True
    assert p_data["story"] is not None
    assert p_data["script"] is None
    assert p_data["current_stage"] == 1

    # Poll artifacts
    poll_res = client.get(
        "/api/documentary/poll-artifacts?channel_id=euro_discovery&episode_id=EP-999&production_name=Iceland&user_id=test_doc_poll_user"
    )
    assert poll_res.status_code == 200
    poll_data = poll_res.json()
    assert poll_data["format"] == "documentary"
    assert poll_data["story"] is not None
    assert len(poll_data["story"]["chapters"]) == 21

