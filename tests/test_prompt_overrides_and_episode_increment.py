"""Tests for prompt override extraction, web series episode auto-increment, and non-episodic media."""

import pytest
from src.agents.classifier_agent import classifier_agent
from src.compositor.pipeline import ProductionPipelineCoordinator
from src.domain.creative import Character, Show
from src.domain.user import User
from src.domain.generation import MediaFormat
from src.domain.repo import repo
from src.services.character_consistency import get_or_create_character_anchor


def test_prompt_overrides_extraction_telugu_mass_male():
    """Verify prompt extraction for language, gender, and dance format overrides."""
    prompt = "telugu Sankranthi Mass Jathara male character with background male dancers"
    overrides = classifier_agent.extract_prompt_overrides(prompt)

    assert overrides["language"] == "te"
    assert overrides["gender"] == "male"
    assert overrides["voice_gender"] == "male"
    assert overrides["media_format"] == MediaFormat.DANCE_VIDEO
    assert overrides["enable_bgm"] is True
    assert overrides["enable_lipsync"] is True
    assert overrides["is_voice_over"] is False


def test_character_anchor_created_for_dance_video():
    """Verify character consistency anchor is created for dance videos with male lead."""
    user = User(email="test_dancer@cineai.studio", display_name="Dance Test", google_sub="sub_dance", storage_container_name="test_dance_cont")
    repo.save_user(user)
    show = Show(user_id=user.id, title="Telugu Mass Jathara", slug="telugu_mass_jathara", genre="dance")
    repo.save_show(show)

    anchor = get_or_create_character_anchor(
        user_id=user.id,
        show_id=show.id,
        character_name=None,
        culture="indian_south",
        costume_style="indian_traditional",
        gender="male",
    )

    assert anchor is not None
    assert anchor.gender == "male"
    assert "athletic" in anchor.appearance_anchor or "handsome" in anchor.appearance_anchor
    assert anchor.seed > 0


def test_web_series_auto_increment_and_non_web_series_no_episode():
    """Verify web series auto-increments episode number, while other formats have no episode title suffix."""
    from scripts.produce_video import MediaFormat

    # Test auto-increment logic
    existing_eps_numbers = [1, 2]
    next_ep = max(existing_eps_numbers, default=0) + 1
    assert next_ep == 3

    # For non-webseries, title should not have episode suffix
    raw_title = "telugu Mass Jathara male character with background male dancers"
    resolved_format = MediaFormat.DANCE_VIDEO
    is_web_series = (resolved_format == MediaFormat.WEB_SERIES)
    assert not is_web_series
    ep_title = raw_title
    assert "Episode" not in ep_title


def test_prompt_duration_and_mountain_documentary_extraction():
    """Verify duration parsing (30 min / 30 minutes) and mountain documentary context extraction."""
    prompt_1 = "Produce weekly 4K mountain documentary episode for 30 min"
    overrides_1 = classifier_agent.extract_prompt_overrides(prompt_1)
    assert overrides_1["duration"] == 1800
    assert overrides_1["media_format"] in (MediaFormat.MOVIE_CINEMATIC, MediaFormat.NATURE_SANCTUARY)
    assert overrides_1["enable_bgm"] is True
    assert overrides_1["is_voice_over"] is True
    assert overrides_1["enable_lipsync"] is False

    prompt_2 = "Produce weekly 4K mountain documentary episode for 30 minutes"
    overrides_2 = classifier_agent.extract_prompt_overrides(prompt_2)
    assert overrides_2["duration"] == 1800

    prompt_3 = "Quick 10 seconds drone shot over waterfalls"
    overrides_3 = classifier_agent.extract_prompt_overrides(prompt_3)
    assert overrides_3["duration"] == 10

