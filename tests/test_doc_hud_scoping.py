"""Tests for Tour Route Map and Barcode Scanner HUD Scoping vs Educational Documentaries."""

import pytest
from src.studios.documentary_studio.doc_directorial_prompt import is_tour_archetype
from src.studios.documentary_studio.doc_nations_archetypes import get_nations_archetype_directive, NATIONS_ARCHETYPE_ALIASES


def test_tour_archetype_classification():
    """Verify that tour and itinerary archetypes are recognized as tours."""
    tour_examples = [
        "tour_itinerary",
        "travel_itinerary_tour",
        "itinerary_map_tour",
        "top_places_to_visit",
        "top_10_cities",
        "top_20_places",
        "grand_tour",
        "tourism_guide",
        "road_trip_tour",
    ]
    for arch in tour_examples:
        assert is_tour_archetype(arch) is True, f"Expected {arch} to be classified as tour"


def test_educational_doc_archetype_classification():
    """Verify that educational sovereign and cultural documentary archetypes are NOT classified as tours."""
    doc_examples = [
        "countries",
        "country_profile",
        "country_dossier",
        "civic_systems",
        "history",
        "elected_leaders",
        "wealthy_dynasties",
        "major_industries_manufacturing",
        "unseen_frontiers",
        "cost_of_living",
        "food_production_consumption",
        "art_and_masterpieces",
        "doc_nature",
    ]
    for arch in doc_examples:
        assert is_tour_archetype(arch) is False, f"Expected {arch} NOT to be classified as tour"


def test_nations_aliases_contain_tours_and_countries():
    """Verify nations archetype aliases resolve tour_itinerary and countries properly."""
    assert NATIONS_ARCHETYPE_ALIASES.get("tour_itinerary") == "tour_itinerary"
    assert NATIONS_ARCHETYPE_ALIASES.get("top_places_to_visit") == "top_places_to_visit"
    assert NATIONS_ARCHETYPE_ALIASES.get("top_10_cities") == "top_10_cities"
    assert NATIONS_ARCHETYPE_ALIASES.get("countries") == "country_dossier"


def test_hud_scoping_rules():
    """Verify the HUD data logic rules: tours get route maps & QR; educational docs get dossier cards & no QR."""
    def build_hud(archetype: str, scene_idx: int, total_scenes: int, chapter_title: str = ""):
        is_tour = is_tour_archetype(archetype)
        if is_tour:
            return {
                "is_tour": True,
                "show_map_locator": True,
                "show_itinerary_qr": bool(scene_idx == total_scenes),
                "qr_url": "https://maps.google.com",
            }
        else:
            show_map = bool(scene_idx == 2 or any(w in chapter_title.lower() for w in ("geography", "border", "climate")))
            return {
                "is_documentary": True,
                "show_map_locator": show_map,
                "show_itinerary_qr": False,
                "qr_url": None,
            }

    # Tour HUD test: Stop 1 should show route map, no QR
    tour_s1 = build_hud("tour_itinerary", scene_idx=1, total_scenes=5)
    assert tour_s1["show_map_locator"] is True
    assert tour_s1["show_itinerary_qr"] is False

    # Tour HUD test: Final stop should show route map AND QR barcode scanner
    tour_s5 = build_hud("tour_itinerary", scene_idx=5, total_scenes=5)
    assert tour_s5["show_map_locator"] is True
    assert tour_s5["show_itinerary_qr"] is True
    assert tour_s5["qr_url"] == "https://maps.google.com"

    # Educational Doc HUD test: Scene 1 should NOT show QR and NOT show map
    doc_s1 = build_hud("country_profile", scene_idx=1, total_scenes=10, chapter_title="National Identity")
    assert doc_s1["show_map_locator"] is False
    assert doc_s1["show_itinerary_qr"] is False
    assert doc_s1["qr_url"] is None

    # Educational Doc HUD test: Scene 2 (Geography) shows cartographic map, NO QR
    doc_s2 = build_hud("country_profile", scene_idx=2, total_scenes=10, chapter_title="Geography & Landforms")
    assert doc_s2["show_map_locator"] is True
    assert doc_s2["show_itinerary_qr"] is False

    # Educational Doc HUD test: Final scene should NEVER show QR barcode scanner
    doc_s10 = build_hud("country_profile", scene_idx=10, total_scenes=10, chapter_title="Strategic Outlook")
    assert doc_s10["show_map_locator"] is False
    assert doc_s10["show_itinerary_qr"] is False
