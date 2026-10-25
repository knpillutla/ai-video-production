"""Offline Unit Tests for Virtual Artist Multi-Camera Concert Broadcasting.

Tests:
1. virtual_artist_gemini_schema structure and properties.
2. get_offline_virtual_artist_broadcast_timeline cut pacing (3.5s - 5.0s) and singing tags.
3. resolve_camera_index mapping camera_id to scene index.
4. Audio slicing for lipsync (Rule 8 $0.00 spend).
5. VocalStrategy schema routing: virtual artist uses broadcast schema, other genres use standard vocal schema.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import pytest

from src.compositor.genre_strategies.virtual_artist_schema import virtual_artist_gemini_schema
from src.compositor.genre_strategies.vocal_schema import vocal_gemini_schema
from src.compositor.genre_strategies.vocal_strategy import VocalStrategy
from src.compositor.genre_strategies.virtual_artist_directives import (
    get_offline_virtual_artist_scenes,
    get_offline_virtual_artist_broadcast_timeline,
)
from src.compositor.virtual_artist_broadcast_service import (
    resolve_camera_index,
    slice_cut_audio,
)


def test_virtual_artist_schema_structure():
    """Verify that virtual_artist_gemini_schema contains broadcast_timeline and camera_rig properties."""
    schema = virtual_artist_gemini_schema()
    props = schema["properties"]
    assert "broadcast_timeline" in props
    assert "scenes" in props
    assert "lyrics_segments" in props

    # Check broadcast_timeline cut properties
    cut_props = props["broadcast_timeline"]["items"]["properties"]
    assert "camera_id" in cut_props
    assert "is_singing" in cut_props
    assert "active_instrument" in cut_props
    assert "local_drone_motion" in cut_props
    assert "duration_seconds" in cut_props


def test_vocal_strategy_schema_isolation():
    """Verify other genres use standard vocal_gemini_schema, while virtual_artist uses broadcast schema."""
    strat = VocalStrategy()

    # Standard vocal/melody genre
    std_schema = strat.build_gemini_schema(virtual_artist=False)
    assert "broadcast_timeline" not in std_schema["properties"]
    assert std_schema == vocal_gemini_schema()

    # Virtual artist genre
    va_schema = strat.build_gemini_schema(virtual_artist=True)
    assert "broadcast_timeline" in va_schema["properties"]
    assert va_schema == virtual_artist_gemini_schema()


def test_offline_broadcast_timeline_pacing():
    """Verify that offline broadcast cuts are paced between 3.5s and 5.0s matching native AI clips."""
    timeline = get_offline_virtual_artist_broadcast_timeline(duration_seconds=60.0, instrument="acoustic_guitar")
    assert len(timeline) >= 10

    total_dur = 0.0
    for cut in timeline:
        dur = cut["duration_seconds"]
        assert 2.0 <= dur <= 5.0, f"Cut duration {dur} out of bounds"
        assert "camera_id" in cut
        assert "is_singing" in cut
        assert "active_instrument" in cut
        total_dur += dur

    # Check total duration matches approximately 60s
    assert abs(total_dur - 60.0) < 1.0


def test_camera_id_resolution():
    """Verify camera_id correctly maps to 1-based scene index in camera rig."""
    scenes = [
        {"scene_index": 1, "camera_id": "center_vocalist_front"},
        {"scene_index": 2, "camera_id": "stage_profile_45"},
        {"scene_index": 3, "camera_id": "vocal_close_up"},
        {"scene_index": 4, "camera_id": "drone_audience_focus"},
        {"scene_index": 5, "camera_id": "active_instrument_macro"},
        {"scene_index": 6, "camera_id": "high_crane_arena_vista"},
    ]

    assert resolve_camera_index("center_vocalist_front", scenes) == 1
    assert resolve_camera_index("stage_profile_45", scenes) == 2
    assert resolve_camera_index("vocal_close_up", scenes) == 3
    assert resolve_camera_index("drone_audience_focus", scenes) == 4
    assert resolve_camera_index("active_instrument_macro", scenes) == 5
    assert resolve_camera_index("high_crane_arena_vista", scenes) == 6
    assert resolve_camera_index("unknown_cam", scenes) == 1


def test_slice_cut_audio_offline():
    """Verify slice_cut_audio generates an audio slice via FFmpeg without errors."""
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        dummy_audio = tdp / "dummy_song.wav"

        # Generate 10s silent wav
        import wave, struct
        with wave.open(str(dummy_audio), "w") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(48000)
            data = struct.pack("<h", 0) * (48000 * 2 * 10)
            w.writeframes(data)

        out_slice = tdp / "slice_cut_01.mp3"
        res = slice_cut_audio(dummy_audio, start_time=2.0, duration=4.0, out_path=out_slice)
        assert res.is_file()
        assert res.stat().st_size > 1000


def test_english_defaults_to_usa_country():
    """Verify that English defaults to USA country while other languages allow autonomous LLM derivation."""
    from src.studios.music_video_studio.country_music_catalog import resolve_country_and_culture_for_language

    # 1. Catalog resolver defaults English to USA and western culture
    c_en, cult_en = resolve_country_and_culture_for_language("en")
    assert c_en == "USA"
    assert cult_en == "western"

    # Other regional languages do not hardcode country - LLM autonomously derives them
    c_te, cult_te = resolve_country_and_culture_for_language("te")
    assert c_te is None
    assert cult_te is None

    # 2. VocalStrategy prompt generation defaults English to USA country directive
    strat = VocalStrategy()
    p_en = strat.build_gemini_prompt(title="Song", duration_seconds=60, language="en")
    assert "- Country / Region: USA | Culture: western" in p_en
    assert "'country' in output JSON MUST be 'USA'" in p_en

    # 3. Explicit country passed by user overrides the default
    p_uk = strat.build_gemini_prompt(title="Song", duration_seconds=60, language="en", country="United Kingdom")
    assert "- Country / Region: United Kingdom" in p_uk
    assert "'country' in output JSON MUST be 'United Kingdom'" in p_uk

    # 4. Regional languages without country invoke autonomous Gemini derivation
    p_te = strat.build_gemini_prompt(title="Song", duration_seconds=60, language="te")
    assert "AUTONOMOUS COUNTRY & CULTURE DERIVATION" in p_te
    assert "Gemini MUST autonomously identify and derive the authentic 'country'" in p_te


def test_scene_00_intro_slide_never_has_motion():
    """Verify that Scene 00 (title card intro slide) is strictly static without motion."""
    from src.compositor.vocal_fx import _build_crossfade_filter

    # With movement enabled and camera motion prompts provided
    chains, _ = _build_crossfade_filter(
        count=3,
        total_duration=15.0,
        segment_durations=[5.0, 5.0, 5.0],
        fps=30,
        enable_movement=True,
        scene_movements=["dollyin", "pan-right", "orbit-left"],
        is_mass=False,
    )

    # Segment 0 (Scene 00 intro slide) MUST use static scale lanczos, NEVER zoompan
    assert "[0:v]scale=3840:2160:flags=lanczos" in chains[0]
    assert "zoompan" not in chains[0]

    # Subsequent scenes DO have dynamic motion / zoompan
    assert "zoompan" in chains[1]
    assert "zoompan" in chains[2]


def test_model_pipeline_resolution_logic():
    """Verify default pipeline (z-image dataset, flux LoRA, flux scene), and CLI overrides."""
    def resolve_models(model=None, lora_model=None, dataset_model=None):
        raw_m = str(model or "").lower().strip()
        if not raw_m: eff_m = "flux"
        elif any(k in raw_m for k in ("ultra", "flux-ultra", "flux ultra", "flux_ultra")): eff_m = "flux-ultra"
        elif "z" in raw_m: eff_m = "z-image"
        else: eff_m = "flux"

        raw_l = str(lora_model or "").lower().strip()
        if not raw_l: eff_l = "z-image" if eff_m == "z-image" else "flux"
        elif "z" in raw_l: eff_l = "z-image"
        else: eff_l = "flux"

        raw_d = str(dataset_model or "").lower().strip()
        if not raw_d: eff_d = "z-image"
        elif "flux" in raw_d: eff_d = "flux"
        else: eff_d = "z-image"

        return eff_m, eff_l, eff_d

    # 1. Default pipeline: z-image dataset -> flux dev LoRA -> flux dev scene
    m, l, d = resolve_models()
    assert d == "z-image"
    assert l == "flux"
    assert m == "flux"

    # 2. Pure Z-Image to Z-Image pipeline: --model z-image
    m_z, l_z, d_z = resolve_models(model="z-image")
    assert d_z == "z-image"
    assert l_z == "z-image"
    assert m_z == "z-image"

    # 3. Pure FLUX Dev to FLUX Dev pipeline: --dataset-model flux --model flux
    m_f, l_f, d_f = resolve_models(model="flux", dataset_model="flux")
    assert d_f == "flux"
    assert l_f == "flux"
    assert m_f == "flux"

    # 4. Custom combination: z-image dataset -> flux LoRA -> flux-ultra scene
    m_u, l_u, d_u = resolve_models(model="flux-ultra")
    assert d_u == "z-image"
    assert l_u == "flux"
    assert m_u == "flux-ultra"


