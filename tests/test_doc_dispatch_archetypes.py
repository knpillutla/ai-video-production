"""Test that documentary dispatch passes archetype-aware default themes when prompt is empty."""
import pytest
from unittest.mock import AsyncMock, patch
from src.studios.director_dispatcher import dispatch_studio_director
from src.studios.documentary_studio.doc_templates import DocStoryboard, DocGenre, DocScene


@pytest.mark.asyncio
async def test_doc_dispatch_uses_archetype_theme_when_prompt_empty():
    mock_sb = DocStoryboard(
        title="Ancient Civilizations Test",
        genre=DocGenre.ANCIENT_STRUCTURES,
        total_duration=60.0,
        scenes=[
            DocScene(
                scene_index=1,
                duration_seconds=12.0,
                shot_type="wide_panoramic_picturesque",
                motion_domain="landscape_solid",
                recommended_model="hunyuan",
                visual_prompt="Ancient stone temples",
                motion_prompt="Slow glide",
                narration_text="Ancient engineering at work.",
            )
        ],
    )

    with patch(
        "src.studios.documentary_studio.doc_storyboard.generate_documentary_storyboard_gemini",
        new=AsyncMock(return_value=mock_sb),
    ) as mock_gen:
        res = await dispatch_studio_director(
            genre="documentary",
            primary_archetype="ancient_civilizations_history",
            custom_prompt="",
            duration_seconds=60.0,
        )

        assert mock_gen.called
        call_kwargs = mock_gen.call_args.kwargs
        assert call_kwargs["genre"] == DocGenre.ANCIENT_STRUCTURES
        assert "Ancient Civilizations" in call_kwargs["theme_seed"]
        assert "Swiss Alps" not in call_kwargs["theme_seed"]
        assert res.primary_archetype == "ancient_civilizations_history"
        assert res.sub_genre == "ancient_civilizations_history"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sub_genre,archetype,expected_keyword",
    [
        ("science_space", "deep_space_webb", "James Webb"),
        ("science_earth", "deep_ocean_abyss", "Mariana Trench"),
        ("science_medicine", "neuroscience_brain_connectome", "Connectome"),
        ("science_physics", "quantum_superposition", "Quantum Superposition"),
        ("science_tech", "fusion_energy_tokamak", "Tokamak"),
        ("human_evolution", "hominin_origins_rift_valley", "Rift Valley Hominins"),
        ("human_evolution", "ice_age_neanderthals", "Neanderthals"),
    ],
)
async def test_science_genre_and_subgenres_dispatch_offline(sub_genre, archetype, expected_keyword):
    mock_sb = DocStoryboard(
        title="Science Test Storyboard",
        genre=DocGenre.SCIENCE,
        total_duration=60.0,
        scenes=[
            DocScene(
                scene_index=1,
                duration_seconds=12.0,
                shot_type="macro_extreme_close_up",
                motion_domain="cosmos_particle",
                recommended_model="wan",
                visual_prompt="Cosmic phenomenon",
                motion_prompt="Slow gravitational orbit",
                narration_text="Exploring the frontiers of science.",
            )
        ],
    )

    with patch(
        "src.studios.documentary_studio.doc_storyboard.generate_documentary_storyboard_gemini",
        new=AsyncMock(return_value=mock_sb),
    ) as mock_gen:
        res = await dispatch_studio_director(
            genre="science",
            primary_archetype=archetype,
            sub_genre=sub_genre,
            custom_prompt="",
            duration_seconds=60.0,
        )

        assert mock_gen.called
        call_kwargs = mock_gen.call_args.kwargs
        assert call_kwargs["genre"] == DocGenre.SCIENCE
        assert expected_keyword in call_kwargs["theme_seed"]
        assert res.genre == "science"
        assert res.cluster == "science"
        assert res.sub_genre == sub_genre
        assert res.primary_archetype == archetype


@pytest.mark.asyncio
async def test_rain_retreat_village_hut_dispatch_offline():
    from src.studios.rain_retreat.rain_prompt import build_rain_prompt

    prompt = build_rain_prompt(
        custom_prompt="",
        duration_seconds=60.0,
        num_shots=1,
        sub_genre="tropical_village_rain",
        primary_archetype="bamboo_hut_veranda",
    )
    assert "bamboo" in prompt.lower()
    assert "eaves" in prompt.lower()
    assert "Tropical Village" in prompt


@pytest.mark.asyncio
async def test_rain_dispatched_even_if_genre_defaulted_to_ocean(monkeypatch):
    from unittest.mock import AsyncMock
    from src.studios.director_dispatcher import dispatch_studio_director

    mock_rain = AsyncMock(return_value={"director": "rain"})
    monkeypatch.setattr("src.studios.director_dispatcher.generate_rain_screenplay", mock_rain)

    # User left genre on relax/ocean, but typed "Beautiful Rain in a village"
    res = await dispatch_studio_director(
        genre="relax/ocean",
        sub_genre="ocean_daytime_shore",
        primary_archetype="ocean_daytime_shore",
        channel_id="nature_rhythms",
        custom_prompt="Beautiful Rain in a village",
    )
    assert mock_rain.called
    assert res == {"director": "rain"}
