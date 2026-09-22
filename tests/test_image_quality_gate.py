"""Tests for Interactive Image Quality Gate in Video Production Pipeline."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.domain.creative import Episode, Show
from src.domain.generation import GenerationOptions, MediaFormat
from src.domain.repo import repo
from src.domain.user import User
from src.scripts.image_quality_gate import (
    ImageQualityGateDecision,
    execute_image_quality_gate,
)
from src.compositor.pipeline import pipeline_coordinator
from src.compositor.pipeline_scenes import (
    PipelineCancelled,
    RecreateScriptRequested,
    synthesize_scenes,
)


@pytest.fixture
def mock_scenes(tmp_path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        img = scenes_dir / f"scene_{i:02d}.jpg"
        img.write_bytes(b"dummy image data" * 100)
    
    scenes_list = [
        {"scene_index": 0, "shot_type": "wide_shot", "duration_seconds": 4.0, "visual_prompt": "Scenic alpine sunrise"},
        {"scene_index": 1, "shot_type": "medium_shot", "duration_seconds": 4.0, "visual_prompt": "Hiker walking on trail"},
        {"scene_index": 2, "shot_type": "close_up", "duration_seconds": 4.0, "visual_prompt": "Crystal clear alpine stream"},
    ]
    return scenes_list, scenes_dir


def test_image_quality_gate_auto_confirm(mock_scenes):
    scenes_list, scenes_dir = mock_scenes
    decision = execute_image_quality_gate(scenes_list, scenes_dir, auto_confirm=True)
    assert decision.action == "proceed"
    assert decision.target_scene_indices == []


@pytest.mark.parametrize("user_input", ["", "1", "y", "yes", "proceed", "approve"])
def test_image_quality_gate_proceed_actions(mock_scenes, user_input):
    scenes_list, scenes_dir = mock_scenes
    decision = execute_image_quality_gate(
        scenes_list, scenes_dir, auto_confirm=False, custom_input_fn=lambda _: user_input
    )
    assert decision.action == "proceed"


@pytest.mark.parametrize("user_input", ["e", "exit", "q", "cancel", "n", "no", "5"])
def test_image_quality_gate_cancel_actions(mock_scenes, user_input):
    scenes_list, scenes_dir = mock_scenes
    decision = execute_image_quality_gate(
        scenes_list, scenes_dir, auto_confirm=False, custom_input_fn=lambda _: user_input
    )
    assert decision.action == "cancel"


def test_image_quality_gate_recreate_all(mock_scenes):
    scenes_list, scenes_dir = mock_scenes
    decision = execute_image_quality_gate(
        scenes_list, scenes_dir, auto_confirm=False, custom_input_fn=lambda _: "3"
    )
    assert decision.action == "recreate_all"


def test_image_quality_gate_recreate_script(mock_scenes):
    scenes_list, scenes_dir = mock_scenes
    decision = execute_image_quality_gate(
        scenes_list, scenes_dir, auto_confirm=False, custom_input_fn=lambda _: "4"
    )
    assert decision.action == "recreate_script"


def test_image_quality_gate_recreate_specific(mock_scenes):
    scenes_list, scenes_dir = mock_scenes
    # Sequence of user responses: select "2", enter "0, 2", enter override for 0, enter blank for 2
    inputs = iter(["2", "0, 2", "Enhanced golden hour lighting", ""])
    decision = execute_image_quality_gate(
        scenes_list, scenes_dir, auto_confirm=False, custom_input_fn=lambda _: next(inputs)
    )
    assert decision.action == "recreate_specific"
    assert decision.target_scene_indices == [0, 2]
    assert decision.prompt_overrides == {0: "Enhanced golden hour lighting"}


@pytest.mark.asyncio
async def test_pipeline_synthesize_scenes_with_image_gate_proceed(mock_scenes, tmp_path):
    scenes_list, scenes_dir = mock_scenes
    stems_dir = tmp_path / "audio_stems"
    stems_dir.mkdir(parents=True, exist_ok=True)

    episode = MagicMock()
    episode.id = uuid4()
    episode.title = "Alpine Walk"
    episode.format = MediaFormat.WALKING_TOUR
    episode.options = GenerationOptions(enable_tts=False)

    vis_mock = AsyncMock()
    vis_mock.generate_to_file.return_value = ("http://img", scenes_dir / "scene_00.jpg")
    tts_mock = AsyncMock()

    # With auto_confirm=True, synthesize_scenes passes through image quality gate
    compiled, subtitles, duration = await synthesize_scenes(
        scenes_list=scenes_list,
        scenes_dir=scenes_dir,
        stems_dir=stems_dir,
        episode=episode,
        scale=1.0,
        char_anchor=None,
        derived_culture=MagicMock(weather_condition="clear", environment_space="outdoor", art_style_prompt="", voice_id="en-US-GuyNeural", recommended_loras=[]),
        visual_adapter=vis_mock,
        tts_adapter=tts_mock,
        enable_voice_over=False,
        enable_video_motion=False,
        auto_confirm=True,
    )

    assert len(compiled) == 3
    assert duration == 12.0


@pytest.mark.asyncio
async def test_pipeline_synthesize_scenes_cancel_at_gate(mock_scenes, tmp_path):
    scenes_list, scenes_dir = mock_scenes
    stems_dir = tmp_path / "audio_stems"
    stems_dir.mkdir(parents=True, exist_ok=True)

    episode = MagicMock()
    episode.id = uuid4()
    episode.title = "Alpine Walk"
    episode.format = MediaFormat.WALKING_TOUR
    episode.options = GenerationOptions(enable_tts=False)

    vis_mock = AsyncMock()
    tts_mock = AsyncMock()

    with pytest.raises(PipelineCancelled):
        await synthesize_scenes(
            scenes_list=scenes_list,
            scenes_dir=scenes_dir,
            stems_dir=stems_dir,
            episode=episode,
            scale=1.0,
            char_anchor=None,
            derived_culture=MagicMock(weather_condition="clear", environment_space="outdoor", art_style_prompt="", voice_id="en-US-GuyNeural", recommended_loras=[]),
            visual_adapter=vis_mock,
            tts_adapter=tts_mock,
            enable_voice_over=False,
            enable_video_motion=False,
            auto_confirm=False,
            custom_gate_input_fn=lambda _: "cancel",
        )


@pytest.mark.asyncio
async def test_pipeline_coordinator_handles_cancel_gracefully(tmp_path):
    user = User(
        email="gate_test@studio.com",
        display_name="Director Gate",
        google_sub="sub_gate_123",
        storage_container_name="user-gate-test",
    )
    repo.save_user(user)
    show = Show(user_id=user.id, title="Quality Gate Show", slug="gate_show")
    repo.save_show(show)
    episode = Episode(user_id=user.id, show_id=show.id, title="Test Gate Ep", episode_number=1, duration_seconds=6)
    repo.save_episode(episode)

    result = await pipeline_coordinator.produce_episode_master(
        user_id=user.id,
        episode_id=episode.id,
        dry_run=True,
        auto_confirm=False,
        custom_gate_input_fn=lambda _: "cancel",
    )
    assert result is None
