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


def test_doc_nations_deduplication_via_topic_memory():
    with patch("src.services.topic_memory.topic_memory.get_recent_topics", return_value=["Poland", "Czech Republic"]):
        _, _, theme = resolve_autonomous_geo_theme(
            sub_genre="europe_nations",
            archetype="great_cities_metropolises",
            custom_prompt="",
        )
        assert "Poland" not in theme
        assert "Czech Republic" not in theme
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
