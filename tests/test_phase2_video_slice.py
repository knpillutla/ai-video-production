"""Phase 2 Video Vertical Slice Verification Test Suite."""

import pytest
from pathlib import Path

from src.compositor.ffmpeg_pipeline import build_single_pass_command
from src.compositor.pipeline import pipeline_coordinator
from src.compositor.timeline import compile_timeline_from_scenes
from src.domain.creative import Episode, Show
from src.domain.repo import repo
from src.domain.user import User
from src.scripts.local_audio_ducking import (
    build_sidechain_ducking_filter,
    build_timeline_volume_expression,
)
from src.scripts.local_pan_zoom import (
    CameraMovement,
    assign_scene_camera_movement,
    build_zoompan_expression,
)
from src.scripts.local_subtitles import (
    format_timestamp_ass,
    format_timestamp_srt,
    generate_kinetic_ass,
    generate_srt,
)


def test_camera_pan_zoom_expressions():
    """Verify deterministic 2.5D camera pan-zoom FFmpeg filter construction."""
    for mov in [
        CameraMovement.SLOW_ZOOM_IN,
        CameraMovement.SLOW_ZOOM_OUT,
        CameraMovement.PAN_LEFT,
        CameraMovement.PAN_RIGHT,
    ]:
        expr = build_zoompan_expression(mov, duration_seconds=4.0, fps=30)
        assert "zoompan=" in expr
        assert "d=120" in expr
        assert "s=1920x1080" in expr
        assert "fps=30" in expr

    # Verify scene movement alternating assignment
    m0 = assign_scene_camera_movement(0, "close_up")
    assert m0 == CameraMovement.SLOW_ZOOM_IN
    m1 = assign_scene_camera_movement(1, "wide")
    assert m1 in (CameraMovement.PAN_LEFT, CameraMovement.PAN_RIGHT)


def test_audio_ducking_filter_expressions():
    """Verify deterministic audio ducking math for dipping BGM during speech."""
    sidechain = build_sidechain_ducking_filter("[voice]", "[bgm]", "[ducked]")
    assert "sidechaincompress=" in sidechain
    assert "attack=200" in sidechain
    assert "release=350" in sidechain

    # Volume expression evaluation
    speech_times = [(0.0, 3.8), (4.5, 8.2)]
    vol_expr = build_timeline_volume_expression(speech_times, base_volume=0.25, ducked_volume=0.07)
    assert "volume=" in vol_expr
    assert "between(t," in vol_expr
    assert "0.07" in vol_expr
    assert "0.25" in vol_expr


def test_subtitles_srt_and_kinetic_ass(tmp_path: Path):
    """Verify standard SRT and Hormozi-style kinetic ASS subtitle generation."""
    assert format_timestamp_srt(65.45) == "00:01:05,450"
    assert format_timestamp_ass(65.45) == "0:01:05.45"

    segments = [
        {"start": 0.0, "end": 3.8, "text": "వర్క్ ఫ్రమ్ హోమ్ గోల!"},
        {"start": 3.8, "end": 7.5, "text": "మేనేజర్ కాల్స్ ఆగవు."},
    ]

    # SRT
    srt_file = tmp_path / "subs.srt"
    res_srt = generate_srt(segments, srt_file)
    assert res_srt.exists()
    assert "00:00:00,000 --> 00:00:03,800" in res_srt.read_text(encoding="utf-8")

    # Kinetic ASS
    ass_file = tmp_path / "subs.ass"
    res_ass = generate_kinetic_ass(segments, ass_file, language="te")
    assert res_ass.exists()
    ass_content = res_ass.read_text(encoding="utf-8")
    assert "[Script Info]" in ass_content
    assert "Suranna" in ass_content  # Regional Telugu font
    assert "\\fscx108\\fscy108" in ass_content  # Active kinetic bounce tag


def test_single_pass_ffmpeg_graph_construction(tmp_path: Path):
    """Verify single-pass -filter_complex command structure with 0 intermediate re-encodings."""
    scenes = [
        {"duration_seconds": 3.8, "shot_type": "close_up", "dialogue": "Scene 1 speech"},
        {"duration_seconds": 4.2, "shot_type": "wide", "dialogue": "Scene 2 speech"},
    ]
    bgm_file = tmp_path / "bgm.wav"
    bgm_file.touch()

    timeline = compile_timeline_from_scenes(scenes, bgm_path=bgm_file)
    assert timeline.total_duration_seconds == 8.0
    assert len(timeline.scenes) == 2

    out_mp4 = tmp_path / "master.mp4"
    cmd = build_single_pass_command(timeline, out_mp4)

    cmd_str = " ".join(cmd)
    assert "ffmpeg" in cmd_str
    assert "-filter_complex" in cmd_str
    assert "concat=n=2:v=1:a=0" in cmd_str
    assert "-c:v libx264" in cmd_str
    assert "-c:a aac" in cmd_str
    assert "-movflags +faststart" in cmd_str


@pytest.mark.asyncio
async def test_end_to_end_production_pipeline_slice(tmp_path: Path):
    """Verify complete Phase 2 vertical slice: Script -> Flux -> Azure TTS -> Suno -> Compositor."""
    repo.clear()
    user = User(
        email="director@studio.com",
        display_name="Director",
        google_sub="sub_12345",
        storage_container_name="user-director-slice",
        api_credit_balance_usd=50.0,
    )
    repo.save_user(user)

    show = Show(user_id=user.id, title="Delhi WFH Confusions", slug="delhi_wfh_confusions", genre="comedy")
    repo.save_show(show)

    episode = Episode(
        user_id=user.id,
        show_id=show.id,
        title="Episode 1: The Remote Standup",
        episode_number=1,
        duration_seconds=480,
    )
    repo.save_episode(episode)

    # Execute full pipeline in dry_run mode (synthesizes assets, compiles timeline, builds single-pass graph)
    final_video = await pipeline_coordinator.produce_episode_master(
        user_id=user.id,
        episode_id=episode.id,
        dry_run=True,
    )

    assert final_video.exists()
    assert "master_16x9_ep01.mp4" in final_video.name

    updated_ep = repo.get_episode(user.id, episode.id)
    assert updated_ep.status == "completed"
    assert updated_ep.master_video_path == str(final_video)
