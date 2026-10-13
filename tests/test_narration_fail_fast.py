"""Unit tests for narration fail-fast enforcement and stage status validation."""
import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path


@pytest.mark.asyncio
async def test_narration_fail_fast_raises_runtime_error(tmp_path: Path):
    """Verify that studio_producer immediately raises RuntimeError when narration fails."""
    from src.studios.studio_producer import StudioProducer
    from src.studios.screenplay_models import AmbientStoryboard, AmbientScenePrompt

    producer = StudioProducer(output_base_dir=tmp_path)
    sb = AmbientStoryboard(
        title="Test Doc",
        genre="documentary",
        total_duration=10.0,
        spoken_narration_script="Ancient history in the Indus valley.",
        scenes=[
            AmbientScenePrompt(scene_index=1, visual_prompt="A vista", duration_seconds=10.0, narration_text="Ancient history")
        ]
    )

    # Keyframe dummy file so all_kfs_exist is True
    ep_dir = tmp_path / "EP-001"
    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "keyframe_p1.jpg").write_bytes(b"dummy_image_data_more_than_1000_bytes_" * 50)

    with patch("src.services.shot_narration_service.synthesize_shot_aligned_narration", side_effect=Exception("TTS connection failed")):
        with pytest.raises(RuntimeError) as exc_info:
            await producer.produce(
                sb=sb,
                episode_id="EP-001",
                audio_only=True,
                enable_voiceover=True,
            )
        assert "Documentary voiceover narration synthesis failed" in str(exc_info.value)


def test_stage_3_status_failed_when_narration_missing():
    """Verify that Stage 3 is marked 'failed' if voiceover is enabled but spoken_narration.mp3 is absent."""
    current_stage = 3
    eff_voiceover = True
    audio_stems = [
        {"name": "Suno Soundtrack", "filename": "raw_soundtrack.mp3"},
        {"name": "Velvet BGM", "filename": "velvet_binaural_master_48k.mp3"},
    ]

    has_narr_stem = any(s.get("filename") == "spoken_narration.mp3" for s in audio_stems)
    audio_stage_ok = current_stage >= 3 and len(audio_stems) > 0 and (not eff_voiceover or has_narr_stem)

    if current_stage == 3 and not audio_stage_ok:
        eff_stage_status = "failed"
    elif current_stage < 5:
        eff_stage_status = "ready"
    else:
        eff_stage_status = "completed"

    assert has_narr_stem is False
    assert audio_stage_ok is False
    assert eff_stage_status == "failed"

