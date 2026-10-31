"""Unit tests for documentary country folder creation, inputs generation, and zero-fallback policy."""
import pytest
from unittest.mock import patch
from src.studios.documentary_studio.doc_geo_rotation import is_known_geo_entity, resolve_autonomous_geo_details
from src.studios.documentary_studio.doc_story_service import (
    build_raw_documentary_story,
    generate_gemini_documentary_story,
)


def test_is_known_geo_entity():
    """Verify that is_known_geo_entity accurately identifies real geographic locations."""
    assert is_known_geo_entity("Slovenia") is True
    assert is_known_geo_entity("Poland") is True
    assert is_known_geo_entity("Rome") is True
    assert is_known_geo_entity("Vienna") is True
    assert is_known_geo_entity("Scenic Nature Sanctuary") is False
    assert is_known_geo_entity("standalone") is False
    assert is_known_geo_entity("") is False


def test_resolve_autonomous_geo_details_with_theme_prompt():
    """Verify that when given a descriptive theme prompt, it selects a real sovereign nation."""
    _, eff_arch, theme_title, entity = resolve_autonomous_geo_details(
        sub_genre="europe_nations",
        archetype="country_overview",
        custom_prompt="Scenic Nature Sanctuary",
    )
    assert eff_arch in ("country_overview", "countries")
    assert is_known_geo_entity(entity) is True
    assert entity != "Scenic Nature Sanctuary"


def test_live_zero_fallback_policy_raises_on_missing_key():
    """Verify that in live mode (mock mode disabled), missing API key raises RuntimeError immediately."""
    with patch("src.providers.base.is_mock_mode", return_value=False):
        with patch("src.providers.llm.gemini_adapter.get_live_gemini_api_key", return_value=None):
            with pytest.raises(RuntimeError, match="Google Gemini API key is missing or not configured"):
                generate_gemini_documentary_story(
                    destination="Slovenia",
                    genre="doc/nations",
                    sub_genre="europe_nations",
                    archetype="country_overview",
                )


def test_live_zero_fallback_policy_raises_in_build_raw_story():
    """Verify that build_raw_documentary_story raises RuntimeError in live mode if Gemini fails."""
    with patch("src.providers.base.is_mock_mode", return_value=False):
        with patch("src.studios.documentary_studio.doc_story_service.generate_gemini_documentary_story", return_value=None):
            with pytest.raises(RuntimeError, match="Live Gemini documentary story generation failed"):
                build_raw_documentary_story(
                    destination="Slovenia",
                    genre="doc/nations",
                    sub_genre="europe_nations",
                    archetype="country_overview",
                )


def test_mock_mode_deterministic_story_generation():
    """Verify that in test/mock mode, offline deterministic story is returned for test safety."""
    with patch("src.providers.base.is_mock_mode", return_value=True):
        story = build_raw_documentary_story(
            destination="Slovenia",
            genre="doc/nations",
            sub_genre="europe_nations",
            archetype="country_overview",
        )
        assert story["destination_entity"] == "Slovenia"
        assert len(story["chapters"]) == 22
        assert story["gemini_story_inputs"]["model"] == "offline_deterministic_mock"


def test_scan_documentary_artifacts_syncs_pipeline_state_stages(tmp_path):
    """Verify that scan_documentary_artifacts ensures all pipeline stages are reflected in pipeline_state.json."""
    import json
    from src.studios.documentary_studio.doc_artifact_scanner import scan_documentary_artifacts
    from src.core.storage import storage_service

    ep_dir = tmp_path / "user-test" / "networks" / "test_channel" / "documentary" / "sweden" / "ep-001"
    ep_dir.mkdir(parents=True)
    (ep_dir / "raw_gemini_story.json").write_text(json.dumps({"title": "Sweden Test", "chapters": [{"title": "Ch 1"}]}))
    (ep_dir / "pipeline_state.json").write_text(json.dumps({"current_stage": 1, "stages_completed": {}}))

    with patch.object(storage_service, "root_dir", tmp_path):
        res = scan_documentary_artifacts(
            channel_id="test_channel",
            episode_id="ep-001",
            format="documentary",
            production_name="sweden",
            user_id="user-test",
        )

        pipe_state = res["pipeline_state"]
        stages = pipe_state["stages_completed"]
        for expected_stage in ["story", "narration", "screenplay", "keyframes", "bgm", "motion", "master", "short", "packaging"]:
            assert expected_stage in stages

        assert stages["story"] is True
        assert stages["narration"] is False
        assert stages["screenplay"] is False

        # Add narration file and rescan
        (ep_dir / "spoken_narration.mp3").write_bytes(b"0" * 2000)
        res2 = scan_documentary_artifacts(
            channel_id="test_channel",
            episode_id="ep-001",
            format="documentary",
            production_name="sweden",
            user_id="user-test",
        )
        assert res2["pipeline_state"]["stages_completed"]["narration"] is True



def test_network_episodes_scanner_detects_documentary_format(tmp_path):
    """Verify that network_episodes_scanner sets format and format_slug to documentary."""
    import json
    from src.api.routes.network_episodes_scanner import scan_all_channel_episodes

    ep_dir = tmp_path / "user-test" / "networks" / "euro_discovery" / "documentary" / "switzerland" / "ep-001"
    ep_dir.mkdir(parents=True)
    (ep_dir / "raw_gemini_story.json").write_text(json.dumps({
        "title": "Switzerland Documentary",
        "destination_entity": "Switzerland",
        "chapters": [{"chapter_index": 1, "chapter_title": "Prologue", "narration": "Switzerland test"}]
    }))
    (ep_dir / "user_inputs.json").write_text(json.dumps({
        "prompt": "Switzerland",
        "production_name": "Switzerland",
        "genre": "doc/nations",
        "channel_id": "euro_discovery",
        "episode_id": "EP-001",
        "format": "documentary",
        "format_slug": "documentary",
    }))

    episodes = scan_all_channel_episodes(tmp_path, user_id="user-test")
    assert len(episodes) == 1
    assert episodes[0]["format"] == "documentary"
    assert episodes[0]["format_slug"] == "documentary"
    assert episodes[0]["title"] == "Switzerland Documentary"
    assert episodes[0]["story"] is not None
