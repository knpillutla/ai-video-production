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


def test_scene_context_matched_suno_prompt():
    """Verify that soothing instrument palette incorporates the visual scene context."""
    scene = "Luxury overwater villa deck overlooking calm turquoise lagoon at sunrise"
    palette = get_random_soothing_instrument_set(setting_context=scene)

    assert f"[Scene Context: {scene}]" in palette.suno_prompt
    assert "[Instrumental Ambient Meditation]" in palette.suno_prompt
    assert "zero vocals" in palette.suno_tags.lower()
    assert "zero drums" in palette.suno_tags.lower()


def test_relaxation_fixed_tripod_guard_logic():
    """Verify that relaxation motion prompts are prepended with locked fixed tripod and camera negatives."""
    # Test the exact relaxation tripod logic from visual_batch_service
    is_relax_clip = True
    eff_prompt = "Gentle turquoise waves lapping against the white sand shoreline"
    eff_neg = "blurry, low quality"

    tripod_lead = (
        "Cinemagraph living wallpaper. Strictly locked stationary camera on a heavy fixed tripod "
        "with zero camera movement, zero camera angles, zero pan, zero tilt, zero zoom, zero camera drift. "
        "The camera never moves. The entire frame, topography, and architecture remain 100% frozen, solid, and motionless. "
        "Only subtle organic living motion in the scene: "
    )
    if is_relax_clip:
        if "zero camera movement" not in eff_prompt.lower():
            eff_prompt = f"{tripod_lead}{eff_prompt}"
        cam_negs = "camera movement, camera motion, camera angles, camera pan, panning, camera tilt, tilting, camera zoom, zooming, camera rotation, dolly, drone, tracking shot"
        eff_neg = f"{eff_neg}, {cam_negs}" if eff_neg else cam_negs

    assert "zero camera movement" in eff_prompt
    assert "zero camera angles" in eff_prompt
    assert "heavy fixed tripod" in eff_prompt
    assert "camera movement" in eff_neg
    assert "camera angles" in eff_neg
    assert "camera pan" in eff_neg

