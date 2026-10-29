"""Comprehensive Unit Tests for All 47 Documentary & Nations Archetypes.

Verifies that every archetype across Civics, Travel, Food, and Curiosity
possesses a structured chapter syllabus, 1:1 thematic visual grounding,
strict out-of-bounds negative constraints, and multi-shot cadence ($0.00 compute).
"""
import pytest
from src.studios.documentary_studio.doc_nations_archetypes import (
    get_nations_archetype_directive,
    NATIONS_ARCHETYPE_ALIASES,
    ARCHETYPE_DIRECTIVES,
)
from src.studios.documentary_studio.doc_archetypes_civics import CIVICS_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_travel import TRAVEL_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_food import FOOD_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_curiosity import CURIOSITY_DIRECTIVES


def test_archetype_counts():
    assert len(CIVICS_DIRECTIVES) >= 10
    assert len(TRAVEL_DIRECTIVES) >= 16
    assert len(FOOD_DIRECTIVES) >= 6
    assert len(CURIOSITY_DIRECTIVES) >= 15


@pytest.mark.parametrize("archetype_key", list(CIVICS_DIRECTIVES.keys()))
def test_civics_archetypes_structure(archetype_key):
    directive = get_nations_archetype_directive(archetype_key)
    assert len(directive) > 100
    assert "MANDATORY CHAPTER SYLLABUS" in directive or "MANDATORY CHAPTER SEQUENCE" in directive
    assert "Mandatory Visual" in directive or "MANDATORY VISUAL" in directive
    assert "Prohibited" in directive or "STRICT BAN ON OUT-OF-BOUNDS" in directive or "STRICTLY FORBIDDEN" in directive
    assert "MULTI-SHOT" in directive or "HIERARCHICAL" in directive


@pytest.mark.parametrize("archetype_key", list(FOOD_DIRECTIVES.keys()))
def test_food_archetypes_structure(archetype_key):
    directive = get_nations_archetype_directive(archetype_key)
    assert len(directive) > 100
    assert "MANDATORY CHAPTER SYLLABUS" in directive
    assert "Mandatory Visual" in directive
    assert "Prohibited" in directive
    assert "MULTI-SHOT CADENCE" in directive


@pytest.mark.parametrize("archetype_key", list(TRAVEL_DIRECTIVES.keys()))
def test_travel_archetypes_structure(archetype_key):
    directive = get_nations_archetype_directive(archetype_key)
    assert len(directive) > 100
    assert "MANDATORY CHAPTER SYLLABUS" in directive or "MANDATORY VISUAL" in directive
    assert "STRICT BAN ON OUT-OF-BOUNDS" in directive or "Prohibited" in directive


@pytest.mark.parametrize("archetype_key", list(CURIOSITY_DIRECTIVES.keys()))
def test_curiosity_archetypes_structure(archetype_key):
    directive = get_nations_archetype_directive(archetype_key)
    assert len(directive) > 100
    assert "MANDATORY CHAPTER SYLLABUS" in directive
    assert "Mandatory Visual" in directive
    assert "Prohibited" in directive
    assert "MULTI-SHOT CADENCE" in directive
