"""Suno v3.5 Pro API music adapter for commercially cleared original soundtracks.

Authoritative global audio engine for all studios and channels.
Zero synthetic/procedural local fallbacks — fails fast with actionable errors.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, MusicProviderProtocol, is_mock_mode


class SunoMusicAdapter(MusicProviderProtocol):
    """Commercially cleared soundtrack generator powered by Suno v3.5 / sonic-v5 via MusicAPI.ai."""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = (
            api_key
            or settings.media.suno_api_key
            or os.getenv("SUNO_API_KEY", "")
            or os.getenv("MUSICAPI_KEY", "")
            or os.getenv("MUSICAPI_API_KEY", "")
        )
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
        """Request an original commercial soundtrack from Suno v3.5 Pro via MusicAPI.ai."""
        if is_mock_mode():
            return f"https://cdn.cineai.studio/audio/suno_track_{abs(hash(genre)) % 10000}.mp3"

        if not self.api_key:
            raise RuntimeError("SUNO_API_KEY is not configured in .env. Please set a valid Suno / MusicAPI key.")

        client = HTTPClientPool.get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

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

        try:
            resp = await client.post(self.endpoint, headers=headers, json=body, timeout=30.0)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"MusicAPI returned HTTP {resp.status_code}: {resp.text[:300]}")

            data = resp.json()
            if "audio_url" in data and data["audio_url"]:
                return str(data["audio_url"])

            task_id = data.get("task_id")
            if not task_id and isinstance(data.get("data"), dict):
                task_id = data["data"].get("task_id")
            elif not task_id and isinstance(data.get("data"), str):
                task_id = data["data"]

            if not task_id:
                raise RuntimeError(f"MusicAPI returned no task_id or audio_url: {data}")

            poll_url = f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}"
            logger.info(f"suno_task_polling_started: task_id={task_id}")

            for poll_i in range(50):  # Poll up to ~180s
                await asyncio.sleep(3.5)
                task_resp = await client.get(poll_url, headers=headers, timeout=15.0)

                if task_resp.status_code == 202:
                    logger.debug(f"suno_task_in_progress: poll={poll_i+1} status=202")
                    continue

                if task_resp.status_code == 200:
                    t_data = task_resp.json()
                    if t_data.get("type") == "not_ready":
                        logger.debug(f"suno_task_not_ready: poll={poll_i+1}")
                        continue

                    items = t_data.get("data")
                    if isinstance(items, list) and items:
                        for entry in items:
                            if entry.get("state") in ("failed", "error"):
                                raise RuntimeError(f"Suno synthesis task failed: {entry.get('error') or 'Unknown error'}")
                            if entry.get("audio_url"):
                                logger.info(f"suno_track_ready: poll={poll_i+1} state={entry.get('state')} url={entry['audio_url']}")
                                return str(entry["audio_url"])
                    elif isinstance(items, dict):
                        if items.get("audio_url"):
                            logger.info(f"suno_track_ready: poll={poll_i+1} state={items.get('state')} url={items['audio_url']}")
                            return str(items["audio_url"])
                    if t_data.get("audio_url"):
                        logger.info(f"suno_track_ready: poll={poll_i+1} url={t_data['audio_url']}")
                        return str(t_data["audio_url"])

            raise TimeoutError(f"Suno synthesis timed out after 180s for task_id: {task_id}")
        except Exception as ex:
            logger.error(f"musicapi_suno_call_failed: {ex}")
            raise RuntimeError(f"Suno Music Generation failed: {ex}") from ex

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

        # Song Deduplication & Disk Cache Guard (Directive 3)
        if out.exists() and out.stat().st_size > 1000:
            logger.info(f"suno_track_cache_hit: reusing existing soundtrack {out.name} ({out.stat().st_size} bytes)")
            return out

        # AudioVault Stem Cache Check
        if not force_live:
            from src.services.audio_vault import audio_vault
            cached_stem = audio_vault.find_matching_stem(
                genre=genre, theme=mood, concept=title, tags=lyrics,
                vocal_gender=vocal_gender, min_similarity=0.70,
            )
            if cached_stem and cached_stem.is_file():
                import shutil
                shutil.copy2(cached_stem, out)
                logger.info(f"audio_vault_stem_reused: {cached_stem.name} -> {out.name}")
                return out

        if is_mock_mode():
            # In offline mock test mode, create deterministic silent test stem
            import wave
            with wave.open(str(out), "wb") as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b"\x00" * int(sample_rate * max(1.0, duration_seconds) * 4))
            return out

        audio_url = await self.generate_track(
            genre=genre,
            mood=mood,
            duration_seconds=int(duration_seconds),
            lyrics=lyrics,
            title=title,
            vocal_gender=vocal_gender,
        )

        if not audio_url:
            raise RuntimeError("Suno v3.5 Pro failed: No audio URL received from MusicAPI endpoint.")

        client = HTTPClientPool.get_client()
        resp = await client.get(audio_url, follow_redirects=True, timeout=60.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download Suno soundtrack from {audio_url} (HTTP {resp.status_code})")

        temp_mp3 = out.with_suffix(".temp.mp3")
        temp_mp3.write_bytes(resp.content)

        from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
        ffmpeg_bin = get_ffmpeg_binary()
        cmd = [
            ffmpeg_bin, "-y", "-i", str(temp_mp3),
            "-ar", str(sample_rate), "-ac", "2", str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True)
        if temp_mp3.exists():
            temp_mp3.unlink()

        if proc.returncode != 0 or not out.exists() or out.stat().st_size < 1000:
            raise RuntimeError(f"FFmpeg audio transcoding to 48kHz WAV failed: {proc.stderr.decode(errors='ignore')}")

        logger.info(f"suno_live_audio_downloaded: {out.name} ({out.stat().st_size} bytes)")
        from src.services.audio_vault import audio_vault
        audio_vault.register_stem(
            source_path=out, genre=genre, theme=mood, concept=title,
            tags=lyrics, title=title or genre, vocal_gender=vocal_gender,
        )
        return out


__all__ = ["SunoMusicAdapter"]
