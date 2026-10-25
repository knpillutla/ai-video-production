"""Targeted unit tests for dynamic soothing instrument diversity and Suno relaxation prompt directions."""

import pytest
from src.services.relaxation_instruments import (
    get_random_soothing_instrument_set,
    get_llm_soothing_music_guidance,
    SoothingInstrumentPalette,
)
from src.services.cultural_acoustic_service import resolve_cultural_acoustic_profile


def test_random_soothing_instruments_diversity():
    """Verify that multiple calls yield different soothing instrument combinations."""
    palettes = [get_random_soothing_instrument_set() for _ in range(10)]
    leads = {p.lead_instrument for p in palettes}
    accompaniments = {p.accompaniment for p in palettes}

    # At least 2 different lead instruments and accompaniments across 10 random picks
    assert len(leads) >= 2, f"Expected diversity in lead instruments, got: {leads}"
    assert len(accompaniments) >= 2, f"Expected diversity in accompaniments, got: {accompaniments}"

    for p in palettes:
        assert isinstance(p, SoothingInstrumentPalette)
        assert 48 <= p.tempo_bpm <= 56
        assert "432hz" in p.suno_tags.lower() or "528hz" in p.suno_tags.lower()
        assert "zero vocals" in p.suno_tags.lower()
        assert "zero drums" in p.suno_tags.lower()
        assert "[Instrumental Ambient Meditation]" in p.suno_prompt
        assert "[Acoustic Direction:" in p.suno_prompt


def test_llm_soothing_music_guidance_text():
    """Verify LLM instructions contain explicit Suno directions and instrument diversity directives."""
    guidance = get_llm_soothing_music_guidance()
    assert "ZERO BACKGROUND SONG" in guidance
    assert "STOCHASTIC INSTRUMENT DIVERSITY" in guidance
    assert "Celtic harp" in guidance
    assert "bansuri" in guidance
    assert "singing bowls" in guidance
    assert "felted upright piano" in guidance
    assert "48-54 BPM" in guidance


def test_cultural_acoustic_service_with_randomize():
    """Verify resolve_cultural_acoustic_profile uses stochastic soothing instruments when randomize=True."""
    prof1 = resolve_cultural_acoustic_profile(archetype="alpine", title="Alpine Meadow", randomize=True)
    prof2 = resolve_cultural_acoustic_profile(archetype="alpine", title="Alpine Meadow", randomize=True)

    assert prof1.culture_key == "swiss_alps"
    assert prof2.culture_key == "swiss_alps"
    assert "432hz" in prof1.suno_tags.lower() or "528hz" in prof1.suno_tags.lower()
    assert "[Instrumental Ambient Meditation]" in prof1.suno_prompt
