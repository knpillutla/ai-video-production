"""Deterministic offline tests for Nations & Civilizations (doc/nations) Studio Dispatch & Geo Rotation."""
import pytest
from unittest.mock import AsyncMock, patch

from src.studios.director_dispatcher import dispatch_studio_director
from src.studios.documentary_studio.doc_templates import DocStoryboard, DocGenre, DocScene
from src.studios.documentary_studio.doc_geo_rotation import (
    resolve_autonomous_geo_theme,
    is_geo_continent_subgenre,
    CONTINENT_COUNTRIES_MAP,
    ARCHETYPE_TEMPLATES,
)
from src.studios.documentary_studio.doc_dispatch_helper import resolve_doc_dispatch_params


def test_is_geo_continent_subgenre():
    assert is_geo_continent_subgenre("europe_nations") is True
    assert is_geo_continent_subgenre("asia_nations") is True
    assert is_geo_continent_subgenre("africa_nations") is True
    assert is_geo_continent_subgenre("americas_nations") is True
    assert is_geo_continent_subgenre("oceania_nations") is True
    assert is_geo_continent_subgenre("nordic_polar_nations") is True
    assert is_geo_continent_subgenre("europe_countries") is True
    assert is_geo_continent_subgenre("ocean_daytime_shore") is False


def test_doc_nations_zero_prompt_autonomous_resolution():
    eff_genre, eff_arch, theme = resolve_autonomous_geo_theme(
        sub_genre="europe_nations",
        archetype="spiritual_sanctuaries",
        custom_prompt="",
    )
    assert eff_genre == DocGenre.ANCIENT_STRUCTURES
    assert eff_arch == "spiritual_sanctuaries"
    assert any(c in theme for c in CONTINENT_COUNTRIES_MAP["europe_nations"])
    assert "Sanctuaries" in theme or "Shrines" in theme or "Temples" in theme


def test_doc_nations_deduplication_via_topic_memory(tmp_path):
    with patch("src.studios.documentary_studio.doc_geo_cache.get_geo_cache_path", return_value=tmp_path / "cache.json"), \
         patch("src.services.topic_memory.topic_memory.get_recent_topics", return_value=["Poland", "Czech Republic"]):
        _, _, theme = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="great_cities_metropolises",
            custom_prompt="",
        )
        assert "Poland" not in theme and "Czech Republic" not in theme
        assert "Austria" in theme or "Italy" in theme or any(c in theme for c in CONTINENT_COUNTRIES_MAP["europe_nations"][2:])


def test_doc_nations_custom_prompt_respected():
    eff_genre, eff_arch, theme = resolve_autonomous_geo_theme(
        sub_genre="asia_nations",
        archetype="culinary_gastronomic_heritage",
        custom_prompt="Artisan Ramen Alchemy of Tokyo Outer Markets",
    )
    assert eff_genre == DocGenre.PLACES
    assert eff_arch == "culinary_gastronomic_heritage"
    assert theme == "Artisan Ramen Alchemy of Tokyo Outer Markets"


@pytest.mark.asyncio
async def test_doc_nations_dispatcher_routing_offline():
    mock_sb = DocStoryboard(
        title="Nations Test Storyboard",
        genre=DocGenre.ANCIENT_STRUCTURES,
        total_duration=60.0,
        scenes=[
            DocScene(
                scene_index=1,
                duration_seconds=12.0,
                shot_type="wide_panoramic_picturesque",
                motion_domain="landscape_solid",
                recommended_model="kling_v3",
                visual_prompt="Historic fortress ramparts at golden dawn",
                motion_prompt="Slow forward drone glide",
                narration_text="Rising above the mist, these stone walls witnessed centuries of imperial glory.",
            )
        ],
    )

    with patch(
        "src.studios.documentary_studio.doc_storyboard.generate_documentary_storyboard_gemini",
        new=AsyncMock(return_value=mock_sb),
    ) as mock_gen:
        res = await dispatch_studio_director(
            genre="doc/nations",
            sub_genre="asia_nations",
            primary_archetype="ancient_history_dynasties",
            custom_prompt="",
            duration_seconds=60.0,
        )

        assert mock_gen.called
        call_kwargs = mock_gen.call_args.kwargs
        assert call_kwargs["genre"] == DocGenre.ANCIENT_STRUCTURES
        assert "Chronicles" in call_kwargs["theme_seed"] or "Dynasties" in call_kwargs["theme_seed"] or "History" in call_kwargs["theme_seed"]
        assert res.primary_archetype == "ancient_history_dynasties"


def test_doc_nations_regions_and_cultures_archetypes():
    # Test Geographic Regions archetype
    eff_genre1, eff_arch1, theme1 = resolve_autonomous_geo_theme(
        sub_genre="americas_nations",
        archetype="geographic_regions_zones",
        custom_prompt="",
    )
    assert eff_genre1 == DocGenre.PLACES
    assert eff_arch1 == "geographic_regions_zones"
    assert "Region" in theme1 or "Territories" in theme1

    # Test Cultural Mosaic archetype
    eff_genre2, eff_arch2, theme2 = resolve_autonomous_geo_theme(
        sub_genre="asia_nations",
        archetype="cultural_mosaic_traditions",
        custom_prompt="",
    )
    assert eff_genre2 == DocGenre.PLACES
    assert eff_arch2 == "cultural_mosaic_traditions"
    assert "Cultural Mosaic" in theme2 or "Cultural Tapestry" in theme2


def test_doc_countries_rotation_and_cache_exclusion(tmp_path):
    test_cache_file = tmp_path / "geo_rotation_cache.json"
    with patch("src.studios.documentary_studio.doc_geo_cache.get_geo_cache_path", return_value=test_cache_file), \
         patch("src.services.topic_memory.topic_memory.get_recent_topics", return_value=[]):
        # 1st execution: Poland
        eff_genre1, eff_arch1, theme1 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="countries",
            custom_prompt="",
        )
        assert eff_genre1 == DocGenre.PLACES
        assert eff_arch1 == "countries"
        assert "Poland" in theme1
        assert "Iconic Wonders" in theme1 or "Attractions" in theme1 or "Historic Squares" in theme1

        # 2nd execution: Poland MUST be excluded, picks Czech Republic
        eff_genre2, eff_arch2, theme2 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="countries",
            custom_prompt="",
        )
        assert "Poland" not in theme2
        assert "Czech Republic" in theme2

        # 3rd execution: Poland & Czech Republic excluded, picks Austria
        eff_genre3, eff_arch3, theme3 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="countries",
            custom_prompt="",
        )
        assert "Poland" not in theme3
        assert "Czech Republic" not in theme3
        assert "Austria" in theme3


def test_doc_cities_rotation_and_cache_exclusion(tmp_path):
    test_cache_file = tmp_path / "geo_rotation_cache.json"
    with patch("src.studios.documentary_studio.doc_geo_cache.get_geo_cache_path", return_value=test_cache_file):
        # 1st execution: Rome
        eff_genre1, eff_arch1, theme1 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="",
        )
        assert eff_genre1 == DocGenre.PLACES
        assert eff_arch1 == "cities"
        assert "Rome" in theme1
        assert "Historic Squares" in theme1 or "Luminaries" in theme1 or "Attractions" in theme1

        # 2nd execution: Rome MUST be excluded, picks Paris
        eff_genre2, eff_arch2, theme2 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="",
        )
        assert "Rome" not in theme2
        assert "Paris" in theme2

        # 3rd execution: Rome & Paris excluded, picks Vienna
        eff_genre3, eff_arch3, theme3 = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="",
        )
        assert "Rome" not in theme3
        assert "Paris" not in theme3
        assert "Vienna" in theme3


def test_doc_cities_custom_prompt_respected_and_cached(tmp_path):
    test_cache_file = tmp_path / "geo_rotation_cache.json"
    with patch("src.studios.documentary_studio.doc_geo_cache.get_geo_cache_path", return_value=test_cache_file):
        eff_genre, eff_arch, theme = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="Gothic Quarters & Gaudi Marvels of Barcelona",
        )
        assert eff_genre == DocGenre.PLACES
        assert eff_arch == "cities"
        assert theme == "Gothic Quarters & Gaudi Marvels of Barcelona"

        # Subsequent autonomous run: Barcelona is in cache, so next unvisited (Rome) is picked
        _, _, next_theme = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="",
        )
        assert "Rome" in next_theme


def test_doc_geo_episode_production_naming_and_folder_path(tmp_path):
    """Verify that when archetype is cities/countries, production_name resolves to city/country and ep_dir uses that name."""
    import re
    from src.studios.documentary_studio.doc_geo_rotation import resolve_autonomous_geo_entity
    test_cache_file = tmp_path / "geo_rotation_cache.json"
    with patch("src.studios.documentary_studio.doc_geo_cache.get_geo_cache_path", return_value=test_cache_file):
        city = resolve_autonomous_geo_entity(
            sub_genre="europe_nations",
            archetype="cities",
            custom_prompt="",
        )
        assert city in ("Rome", "Paris", "Barcelona", "Vienna", "Prague")
        clean_prod = re.sub(r"[^a-zA-Z0-9_-]", "_", city.lower()).strip("_")
        assert clean_prod != "nations_of_europe"
        assert clean_prod == city.lower()


def test_doc_prompt_scene1_welcome_hook_and_no_summary_slide():
    """Verify prompt mandates Scene 1 Welcome Hook (10-12s Ken Burns) and bans outro summary slides."""
    from src.studios.documentary_studio.doc_directorial_prompt import build_doc_directorial_prompt
    prompt = build_doc_directorial_prompt(
        genre="documentary",
        archetype="countries",
        custom_prompt="Poland: Royal Castles & Living Heritage",
        duration_seconds=60.0,
        num_shots=6,
    )
    assert "MANDATORY SCENE 1 WELCOME HOOK & ROADMAP DIRECTIVE" in prompt
    assert "10.0 to 12.0 seconds" in prompt
    assert 'Welcome to [Destination Name]...' in prompt
    assert "STRICT BAN ON OUTRO INFOGRAPHIC SUMMARY CARDS & RECAP SLIDES" in prompt


@pytest.mark.asyncio
async def test_doc_storyboard_enforces_scene1_welcome_hook_and_filters_summary_card():
    """Verify doc_storyboard enforces 10-12s Ken Burns Welcome hook on Scene 1 and filters out summary slides."""
    from unittest.mock import AsyncMock
    from src.studios.documentary_studio.doc_storyboard import generate_documentary_storyboard_gemini, DocGenre
    mock_payload = {
        "title": "Poland: Living Heritage & Royal Castles",
        "destination_entity": "Poland",
        "destination_category": "country",
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "wide",
                "duration_seconds": 6.0,
                "motion_type": "ai_diffusion",
                "visual_prompt": "Warsaw Castle Square with Sigismund Column under daylight.",
                "narration_text": "A nation of deep resilience and architectural splendor.",
            },
            {
                "scene_index": 2,
                "shot_type": "medium",
                "duration_seconds": 8.0,
                "motion_type": "ken_burns",
                "visual_prompt": "Wawel Castle in Krakow.",
                "narration_text": "Krakow stands as the ancient royal soul of Poland.",
            },
            {
                "scene_index": 3,
                "shot_type": "itinerary_summary_card",
                "location_hub": "Master Summary Recap",
                "duration_seconds": 8.0,
                "is_itinerary_summary": True,
                "visual_prompt": "Infographic summary card table with schedule.",
                "narration_text": "Here is the summary of your itinerary.",
            },
        ],
    }
    with patch("src.providers.llm.gemini_adapter.GeminiLLMAdapter.generate_structured", new_callable=AsyncMock) as m_call:
        m_call.return_value = mock_payload
        sb = await generate_documentary_storyboard_gemini(
            genre=DocGenre.PLACES,
            theme_seed="Poland exploration",
            duration_seconds=60.0,
            num_shots=3,
            archetype="countries",
        )
        assert len(sb.scenes) == 2  # Scene 3 summary card must be filtered out!
        s1 = sb.scenes[0]
        assert 10.0 <= s1.duration_seconds <= 12.0 and s1.motion_type == "ken_burns"
        assert s1.recommended_model == "local_drone" and s1.narration_text.startswith("Welcome to Poland")
        s2 = sb.scenes[1]  # Conclusion scene
        assert 10.0 <= s2.duration_seconds <= 12.0 and s2.motion_type == "ken_burns" and s2.camera_movement == "dollyout"
        assert ("twilight" in s2.visual_prompt.lower() or "sunset" in s2.visual_prompt.lower())
        assert not any(getattr(sc, "is_itinerary_summary", False) for sc in sb.scenes)
