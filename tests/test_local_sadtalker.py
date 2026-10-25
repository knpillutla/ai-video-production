"""Targeted Unit Tests for Local CPU SadTalker Lipsync Adapter ($0.00 spend, Rule 8)."""

from __future__ import annotations

from pathlib import Path
import pytest
import numpy as np

from src.providers.lipsync.fal_latentsync import normalize_lipsync_model
from src.providers.lipsync.local_sadtalker import (
    LocalSadTalkerAdapter,
    detect_face_square_crop,
    local_sadtalker_adapter,
)


def test_normalize_lipsync_model_sadtalker_local_vs_fal():
    # Plain sadtalker defaults to local CPU sadtalker
    assert normalize_lipsync_model("sadtalker") == "sadtalker"
    assert normalize_lipsync_model("sad-talker") == "sadtalker"
    assert normalize_lipsync_model("local_sadtalker") == "sadtalker"

    # Explicit fal request routes to fal-ai/sadtalker
    assert normalize_lipsync_model("fal-ai/sadtalker") == "fal-ai/sadtalker"
    assert normalize_lipsync_model("fal_sadtalker") == "fal-ai/sadtalker"


def test_detect_face_square_crop_dimensions():
    # Create test canvas
    dummy = np.zeros((720, 1280, 3), dtype=np.uint8)
    crop256 = detect_face_square_crop(dummy, crop_size=256)
    assert crop256.shape == (256, 256, 3)

    crop512 = detect_face_square_crop(dummy, crop_size=512)
    assert crop512.shape == (512, 512, 3)


def test_local_sadtalker_adapter_discovery():
    adapter = LocalSadTalkerAdapter()
    # is_available safely returns boolean without throwing
    available = adapter.is_available()
    assert isinstance(available, bool)


@pytest.mark.asyncio
async def test_local_sadtalker_mock_fallback(tmp_path: Path):
    adapter = LocalSadTalkerAdapter()
    in_video = tmp_path / "in.mp4"
    in_audio = tmp_path / "in.mp3"
    out_video = tmp_path / "out.mp4"

    in_video.write_bytes(b"dummy_mp4_bytes")
    in_audio.write_bytes(b"dummy_audio_bytes")

    # In mock mode, falls back without error or paid external API calls ($0.00)
    res = await adapter.sync_lips(
        video_path=in_video,
        audio_path=in_audio,
        output_path=out_video,
        force_live=False,
    )
    assert res == out_video
