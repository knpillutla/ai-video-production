"""Google Gemini Multimodal Audio TTS Adapter for broadcast-grade voiceover."""

import io
import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Optional

from src.core.config import settings
from src.core.step_logger import log_pipeline_step
from src.core.telemetry import logger
from src.providers.base import TTSProviderProtocol, is_mock_mode
from src.providers.llm.gemini_adapter import get_live_gemini_api_key


class GeminiAudioTTSAdapter(TTSProviderProtocol):
    """Studio-grade voiceover narration powered by Gemini Flash Audio TTS."""

    def __init__(self, api_key: Optional[str] = None, default_voice: str = "Charon"):
        self.api_key = get_live_gemini_api_key(api_key)
        self.default_voice = default_voice

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str = "Charon",
        language_code: str = "en",
        speech_rate: str = "-16%",
    ) -> bytes:
        """Synthesize text into studio-grade 48kHz mono 16-bit PCM WAV bytes."""
        if is_mock_mode():
            return self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            await self.synthesize_to_file(
                text=text,
                output_path=tmp_path,
                voice_id=voice_id,
                speech_rate=speech_rate,
            )
            return tmp_path.read_bytes()
        finally:
            tmp_path.unlink(missing_ok=True)

    async def synthesize_to_file(
        self,
        text: str,
        output_path: Path | str,
        voice_id: str = "Charon",
        speech_rate: str = "-16%",
        force_live: bool = False,
    ) -> Path:
        """Synthesize voiceover narration and write directly to disk as 48kHz WAV."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact Caching Guard (Rule 3): Reuse existing voice stem if already on disk
        if out.exists() and out.stat().st_size > 1000:
            logger.info(f"tts_voice_cache_hit: reusing existing voice stem {out.name} ({out.stat().st_size} bytes)")
            return out

        if is_mock_mode() and not force_live:
            out.write_bytes(self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4)))
            return out

        import imageio_ffmpeg
        from google import genai
        from google.genai import types

        eff_key = get_live_gemini_api_key(self.api_key)
        if not eff_key:
            raise RuntimeError("Gemini API key is missing for Gemini Audio TTS.")

        client = genai.Client(api_key=eff_key)
        # Select voice: Charon/Fenrir (male authoritative), Puck/Aoede/Kore (female or versatile)
        target_voice = voice_id if voice_id in ("Charon", "Puck", "Fenrir", "Aoede", "Kore") else self.default_voice

        # Documentary tone prompt wrapper
        prompt = (
            f"Read the following documentary narration in a measured, authoritative BBC / National Geographic "
            f"cadence with natural pauses and warm clarity:\n\n\"{text}\""
        )

        candidate_models = ["gemini-2.5-flash-preview-tts", "gemini-3.8-flash-tts", "gemini-2.5-pro-preview-tts"]
        pcm_bytes = None
        last_error = None

        for model_name in candidate_models:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=target_voice)
                            )
                        ),
                    ),
                )
                if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
                    for part in resp.candidates[0].content.parts:
                        if getattr(part, "inline_data", None) and part.inline_data.data:
                            pcm_bytes = part.inline_data.data
                            break
                if pcm_bytes:
                    break
            except Exception as ex:
                last_error = ex
                logger.warning(f"gemini_tts_model_failed: model='{model_name}' error='{ex}'")

        if not pcm_bytes:
            raise RuntimeError(f"Gemini Audio TTS synthesis failed: {last_error or 'No audio parts returned'}")

        # Convert 24kHz raw PCM to broadcast 48kHz mono 16-bit PCM WAV via FFmpeg
        with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as raw_tmp:
            raw_tmp_name = raw_tmp.name
            raw_tmp.write(pcm_bytes)

        try:
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            conv_cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-f", "s16le", "-ar", "24000", "-ac", "1",
                "-i", raw_tmp_name,
                "-ar", "48000", "-ac", "1",
                str(out),
            ]
            subprocess.run(conv_cmd, check=True, creationflags=flags)
        finally:
            Path(raw_tmp_name).unlink(missing_ok=True)

        if out.exists() and out.stat().st_size > 100:
            logger.info(f"gemini_tts_synthesized: {out.name} ({out.stat().st_size} bytes, voice={target_voice})")
            return out

        raise RuntimeError(f"Gemini Audio TTS conversion failed for {out.name}")

    def _generate_synthetic_wav(self, duration_seconds: float = 3.0, sample_rate: int = 48000) -> bytes:
        """Deterministic 48kHz mono 16-bit PCM WAV for mock testing."""
        buf = io.BytesIO()
        total_samples = int(sample_rate * duration_seconds)
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                val = int(800 * math.sin(2 * math.pi * 180 * t))
                frames.extend(struct.pack("<h", val))
            wav_file.writeframes(frames)
        return buf.getvalue()


__all__ = ["GeminiAudioTTSAdapter"]
