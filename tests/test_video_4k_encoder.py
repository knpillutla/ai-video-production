"""Unit tests for the reusable 4K video encoder utility (Rule 8: $0.00 spend)."""

import os
import subprocess
from pathlib import Path
import pytest
import imageio_ffmpeg

from src.services.video_4k_encoder import (
    ensure_video_4k,
    get_video_resolution,
    is_clip_4k,
)


@pytest.fixture
def sample_720p_video(tmp_path: Path) -> Path:
    """Create a 1-second 1280x720 local MP4 using FFmpeg lavfi."""
    out_video = tmp_path / "test_720p.mp4"
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=1:r=24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out_video),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=flags)
    assert res.returncode == 0
    assert out_video.is_file() and out_video.stat().st_size > 1000
    return out_video


def test_probe_and_upscale_to_4k(sample_720p_video: Path):
    """Verify that a 720p clip is detected as non-4k and successfully upscaled to 3840x2160."""
    # 1. Before upscale: resolution is 1280x720
    res_before = get_video_resolution(sample_720p_video)
    assert res_before == (1280, 720)
    assert not is_clip_4k(sample_720p_video)

    # 2. Run ensure_video_4k
    out_path = ensure_video_4k(sample_720p_video)
    assert out_path == sample_720p_video

    # 3. After upscale: resolution must be 3840x2160 (4K UHD)
    res_after = get_video_resolution(sample_720p_video)
    assert res_after == (3840, 2160)
    assert is_clip_4k(sample_720p_video)


def test_already_4k_is_noop(sample_720p_video: Path):
    """Verify that calling ensure_video_4k on an already 4K clip is an immediate no-op."""
    ensure_video_4k(sample_720p_video)
    mtime_1 = sample_720p_video.stat().st_mtime

    # Calling again should not re-encode
    ensure_video_4k(sample_720p_video)
    mtime_2 = sample_720p_video.stat().st_mtime
    assert mtime_1 == mtime_2


def test_nonexistent_or_empty_file(tmp_path: Path):
    """Verify graceful handling of missing or empty files."""
    missing = tmp_path / "does_not_exist.mp4"
    assert not is_clip_4k(missing)
    assert ensure_video_4k(missing) == missing
