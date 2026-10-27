"""Targeted offline unit tests for motion hybrid expansion (5s diffusion -> full duration)."""
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.services.motion_hybrid_expander import expand_motion_clip_if_needed


@pytest.mark.asyncio
async def test_expand_motion_clip_not_needed(tmp_path: Path):
    """When diff clip already matches target duration, rename directly with zero ffmpeg overhead."""
    diff_clip = tmp_path / "raw_diff.mp4"
    diff_clip.write_bytes(b"dummy_video_bytes" * 100)
    out_clip = tmp_path / "final_motion.mp4"
    img_path = tmp_path / "keyframe.jpg"
    img_path.write_bytes(b"dummy_img_bytes" * 100)

    with patch("src.services.video_4k_encoder.ensure_video_4k"), \
         patch("src.services.ambient_export_service.get_media_duration", return_value=5.0):
        res = await expand_motion_clip_if_needed(
            diff_clip=diff_clip,
            target_duration=5.5,
            image_path=img_path,
            output_path=out_clip,
        )

    assert res == out_clip
    assert out_clip.is_file()
    assert not diff_clip.exists()


@pytest.mark.asyncio
async def test_expand_motion_clip_with_local_drone_expansion(tmp_path: Path):
    """When target duration is 14.8s and diffusion is 5.0s, expand via local drone and xfade."""
    diff_clip = tmp_path / "raw_diff.mp4"
    diff_clip.write_bytes(b"dummy_diff_video" * 100)
    out_clip = tmp_path / "final_motion.mp4"
    img_path = tmp_path / "keyframe.jpg"
    img_path.write_bytes(b"dummy_img_bytes" * 100)

    mock_drone = AsyncMock()
    async def fake_drone(**kwargs):
        # Create the rem_clip output file
        out_p = Path(kwargs["output_path"])
        out_p.write_bytes(b"dummy_drone_video" * 100)
        return out_p
    mock_drone.side_effect = fake_drone

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))

    async def fake_proc(*args, **kwargs):
        # Create output_path
        out_clip.write_bytes(b"dummy_xfade_video" * 200)
        return mock_proc

    with patch("src.services.video_4k_encoder.ensure_video_4k"), \
         patch("src.services.ambient_export_service.get_media_duration", return_value=5.0), \
         patch("src.scripts.local_perspective_drone.render_perspective_drone_clip", mock_drone), \
         patch("asyncio.create_subprocess_exec", side_effect=fake_proc) as mock_exec:
        res = await expand_motion_clip_if_needed(
            diff_clip=diff_clip,
            target_duration=14.78,
            image_path=img_path,
            output_path=out_clip,
            motion_prompt="mist rising from lake",
            visual_prompt="aerial wide view of lake",
        )

    assert res == out_clip
    assert out_clip.is_file()

    # Verify drone was called with zoom="medium" for intimate perspective shift on primary keyframe
    drone_call = mock_drone.call_args[1]
    assert drone_call["start_zoom"] == "medium"
    assert drone_call["image_path"] == img_path
    assert drone_call["duration_seconds"] == pytest.approx(10.28, abs=0.1)

    # Verify FFmpeg was invoked with xfade offset 4.5s
    cmd_args = mock_exec.call_args[0]
    filter_complex_arg = next(cmd_args[i + 1] for i, arg in enumerate(cmd_args) if arg == "-filter_complex")
    assert "offset=4.5" in filter_complex_arg
    assert "duration=0.5" in filter_complex_arg


@pytest.mark.asyncio
async def test_expand_motion_clip_with_distinct_secondary_image(tmp_path: Path):
    """When a distinct detail keyframe is provided, use normal zoom on that secondary image."""
    diff_clip = tmp_path / "raw_diff.mp4"
    diff_clip.write_bytes(b"dummy_diff_video" * 100)
    out_clip = tmp_path / "final_motion.mp4"
    img_path = tmp_path / "keyframe.jpg"
    img_path.write_bytes(b"dummy_img_bytes" * 100)
    sec_img = tmp_path / "keyframe_detail.jpg"
    sec_img.write_bytes(b"dummy_detail_img" * 100)

    mock_drone = AsyncMock()
    async def fake_drone(**kwargs):
        out_p = Path(kwargs["output_path"])
        out_p.write_bytes(b"dummy_drone_video" * 100)
        return out_p
    mock_drone.side_effect = fake_drone

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))

    async def fake_proc(*args, **kwargs):
        out_clip.write_bytes(b"dummy_xfade_video" * 200)
        return mock_proc

    with patch("src.services.video_4k_encoder.ensure_video_4k"), \
         patch("src.services.ambient_export_service.get_media_duration", return_value=5.0), \
         patch("src.scripts.local_perspective_drone.render_perspective_drone_clip", mock_drone), \
         patch("asyncio.create_subprocess_exec", side_effect=fake_proc):
        res = await expand_motion_clip_if_needed(
            diff_clip=diff_clip,
            target_duration=14.0,
            image_path=img_path,
            output_path=out_clip,
            secondary_image_path=sec_img,
        )

    assert res == out_clip
    drone_call = mock_drone.call_args[1]
    # Distinct image should use normal framing
    assert drone_call["start_zoom"] == "normal"
    assert drone_call["image_path"] == sec_img
