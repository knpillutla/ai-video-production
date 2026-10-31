"""Targeted unit tests for the 360 Country Profile Master Syllabus.

Verifies duration-aware scaling, 21 master sovereign pillars,
strict visual grounding, and user priority focus detection ($0.00 API expenditure).
"""
import pytest
from src.studios.documentary_studio.doc_country_syllabus import (
    build_country_syllabus_directive,
    CORE_10_KEYS,
    PRINCIPAL_15_KEYS,
    ALL_21_KEYS,
    ALL_22_KEYS,
    PILLARS,
)
from src.studios.documentary_studio.doc_directorial_prompt import build_doc_directorial_prompt


def test_syllabus_pillar_definitions():
    assert len(ALL_22_KEYS) == 22
    assert len(ALL_21_KEYS) == 21
    assert len(CORE_10_KEYS) == 10
    assert len(PRINCIPAL_15_KEYS) == 15

    for key, p in PILLARS.items():
        assert "title" in p
        assert "focus" in p
        assert "visual" in p
        assert "banned" in p
        assert "badge" in p


def test_short_dossier_scaling():
    directive = build_country_syllabus_directive(duration_seconds=120.0)
    assert "SHORT MASTER DOSSIER (10 CORE CHAPTERS)" in directive
    assert "EDUCATION, RESEARCH & TOP UNIVERSITIES" in directive
    assert "NATIONAL TRANSIT: AIRPORTS & AVIATION" in directive
    assert "TRADE & MARITIME COMMERCE: MAJOR PORTS" in directive
    assert "POWER, CLEAN ENERGY & NATIONAL UTILITIES" in directive


def test_extended_dossier_scaling():
    directive = build_country_syllabus_directive(duration_seconds=600.0)
    assert "STANDARD EXTENDED DOSSIER (15 PRINCIPAL CHAPTERS)" in directive
    assert "GREAT METROPOLISES & REGIONAL CITIES" in directive
    assert "MANUFACTURING, INDUSTRY & HIGH-TECH" in directive


def test_long_master_dossier_scaling():
    directive = build_country_syllabus_directive(duration_seconds=1500.0)
    assert "25-MINUTE BROADCAST MASTER DOSSIER (22 COMPLETE CHAPTERS)" in directive
    assert "PROLOGUE & SOVEREIGN EXPEDITION ROADMAP" in directive
    assert "ORIGINS, INDEPENDENCE & CONSTITUTIONAL DAWN" in directive
    assert "COASTAL SANCTUARIES: BEACHES & HEADLANDS" in directive
    assert "CULINARY SOUL & FOOD CULTURE" in directive
    assert "MUSIC, TRADITIONAL DANCE & ENTERTAINMENT" in directive
    assert "NATIONAL PARKS & CONSERVED BIOMES" in directive


def test_custom_user_priority_focus():
    directive = build_country_syllabus_directive(
        duration_seconds=120.0,
        custom_prompt="Deep dive into New Zealand airports, culinary traditions, and universities"
    )
    assert "[★ USER PRIORITY FOCUS]" in directive
    assert "CULINARY SOUL & FOOD CULTURE" in directive
    assert "NATIONAL TRANSIT: AIRPORTS & AVIATION" in directive


def test_directorial_prompt_integration():
    prompt = build_doc_directorial_prompt(
        genre="documentary",
        archetype="country_profile",
        custom_prompt="New Zealand 360",
        duration_seconds=1500.0,
        num_shots=22,
    )
    assert "25-MINUTE BROADCAST MASTER DOSSIER (22 COMPLETE CHAPTERS)" in prompt
    assert "EDUCATION, RESEARCH & TOP UNIVERSITIES" in prompt
    assert "TRADE & MARITIME COMMERCE: MAJOR PORTS" in prompt
    assert "NATIONAL TRANSIT: AIRPORTS & AVIATION" in prompt
    assert "STRICTLY FORBIDDEN: Showing out-of-bounds imagery" in prompt
