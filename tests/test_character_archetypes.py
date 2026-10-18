"""Unit tests for the 30-Production Character Archetype Rotation Engine."""

import pytest
from src.services.character_archetypes import (
    ROTATION_CYCLE_LIMIT,
    get_and_increment_production_slot,
    resolve_cast_archetypes,
    build_fresh_cast_prompt_directive,
)


def test_50_production_rotation_distinctness():
    """Verify all 50 slots yield distinct character pairs, and slot 50 wraps to slot 0."""
    female_names = set()
    male_names = set()

    for slot in range(ROTATION_CYCLE_LIMIT):
        fem, male = resolve_cast_archetypes(slot=slot, culture="te", language="te")
        assert fem.name not in female_names, f"Duplicate female name found at slot {slot}: {fem.name}"
        assert male.name not in male_names, f"Duplicate male name found at slot {slot}: {male.name}"
        female_names.add(fem.name)
        male_names.add(male.name)

    assert len(female_names) == 50
    assert len(male_names) == 50

    # Verify wrap-around after 50 productions
    fem_0, male_0 = resolve_cast_archetypes(slot=0, culture="te", language="te")
    fem_50, male_50 = resolve_cast_archetypes(slot=50, culture="te", language="te")
    assert fem_50.name == fem_0.name
    assert male_50.name == male_0.name


def test_slot_increment_persistence(tmp_path, monkeypatch):
    """Verify production slot advances on each call and cycles modulo 50."""
    from src.services import character_archetypes
    state_file = tmp_path / "character_rotation.json"
    monkeypatch.setattr(character_archetypes, "get_rotation_state_file", lambda u, n: state_file)

    slot_1 = get_and_increment_production_slot("test_user", "test_net")
    slot_2 = get_and_increment_production_slot("test_user", "test_net")
    slot_3 = get_and_increment_production_slot("test_user", "test_net")

    assert slot_1 == 0
    assert slot_2 == 1
    assert slot_3 == 2


def test_attractive_and_snow_weather_wardrobe_directive():
    """Verify snow settings enforce attractive, fully covering, warm winter clothing."""
    fem, male = resolve_cast_archetypes(slot=0, culture="te", language="te")
    directive = build_fresh_cast_prompt_directive(slot=0, fem=fem, male=male, setting="snow filled mountains of swiss alps")

    # Beautiful female lead & attractive clothing directives
    assert "Strikingly beautiful" in directive
    assert "graceful SLIM build" in directive
    assert "MEDIUM BUILT" in directive
    assert "Strikingly handsome" in directive

    # Weather-authentic warm winter covering
    assert "high-altitude snow" in directive.lower()
    assert "cashmere turtleneck" in directive.lower()
    assert "wool trousers" in directive.lower()
    assert "alpine winter boots" in directive.lower()
    assert "PROHIBITION against thin fabrics, sleeveless tops, bare midriffs" in directive


def test_language_specific_regional_character_distinctness():
    """Verify distinct regional facial features and names across South, North, East India and Global regions."""
    # South Indian (te)
    te_fem, te_male = resolve_cast_archetypes(slot=0, language="te", culture="south_indian")
    assert te_fem.name == "Vennela"
    assert "warm golden-wheatish" in te_fem.skin or "wheatish" in te_fem.skin
    assert te_male.name == "Siddharth"

    # North Indian (hi)
    hi_fem, hi_male = resolve_cast_archetypes(slot=0, language="hi", culture="north_indian")
    assert hi_fem.name == "Ananya"
    assert "fair golden-wheatish" in hi_fem.skin or "wheatish" in hi_fem.skin
    assert hi_male.name == "Kabir"

    # East Indian (bn)
    bn_fem, bn_male = resolve_cast_archetypes(slot=0, language="bn", culture="bengali")
    assert bn_fem.name == "Poulomi"
    assert "pata-chokh" in bn_fem.face or "doe eyes" in bn_fem.face
    assert bn_male.name == "Sourav"

    # Japanese (ja)
    ja_fem, ja_male = resolve_cast_archetypes(slot=0, language="ja", culture="japanese")
    assert ja_fem.name == "Sakura"
    assert "almond eyes" in ja_fem.face
    assert ja_male.name == "Haruto"

    # French (fr)
    fr_fem, fr_male = resolve_cast_archetypes(slot=0, language="fr", culture="french")
    assert fr_fem.name == "Camille"
    assert "Roman nose" in fr_fem.face or "hazel-green" in fr_fem.face
    assert fr_male.name == "Antoine"

    # Spanish (es)
    es_fem, es_male = resolve_cast_archetypes(slot=0, language="es", culture="spanish")
    assert es_fem.name == "Lucia"
    assert "olive" in es_fem.skin
    assert es_male.name == "Mateo"

    # Korean (ko)
    ko_fem, ko_male = resolve_cast_archetypes(slot=0, language="ko", culture="korean")
    assert ko_fem.name == "Ji-woo"
    assert "glass" in ko_fem.skin or "V-line" in ko_fem.face
    assert ko_male.name == "Min-jun"

    # Western English (en)
    en_fem, en_male = resolve_cast_archetypes(slot=0, language="en", culture="western")
    assert en_fem.name == "Emma"
    assert en_male.name == "Liam"
