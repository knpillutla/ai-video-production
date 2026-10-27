"""
Unit tests for Archetypes Ascending (ASC) sorting and first-letter navigation logic.
Guarantees 100% deterministic local execution ($0.00 model cost).
"""

import re
import pytest
from src.studios.documentary_studio.doc_templates_food import FOOD_TEMPLATES
from src.studios.documentary_studio.doc_archetypes_food import FOOD_ALIASES, FOOD_DIRECTIVES


def clean_archetype_label(label: str) -> str:
    """Mirrors frontend cleanText = label.replace(/^[^a-zA-Z0-9]+/, '').trim().toLowerCase()"""
    return re.sub(r"^[^a-zA-Z0-9]+", "", label).strip().lower()


def test_supermarkets_backend_archetype_registered():
    """Verify supermarkets_and_grocery_culture is present in templates and alias resolver."""
    assert "supermarkets_and_grocery_culture" in FOOD_TEMPLATES
    assert "supermarkets" in FOOD_ALIASES
    assert FOOD_ALIASES["supermarkets"] == "supermarkets_and_grocery_culture"
    assert FOOD_ALIASES["grocery_stores"] == "supermarkets_and_grocery_culture"
    assert "supermarkets_and_grocery_culture" in FOOD_DIRECTIVES


def test_archetypes_asc_alphabetical_order():
    """Verify that sorting by clean text orders items strictly A-Z in ascending order."""
    sample_labels = [
        "🛒 Supermarkets & Grocery Culture",
        "🌍 Country Dossier & Almanac",
        "🏛️ Architecture & Historic Wonders",
        "✈️ Aviation Gateways",
        "🏖️ Beach Towns",
        "🌱 Cleanest Cities & Places",
        "🌾 Food Production & Agriculture",
        "🏆 Top 20 Places Countdown",
        "👩 Women of the Nation",
        "💍 Family & Marriage Culture",
        "🎬 Movie History & Cinema Industries",
    ]

    sorted_labels = sorted(sample_labels, key=lambda l: clean_archetype_label(l))
    cleaned_sorted = [clean_archetype_label(l) for l in sorted_labels]

    # Verify strictly ascending
    for i in range(len(cleaned_sorted) - 1):
        assert cleaned_sorted[i] <= cleaned_sorted[i + 1]

    # Check key placements
    assert cleaned_sorted[0].startswith("architecture")
    assert cleaned_sorted[1].startswith("aviation")
    assert cleaned_sorted[2].startswith("beach")
    assert cleaned_sorted[3].startswith("cleanest")
    assert cleaned_sorted[4].startswith("country")
    assert any(c.startswith("supermarkets") for c in cleaned_sorted)


def test_first_letter_navigation_selects_first_match():
    """Simulate keyboard navigation logic: typing a letter selects the first item starting with it."""
    sample_options = [
        "🏛️ Architecture & Historic Wonders",
        "✈️ Aviation Gateways",
        "🌱 Cleanest Cities & Places",
        "🌍 Country Dossier & Almanac",
        "🎭 Cultural Curiosities",
        "💍 Family & Marriage Culture",
        "🏡 Small Towns & Villages",
        "🗺️ States & Provinces Breakdown",
        "🛒 Supermarkets & Grocery Culture",
        "🌋 Survival Paradox",
    ]

    clean_options = [clean_archetype_label(opt) for opt in sample_options]

    # Typing 's' for the first time should jump to 'Small Towns & Villages' (index 6), NOT Supermarkets (index 8)
    first_s_idx = next(i for i, c in enumerate(clean_options) if c.startswith("s"))
    assert first_s_idx == 6
    assert sample_options[first_s_idx].startswith("🏡 Small Towns")

    # Typing 'c' should jump to 'Cleanest Cities & Places' (index 2), NOT Cultural Curiosities (index 4)
    first_c_idx = next(i for i, c in enumerate(clean_options) if c.startswith("c"))
    assert first_c_idx == 2
    assert sample_options[first_c_idx].startswith("🌱 Cleanest Cities")

    # Typing 'su' (multi-char search) should match Supermarkets
    first_su_idx = next(i for i, c in enumerate(clean_options) if c.startswith("su"))
    assert first_su_idx == 8
    assert sample_options[first_su_idx].startswith("🛒 Supermarkets")
