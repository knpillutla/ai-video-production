"""Targeted unit tests for Local CPU Wav2Lip Adapter ($0.00 spend, Rule 8)."""

from __future__ import annotations

import asyncio
from pathlib import Path
import cv2
import numpy as np
import pytest

from src.providers.lipsync.local_wav2lip import LocalWav2LipAdapter, _detect_face_box


def test_detect_face_box_fallback():
    # Test with synthetic black image
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    box = _detect_face_box(img)
    assert box is not None
    x1, y1, x2, y2 = box
    assert 0 <= x1 < x2 <= 1280
    assert 0 <= y1 < y2 <= 720


@pytest.mark.asyncio
async def test_wav2lip_chunking_short_passthrough(tmp_path: Path):
    # Create small synthetic test video (24 frames, 640x360)
    test_vid = tmp_path / "test_vid.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(test_vid), fourcc, 24.0, (640, 360))
    for _ in range(24):
        frame = np.full((360, 640, 3), 100, dtype=np.uint8)
        writer.write(frame)
    writer.release()

    # Create dummy audio file
    test_aud = tmp_path / "test_aud.wav"
    import soundfile as sf
    dummy_wav = np.zeros(24000, dtype=np.float32)
    sf.write(str(test_aud), dummy_wav, 16000)

    out_vid = tmp_path / "out_synced.mp4"
    adapter = LocalWav2LipAdapter()
    res = await adapter.sync_lips(test_vid, test_aud, out_vid, force_live=False)
    assert res.is_file()
    assert res.stat().st_size > 1000


def test_wav2lip_render_chunked_sync(tmp_path: Path):
    adapter = LocalWav2LipAdapter()
    if not adapter.model_path.is_file():
        pytest.skip("wav2lip.onnx not present")

    # 48 frames (2 seconds at 24fps)
    test_vid = tmp_path / "test_48f.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(test_vid), fourcc, 24.0, (320, 240))
    for _ in range(48):
        frame = np.full((240, 320, 3), 120, dtype=np.uint8)
        # draw a simple face circle
        cv2.circle(frame, (160, 100), 40, (200, 180, 160), -1)
        cv2.rectangle(frame, (150, 110), (170, 125), (50, 50, 200), -1)
        writer.write(frame)
    writer.release()

    test_aud = tmp_path / "test_48f.wav"
    import soundfile as sf
    dummy_wav = np.sin(2 * np.pi * 440 * np.linspace(0, 2.0, 32000)).astype(np.float32)
    sf.write(str(test_aud), dummy_wav, 16000)

    out_vid = tmp_path / "out_synced_chunks.mp4"
    res = adapter._render_wav2lip_sync(test_vid, test_aud, out_vid)
    assert res.is_file()
    assert res.stat().st_size > 5000
