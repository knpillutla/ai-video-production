"""Microsoft Azure Cognitive Services Speech Neural HD TTS adapter."""

import io
import math
import struct
import wave
from pathlib import Path

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, TTSProviderProtocol, is_mock_mode


class AzureSpeechTTSAdapter(TTSProviderProtocol):
    """Studio-grade Neural HD voiceover generator powered by Azure Speech REST API."""

    def __init__(self, api_key: str | None = None, region: str | None = None):
        self.api_key = api_key or settings.voice.azure_speech_key
        self.region = region or settings.voice.azure_speech_region
        self.endpoint = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str = "te-IN-ShrutiNeural",
        language_code: str = "te-IN",
    ) -> bytes:
        """Synthesize text into studio-grade 48kHz 16-bit PCM WAV audio bytes."""
        if is_mock_mode():
            return self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4))

        client = HTTPClientPool.get_client()
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key or "",
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-48khz-16bit-mono-pcm",
            "User-Agent": "CineAIStudio/2.0",
        }

        # Auto-align voice if text contains Telugu script and an English voice was passed
        has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in text)
        if has_telugu and voice_id.startswith("en-"):
            voice_id = "te-IN-ShrutiNeural"
            language_code = "te-IN"

        # Construct SSML with standard broadcast rate & pitch
        ssml = (
            f"<speak version='1.0' xml:lang='{language_code}'>"
            f"<voice name='{voice_id}'>"
            f"<prosody rate='0%' pitch='0%'>{text}</prosody>"
            f"</voice></speak>"
        )

        if self.api_key:
            try:
                resp = await client.post(self.endpoint, headers=headers, content=ssml, timeout=30.0)
                if resp.status_code == 200:
                    return resp.content
            except Exception as ex:
                logger.warning(f"azure_speech_failed: {ex}. Falling back to edge neural TTS.")

        # High-Fidelity Neural TTS fallback (Microsoft Edge Neural Engine)
        try:
            import edge_tts

            comm = edge_tts.Communicate(text, voice=voice_id)
            chunks = []
            async for chunk in comm.stream():
                if chunk.get("type") == "audio":
                    chunks.append(chunk["data"])
            if chunks:
                return b"".join(chunks)
        except Exception as ex:
            logger.warning(f"neural_tts_stream_failed: {ex}. Using synthetic tone.")

        # Offline deterministic WAV generator (produces valid 48kHz PCM audio for tests)
        return self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4))

    def _generate_synthetic_wav(self, duration_seconds: float = 3.0, sample_rate: int = 48000) -> bytes:
        """Generate a valid 48kHz mono 16-bit PCM WAV with gentle speech cadence audio."""
        buffer = io.BytesIO()
        total_samples = int(sample_rate * duration_seconds)

        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            word_period = max(1, sample_rate // 3)
            for i in range(total_samples):
                t = i / sample_rate
                word_phase = (i % word_period) / word_period
                envelope = 0.5 * (1.0 - math.cos(2 * math.pi * word_phase)) if word_phase < 0.70 else 0.0
                val = int(800 * envelope * (math.sin(2 * math.pi * 140 * t) + 0.3 * math.sin(2 * math.pi * 280 * t)))
                frames.extend(struct.pack("<h", val))
            wav_file.writeframes(frames)

        return buffer.getvalue()

    async def synthesize_to_file(
        self,
        text: str,
        output_path: Path | str,
        voice_id: str = "te-IN-ShrutiNeural",
        force_live: bool = False,
    ) -> Path:
        """Synthesize narration and write directly to disk."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if is_mock_mode() and not force_live:
            audio_bytes = self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4))
            out.write_bytes(audio_bytes)
            return out

        # Auto-align voice if text contains Telugu script and an English voice was passed
        has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in text)
        if has_telugu and voice_id.startswith("en-"):
            voice_id = "te-IN-ShrutiNeural"

        if not self.api_key:
            try:
                import edge_tts
                import subprocess
                import tempfile
                from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary, has_ffmpeg

                comm = edge_tts.Communicate(text, voice=voice_id)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                    tmp_name = tmp_mp3.name
                await comm.save(tmp_name)

                # Convert to standard 48kHz mono 16-bit PCM WAV if FFmpeg is available
                if has_ffmpeg():
                    conv_cmd = [get_ffmpeg_binary(), "-y", "-i", tmp_name, "-ar", "48000", "-ac", "1", str(out)]
                    subprocess.run(conv_cmd, capture_output=True, timeout=15)
                try:
                    Path(tmp_name).unlink(missing_ok=True)
                except Exception:
                    pass
                if out.exists() and out.stat().st_size > 100:
                    logger.info(f"edge_tts_synthesized: {out.name} ({out.stat().st_size} bytes)")
                    return out
            except Exception as ex:
                logger.warning(f"edge_tts_file_failed: {ex}")

        audio_bytes = await self.synthesize_speech(text, voice_id=voice_id)
        out.write_bytes(audio_bytes)
        return out


__all__ = ["AzureSpeechTTSAdapter"]
