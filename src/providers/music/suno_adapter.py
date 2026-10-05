"""Suno v3.5 Pro API music adapter for commercially cleared original soundtracks.

Authoritative global audio engine for all studios and channels.
Enforces Rule 3 Idempotency: Tier 1 Disk Check & Tier 2 In-Flight Task Token Resumption.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, MusicProviderProtocol, is_mock_mode


class SunoMusicAdapter(MusicProviderProtocol):
    """Commercially cleared soundtrack generator powered by Suno v3.5 / sonic-v5 via MusicAPI.ai."""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or settings.media.suno_api_key or os.getenv("SUNO_API_KEY", "") or os.getenv("MUSICAPI_KEY", "") or os.getenv("MUSICAPI_API_KEY", "")
        self.endpoint = endpoint or "https://api.musicapi.ai/api/v1/sonic/create"

    async def _poll_task(self, client: Any, headers: Dict[str, str], task_id: str, poll_url: str) -> str:
        """Poll MusicAPI task status until ready (up to 180s)."""
        logger.info(f"suno_task_polling_started: task_id={task_id}")
        for poll_i in range(50):
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

    async def generate_track(
        self,
        genre: str = "cinematic comedy",
        mood: str = "playful energetic",
        duration_seconds: int = 120,
        lyrics: str = "",
        title: str = "",
        vocal_gender: str = "female",
        task_sidecar: Optional[Path] = None,
    ) -> str:
        """Request or resume an original commercial soundtrack from Suno v3.5 Pro."""
        if is_mock_mode():
            return f"https://cdn.cineai.studio/audio/suno_track_{abs(hash(genre)) % 10000}.mp3"

        if not self.api_key:
            raise RuntimeError("SUNO_API_KEY is not configured in .env. Please set a valid Suno / MusicAPI key.")

        client = HTTPClientPool.get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Rule 3 Tier 2: Check for in-flight task token sidecar before initiating new paid API call
        if task_sidecar and task_sidecar.is_file():
            try:
                state = json.loads(task_sidecar.read_text(encoding="utf-8"))
                saved_id = state.get("task_id")
                saved_poll = state.get("poll_url") or f"https://api.musicapi.ai/api/v1/sonic/task/{saved_id}"
                if saved_id:
                    logger.info(f"suno_inflight_resumption: found token task_id={saved_id} in {task_sidecar.name}")
                    print(f"[DECISION - SUNO IN-FLIGHT RESUMPTION] Polling existing task {saved_id} ($0.00 new spend)...")
                    return await self._poll_task(client, headers, saved_id, saved_poll)
            except Exception as resume_ex:
                logger.warning(f"suno_inflight_resume_failed: {resume_ex}, re-submitting task")
                task_sidecar.unlink(missing_ok=True)

        if lyrics:
            v_tag = f", {vocal_gender.lower()} vocals" if vocal_gender and vocal_gender.lower() in ("female", "male", "duet", "chorus") else ""
            tags_str = f"{genre}, {mood}{v_tag}"
            body = {
                "custom_mode": True, "prompt": lyrics, "tags": tags_str[:120],
                "title": (title or f"{genre[:50]} track")[:75], "mv": "sonic-v5",
            }
        else:
            is_ambient = any(w in (genre + " " + mood).lower() for w in ["ambient", "relax", "meditat", "sleep", "soundscape", "zen", "nature"])
            if is_ambient:
                body = {
                    "custom_mode": True,
                    "prompt": "[Instrumental Ambient Meditation]\n[432Hz Solfeggio Harmonic Resonance]\n[Joyful Uplifting Handpan & Singing Bowls]\n[Warm Velvet Ambient Pads & Celtic Harp]\n[Airy Nay Flute & Serene Soundbath]\n[Deep De-stressing & Restful Sleep Drone]\n[Outro: Infinite Peaceful Fade]",
                    "tags": f"{genre}, {mood}, zero solo guitar"[:120],
                    "title": (title or f"{genre[:50]} track")[:75], "mv": "sonic-v5",
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

            # Persist in-flight token sidecar immediately for crash resilience
            if task_sidecar:
                try:
                    task_sidecar.parent.mkdir(parents=True, exist_ok=True)
                    task_sidecar.write_text(json.dumps({
                        "task_id": task_id,
                        "poll_url": poll_url,
                        "created_at": time.time(),
                        "genre": genre,
                        "title": title,
                    }, indent=2), encoding="utf-8")
                    logger.info(f"suno_task_token_saved: {task_sidecar.name}")
                except Exception as save_ex:
                    logger.warning(f"suno_task_token_save_failed: {save_ex}")

            return await self._poll_task(client, headers, task_id, poll_url)
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
        episode_id: Optional[str] = None,
        force_live: bool = False,
    ) -> Path:
        """Generate and save background music with Rule 3 multi-tier idempotency."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Rule 3 Tier 1: Local Disk Check
        if out.exists() and out.stat().st_size > 1000:
            logger.info(f"suno_track_cache_hit: reusing existing soundtrack {out.name} ({out.stat().st_size} bytes)")
            return out

        url_sidecar = out.with_suffix(out.suffix + ".suno_url")
        task_sidecar = out.with_suffix(out.suffix + ".suno_task.json")
        audio_url = None

        # Rule 3 Tier 1.5: Persistent .suno_url Sidecar Re-download ($0.00 spend)
        if url_sidecar.is_file() and url_sidecar.stat().st_size > 10:
            cached_url = url_sidecar.read_text(encoding="utf-8").strip()
            if cached_url.startswith("http"):
                logger.info(f"suno_url_sidecar_hit: re-downloading existing audio from {cached_url} ($0.00 spend)")
                print(f"[DECISION - SUNO URL CACHE HIT] Re-downloading existing audio from {cached_url} ($0.00 spend)...")
                audio_url = cached_url

        # Rule 3 Tier 3: AudioVault Stem Cache Check (if no specific .suno_url exists for this episode)
        if not audio_url and not force_live:
            from src.services.audio_vault import audio_vault
            cached_stem = audio_vault.find_matching_stem(
                genre=genre, theme=mood, concept=title, tags=lyrics,
                vocal_gender=vocal_gender, min_similarity=0.70, current_episode_id=episode_id,
            )
            if cached_stem and cached_stem.is_file():
                import shutil
                shutil.copy2(cached_stem, out)
                logger.info(f"audio_vault_stem_reused: {cached_stem.name} -> {out.name}")
                return out

        if is_mock_mode():
            import wave
            with wave.open(str(out), "wb") as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b"\x00" * int(sample_rate * max(1.0, duration_seconds) * 4))
            return out

        try:
            if not audio_url:
                audio_url = await self.generate_track(
                    genre=genre, mood=mood, duration_seconds=int(duration_seconds),
                    lyrics=lyrics, title=title, vocal_gender=vocal_gender, task_sidecar=task_sidecar,
                )

            if not audio_url:
                raise RuntimeError("Suno v3.5 Pro failed: No audio URL received from MusicAPI endpoint.")

            try:
                url_sidecar.write_text(audio_url.strip(), encoding="utf-8")
                logger.info(f"suno_url_sidecar_saved: {url_sidecar.name}")
            except Exception as save_err:
                logger.warning(f"failed_to_save_suno_url_sidecar: {save_err}")

            client = HTTPClientPool.get_client()
            resp = await client.get(audio_url, follow_redirects=True, timeout=60.0)
            if resp.status_code != 200 or len(resp.content) < 1000:
                logger.warning(f"suno_url_download_empty_or_failed: status={resp.status_code} bytes={len(resp.content)}")
                from src.services.audio_vault import audio_vault
                vault_stem = audio_vault.find_matching_stem(
                    genre=genre, theme=mood, concept=title, tags=lyrics,
                    vocal_gender=vocal_gender, min_similarity=0.70, current_episode_id=episode_id,
                )
                if vault_stem and vault_stem.is_file():
                    import shutil
                    shutil.copy2(vault_stem, out)
                    logger.info(f"audio_vault_fallback_after_failed_download: {vault_stem.name} -> {out.name}")
                    return out
                raise RuntimeError(f"Failed to download Suno soundtrack from {audio_url} (HTTP {resp.status_code}, {len(resp.content)} bytes)")

            temp_mp3 = out.with_suffix(".temp.mp3")
            temp_mp3.write_bytes(resp.content)

            from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
            cmd = [get_ffmpeg_binary(), "-y", "-i", str(temp_mp3), "-ar", str(sample_rate), "-ac", "2", str(out)]
            proc = subprocess.run(cmd, capture_output=True)
            if temp_mp3.exists():
                temp_mp3.unlink()

            if proc.returncode != 0 or not out.exists() or out.stat().st_size < 1000:
                raise RuntimeError(f"FFmpeg audio transcoding to 48kHz WAV failed: {proc.stderr.decode(errors='ignore')}")

            if task_sidecar.exists():
                task_sidecar.unlink(missing_ok=True)
                logger.info(f"suno_task_token_cleared: {task_sidecar.name}")

            logger.info(f"suno_live_audio_downloaded: {out.name} ({out.stat().st_size} bytes)")
            from src.services.audio_vault import audio_vault
            audio_vault.register_stem(
                source_path=out, genre=genre, theme=mood, concept=title,
                tags=lyrics, title=title or genre, vocal_gender=vocal_gender,
                episode_id=episode_id,
            )
            return out
        except Exception as live_audio_err:
            logger.warning(f"suno_live_audio_failed_using_procedural_dsp: {live_audio_err}")
            from src.services.procedural_foley import synthesize_foley_stem
            synthesize_foley_stem(
                weather_type=genre, setting_type=mood, space="outdoor",
                duration_seconds=max(5.0, duration_seconds), output_path=out, sample_rate=sample_rate,
            )
            if out.exists() and out.stat().st_size > 1000:
                logger.info(f"procedural_dsp_stem_fallback_created: {out.name} ({out.stat().st_size} bytes)")
                return out
            raise RuntimeError(f"Audio synthesis failed: {live_audio_err}") from live_audio_err


__all__ = ["SunoMusicAdapter"]
