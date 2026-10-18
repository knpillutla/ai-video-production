"""Local Kokoro-82M ONNX TTS Adapter for zero-cost, 100% offline voiceover narration."""

import io
import math
import struct
import subprocess
import sys
import tempfile
import urllib.request
import wave
from pathlib import Path
from typing import Optional

from src.core.telemetry import logger
from src.providers.base import TTSProviderProtocol, is_mock_mode

MODEL_DIR = Path("models/kokoro")
ONNX_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json"


class KokoroTTSAdapter(TTSProviderProtocol):
    """Studio-grade 100% offline local TTS powered by Kokoro-82M ONNX."""

    def __init__(self, default_voice: str = "bm_george"):
        self.default_voice = default_voice
        self._kokoro = None

    def _ensure_models(self) -> tuple[Path, Path]:
        """Ensure Kokoro ONNX model and voice vectors exist locally, downloading if necessary."""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        onnx_path = MODEL_DIR / "kokoro-v0_19.onnx"
        voices_path = MODEL_DIR / "voices.json"

        if not onnx_path.exists() or onnx_path.stat().st_size < 1000000:
            logger.info("kokoro_downloading_model: fetching kokoro-v0_19.onnx from github release...")
            urllib.request.urlretrieve(ONNX_URL, str(onnx_path))
            logger.info("kokoro_model_downloaded: kokoro-v0_19.onnx ready")

        if not voices_path.exists() or voices_path.stat().st_size < 10000:
            logger.info("kokoro_downloading_voices: fetching voices.json...")
            urllib.request.urlretrieve(VOICES_URL, str(voices_path))
            logger.info("kokoro_voices_downloaded: voices.json ready")

        return onnx_path, voices_path

    def _get_kokoro_instance(self):
        """Lazy-initialize Kokoro ONNX session."""
        if self._kokoro is None:
            from kokoro_onnx import Kokoro
            onnx_path, voices_path = self._ensure_models()
            self._kokoro = Kokoro(str(onnx_path), str(voices_path))
        return self._kokoro

    async def synthesize_speech(
        self,
        text: str,
        voice_id: str = "bm_george",
        language_code: str = "en",
        speech_rate: str = "-16%",
    ) -> bytes:
        """Synthesize text into studio-grade 48kHz mono 16-bit PCM WAV bytes."""
        if is_mock_mode():
            return self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            await self.synthesize_to_file(text, output_path=tmp_path, voice_id=voice_id)
            return tmp_path.read_bytes()
        finally:
            tmp_path.unlink(missing_ok=True)

    async def synthesize_to_file(
        self,
        text: str,
        output_path: Path | str,
        voice_id: str = "bm_george",
        speech_rate: str = "-16%",
        force_live: bool = False,
    ) -> Path:
        """Synthesize voiceover narration locally on CPU and save as broadcast 48kHz WAV."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 1000:
            logger.info(f"kokoro_cache_hit: reusing existing stem {out.name} ({out.stat().st_size} bytes)")
            return out

        if is_mock_mode() and not force_live:
            out.write_bytes(self._generate_synthetic_wav(duration_seconds=max(2.0, len(text.split()) * 0.4)))
            return out

        import imageio_ffmpeg
        import soundfile as sf

        kokoro = self._get_kokoro_instance()
        target_voice = voice_id or self.default_voice

        # Calculate speed multiplier
        speed = 1.0
        if "-16%" in speech_rate:
            speed = 0.88
        elif "-10%" in speech_rate:
            speed = 0.92

        samples, sample_rate = kokoro.create(text, voice=target_voice, speed=speed, lang="en-us")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as raw_tmp:
            raw_tmp_name = raw_tmp.name
            sf.write(raw_tmp_name, samples, sample_rate)

        try:
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            conv_cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-i", raw_tmp_name,
                "-ar", "48000", "-ac", "1",
                str(out),
            ]
            subprocess.run(conv_cmd, check=True, creationflags=flags)
        finally:
            Path(raw_tmp_name).unlink(missing_ok=True)

        if out.exists() and out.stat().st_size > 100:
            logger.info(f"kokoro_synthesized: {out.name} ({out.stat().st_size} bytes, voice={target_voice})")
            return out

        raise RuntimeError(f"Kokoro TTS generation failed for {out.name}")

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


__all__ = ["KokoroTTSAdapter"]
