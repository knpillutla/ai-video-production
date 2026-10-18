"""Offline Unit Test for Telugu Lo-Fi Music Video Production Script."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scripts.test_lofi_singer import run_pipeline


@pytest.mark.asyncio
async def test_lofi_singer_pipeline_offline(tmp_path, monkeypatch):
    """Verify test_lofi_singer pipeline runs end-to-end with local mocks and multi-scene idempotency."""
    test_audio = tmp_path / "mock_song.mp3"
    test_audio.write_bytes(b"0" * 20000)

    test_video = tmp_path / "character_living_motion_5s.mp4"
    test_video.write_bytes(b"0" * 600000)

    out_dir = tmp_path / "output"

    args = MagicMock()
    args.topic = "Oka Brundavanam Telugu Lo-Fi"
    args.vocal_start = 18.0
    args.audio = str(test_audio)
    args.video = str(test_video)
    args.duration = 72.0
    args.output_dir = str(out_dir)

    dummy_sc = out_dir / "scene_dummy.mp4"
    dummy_sc.parent.mkdir(parents=True, exist_ok=True)
    dummy_sc.write_bytes(b"0" * 60000)

    with patch("scripts.test_lofi_singer.produce_scene_clip_idempotent", new_callable=AsyncMock) as mock_scene, \
         patch("scripts.test_lofi_singer.slice_scene_audio") as mock_slice, \
         patch("scripts.test_lofi_singer.concatenate_and_master") as mock_master:

        mock_slice.return_value = tmp_path / "slice.mp3"
        mock_scene.return_value = dummy_sc
        mock_master.return_value = out_dir / "master_4k_lofi_music_video.mp4"

        res = await run_pipeline(args)

        assert res["status"] == "success"
        assert "master_4k_lofi_music_video.mp4" in res["master_video"]
        assert mock_scene.call_count == 4
        mock_master.assert_called_once()
