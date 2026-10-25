"""Unit tests for Concert Audio Slicing & Movement Physics ($0.00 spend offline mocks, Rule 8)."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from src.studios.concert_studio.concert_audio_slicer import (
    AudioConcertSegment,
    _assign_camera_direction,
    slice_concert_audio,
)
from src.studios.concert_studio.concert_movement_engine import (
    extract_pitch_and_energy_curves,
)


def test_slice_concert_audio_procedural_fallback(tmp_path: Path):
    non_existent = tmp_path / "missing.mp3"
    segs = slice_concert_audio(non_existent, total_duration=30.0, default_bpm=120.0)
    assert len(segs) >= 3
    assert segs[0].start_time == 0.0
    assert segs[-1].end_time == 30.0
    for s in segs:
        assert 2.5 <= s.duration <= 10.5
        assert s.segment_type in ("ORCHESTRA", "VERSE_MODERATE", "CHORUS_INTENSE", "OUTRO_FINALE")
        assert 0.0 <= s.intensity_score <= 1.0
        assert s.recommended_camera in ("singer_orchestra_stage", "stadium_audience_crowd", "overall_stage_vista")


def test_assign_camera_direction_rules():
    # 1. ORCHESTRA cuts cycle through wide vista, audience orbit, and singer groove
    cam1, shot1, mot1 = _assign_camera_direction("ORCHESTRA", is_singing=False, cut_index=0)
    assert cam1 == "overall_stage_vista" and mot1 == "wide_stage_pullback"
    cam2, shot2, mot2 = _assign_camera_direction("ORCHESTRA", is_singing=False, cut_index=1)
    assert cam2 == "stadium_audience_crowd" and mot2 == "orbit_stage_to_audience"
    cam3, shot3, mot3 = _assign_camera_direction("ORCHESTRA", is_singing=False, cut_index=2)
    assert cam3 == "singer_orchestra_stage" and shot3 == "medium"

    # 2. CHORUS_INTENSE prioritizes close-up locking onto face with zoom_in_singer
    c_cam, c_shot, c_mot = _assign_camera_direction("CHORUS_INTENSE", is_singing=True, cut_index=1)
    assert c_cam == "singer_orchestra_stage" and c_shot == "closeup" and c_mot == "zoom_in_singer"

    # 3. VERSE_MODERATE follows 60/40 rule
    v_cam1, v_shot1, _ = _assign_camera_direction("VERSE_MODERATE", is_singing=True, cut_index=0)
    assert v_cam1 == "singer_orchestra_stage" and v_shot1 == "medium"
    v_cam2, v_shot2, _ = _assign_camera_direction("VERSE_MODERATE", is_singing=True, cut_index=2)
    assert v_cam2 == "stadium_audience_crowd" and v_shot2 == "wide_vista"


def test_extract_pitch_and_energy_curves_fallback(tmp_path: Path):
    dummy_audio = tmp_path / "test.mp3"
    dummy_audio.write_bytes(b"dummy" * 50)
    bpm, beats, rms, pitch = extract_pitch_and_energy_curves(dummy_audio, duration=3.0, fps=24, default_bpm=125.0)
    assert bpm == 125.0
    assert len(beats) > 0
    assert len(rms) == 72  # 3s * 24fps
    assert len(pitch) == 72
    assert np.all(rms >= 0.0) and np.all(rms <= 1.0)
    assert np.all(pitch >= 0.0) and np.all(pitch <= 1.0)


def test_artist_gender_inference_and_vocal_consistency():
    from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt, infer_artist_gender

    assert infer_artist_gender("Radha") == "female"
    assert infer_artist_gender("radha_lora") == "female"
    assert infer_artist_gender("Arjun") == "male"
    assert infer_artist_gender("krishna_lora") == "male"
    assert infer_artist_gender("Radha", explicit_gender="male") == "male"

    # Prompt contains male vocal directive for male artist
    p_male = build_concert_gemini_prompt(chars="Arjun")
    assert "MALE VOCALS" in p_male and "Male, age 25" in p_male

    # Prompt contains female vocal directive for female artist
    p_female = build_concert_gemini_prompt(chars="Radha")
    assert "FEMALE VOCALS" in p_female and "Female, age 24" in p_female


def test_new_concert_styles_and_posture_resolution():
    from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt
    from src.studios.concert_studio.concert_style_catalog import resolve_concert_style

    # 1. Carnatic-Fusion
    s_cf = resolve_concert_style("carnatic-fusion")
    assert s_cf.style_id == "carnatic-fusion" and s_cf.default_position == "standing"
    assert "electric violin" in s_cf.prompt.lower()

    # 2. Party
    s_pty = resolve_concert_style("party")
    assert s_pty.style_id == "party" and s_pty.default_position == "standing"
    assert "party" in s_pty.prompt.lower()

    # 3. Entertainer
    s_ent = resolve_concert_style("entertainer")
    assert s_ent.style_id == "entertainer" and s_ent.default_position == "standing"
    assert "entertainer" in s_ent.prompt.lower()

    # 4. Beach
    s_bch = resolve_concert_style("beach")
    assert s_bch.style_id == "beach" and s_bch.default_position == "standing"
    assert "beach" in s_bch.prompt.lower()

    # 5. Traditional Carnatic defaults to sitting
    s_carn = resolve_concert_style("carnatic")
    assert s_carn.default_position == "sitting"

    # 6. Posture in Gemini Prompt
    p_sit = build_concert_gemini_prompt(style="carnatic")
    assert "SITTING" in p_sit and "SEATED" in p_sit

    # 7. User override: Carnatic with standing position
    p_stand = build_concert_gemini_prompt(style="carnatic", position="standing")
    assert "STANDING" in p_stand


def test_5axis_concert_setting_resolution_and_global_venues():
    from src.studios.concert_studio.concert_setting_catalog import resolve_concert_setting

    # 1. Rooftop sunset over city skyline
    s1 = resolve_concert_setting(stage_setting="rooftop", time_of_day="sunset", background="city_skyline", weather="clear", venue_type="outdoor")
    assert s1.venue_type == "outdoor"
    assert s1.stage_setting == "rooftop"
    assert s1.time_of_day == "sunset"
    assert s1.background == "city_skyline"
    assert "rooftop terrace" in s1.stage_environment
    assert "sunset" in s1.lighting_environment.lower()

    # 2. NPR Tiny Desk acoustic broadcast session
    s_desk = resolve_concert_setting(stage_setting="tiny_desk", time_of_day="afternoon", venue_type="indoor")
    assert s_desk.stage_setting == "tiny_desk"
    assert s_desk.time_of_day == "noon"  # 'afternoon' mapped to 'noon'
    assert "bookshelf" in s_desk.stage_environment or "office desk" in s_desk.stage_environment

    # 3. Gothic Cathedral with rose stained-glass window at twilight
    s_cath = resolve_concert_setting(stage_setting="cathedral", time_of_day="dusk", background="cathedral_nave")
    assert s_cath.stage_setting == "cathedral"
    assert s_cath.time_of_day == "twilight"
    assert s_cath.background == "cathedral_nave"
    assert "cathedral sanctuary" in s_cath.stage_environment.lower()

    # 4. Global venues: Jazz club, Warehouse rave, Yacht deck, Garden courtyard, Desert oasis, Cavern
    for venue_key in ["jazz_club", "warehouse", "yacht_deck", "garden_courtyard", "desert_oasis", "cavern", "balcony", "temple_hall", "beach_platform"]:
        s_g = resolve_concert_setting(stage_setting=venue_key)
        assert s_g.stage_setting == venue_key
        assert len(s_g.plate1_desc) > 20
        assert len(s_g.plate2_desc) > 20
        assert len(s_g.plate3_desc) > 20

    # 5. Global scenery: Tokyo neon, Amalfi coast, Industrial brick, Botanical garden
    s_scenery = resolve_concert_setting(background="tokyo", weather="rain")
    assert s_scenery.background == "tokyo_neon"
    assert s_scenery.weather == "rain"
    assert "tokyo" in s_scenery.audience_environment.lower() or "shibuya" in s_scenery.audience_environment.lower()


def test_gemini_prompt_incorporates_5axis_settings():
    from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt

    prompt = build_concert_gemini_prompt(
        language="en",
        chars="David",
        style="rock",
        stage_setting="warehouse",
        time_of_day="night",
        background="industrial_brick",
        weather="mist_fog",
        venue_type="indoor",
    )
    assert "Warehouse" in prompt
    assert "industrial warehouse deck" in prompt.lower()
    assert "fog" in prompt.lower() or "mist" in prompt.lower()
    assert "MALE VOCALS" in prompt


def test_dj_concert_style_and_prompt_generation():
    from src.studios.concert_studio.concert_style_catalog import resolve_concert_style
    from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt

    # 1. DJ style preset resolution
    s_dj = resolve_concert_style("dj")
    assert s_dj.style_id == "dj"
    assert s_dj.default_instrument == "dj_controller"
    assert s_dj.default_position == "standing"
    assert "edm" in s_dj.suno_tags_template.lower()

    # 2. DJ flag in Gemini Prompt
    prompt = build_concert_gemini_prompt(
        chars="Arjun",
        is_dj=True,
        language="en",
        venue_type="indoor",
        stage_setting="club_deck",
    )
    assert "DJ Arjun" in prompt
    assert "DJ Console" in prompt or "CDJ" in prompt
    assert "headphones" in prompt.lower()


def test_dj_character_plate_prompt_builder():
    from src.studios.concert_studio.concert_image_service import _build_lead_character_prompt

    sb_dj = {
        "characters": [{"name": "Radha", "gender": "Female", "age": 24}],
        "is_dj": True,
        "style": "dj",
        "character_wardrobe": {
            "outfit_description": "chic metallic bomber jacket and tailored trousers",
            "accessories": "over-ear DJ headphones and silver wrist cuff",
        },
    }
    p = _build_lead_character_prompt(sb_dj, raw_prompt="", trigger_words="radha_face")
    assert "DJ Radha" in p
    assert "DJ booth console" in p or "CDJ mixer" in p
    assert "headphones" in p.lower()


@pytest.mark.asyncio
async def test_master_singer_lipsync_caching(tmp_path: Path):
    from src.studios.concert_studio.concert_lipsync_engine import synthesize_master_singer_plate, _is_valid_mp4

    fake_video = tmp_path / "master_singer_lipsync.mp4"
    fake_video.write_bytes(b"moov" + b"\x00" * 60_000)
    assert _is_valid_mp4(fake_video)

    stage_img = tmp_path / "scene_01.jpg"
    stage_img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"ID3" + b"\x00" * 2000)

    # Rule 3 Tier 1 check: reuses existing non-empty plate
    res = await synthesize_master_singer_plate(
        stage_image=stage_img,
        audio_path=audio,
        output_path=fake_video,
        total_duration=60.0,
        force_live=False,
    )
    assert res == fake_video


def test_detect_chorus_presence_and_stage_representation():
    from src.studios.concert_studio.concert_prompt_engine import detect_chorus_presence
    from src.studios.concert_studio.concert_image_service import _build_lead_character_prompt

    # 1. Detect from lyrics tag
    assert detect_chorus_presence({"lyrics": "[Chorus]\nSaagara teeraana swara lahari"}) is True
    assert detect_chorus_presence({"lyrics": "[Hook]\nCatchy refrain"}) is True

    # 2. Detect from suno_tags
    assert detect_chorus_presence({"suno_tags": "classical concert, female vocals, harmonies"}) is True
    assert detect_chorus_presence({"suno_tags": "rock anthem, chorus"}) is True

    # 3. Detect from timeline
    assert detect_chorus_presence({"broadcast_timeline": [{"cut_type": "CHORUS"}]}) is True

    # 4. No chorus
    assert detect_chorus_presence({"lyrics": "Solo verse only", "suno_tags": "solo sitar"}) is False

    # 5. Chorus singers on stage in lead character prompt
    sb_chorus = {
        "characters": [{"name": "Radha", "gender": "Female", "age": 24}],
        "lyrics": "[Chorus]\nSaagara teeraana...",
        "character_wardrobe": {"outfit_description": "silk saree", "accessories": "necklace"},
    }
    p_chorus = _build_lead_character_prompt(sb_chorus, raw_prompt="", trigger_words="radha_face")
    assert "chorus vocalists" in p_chorus.lower()
    assert "standing at choir microphones" in p_chorus.lower() or "seated gracefully" in p_chorus.lower()


@pytest.mark.asyncio
async def test_living_stage_loop_prompt_steady_and_chorus(tmp_path: Path):
    from src.studios.concert_studio.concert_kling_3d import synthesize_living_stage_loop

    img = tmp_path / "scene_01.jpg"
    img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)
    out = await synthesize_living_stage_loop(
        stage_master_image=img, scenes_dir=tmp_path, force_live=False, has_chorus=True,
    )
    assert out.is_file() and out.name == "stage_living_5s.mp4"




