"""Targeted unit test for Ambient World, Live Broadcaster, and Packaging."""

from src.services.ambient_metadata_packager import generate_youtube_ambient_package
from src.services.ambient_translator import localize_metadata_for_languages
from src.services.binaural_spatial_audio import build_binaural_delta_filter
from src.services.live_stream_broadcaster import YouTubeLiveBroadcaster
from src.services.thumbnail_ab_packager import generate_thumbnail_ab_variants
from src.studios.ambient_world.ambient_catalog import ARCHETYPES, AtmosphericArchetype
from src.orchestrator.studio_registry import studio_registry
import src.studios.ambient_world  # trigger registration


def test_archetype_catalog_has_all_14_themes():
    expected = [
        "swiss_alps", "himalayas", "ocean_world", "mountains",
        "rain", "lake", "beach", "camp_fire", "forest",
        "beach_house", "night_sleep", "blizzard", "winter", "autumn"
    ]
    for key in expected:
        assert key in ARCHETYPES, f"Missing archetype {key}"
        arch = ARCHETYPES[key]
        assert isinstance(arch, AtmosphericArchetype)


def test_live_stream_broadcaster_url_builder():
    broadcaster = YouTubeLiveBroadcaster(stream_key="abcd-1234-wxyz")
    url = broadcaster.build_stream_url()
    assert url == "rtmp://a.rtmp.youtube.com/live2/abcd-1234-wxyz"


def test_ambient_multi_language_translator():
    localized = localize_metadata_for_languages(
        archetype_key="swiss_alps",
        base_title="Swiss Alps Rain",
        base_description="Relaxing sleep video",
    )
    assert "ja" in localized
    assert "de" in localized
    assert "es" in localized
    assert "4K" in localized["ja"].title


def test_thumbnail_ab_packager():
    ab_pack = generate_thumbnail_ab_variants("beach_house")
    assert len(ab_pack.variants) == 3
    assert ab_pack.variants[0].variant_id == "variant_a_interior_pov"
    assert ab_pack.variants[1].variant_id == "variant_b_wide_sanctuary"
    assert ab_pack.variants[2].variant_id == "variant_c_hearth_detail"


def test_cultural_acoustic_engine_archetypes():
    from src.services.cultural_acoustic_service import resolve_cultural_acoustic_profile

    # Desert check
    desert_prof = resolve_cultural_acoustic_profile(archetype="desert_daytime_tent", title="Rub' al Khali Oasis Pavilion")
    assert desert_prof.culture_key == "desert"
    assert "Ney Flute" in desert_prof.lead_instrument
    assert "Qanun" in desert_prof.secondary_textures
    assert "guitar" not in desert_prof.suno_prompt.lower()
    assert "guitar" not in desert_prof.suno_tags.lower()

    # Swiss Alps check
    alps_prof = resolve_cultural_acoustic_profile(archetype="swiss_alps", title="Alpe di Siusi Floral Meadow")
    assert alps_prof.culture_key == "swiss_alps"
    assert "Alpine Wooden Flute" in alps_prof.lead_instrument
    assert "Zither" in alps_prof.secondary_textures
    assert "guitar" not in alps_prof.suno_prompt.lower()

    # Zen check
    zen_prof = resolve_cultural_acoustic_profile(archetype="zen", title="Kyoto Bamboo Lotus Sanctuary")
    assert zen_prof.culture_key == "zen"
    assert "Shakuhachi" in zen_prof.lead_instrument
    assert "Koto" in zen_prof.secondary_textures

    # Ocean check
    ocean_prof = resolve_cultural_acoustic_profile(archetype="ocean", title="Maldives Overwater Villa")
    assert ocean_prof.culture_key == "ocean"
    assert "Handpan" in ocean_prof.lead_instrument
    assert "Kalimba" in ocean_prof.secondary_textures
