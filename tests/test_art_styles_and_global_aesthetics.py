"""Unit and Integration Tests for Global Aesthetics, Art Styles, and Scenic Formats."""

import pytest
from uuid import uuid4
from src.mcp.model_selector.cultural_catalog import lookup_art_style, ART_STYLE_INTELLIGENCE_CATALOG
from src.mcp.model_selector.stack_resolver import resolve_production_stack, ScriptMetadata
from src.services.cultural_derivation import derive_cultural_context
from src.agents.script_agent import script_agent
from src.domain.generation import MediaFormat
from src.domain.creative import Episode, Show
from src.domain.user import User
from src.domain.repo import repo
from src.compositor.pipeline import pipeline_coordinator


def test_art_style_catalog_definitions():
    """Verify all 18 global art styles and aesthetics are present and fully configured."""
    expected_styles = [
        "swiss_alpine_rainy_village",
        "swiss_alpine_scenic_8k",
        "alpine_rainy_scenic_drive",
        "greek_cycladic_coastal",
        "italian_coastal_lake_como",
        "ibiza_luxury_sunset_lounge",
        "primeval_forest_sanctuary",
        "tropical_thailand_karst",
        "japanese_ukiyo_e",
        "cyberpunk_neo_tokyo",
        "french_impressionism",
        "italian_baroque_chiaroscuro",
        "korean_kpop_cyber_glam",
        "african_afrofuturism",
        "mexican_muralism_magical_realism",
        "nordic_noir_minimalism",
        "indian_mughal_miniature",
        "retro_80s_synthwave",
        "photorealistic_cinematic",
    ]
    for key in expected_styles:
        assert key in ART_STYLE_INTELLIGENCE_CATALOG
        style = ART_STYLE_INTELLIGENCE_CATALOG[key]
        assert "display_name" in style
        assert "lighting_scheme" in style
        assert "color_palette" in style
        assert "directorial_guidance" in style
        assert "prompt_decorations" in style


def test_art_style_lookup_matching():
    """Verify smart matching by keywords, countries, and style queries."""
    # Reference Video 1: Lauterbrunnen Rain Walk
    swiss_rain = lookup_art_style("lauterbrunnen walking tour")
    assert swiss_rain["display_name"] == "Swiss Alpine Rainy Village & Walking Tour"
    assert "Lauterbrunnen" in swiss_rain["prompt_decorations"]

    # Reference Video 2: Grindelwald 8K Nature
    swiss_8k = lookup_art_style("grindelwald alpine wonderland")
    assert swiss_8k["display_name"] == "Swiss Alpine Grindelwald 8K Scenic Nature"

    # Reference Video 3: Alpine Scenic Drive (Innsbruck to Tegernsee)
    drive = lookup_art_style("innsbruck to tegernsee road trip")
    assert drive["display_name"] == "Alpine Rainy Scenic Drive & Lake Church"

    # Reference Video 4: Greek Sea Caves
    aegean = lookup_art_style("aegean sea caves relaxation")
    assert aegean["display_name"] == "Greek Cycladic Coastal & Aegean Sea Caves"

    # Reference Video 5: Lake Como Morning Coffee
    como = lookup_art_style("lake como morning coffee")
    assert como["display_name"] == "Italian Coastal & Lake Como Morning Coffee"

    # Reference Video 6: Ibiza Luxury Lounge
    ibiza = lookup_art_style("ibiza rooftop sunset lounge")
    assert ibiza["display_name"] == "Ibiza Luxury Sunset Rooftop Lounge"

    # Reference Video 7: Primeval Emerald Forest
    forest = lookup_art_style("primeval forest stream sanctuary")
    assert forest["display_name"] == "Primeval Emerald Forest & Stream Relaxation"

    # Reference Video 8: Thailand Karst Wonders
    thailand = lookup_art_style("thailand karst mountains and pagodas")
    assert thailand["display_name"] == "Tropical Thailand Karst Wonders & Teak Chalets"

    # Other Global Movements
    ukiyo = lookup_art_style("ukiyo-e woodblock")
    assert ukiyo["display_name"] == "Japanese Ukiyo-e Woodblock Print (Edo Period)"

    afro = lookup_art_style("afrofuturism tribal cyber")
    assert afro["display_name"] == "African Afrofuturism & Neo-Wakanda"


def test_cultural_derivation_with_art_style():
    """Verify cultural derivation injects art style prompt anchors and LoRAs."""
    ctx = derive_cultural_context(
        script_text="Rainy village walk in Lauterbrunnen",
        video_format="walking_tour",
        art_style="swiss_alpine_rainy_village",
    )
    assert ctx.art_style_display == "Swiss Alpine Rainy Village & Walking Tour"
    assert "Lauterbrunnen" in ctx.art_style_prompt
    assert "overcast rainy" in ctx.art_style_lighting.lower()
    assert any("swiss_alpine" in str(l.get("path", "")) for l in ctx.recommended_loras)
    assert "piano" in ctx.music_style.lower() or "rainfall" in ctx.music_style.lower()


def test_stack_resolver_for_scenic_relaxation():
    """Verify stack resolver configures zero-cost 2.5D optical motion and Flux Dev for art styles."""
    stack = resolve_production_stack({
        "title": "Milos Sea Caves Relaxation",
        "genre": "relaxation",
        "video_format": "scenic_relaxation",
        "art_style": "greek_cycladic_coastal",
    })
    assert stack["visual_diffusion"]["model"] == "flux-1-dev"
    assert stack["motion_animation"]["model"] == "camera-pan-zoom-2.5d"
    assert stack["motion_animation"]["unit_cost_usd"] == 0.0
    assert any("greek_aegean" in str(l.get("path", "")) for l in stack["recommended_loras"])


@pytest.mark.asyncio
async def test_script_agent_directorial_guidance_injection():
    """Verify ScriptAgent crafts directorial scene plans with art style lighting and color palettes."""
    storyboard = await script_agent.draft_episode_storyboard(
        topic="Lauterbrunnen Rainy Walking Tour",
        genre="relaxation",
        target_duration_seconds=15,
        video_format="walking_tour",
        art_style="swiss_alpine_rainy_village",
    )
    assert storyboard["title"]
    assert len(storyboard["scenes"]) >= 3
    assert storyboard["art_style"] == "Swiss Alpine Rainy Village & Walking Tour"
    assert "overcast" in storyboard["lighting_scheme"].lower()
    assert "emerald" in storyboard["color_palette"].lower()


@pytest.mark.asyncio
async def test_scenic_pipeline_offline_production():
    """Test full pipeline dry-run synthesis of a scenic walking tour video with art style."""
    user = User(
        email="scenic_director@cineai.studio",
        display_name="Scenic Director",
        google_sub="sub_scenic_001",
        storage_container_name="user_scenic_director",
        api_credit_balance_usd=50.0,
    )
    repo.save_user(user)

    show = Show(user_id=user.id, title="Swiss Alpine Escapes", slug="swiss_escapes", genre="scenic")
    repo.save_show(show)

    ep = Episode(
        user_id=user.id,
        show_id=show.id,
        title="Lauterbrunnen Rainy Village Walk",
        episode_number=1,
        duration_seconds=15,
        format=MediaFormat.WALKING_TOUR,
    )
    repo.save_episode(ep)

    master_path = await pipeline_coordinator.produce_episode_master(
        user_id=user.id,
        episode_id=ep.id,
        dry_run=True,
        language="en",
        art_style="swiss_alpine_rainy_village",
    )
    assert master_path.exists()
    assert master_path.suffix == ".mp4"

    updated_ep = repo.get_episode(user.id, ep.id)
    assert updated_ep.status == "completed"
    assert updated_ep.master_video_path
