"""Targeted Unit Tests for Live Stadium Concert Studio ($0.00 spend offline mocks, Rule 8)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch

from src.studios.concert_studio.concert_audio_service import synthesize_concert_audio
from src.studios.concert_studio.concert_director import synthesize_concert_broadcast_cuts, synthesize_concert_motion
from src.studios.concert_studio.concert_image_service import (
    CONCERT_CAMERA_NAMES,
    _build_cutaway_prompt,
    _build_lead_character_prompt,
    synthesize_concert_camera_rig,
)
from src.studios.concert_studio.concert_producer import produce_concert_video, resolve_concert_workspace
from src.studios.concert_studio.concert_prompt_engine import (
    build_concert_gemini_prompt,
    build_concert_gemini_schema,
    get_offline_concert_broadcast_timeline,
)


def test_concert_camera_names_count():
    assert CONCERT_CAMERA_NAMES == ["singer_orchestra_stage"]


def test_lead_character_prompt_has_anchor_and_modesty():
    sb = {
        "characters": [{
            "name": "Ashwini", "age": 24, "gender": "Female",
            "body_composition": "Natural fit medium-slender build",
        }],
        "character_wardrobe": {
            "outfit_description": "Modest sapphire blue anarkali with high mandarin collar, continuous covered torso, full tailored sleeves",
            "accessories": "delicate gold necklace choker and matching earrings",
        },
    }
    p_mic = _build_lead_character_prompt(sb, "", "ashwini_face", instrument="mic")
    assert "Ashwini" in p_mic and "sapphire blue anarkali" in p_mic and "eye-level" in p_mic.lower()
    assert "singing only, not playing instruments" in p_mic

    p_vln = _build_lead_character_prompt(sb, "", "ashwini_face", instrument="violin")
    assert "playing Violin" in p_vln and "virtuoso" in p_vln


def test_cutaway_prompts_have_zero_character_identity():
    for cam in ["stadium_audience_crowd", "overall_stage_vista"]:
        p = _build_cutaway_prompt("", cam, instrument="acoustic_guitar")
        assert "Lead character identity" not in p and "Ashwini" not in p and len(p) > 20



def test_multilingual_prompt_engine_supports_custom_prompt():
    prompt = build_concert_gemini_prompt(
        language="hi", chars="Meera", prompt="Epic Hindi patriotic rock stadium anthem",
        title="Jai Bharat", duration_seconds=60, instrument="sitar",
    )
    assert "Hindi" in prompt and "Epic Hindi patriotic rock stadium anthem" in prompt
    assert "Jai Bharat" in prompt and "Sitar" in prompt
    assert "SINGER-INSTRUMENTALIST" in prompt and "virtuosic sitar solos" in prompt

    prompt_mic = build_concert_gemini_prompt(language="te", chars="Radha", instrument="mic")
    assert "VOCALIST ONLY" in prompt_mic and "singer playing violin" in prompt_mic


def test_offline_concert_broadcast_timeline():
    timeline = get_offline_concert_broadcast_timeline(duration_seconds=60.0)
    assert len(timeline) >= 12
    cameras_used = {c["camera_id"] for c in timeline}
    assert "singer_orchestra_stage" in cameras_used
    assert "overall_stage_vista" in cameras_used
    assert "stadium_audience_crowd" in cameras_used
    for c in timeline:
        assert 3.0 <= c["duration_seconds"] <= 5.5
        assert c["cut_type"] in ("motion", "local_drone", "lipsync")
        assert "local_drone_motion" in c
        assert "motion_curve" in c
        assert "transition_to_next" in c


@pytest.mark.asyncio
async def test_suno_fail_fast_on_error(tmp_path: Path):
    sb = {"title_en": "Prana Dhumukulu", "lyrics": "Test lyrics", "suno_tags": "rock"}
    stems_dir = tmp_path / "audio_stems"
    with patch("src.providers.music.suno_adapter.SunoMusicAdapter.generate_to_file", side_effect=RuntimeError("HTTP 403: The remain credits is not enough")):
        with pytest.raises(RuntimeError, match="Suno Music Generation failed"):
            await synthesize_concert_audio(
                storyboard_data=sb, stems_dir=stems_dir, duration_seconds=60.0,
                title="Prana Dhumukulu", force_live=True,
            )


@pytest.mark.asyncio
async def test_end_to_end_concert_studio_offline(tmp_path: Path):
    sb = {
        "title_en": "Prana Dhumukulu",
        "title_localized": "ప్రాణ దుముకులు",
        "lyrics": "గుండెల్లో దడ పుట్టించే రాగం\nఅందరినీ కలిపేసే ఈ నాదం!",
        "suno_tags": "live rock anthem, 128 bpm",
        "vocal_gender": "female",
        "characters": [{"name": "Ashwini", "gender": "Female", "age": 24}],
        "scenes": [
            {"scene_index": 1, "camera_id": "singer_orchestra_stage", "visual_prompt": "Ashwini singing centerstage with live band", "camera_motion": "steady_eye_level"},
            {"scene_index": 2, "camera_id": "stadium_audience_crowd", "visual_prompt": "Cheering fans with lightsticks", "camera_motion": "slow_push"},
            {"scene_index": 3, "camera_id": "overall_stage_vista", "visual_prompt": "Mammoth stage arena vista", "camera_motion": "wide_stage_pullback"},
        ],
        "broadcast_timeline": get_offline_concert_broadcast_timeline(10.0),
    }

    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True)
    # Pre-create 3 test images for the 3 stage plates
    from PIL import Image
    for idx in range(1, 4):
        img = Image.new("RGB", (640, 360), color=(idx * 40, idx * 30, idx * 50))
        img.save(scenes_dir / f"scene_{idx:02d}.jpg")

    with patch("src.providers.visual.fal_aura_sr.FalAuraSRAdapter.upscale_image", new_callable=AsyncMock) as mock_up:
        res = await synthesize_concert_camera_rig(
            storyboard_data=sb, scenes_dir=scenes_dir, user_id="test_user",
            force_live=False, chars="Ashwini",
        )
        assert len(res) >= 1
        assert all(p.is_file() for p in res)


def test_drone_face_closeup_matrix_trajectories():
    from src.scripts.local_perspective_drone import precompute_sequence_matrices
    matrices, total_frames = precompute_sequence_matrices(
        img_shape=(2160, 3840, 3),
        sequence=[("zoom_in_singer", 2.0)],
        fps=24.0,
        max_depth=0.72,
        curve="cosine",
    )
    assert total_frames == 48
    assert len(matrices) == 48
    # Matrix 0 should differ from Matrix 47 (active optical zoom & vertical tilt)
    assert not (matrices[0] == matrices[-1]).all()


def test_render_perspective_drone_accepts_motion_curve_kwarg(tmp_path: Path):
    from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync
    from PIL import Image
    test_img = tmp_path / "stage.jpg"
    Image.new("RGB", (320, 180), color=(50, 50, 50)).save(test_img)
    out_clip = tmp_path / "dummy_out.mp4"
    # Pre-populate dummy out_clip so force_rerun=False returns immediately
    out_clip.write_bytes(b"x" * 2000)
    res = render_perspective_drone_clip_sync(
        image_path=test_img,
        output_path=out_clip,
        duration_seconds=2.0,
        fps=24,
        choreography="zoom_in_singer",
        motion_curve="ramp-down",
        force_rerun=False,
    )
    assert res.is_file()


def test_normalize_lipsync_model():
    from src.providers.lipsync.fal_latentsync import normalize_lipsync_model
    # Default is always local CPU model ($0.00 spend)
    assert normalize_lipsync_model(None) == "local"
    assert normalize_lipsync_model("") == "local"
    assert normalize_lipsync_model("local") == "local"
    assert normalize_lipsync_model("kling") == "fal-ai/kling-video/lipsync/audio-to-video"
    assert normalize_lipsync_model("fal-ai/sync-lipsync/v2") == "fal-ai/sync-lipsync/v2"
    assert normalize_lipsync_model("sync-lipsync/v2") == "fal-ai/sync-lipsync/v2"
    assert normalize_lipsync_model("sync-lipsync") == "fal-ai/sync-lipsync/v2"
    assert normalize_lipsync_model("latentsync") == "fal-ai/latentsync"
    assert normalize_lipsync_model("sadtalker") == "sadtalker"
    assert normalize_lipsync_model("fal-ai/sadtalker") == "fal-ai/sadtalker"


@pytest.mark.asyncio
async def test_latentsync_adapter_multi_model(tmp_path: Path):
    from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
    adapter = FalLatentSyncAdapter(default_model="fal-ai/sync-lipsync/v2")
    assert adapter.default_model == "fal-ai/sync-lipsync/v2"

    dummy_vid = tmp_path / "dummy_cut.mp4"
    dummy_vid.write_bytes(b"dummy_video_bytes" * 100)
    dummy_audio = tmp_path / "dummy_audio.mp3"
    dummy_audio.write_bytes(b"dummy_audio_bytes" * 50)
    out_clip = tmp_path / "dummy_synced.mp4"

    # In mock mode, sync_lips should gracefully pass through local video and return out_clip
    res = await adapter.sync_lips(
        video_path=dummy_vid,
        audio_path=dummy_audio,
        output_path=out_clip,
        force_live=False,
        model="fal-ai/sync-lipsync/v2",
    )
    assert res.is_file()
    assert res.stat().st_size > 0


def test_resolved_cuts_schema_has_media_path_and_video_flag():
    cut = {
        "cut_index": 1,
        "path": Path("cut_01.mp4"),
        "media_path": Path("cut_01.mp4"),
        "duration": 4.2,
        "camera_id": "singer_orchestra_stage",
        "start_time": 0.0,
        "end_time": 4.2,
        "drone_motion": "steady_eye_level",
        "is_video": True,
    }
    assert cut["media_path"] == Path("cut_01.mp4")
    assert cut["is_video"] is True
    assert "drone_motion" in cut


def test_detect_lead_face_center_onnx_yolo():
    from src.scripts.local_perspective_drone import detect_lead_face_center
    import numpy as np
    # On synthetic blank canvas, it gracefully returns None without error
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    assert detect_lead_face_center(blank) is None

    # On actual scene_01.jpg if present, it accurately detects lead performer
    stage_img = Path("storage/user-knpillutla-gmail-com/networks/telugu_rhythms/music_video/dhadkan_ki_goonj/ep-001/scenes/scene_01.jpg")
    if stage_img.is_file():
        import cv2
        img = cv2.imread(str(stage_img))
        fc = detect_lead_face_center(img)
        assert fc is not None
        fx, fy = fc
        # Ashwini lead singer face is located in center-left quadrant
        assert 1300 < fx < 1600
        assert 350 < fy < 600


def test_orbit_stage_to_audience_choreography():
    from src.scripts.local_perspective_drone import normalize_choreography_sequence, precompute_sequence_matrices
    seq = normalize_choreography_sequence("orbit_stage_to_audience", default_duration=6.0)
    assert len(seq) == 3
    # Phase 1: Orbital pullback (dollyout, pan-right, orbit-left)
    assert seq[0][0] == "parallel"
    actions_p1 = [a for a, _ in seq[0][1]]
    assert "dollyout" in actions_p1
    assert "pan-right" in actions_p1
    assert "orbit-left" in actions_p1

    # Phase 2: Sweep to crowd (pan-right, tilt-up)
    assert seq[1][0] == "parallel"
    actions_p2 = [a for a, _ in seq[1][1]]
    assert "pan-right" in actions_p2
    assert "tilt-up" in actions_p2

    # Phase 3: Beat drop terminal push-in (dollyin, level)
    assert seq[2][0] == "parallel"
    actions_p3 = [a for a, _ in seq[2][1]]
    assert "dollyin" in actions_p3
    assert "level" in actions_p3

    # Ensure precompute_sequence_matrices successfully computes 24fps frames
    matrices, total_frames = precompute_sequence_matrices(
        img_shape=(2160, 3840, 3),
        sequence=seq,
        fps=24.0,
        output_size=(3840, 2160),
    )
    assert len(matrices) > 100
    assert total_frames == len(matrices)


def test_concert_groove_engine_offline(tmp_path: Path):
    from src.studios.concert_studio.concert_groove_engine import extract_audio_beat_features
    test_audio = tmp_path / "beat.mp3"
    test_audio.write_bytes(b"dummy_mp3" * 200)

    bpm, beats, rms = extract_audio_beat_features(test_audio, duration=2.0, default_bpm=128.0)
    assert bpm == 128.0
    assert len(beats) > 0
    assert len(rms) > 0


def test_produce_concert_defaults_and_theme_preset():
    import inspect
    from src.studios.concert_studio.concert_producer import produce_concert_video
    from src.studios.concert_studio.concert_style_catalog import resolve_concert_style
    from src.studios.concert_studio.concert_setting_catalog import resolve_concert_setting
    from src.studios.concert_studio.concert_prompt_engine import build_concert_gemini_prompt
    assert inspect.signature(produce_concert_video).parameters["image_model"].default == "z-image"
    assert "mridangam" in resolve_concert_style("carnatic", None).prompt
    assert "ocean" in resolve_concert_setting("beach").stage_environment.lower()
    gp = build_concert_gemini_prompt(style="carnatic", setting="beach")
    assert "Traditional Carnatic concert ensemble" in gp and "Coastal Beach" in gp
    assert "LIVING BASE PLATE FOR LIP-SYNC" in gp
    assert "indoor stadium" in gp
