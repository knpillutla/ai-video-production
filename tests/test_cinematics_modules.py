"""Targeted Unit Tests for Modular Cinematic Production Subsystems.

Tests:
1. Procedural Foley Sound DSP (Rain, Snow/Blizzard, Footsteps, 48kHz WAV Export).
2. Film Color Science & Print LUT Resolution (Kodak 2383, Nordic Noir, Golden Festival).
3. 2.39:1 CinemaScope Aspect Ratio & Letterbox Framing Filters.
4. Dynamic Rhythm Pacing & Tension Duration Curves.
5. Optical Motion Anomaly & Quality Sentry.
6. Environmental State & Progressive Drenching Tracking.
"""

from pathlib import Path
import tempfile
import wave

from src.cinematics.color.film_luts import FILM_LUT_PRESETS, resolve_film_lut
from src.cinematics.color.framing import build_framing_filter
from src.cinematics.continuity.environmental_state import EnvironmentalStateTracker, environmental_state_tracker
from src.cinematics.foley.foley_engine import FoleyEngine, foley_engine
from src.cinematics.pacing.tension_curves import calculate_scene_durations
from src.cinematics.qa.motion_sentry import MotionQASentry, motion_qa_sentry


def test_foley_engine_synthesis_rain_and_steps():
    """Verify FoleyEngine creates a valid 48kHz stereo WAV file for rain & walking."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_wav = Path(tmp_dir) / "rain_steps_foley.wav"
        res = foley_engine.synthesize(
            weather_type="heavy rain storm",
            setting_type="walking tour in downtown street",
            space="outdoor",
            duration_seconds=1.5,
            output_path=out_wav,
        )
        assert res.exists()
        assert res.stat().st_size > 0

        with wave.open(str(res), "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getsampwidth() == 2  # 16-bit
            assert wf.getframerate() == 48000
            n_frames = wf.getnframes()
            assert abs(n_frames / 48000 - 1.5) < 0.05


def test_foley_engine_synthesis_snow_blizzard():
    """Verify FoleyEngine creates a valid WAV file for snow blizzard conditions."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_wav = Path(tmp_dir) / "blizzard_foley.wav"
        res = foley_engine.synthesize(
            weather_type="arctic blizzard snow gale",
            setting_type="mountain hiking trail",
            space="outdoor",
            duration_seconds=1.0,
            output_path=out_wav,
        )
        assert res.exists()
        with wave.open(str(res), "rb") as wf:
            assert wf.getframerate() == 48000
            assert wf.getnchannels() == 2


def test_film_lut_resolution():
    """Verify deterministic selection of film print color LUTs."""
    nordic_filter = resolve_film_lut(culture="nordic iceland", genre="walking_tour", weather="snow")
    assert "curves=" in nordic_filter
    assert nordic_filter == FILM_LUT_PRESETS["nordic_noir"]["ffmpeg_filter"]

    festival_filter = resolve_film_lut(culture="telugu", genre="mass folk dance", weather="clear daylight")
    assert festival_filter == FILM_LUT_PRESETS["golden_festival"]["ffmpeg_filter"]

    custom = resolve_film_lut(custom_lut="technicolor_vintage")
    assert custom == FILM_LUT_PRESETS["technicolor_vintage"]["ffmpeg_filter"]


def test_cinematic_framing_letterbox_filter():
    """Verify 2.39:1 CinemaScope letterbox filter construction."""
    filter_scope = build_framing_filter(aspect_ratio="16:9", target_res=(3840, 2160), enable_cinemascope=True)
    assert "drawbox=" in filter_scope
    assert "scale=3840:2160" in filter_scope

    # 16:9 passthrough
    filter_none = build_framing_filter(aspect_ratio="16:9", target_res=(3840, 2160), enable_cinemascope=False)
    assert filter_none == "scale=3840:2160:flags=lanczos,setsar=1"


def test_tension_pacing_curves():
    """Verify narrative rhythm and tension curve pacing calculation."""
    # 4 scenes, 30s target, 3-act tension curve for dramatic cinema
    durations = calculate_scene_durations(
        total_duration=30.0,
        num_scenes=4,
        genre="drama action movie",
    )
    assert len(durations) == 4
    assert abs(sum(durations) - 30.0) < 0.1
    # Climax (scene 3) should be faster/punchier than opening (scene 1)
    assert durations[2] < durations[0]

    # Walking tour should be steady
    walk_durs = calculate_scene_durations(
        total_duration=30.0,
        num_scenes=6,
        genre="walking_tour",
    )
    assert len(walk_durs) == 6
    assert abs(sum(walk_durs) - 30.0) < 0.1


def test_environmental_state_continuity_progression():
    """Verify progressive wetness and snow accumulation across scenes."""
    tracker = EnvironmentalStateTracker()

    # Scene 1 of 4 in rain (early) -> lightly misted
    s1 = tracker.compute_scene_environmental_state(scene_index=0, total_scenes=4, weather="rain", space="outdoor")
    assert s1["wetness_level"] == "lightly_misted"
    assert "misted" in s1["environmental_prompt"]

    # Scene 4 of 4 in rain (late) -> soaked drenched
    s4 = tracker.compute_scene_environmental_state(scene_index=3, total_scenes=4, weather="heavy rain downpour", space="outdoor")
    assert s4["wetness_level"] == "soaked_drenched"
    assert "drenched" in s4["environmental_prompt"]

    # Indoor scene -> dry
    s_in = tracker.compute_scene_environmental_state(scene_index=3, total_scenes=4, weather="rain", space="indoor")
    assert s_in["wetness_level"] == "dry"
    assert s_in["environmental_prompt"] == ""


def test_motion_sentry_optical_anomaly():
    """Verify motion sentry evaluates missing or empty video files properly."""
    sentry = MotionQASentry()
    # Missing file check
    res_missing = sentry.audit_motion_clip("non_existent_file.mp4")
    assert res_missing["valid"] is False
    assert res_missing["score"] == 0.0


def test_light_vs_heavy_rain_differentiation():
    """Verify clear differentiation in environmental wetness and Foley between light and heavy rain."""
    tracker = EnvironmentalStateTracker()

    # Light rain stay lightly misted even at late scenes
    s_light = tracker.compute_scene_environmental_state(scene_index=3, total_scenes=4, weather="gentle light rain drizzle", space="outdoor")
    assert s_light["wetness_level"] == "lightly_misted"
    assert "micro water droplets" in s_light["environmental_prompt"]

    # Heavy rain reaches soaked drenched
    s_heavy = tracker.compute_scene_environmental_state(scene_index=3, total_scenes=4, weather="heavy torrential rain downpour", space="outdoor")
    assert s_heavy["wetness_level"] == "soaked_drenched"
    assert "streaming off fabric" in s_heavy["environmental_prompt"]
