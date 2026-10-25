"""Unit tests for ByteDance OmniHuman 1-Pass Audio-to-Video Avatar Adapter ($0.00 spend, Rule 8)."""

from __future__ import annotations

from pathlib import Path
import pytest

from src.providers.lipsync.fal_bytedance_omnihuman import (
    FalByteDanceOmniHumanAdapter,
    _extract_image_from_source,
    fal_bytedance_omnihuman_adapter,
)
from src.providers.lipsync.fal_latentsync import normalize_lipsync_model


def test_normalize_lipsync_model_bytedance():
    assert normalize_lipsync_model("bytedance") == "fal-ai/bytedance/omnihuman"
    assert normalize_lipsync_model("onepass-bytedance") == "fal-ai/bytedance/omnihuman"
    assert normalize_lipsync_model("omnihuman") == "fal-ai/bytedance/omnihuman"
    assert normalize_lipsync_model("bytedance_1pass") == "fal-ai/bytedance/omnihuman"


def test_extract_image_from_source(tmp_path: Path):
    img = tmp_path / "test_plate.jpg"
    img.write_bytes(b"\xFF\xD8\xFF" + b"\x00" * 6000)
    assert _extract_image_from_source(img) == img


@pytest.mark.asyncio
async def test_omnihuman_offline_mock(tmp_path: Path):
    img = tmp_path / "test_plate.jpg"
    img.write_bytes(b"\xFF\xD8\xFF" + b"\x00" * 6000)

    # Synthetic tiny valid wav/mp3 for test
    audio = tmp_path / "test_vocal.mp3"
    audio.write_bytes(b"ID3" + b"\x00" * 2000)

    out = tmp_path / "omnihuman_out.mp4"
    adapter = FalByteDanceOmniHumanAdapter(api_key=None)

    # In mock mode, it calls _fallback_local with $0.00 spend
    res = await adapter.generate_avatar_video(image_path=img, audio_path=audio, output_path=out, force_live=False)
    assert res == out


@pytest.mark.asyncio
async def test_omnihuman_cache_hit(tmp_path: Path):
    out = tmp_path / "cached_cut.mp4"
    out.write_bytes(b"\x00" * 15_000)
    adapter = FalByteDanceOmniHumanAdapter(api_key="mock_key")
    res = await adapter.generate_avatar_video(image_path="img.jpg", audio_path="aud.mp3", output_path=out, force_live=True)
    assert res == out
