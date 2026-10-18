"""Unit tests for Multilingual Music Video Director Agent."""

import pytest
from src.studios.music_video_studio.music_video_director import (
    generate_music_video_screenplay,
    _convert_vocal_storyboard_to_screenplay,
    _build_offline_multilingual_storyboard,
)
from src.compositor.genre_strategies.vocal_strategy import vocal_gemini_schema


@pytest.mark.asyncio
async def test_music_video_director_offline_multilingual():
    """Verify music video director generates authentic multilingual screenplay offline without paid API calls."""
    test_cases = [
        ("India", "te", "south_indian"),
        ("India", "hi", "north_indian"),
        ("Japan", "ja", "japanese"),
        ("France", "fr", "french"),
        ("Spain", "es", "spanish"),
        ("South Korea", "ko", "korean"),
        ("United States", "en", "western"),
    ]

    for country, lang, culture in test_cases:
        sp = await generate_music_video_screenplay(
            genre="music/static_vocal",
            sub_genre="romantic_melody",
            primary_archetype="local_country_heritage",
            channel_id="test_channel",
            country=country,
            language=lang,
            culture=culture,
            duration_seconds=30.0,
            num_shots=1,
        )

        assert sp is not None
        assert sp.cluster == "music_video"
        assert sp.recommended_fps == 30  # Rule 14
        assert sp.audio_master is not None
        assert sp.audio_master.spoken_narration_script == ""  # Rule 15: Zero spoken voiceover
        assert sp.primary_language == lang
        assert sp.title != ""
        assert country.lower() in sp.story_topic.lower()
        assert len(sp.scenes) >= 1
        assert "4k" in sp.scenes[0].visual_prompt.lower()



def test_storyboard_schema_matching_produce_music():
    """Verify that the generated storyboard strictly satisfies the vocal_gemini_schema structure."""
    sb = _build_offline_multilingual_storyboard(
        genre="music/solo_singer",
        sub_genre="happy_uplifting",
        country="Japan",
        language="ja",
        culture="japanese",
        character_desc="Mid-20s graceful Japanese singer",
        custom_prompt="Sakura morning melody",
        duration_seconds=30.0,
        num_shots=2,
    )

    schema = vocal_gemini_schema()
    for req_field in schema["required"]:
        assert req_field in sb, f"Missing required produce music video field: {req_field}"

    assert sb["vocal_gender"] in ("female", "male", "duet")
    assert len(sb["scenes"]) == 2
    assert sb["language"] == "ja"
    assert sb["country"] == "Japan"
    assert sb["tempo_bpm"] == 100
    assert "youtube_metadata" in sb
    assert "prompts_by_model" in sb
    assert "flux_dev" in sb["prompts_by_model"]
    assert "z_image" in sb["prompts_by_model"]
    assert len(sb["lyrics_segments"]) >= 1
    assert "text" in sb["lyrics_segments"][0]
    assert "text_en" in sb["lyrics_segments"][0]
    assert "|" in sb["lyrics_segments"][0]["text_en"]  # Dual-line format: transliteration | English translation

    # Test conversion to pipeline RelaxScreenplay container
    screenplay = _convert_vocal_storyboard_to_screenplay(sb, genre="music/solo_singer", sub_genre="happy_uplifting", archetype="kyoto_bamboo_temple")
    assert screenplay.title == sb["title_en"]
    assert screenplay.primary_language == "ja"
    assert screenplay.recommended_fps == 30
    assert screenplay.audio_master.spoken_narration_script == ""
    assert len(screenplay.scenes) == 2

