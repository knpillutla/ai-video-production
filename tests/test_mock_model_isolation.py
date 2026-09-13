"""Test offline model isolation and automated model testing cost guard.

Verifies:
1. is_mock_mode() is active across pytest.
2. All provider adapters produce local deterministic outputs with zero network calls,
   even when live API keys are provided.
3. Network guard blocks any outbound call to external AI model endpoints.
4. Duration clamping enforces the 10-second cap when testing models.
"""

from pathlib import Path
import pytest
import httpx

from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter
from src.providers.visual.together_flux import TogetherFluxAdapter
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.providers.lipsync.fal_liveportrait import FalLivePortraitAdapter
from tests.conftest import clamp_model_test_duration, LIVE_MODEL_MAX_DURATION_SECONDS


def test_mock_mode_is_active():
    """Verify that is_mock_mode() returns True during test suite execution."""
    assert is_mock_mode() is True


def test_clamp_model_test_duration():
    """Verify that live model testing durations are clamped to a maximum of 10 seconds."""
    assert clamp_model_test_duration(5.0) == 5.0
    assert clamp_model_test_duration(10.0) == 10.0
    assert clamp_model_test_duration(30.0) == LIVE_MODEL_MAX_DURATION_SECONDS
    assert clamp_model_test_duration(480.0) == 10.0


@pytest.mark.asyncio
async def test_gemini_adapter_runs_locally_with_key():
    """Verify Gemini adapter executes 100% locally even with an API key provided."""
    adapter = GeminiLLMAdapter(api_key="AIzaSyTestLiveKeyThatShouldNeverBeCalled12345")
    text = await adapter.generate_text("Test prompt about Hyderabad tech parks")
    assert "[Generated Script]" in text

    structured = await adapter.generate_structured("Generate a comedy scene plan")
    assert "scenes" in structured
    assert len(structured["scenes"]) >= 3
    assert "IT Employee Remote Work Confusions" in structured["title"]


@pytest.mark.asyncio
async def test_together_flux_adapter_runs_locally_with_key(tmp_path: Path):
    """Verify Together Flux adapter generates images locally without network calls."""
    adapter = TogetherFluxAdapter(api_key="together_live_key_that_must_never_be_called")
    mock_url = await adapter.generate_image("Cinematic 4K close up of tea stall")
    assert mock_url.startswith("https://cdn.cineai.studio/assets/flux_mock_")

    out_file = tmp_path / "flux_test.jpg"
    res_path = await adapter.generate_to_file("Cinematic shot of workspace", out_file)
    assert res_path.exists()
    assert res_path.stat().st_size > 1000


@pytest.mark.asyncio
async def test_azure_speech_adapter_runs_locally_with_key(tmp_path: Path):
    """Verify Azure Speech adapter synthesizes 48kHz audio locally with 0 network calls."""
    adapter = AzureSpeechTTSAdapter(api_key="azure_speech_key_never_called", region="eastus")
    wav_bytes = await adapter.synthesize_speech("ఈ రోజు చాలా ముఖ్యమైన రోజు!", voice_id="te-IN-MohanNeural")
    assert len(wav_bytes) > 1000
    assert wav_bytes[:4] == b"RIFF"

    out_file = tmp_path / "voice_test.wav"
    res_path = await adapter.synthesize_to_file("టెస్ట్ ఆడియో డైలాగ్", out_file)
    assert res_path.exists()
    assert res_path.stat().st_size > 1000


@pytest.mark.asyncio
async def test_suno_music_adapter_runs_locally_with_key(tmp_path: Path):
    """Verify Suno adapter synthesizes 48kHz stereo WAV locally with 0 network calls."""
    adapter = SunoMusicAdapter(api_key="suno_live_key_never_called")
    mock_url = await adapter.generate_track(genre="cinematic comedy")
    assert "suno_track_" in mock_url

    out_file = tmp_path / "suno_test.wav"
    res_path = await adapter.generate_to_file(out_file, genre="cinematic comedy", duration_seconds=2.0)
    assert res_path.exists()
    assert res_path.stat().st_size > 1000


@pytest.mark.asyncio
async def test_fal_liveportrait_adapter_runs_locally_with_key(tmp_path: Path):
    """Verify Fal LivePortrait adapter runs local compositor without external network call."""
    adapter = FalLivePortraitAdapter(api_key="fal_live_key_never_called")
    fake_img = tmp_path / "avatar.jpg"
    fake_img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 200)  # minimal jpeg header
    fake_audio = tmp_path / "voice.wav"
    fake_audio.write_bytes(b"RIFF" + b"\x00" * 200)

    out_file = tmp_path / "avatar_clip.mp4"
    res_path = await adapter.animate_avatar(fake_img, fake_audio, out_file, duration_seconds=2.0)
    assert res_path.exists()
    assert res_path.stat().st_size > 0


@pytest.mark.asyncio
async def test_network_guard_blocks_external_model_domains():
    """Verify that network guard strictly raises RuntimeError on attempted model API calls."""
    client = httpx.AsyncClient()

    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        await client.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent")

    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        await client.post("https://api.together.xyz/v1/images/generations")

    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        await client.post("https://api.suno.ai/v1/generate")

    with pytest.raises(RuntimeError, match="CRITICAL SAFETY VIOLATION"):
        await client.post("https://queue.fal.run/fal-ai/live-portrait")

    await client.aclose()
