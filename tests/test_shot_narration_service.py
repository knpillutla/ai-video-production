"""Deterministic offline unit tests for shot-aligned narration cadence and fast dual master remux."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from pydantic import BaseModel
from src.services.shot_narration_service import synthesize_shot_aligned_narration


class MockScene(BaseModel):
    narration_text: str
    duration_seconds: float


@pytest.mark.asyncio
async def test_dynamic_duration_extension_when_narration_is_longer(tmp_path: Path):
    """Test that if narration speech is longer than planned shot duration, the shot automatically extends."""
    scenes = [
        MockScene(narration_text="Scene 1 text", duration_seconds=15.0),
        MockScene(narration_text="Scene 2 text", duration_seconds=20.0),
    ]

    # Mock AzureSpeechTTSAdapter and get_media_duration
    # Shot 1 speech: 16.0s (longer than 15s planned! Needs 16.0 + 0.8 + 2.0 = 18.8s)
    # Shot 2 speech: 10.0s (shorter than 20s planned -> remains 20.0s)
    speech_durs = {"shot_1_raw.mp3": 16.0, "shot_2_raw.mp3": 10.0}

    with patch("src.providers.tts.azure_speech.AzureSpeechTTSAdapter.synthesize_to_file", new_callable=AsyncMock) as mock_tts, \
         patch("src.services.shot_narration_service.get_media_duration") as mock_dur, \
         patch("subprocess.run") as mock_run:

        def fake_dur(p: Path):
            for k, d in speech_durs.items():
                if k in str(p):
                    return d
            return 10.0

        mock_dur.side_effect = fake_dur

        res = await synthesize_shot_aligned_narration(
            scenes=scenes,
            ep_dir=tmp_path,
            lead_in_sec=0.8,
            min_tail_pause_sec=2.0,
        )

        assert len(res["shot_durations"]) == 2
        # Shot 1 should have extended from 15.0s to 18.8s!
        assert res["shot_durations"][0] == 18.8
        # Shot 2 should stay at 20.0s since 10.0 + 0.8 + 2.0 = 12.8s <= 20.0s
        assert res["shot_durations"][1] == 20.0
        # Total duration is 18.8 + 20.0 = 38.8s
        assert res["total_duration"] == 38.8


@pytest.mark.asyncio
async def test_anti_fatigue_pause_guaranteed(tmp_path: Path):
    """Test that if speech is exactly equal to planned shot duration, it still extends to guarantee tail silence."""
    scenes = [
        MockScene(narration_text="Scene 1 text", duration_seconds=10.0),
    ]
    # Speech is 9.5s. Planned was 10.0s. 9.5 + 0.8 + 2.0 = 12.3s -> must extend to 12.3s
    with patch("src.providers.tts.azure_speech.AzureSpeechTTSAdapter.synthesize_to_file", new_callable=AsyncMock), \
         patch("src.services.shot_narration_service.get_media_duration", return_value=9.5), \
         patch("subprocess.run"):

        res = await synthesize_shot_aligned_narration(
            scenes=scenes,
            ep_dir=tmp_path,
            lead_in_sec=0.8,
            min_tail_pause_sec=2.0,
        )

        assert res["shot_durations"][0] == 12.3
        assert res["total_duration"] == 12.3
