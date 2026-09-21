"""Suno v3.5 Pro API music adapter for commercially cleared original soundtracks."""

import asyncio
import math
import struct
import wave
from pathlib import Path

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, MusicProviderProtocol, is_mock_mode


class SunoMusicAdapter(MusicProviderProtocol):
    """Commercially cleared soundtrack generator powered by Suno v3.5 / sonic-v5 via MusicAPI.ai."""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self.api_key = api_key or settings.media.suno_api_key
        # Target MusicAPI.ai Sonic / Suno REST API
        self.endpoint = endpoint or "https://api.musicapi.ai/api/v1/sonic/create"

    async def generate_track(
        self,
        genre: str = "cinematic comedy",
        mood: str = "playful energetic",
        duration_seconds: int = 120,
        lyrics: str = "",
        title: str = "",
        vocal_gender: str = "female",
    ) -> str:
        """Request an original commercial soundtrack from Suno via MusicAPI.ai."""
        if is_mock_mode():
            return f"https://cdn.cineai.studio/audio/suno_track_{abs(hash(genre)) % 10000}.mp3"

        client = HTTPClientPool.get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Content-Type": "application/json",
        }

        # Structure payload according to MusicAPI.ai specifications
        if lyrics:
            tags_str = f"{genre}, {mood}"
            if vocal_gender and vocal_gender.lower() in ("female", "male", "duet"):
                tags_str = f"{tags_str}, {vocal_gender.lower()} vocals"
            elif vocal_gender and "chorus" in vocal_gender.lower():
                tags_str = f"{tags_str}, chorus vocals"

            body = {
                "custom_mode": True,
                "prompt": lyrics,
                "tags": tags_str,
                "title": title or f"{genre} track",
                "mv": "sonic-v5",
            }
        else:
            body = {
                "custom_mode": False,
                "mv": "sonic-v5",
                "gpt_description_prompt": f"Instrumental {genre}, {mood}, cinematic high-production mix",
            }

        if self.api_key:
            try:
                resp = await client.post(self.endpoint, headers=headers, json=body, timeout=30.0)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    # Immediate audio url check
                    if "audio_url" in data:
                        return data["audio_url"]

                    # MusicAPI.ai task-based async polling
                    task_id = data.get("task_id")
                    if not task_id and isinstance(data.get("data"), dict):
                        task_id = data["data"].get("task_id")
                    elif not task_id and isinstance(data.get("data"), str):
                        task_id = data["data"]
                    if task_id:
                        poll_url = f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}"
                        for poll_i in range(40):  # Poll up to ~180s (MusicAPI→Suno custom lyrics takes 60-120s)
                            await asyncio.sleep(4.5)
                            task_resp = await client.get(poll_url, headers=headers, timeout=15.0)
                            if task_resp.status_code == 200:
                                t_data = task_resp.json()
                                items = t_data.get("data")
                                if isinstance(items, list) and items:
                                    entry = items[0]
                                    if entry.get("state") in ("succeeded", "success", "completed"):
                                        if entry.get("audio_url"):
                                            return entry["audio_url"]
                                elif isinstance(items, dict):
                                    if items.get("state") in ("succeeded", "success", "completed") and items.get("audio_url"):
                                        return items["audio_url"]
                                if t_data.get("state") in ("succeeded", "success", "completed") and t_data.get("audio_url"):
                                    return t_data["audio_url"]
            except Exception as ex:
                logger.warning(f"musicapi_suno_call_failed: {ex}. Using local synthetic soundtrack fallback.")

        return ""

    async def generate_to_file(
        self,
        output_path: Path | str,
        genre: str = "cinematic comedy",
        mood: str = "playful energetic",
        duration_seconds: float = 12.0,
        sample_rate: int = 48000,
        lyrics: str = "",
        vocal_gender: str = "female",
        title: str = "",
        force_live: bool = False,
    ) -> Path:
        """Generate and save background music to a valid 48kHz stereo WAV file."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Song Deduplication Guard: If song already exists for this project, reuse it and never invoke Suno again
        if out.exists() and out.stat().st_size > 50000:
            logger.info(f"suno_track_cache_hit: reusing existing soundtrack {out.name} ({out.stat().st_size} bytes)")
            return out

        if (force_live or lyrics) and self.api_key and not is_mock_mode():
            try:
                audio_url = await self.generate_track(
                    genre=genre,
                    mood=mood,
                    duration_seconds=int(duration_seconds),
                    lyrics=lyrics,
                    title=title,
                    vocal_gender=vocal_gender,
                )
                if audio_url and not is_mock_mode():
                    client = HTTPClientPool.get_client()
                    resp = await client.get(audio_url, timeout=60.0)
                    if resp.status_code == 200:
                        temp_mp3 = out.with_suffix(".temp.mp3")
                        temp_mp3.write_bytes(resp.content)
                        from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
                        import subprocess
                        ffmpeg_bin = get_ffmpeg_binary()
                        cmd = [
                            ffmpeg_bin, "-y", "-i", str(temp_mp3),
                            "-ar", str(sample_rate), "-ac", "2", str(out)
                        ]
                        proc = subprocess.run(cmd, capture_output=True)
                        if temp_mp3.exists():
                            temp_mp3.unlink()
                        if proc.returncode == 0 and out.exists() and out.stat().st_size > 1000:
                            logger.info(f"suno_live_audio_downloaded: {out.name} ({out.stat().st_size} bytes)")
                            return out
            except Exception as ex:
                logger.warning(f"suno_live_download_failed: {ex}. Falling back to local synthesizer.")

        total_samples = int(sample_rate * duration_seconds)
        is_nature_rain = any(
            k in genre.lower()
            for k in (
                "rain", "drop", "nature", "stream", "forest", "ambient", "thunder",
                "water", "waterfall", "walk", "river", "ocean", "canopy", "mountain"
            )
        )

        with wave.open(str(out), "wb") as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            if is_nature_rain:
                try:
                    import numpy as np

                    t = np.linspace(0, duration_seconds, total_samples, endpoint=False)
                    nature_bed = (
                        0.28 * np.sin(2 * np.pi * 65 * t)
                        + 0.16 * np.sin(2 * np.pi * 130 * t)
                        + 0.12 * np.sin(2 * np.pi * 432 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t))
                    )
                    interval = sample_rate // 14
                    pitches = np.array([1650.0, 2200.0, 1850.0, 2800.0, 1420.0, 2450.0, 1980.0, 3100.0])
                    indices = np.arange(total_samples)
                    offset = (indices % interval) / sample_rate
                    drop_step = (indices // interval) % len(pitches)
                    drop_freq = pitches[drop_step]
                    drop_decay = np.exp(-60.0 * offset)
                    drop_val = drop_decay * np.sin(2 * np.pi * drop_freq * offset)

                    sig_l = np.clip((5000 * (nature_bed * 0.45 + drop_val * 0.55) * 0.85), -32767, 32767).astype(np.int16)
                    sig_r = np.clip((5000 * (nature_bed * 0.45 + drop_val * 0.55) * 0.65), -32767, 32767).astype(np.int16)
                    wav_file.writeframes(np.column_stack((sig_l, sig_r)).tobytes())
                    return out
                except Exception as ex:
                    logger.warning(f"numpy_nature_audio_fallback: {ex}")

            is_ambient = any(
                k in genre.lower()
                for k in ("ambient", "lofi", "piano", "calm", "relax", "peaceful", "scenic", "acoustic", "travel")
            )
            if is_ambient:
                pitches = [196.00, 261.63, 329.63, 392.00]  # G3, C4, E4, G4 - Warm peaceful chord
                beat_len = max(1, sample_rate)  # 60 BPM calm cadence
                decay_rate = 1.8
                max_amp = 4000
            else:
                pitches = [261.63, 329.63, 392.00, 523.25, 440.00, 329.63]
                beat_len = max(1, sample_rate // 4)  # 120 BPM tempo
                decay_rate = 4.5
                max_amp = 5000

            frames = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                step = (i // beat_len) % len(pitches)
                freq = pitches[step]
                decay = math.exp(-decay_rate * ((i % beat_len) / beat_len))

                base_tone = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
                bass_tone = 0.4 * math.sin(2 * math.pi * (freq / 2) * t)

                sample_val = int(max_amp * decay * (base_tone + bass_tone))
                sig_left = int(sample_val * (0.85 if step % 2 == 0 else 0.65))
                sig_right = int(sample_val * (0.65 if step % 2 == 0 else 0.85))
                frames.extend(struct.pack("<hh", sig_left, sig_right))

            wav_file.writeframes(frames)

        return out


__all__ = ["SunoMusicAdapter"]
