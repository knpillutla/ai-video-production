"""Fal.ai LatentSync beat-synchronized lipsync adapter.

Calls ``fal-ai/latentsync`` — beat-synchronized vocal lipsync matching
mouth motion to the Suno music track stem. Falls back to FalLivePortraitAdapter
when the Fal key is absent or LatentSync is unavailable.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal


_LATENTSYNC_ENDPOINT = "https://queue.fal.run/fal-ai/latentsync"
_POLL_INTERVAL_S = 3.0
_POLL_MAX_ATTEMPTS = 45   # 135 seconds max


class FalLatentSyncAdapter:
    """Beat-synchronized vocal lipsync via Fal LatentSync.

    Unlike LivePortrait (single talking-head phoneme animation), LatentSync
    synchronizes mouth motion to musical beat transients and lyrical phrases,
    making it appropriate for dance / song productions.

    Cost: ~$0.05–$0.10 per 10-second clip.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def lipsync_video(
        self,
        video_url: str,
        audio_path: Path,
        output_path: Path | str,
        force_live: bool = False,
    ) -> Path:
        """Apply beat-synchronized lipsync to a video using an audio stem.

        Args:
            video_url:   Remote URL of the Kling-generated video.
            audio_path:  Local path to the Suno audio stem (mp3/wav).
            output_path: Local path to write the lip-synced MP4.
            force_live:  Bypass mock mode.

        Returns:
            Local path of the lip-synced video. On failure, returns the
            original video path (kling raw) so the pipeline can continue.
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"fal_latentsync_cache_hit: {out.name} ({out.stat().st_size} B)")
            return out

        if is_mock_mode() and not force_live:
            return await self._fallback_liveportrait(video_url, audio_path, out)

        if not self.api_key:
            logger.warning("fal_latentsync: no FAL_KEY — falling back to LivePortrait")
            return await self._fallback_liveportrait(video_url, audio_path, out)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                # Upload audio to Fal storage so LatentSync can read it
                audio_fal_url = await upload_to_fal(audio_path, self.api_key)
                payload = {"video_url": video_url, "audio_url": audio_fal_url}

                sub_resp = await client.post(_LATENTSYNC_ENDPOINT, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201):
                    raise RuntimeError(f"LatentSync submit failed: {sub_resp.text[:200]}")
                sub_data = sub_resp.json()
                status_url: str = sub_data["status_url"]
                response_url: str = sub_data["response_url"]

                for attempt in range(_POLL_MAX_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    s = (await client.get(status_url, headers=headers)).json()
                    status = s.get("status")
                    if status == "COMPLETED":
                        r = (await client.get(response_url, headers=headers)).json()
                        res_url: str = r.get("video", {}).get("url", "")
                        if not res_url:
                            raise RuntimeError(f"LatentSync response missing video URL: {r}")
                        v_bytes = (await client.get(res_url, timeout=60.0)).content
                        out.write_bytes(v_bytes)
                        logger.info(f"fal_latentsync_ok: {out.name} ({out.stat().st_size} B)")
                        return out
                    if status in ("FAILED", "CANCELLED"):
                        logger.warning(f"fal_latentsync_api_failed: {s} — using Kling raw video")
                        break
                    if attempt % 3 == 0:
                        logger.info(f"fal_latentsync_poll: status={status} ({attempt * _POLL_INTERVAL_S:.0f}s)")

            except Exception as ex:
                logger.warning(f"fal_latentsync_error: {ex} — falling back to LivePortrait")

        return await self._fallback_liveportrait(video_url, audio_path, out)

    async def _fallback_liveportrait(
        self,
        video_url: str,
        audio_path: Path,
        out: Path,
    ) -> Path:
        """Fallback: download raw Kling video if LatentSync fails (skip lipsync)."""
        # If video_url is a real remote URL, download the Kling raw video as-is
        if video_url.startswith("http") and "fal" in video_url:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.get(video_url, timeout=60.0)
                    if resp.status_code == 200 and len(resp.content) > 10_000:
                        out.write_bytes(resp.content)
                        logger.info(f"latentsync_fallback_raw_kling: {out.name}")
                        return out
            except Exception as ex:
                logger.warning(f"latentsync_raw_download_failed: {ex}")
        # Last resort: LivePortrait talking-head lipsync
        from src.providers.lipsync.fal_liveportrait import FalLivePortraitAdapter
        from src.providers.fal_storage import upload_to_fal as _upload
        adapter = FalLivePortraitAdapter()
        # LivePortrait needs a face image not a video — generate a placeholder
        placeholder = out.parent / "lipsync_placeholder_frame.jpg"
        if not placeholder.exists():
            placeholder.write_bytes(b"")
        return await adapter.animate_avatar(placeholder, audio_path, out)


fal_latentsync_adapter = FalLatentSyncAdapter()

__all__ = ["FalLatentSyncAdapter", "fal_latentsync_adapter"]
