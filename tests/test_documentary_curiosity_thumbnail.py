"""Deterministic offline tests for Documentary Curiosity Thumbnail Generation ."""
from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from src.studios.documentary_studio.doc_templates import DocStoryboard, DocGenre, DocScene
from src.studios.documentary_studio.doc_thumbnail_service import (
    render_high_ctr_curiosity_thumbnail,
    generate_documentary_thumbnail_variants,
)


def _make_dummy_scene(index: int, narration: str) -> DocScene:
    return DocScene(
        scene_index=index,
        duration_seconds=12.0,
        shot_type="wide",
        motion_domain="landscape_solid",
        recommended_model="local_drone",
        visual_prompt="Historic monument in soft daylight",
        motion_prompt="Slow forward drone glide",
        narration_text=narration,
    )


def test_render_high_ctr_curiosity_thumbnail_3_slice(tmp_path: Path):
    """Verify curiosity thumbnail renders valid high-res JPEG with 3 attraction cuts and 3D headline."""
    kfs = []
    for i, color in enumerate([(180, 50, 50), (40, 140, 60), (40, 80, 180)], start=1):
        p = tmp_path / f"keyframe_p{i}.jpg"
        Image.new("RGB", (1920, 1080), color=color).save(p, "JPEG")
        kfs.append(p)

    out_thumb = tmp_path / "thumbnail.jpg"
    res = render_high_ctr_curiosity_thumbnail(
        bg_image_paths=kfs,
        headline="WHAT IS POLAND BEST KNOWN FOR?",
        output_path=out_thumb,
        badge_text="4K UHD • POLAND",
        target_res=(1920, 1080),
    )

    assert res.is_file()
    assert res.stat().st_size > 8000
    with Image.open(res) as rendered:
        assert rendered.size == (1920, 1080)
        assert rendered.format == "JPEG"


def test_generate_documentary_thumbnail_variants_uses_story_headline(tmp_path: Path):
    """Verify thumbnail packaging creates single winning thumbnail using storyboard's headline and multi-cuts."""
    ep_dir = tmp_path / "ep_doc_poland"
    ep_dir.mkdir(parents=True, exist_ok=True)

    kfs = []
    for i, color in enumerate([(80, 40, 40), (30, 90, 60), (40, 70, 120)], start=1):
        p = ep_dir / f"keyframe_p{i}.jpg"
        Image.new("RGB", (1920, 1080), color=color).save(p, "JPEG")
        kfs.append(p)

    sb = DocStoryboard(
        title="Poland: Living Heritage",
        genre=DocGenre.PLACES,
        total_duration=60.0,
        thumbnail_headline="EUROPE'S GREATEST SECRET",
        thumbnail_hero_scene_index=2,
        thumbnail_curiosity_rationale="Highlights Poland's astonishing post-war rebirth.",
        scenes=[
            _make_dummy_scene(1, "Welcome to Poland..."),
            _make_dummy_scene(2, "In conclusion..."),
        ],
    )

    pkg = generate_documentary_thumbnail_variants(sb, ep_dir, kfs)
    assert pkg
    assert pkg["thumbnail_headline"] == "EUROPE'S GREATEST SECRET"
    assert Path(pkg["primary_thumbnail"]).is_file()
    assert Path(pkg["hero_image"]).name == "keyframe_p2.jpg"
    assert len(pkg["attraction_cuts"]) == 3
    assert (ep_dir / "thumbnail.jpg").is_file()
    assert (ep_dir / "thumbnail_packaging.json").is_file()


def test_generate_documentary_thumbnail_fallback_headline(tmp_path: Path):
    """Verify fallback headline when storyboard has no explicit headline."""
    ep_dir = tmp_path / "ep_doc_rome"
    ep_dir.mkdir(parents=True, exist_ok=True)
    kf1 = ep_dir / "keyframe_p1.jpg"
    Image.new("RGB", (1920, 1080), color=(100, 100, 100)).save(kf1, "JPEG")

    sb = DocStoryboard(
        title="Rome: The Eternal City",
        genre=DocGenre.PLACES,
        total_duration=30.0,
        scenes=[_make_dummy_scene(1, "Welcome to Rome...")],
    )

    pkg = generate_documentary_thumbnail_variants(sb, ep_dir, [kf1])
    assert pkg
    assert pkg["thumbnail_headline"] == "THE ETERNAL CITY"
    assert (ep_dir / "thumbnail.jpg").is_file()


def test_derive_contextual_doc_titles_different_countries():
    """Verify each country derives a unique context-driven title and 2-to-4 word thumbnail hook."""
    from src.studios.documentary_studio.doc_curiosity_title_service import derive_contextual_doc_titles

    # Slovakia
    t1, h1, vars1 = derive_contextual_doc_titles("Slovakia", "Slovakia: Fortress of the Carpathians")
    assert "Fortress of the Carpathians" in t1
    assert "Slovakia" in t1
    assert h1 == "FORTRESS OF THE CARPATHIANS"
    assert vars1[1]["headline"] == "SLOVAKIA'S SECRET"

    # Croatia (uses different rotated formula than Slovakia)
    t2, h2, vars2 = derive_contextual_doc_titles("Croatia", "Croatia: Jewel of the Adriatic")
    assert "Jewel of the Adriatic" in t2
    assert "Croatia" in t2
    assert t2 != t1  # Formula varies!
    assert h2 == "JEWEL OF THE ADRIATIC"
    assert vars2[2]["headline"] == "HOW CROATIA SURVIVED"

    # Estonia (uses modern republic / sovereign formula)
    t3, h3, vars3 = derive_contextual_doc_titles("Estonia", "Estonia: Sovereign Sanctuary of Forest and Code")
    assert "Sanctuary of Forest and Code" in t3
    assert "Estonia" in t3
    assert t3 != t2
    assert len(h3.split()) <= 4

    # Plain generic input (e.g. "Croatia: Travel")
    t4, h4, vars4 = derive_contextual_doc_titles("Croatia", "Croatia: Travel")
    assert "Croatia" in t4
    assert "Travel" not in t4  # Strips generic junk
    assert h4 == "THE REAL CROATIA"

    # Dynamic Gemini authored title takes 100% precedence over fallbacks
    gemini_yt = "The Secret Nation Out-Producing the World's Superpowers ? Slovakia 4K"
    gemini_thumb = "EUROPE'S SECRET"
    t5, h5, vars5 = derive_contextual_doc_titles(
        "Slovakia",
        "Slovakia: Fortress of the Carpathians",
        gemini_yt_title=gemini_yt,
        gemini_thumb_headline=gemini_thumb,
    )
    assert t5 == gemini_yt
    assert h5 == gemini_thumb


def test_all_new_archetypes_directives_and_templates():
    """Verify all new archetypes and aliases resolve to specialized directives and templates."""
    from src.studios.documentary_studio.doc_nations_archetypes import get_nations_archetype_directive
    from src.studios.documentary_studio.doc_geo_pools import ARCHETYPE_TEMPLATES, ARCHETYPE_GENRE_MAP

    new_archetypes = [
        "elected_leaders", "wealthy_dynasties", "culture_heritage", "aviation_gateways",
        "coastal_beaches", "luxury_resorts", "medical_tourism", "beach_towns",
        "tourism_guide", "ancient_forests", "art_and_masterpieces",
        "music_and_dance", "cinema_and_film_industry", "wellness_retreats",
        "top_20_places", "cleanest_cities_places", "food_production_consumption",
        "regional_cuisines", "food_culture_rituals", "most_dangerous",
        "women_of_nation", "men_of_nation", "family_and_marriage_culture",
        "islands_archipelagos", "agriculture_farming_harvests", "major_industries_manufacturing",
        "states_and_provinces",
        # user requested alias keywords
        "art", "forests", "tourism", "beach_towns", "medical_tourism", "top_resorts",
        "beaches", "airports", "culture", "rich_families", "presidents",
        "music", "dance", "movie_history", "cinema_history", "bollywood_tollywood",
        "wellness", "top_20", "cleanest_cities", "food_production", "regional_food",
        "food_culture", "about_women", "women", "about_men", "men",
        "family_marriage", "weddings", "extreme_danger_zones",
        "islands", "agriculture", "industries", "states", "provinces",
    ]

    for arch in new_archetypes:
        directive = get_nations_archetype_directive(arch)
        assert directive != "", f"Directive missing for archetype: {arch}"
        assert arch in ARCHETYPE_TEMPLATES, f"Template missing for archetype: {arch}"
        assert len(ARCHETYPE_TEMPLATES[arch]) >= 2, f"Template list empty for archetype: {arch}"
        assert arch in ARCHETYPE_GENRE_MAP, f"Genre mapping missing for archetype: {arch}"


