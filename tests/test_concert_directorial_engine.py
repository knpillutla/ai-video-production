"""Unit tests for Time-Coded Directorial Screenplay Engine ($0.00 spend)."""

import pytest
from src.studios.concert_studio.concert_audio_slicer import AudioConcertSegment, slice_concert_audio
from src.studios.concert_studio.concert_directorial_engine import (
    build_timecoded_directorial_prompt,
    build_timecoded_directorial_schema,
    direct_concert_broadcast_timeline,
    direct_timecoded_timeline_deterministic,
)


def test_timecoded_directorial_prompt_building():
    segments = [
        AudioConcertSegment(1, 0.0, 5.29, 5.29, "ORCHESTRA", 0.45, False, "stadium_audience_crowd", "orbit_audience", "orbit_stage_to_audience"),
        AudioConcertSegment(2, 5.29, 10.58, 5.29, "VERSE_MODERATE", 0.85, True, "singer_orchestra_stage", "closeup", "zoom_in_singer"),
    ]
    prompt = build_timecoded_directorial_prompt(
        segments=segments,
        lyrics="Sample lyrics line",
        language="te",
        artist_name="Radha",
        instrument="mic",
        style="Carnatic Classical",
    )
    assert "You are the Grand Director" in prompt
    assert "Cut 01 [ 0.00s -  5.29s]" in prompt
    assert "ORCHESTRA ONLY" in prompt
    assert "VOCALS ACTIVE" in prompt
    assert "Radha" in prompt


def test_timecoded_directorial_schema():
    schema = build_timecoded_directorial_schema()
    assert schema["type"] == "OBJECT"
    assert "broadcast_timeline" in schema["properties"]
    assert "camera_id" in schema["properties"]["broadcast_timeline"]["items"]["properties"]
    assert "lip_sync" in schema["properties"]["broadcast_timeline"]["items"]["properties"]


def test_direct_timecoded_timeline_deterministic():
    segments = [
        AudioConcertSegment(1, 0.0, 5.29, 5.29, "ORCHESTRA", 0.45, False, "stadium_audience_crowd", "orbit_audience", "orbit_stage_to_audience"),
        AudioConcertSegment(2, 5.29, 10.58, 5.29, "ORCHESTRA", 0.48, False, "singer_orchestra_stage", "medium", "steady_eye_level"),
        AudioConcertSegment(3, 10.58, 15.87, 5.29, "VERSE_MODERATE", 0.88, True, "singer_orchestra_stage", "closeup", "zoom_in_singer"),
        AudioConcertSegment(4, 15.87, 21.16, 5.29, "CHORUS_INTENSE", 0.95, True, "singer_orchestra_stage", "closeup", "zoom_in_singer"),
        AudioConcertSegment(5, 21.16, 26.45, 5.29, "ORCHESTRA", 0.50, False, "overall_stage_vista", "wide_vista", "wide_stage_pullback"),
    ]
    cuts = direct_timecoded_timeline_deterministic(segments, lyrics="Verse 1\nChorus line")
    assert len(cuts) == 5

    # Verify Cut 1 is Orchestra: lip_sync must be False
    assert cuts[0]["is_singing"] is False
    assert cuts[0]["lip_sync"] is False

    # Verify Cut 3 is Singing on Cam 1: lip_sync must be True
    assert cuts[2]["is_singing"] is True
    assert cuts[2]["camera_id"] == "singer_orchestra_stage"
    assert cuts[2]["lip_sync"] is True

    # Verify Cut 5 is Orchestra Vista: lip_sync must be False
    assert cuts[4]["is_singing"] is False
    assert cuts[4]["lip_sync"] is False


@pytest.mark.asyncio
async def test_direct_concert_broadcast_timeline_offline():
    segments = [
        AudioConcertSegment(1, 0.0, 5.0, 5.0, "ORCHESTRA", 0.4, False, "stadium_audience_crowd", "orbit_audience", "orbit_stage_to_audience"),
        AudioConcertSegment(2, 5.0, 10.0, 5.0, "VERSE_MODERATE", 0.8, True, "singer_orchestra_stage", "closeup", "zoom_in_singer"),
    ]
    cuts = await direct_concert_broadcast_timeline(
        llm=None,
        segments=segments,
        lyrics="Sample lyrics",
        force_live=False,
    )
    assert len(cuts) == 2
    assert cuts[0]["duration_seconds"] == 5.0
    assert cuts[0]["lip_sync"] is False
    assert cuts[1]["lip_sync"] is True


def test_resolve_concert_workspace_via_user_inputs_without_storyboard(tmp_path):
    import json
    from uuid import uuid4
    from src.domain.user import User
    from src.studios.concert_studio.concert_workspace import resolve_concert_workspace

    test_ep_id = str(uuid4())
    user = User(email="test@example.com", display_name="Test User", google_sub="sub_123", storage_container_name="test_user")
    
    # Create workspace with user_inputs.json but NO storyboard.json
    ep_dir = tmp_path / "test_user" / "networks" / "telugu_rhythms" / "music_video" / "test_song" / "ep-001"
    ep_dir.mkdir(parents=True)
    (ep_dir / "user_inputs.json").write_text(json.dumps({
        "episode_id": test_ep_id,
        "title": "Test Song",
        "theme": "Classical Concert",
    }), encoding="utf-8")

    from unittest.mock import patch
    with patch("src.studios.concert_studio.concert_workspace.settings") as mock_settings:
        mock_settings.storage.local_storage_root = str(tmp_path)
        resolved_dir, ep = resolve_concert_workspace(test_ep_id, "telugu_rhythms", user, None)
        assert resolved_dir == ep_dir
        assert str(ep.id) == test_ep_id
        assert ep.title == "Test Song"

