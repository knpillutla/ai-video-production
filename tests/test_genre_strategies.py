"""Tests for Genre Strategy Pattern and Universal Scene Intelligence."""

import pytest
from src.agents.classifier_agent import classifier_agent
from src.compositor.genre_strategies import resolve_strategy
from src.domain.generation import MediaFormat
from src.services.cultural_derivation import derive_cultural_context


def test_strategy_resolution_all_genres():
    """Verify that all standard formats resolve to their respective strategies."""
    dance = resolve_strategy("dance_video")
    assert dance.genre_id == "dance"
    assert dance.audio_mode == "song"
    assert dance.lipsync_mode == "musical"
    assert dance.default_fps == 30

    nature = resolve_strategy("nature_documentary")
    assert nature.genre_id == "nature_documentary"
    assert nature.audio_mode == "narration"
    assert nature.default_fps == 24

    walking = resolve_strategy("walking_tour")
    assert walking.genre_id == "walking_tour"
    assert walking.default_fps == 60

    comedy = resolve_strategy("comedy")
    assert comedy.genre_id == "comedy"
    assert comedy.default_fps == 24

    epic = resolve_strategy("epic_cinematic")
    assert epic.genre_id == "epic_cinematic"
    assert epic.default_fps == 24

    survival = resolve_strategy("mountain_survival")
    assert survival.genre_id == "mountain_survival"
    assert survival.default_fps == 24


def test_strategy_keyword_fallback():
    """Verify fallback by keyword matching when format is not an exact match."""
    strat = resolve_strategy("custom_format", genre="folk", idea="high energy village dance")
    assert strat.genre_id == "dance"

    strat2 = resolve_strategy("unknown_format", genre="documentary", idea="subzero blizzard mountain survival")
    assert strat2.genre_id == "mountain_survival"

    strat3 = resolve_strategy("custom", genre="nature", idea="wildlife safari in serengeti")
    assert strat3.genre_id == "nature_documentary"


def test_strategy_prompt_and_schema():
    """Verify each strategy generates valid prompts and schemas."""
    for genre_id in ["dance_video", "nature_documentary", "walking_tour", "comedy", "epic_cinematic", "mountain_survival"]:
        strat = resolve_strategy(genre_id)
        prompt = strat.build_gemini_prompt("Test Title", 60, "en", "general", "An exciting video", None, None)
        assert len(prompt) > 50
        schema = strat.build_gemini_schema()
        assert schema.get("type") == "OBJECT"
        assert "scenes" in schema.get("properties", {})


def test_strategy_sanity_check_validation():
    """Verify lightweight sanity checking without rigid contract exceptions."""
    strat = resolve_strategy("comedy")
    valid_sb = {
        "characters": [{"name": "Lead"}],
        "scenes": [{"scene_index": 0, "duration_seconds": 5.0, "visual_prompt": "Office scene", "dialogue": [{"text": "Hello"}]}],
    }
    assert strat.validate_storyboard(valid_sb) == []

    empty_sb = {}
    issues = strat.validate_storyboard(empty_sb)
    assert len(issues) > 0


def test_universal_cultural_and_scene_derivation():
    """Verify deterministic scene intelligence derivation across different genres."""
    ctx_dance = derive_cultural_context(
        script_text="Telangana village jathara teenmaar mass dance celebration",
        genre="bollywood_dance",
    )
    assert ctx_dance.culture == "indian_south"
    assert ctx_dance.setting_type == "village_rural"
    assert "dholak" in ctx_dance.props_instruments
    assert ctx_dance.social_context == "festive_crowd"

    ctx_alpine = derive_cultural_context(
        script_text="Alpine snow hiking in Norway peaks",
        genre="walking_tour",
    )
    assert ctx_alpine.setting_type == "alpine_wilderness"
    assert ctx_alpine.weather_climate == "snowy_subzero"
    assert "walking stick" in ctx_alpine.props_instruments
    assert ctx_alpine.social_context == "solo_walk"

    ctx_palace = derive_cultural_context(
        script_text="Ancient royal dynasty battle in monumental palace fort",
        genre="epic_action",
    )
    assert ctx_palace.setting_type == "historical_palace"
    assert ctx_palace.time_period == "ancient_mythological"


def test_classifier_agent_new_media_formats():
    """Verify that classifier agent recognizes new media formats."""
    epic_det = classifier_agent.detect("Epic monumental Bahubali style cinematic battle with VFX")
    assert epic_det.media_format == MediaFormat.EPIC_CINEMATIC

    survival_det = classifier_agent.detect("Subzero blizzard extreme weather mountain survival with shepherds in Pamir")
    assert survival_det.media_format == MediaFormat.MOUNTAIN_SURVIVAL


def test_all_user_enterprise_prompts_resolve_correct_strategy():
    """Verify that every real user prompt example resolves to the exact right format and strategy."""
    test_cases = [
        ("norway walking tour", MediaFormat.WALKING_TOUR, "walking_tour"),
        ("milan walking tour", MediaFormat.WALKING_TOUR, "walking_tour"),
        ("Newyork Tourist attractions", MediaFormat.TRAVEL_GUIDE, "tourist_guide"),
        ("Paris in 3 days", MediaFormat.TRAVEL_GUIDE, "tourist_guide"),
        ("top attractions in London", MediaFormat.TRAVEL_GUIDE, "tourist_guide"),
        ("beautiful norway", MediaFormat.NATURE_SANCTUARY, "nature_documentary"),
        ("amazon rain forest", MediaFormat.NATURE_SANCTUARY, "nature_documentary"),
        ("telugu mass dance song", MediaFormat.DANCE_VIDEO, "dance"),
        ("hindi music video", MediaFormat.MUSIC_VIDEO, "music_video"),
        ("war for a kingdom in uk", MediaFormat.MOVIE_CINEMATIC, "epic_cinematic"),
        ("Yodha - the protector", MediaFormat.MOVIE_CINEMATIC, "epic_cinematic"),
    ]
    for prompt_text, expected_format, expected_strategy_id in test_cases:
        det = classifier_agent.detect(prompt_text)
        assert det.media_format == expected_format, f"Prompt '{prompt_text}' got {det.media_format}, expected {expected_format}"
        strat = resolve_strategy(media_format=det.media_format.value, genre=det.theme.value, idea=prompt_text)
        assert strat.genre_id == expected_strategy_id, f"Prompt '{prompt_text}' got strategy {strat.genre_id}, expected {expected_strategy_id}"

