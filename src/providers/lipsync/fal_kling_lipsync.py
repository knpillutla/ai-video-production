"""Fal.ai Kling LipSync Adapter (Audio-to-Video).

High-fidelity singing and conversational lip-synchronization powered by Kling AI on Fal.ai
($0.014 per 5s cut) for final 4K broadcast masters.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.services.video_4k_encoder import ensure_video_4k

_KLING_LIPSYNC_ENDPOINT = "https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video"
_POLL_INTERVAL_S = 3.0
_POLL_MAX_ATTEMPTS = 60  # 180 seconds max


def _normalize_video_for_kling(input_video: Path) -> Path:
    """Ensure video resolution width & height are strictly between 512px and 2160px (standard 1080p)."""
    import subprocess
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    norm_video = input_video.parent / f"norm_{input_video.name}"
    if norm_video.is_file() and norm_video.stat().st_size > 10_000:
        return norm_video
    cmd = [
        ffmpeg_bin, "-y", "-i", str(input_video),
        "-vf", "scale='min(1920,iw)':-2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(norm_video)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return norm_video if norm_video.is_file() and norm_video.stat().st_size > 10_000 else input_video


class FalKlingLipsyncAdapter:
    """Kling LipSync Adapter via Fal.ai."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def sync_lips(
        self,
        video_path: Path | str,
        audio_path: Path | str,
        output_path: Path | str,
        force_live: bool = False,
        **kwargs: Any,
    ) -> Path:
        """Alias matching standard studio directorial calls."""
        return await self.lipsync_video(
            video_url=str(video_path),
            audio_path=Path(audio_path),
            output_path=output_path,
            force_live=force_live,
        )

    async def lipsync_video(
        self,
        video_url: str | Path,
        audio_path: Path,
        output_path: Path | str,
        force_live: bool = False,
        **kwargs: Any,
    ) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Rule 3)
        if out.exists() and out.stat().st_size > 10_000:
            ensure_video_4k(out)
            logger.info(f"fal_kling_lipsync_cache_hit: {out.name} ({out.stat().st_size} B, 4K)")
            return out

        url_file = out.with_suffix(".fal_url")
        if url_file.is_file():
            saved_u = url_file.read_text(encoding="utf-8").strip()
            if saved_u.startswith("http"):
                logger.info(f"fal_kling_lipsync_resuming_remote: {out.name} downloading from {saved_u}")
                async with httpx.AsyncClient(timeout=120.0) as dl_client:
                    dl_resp = await dl_client.get(saved_u)
                    if dl_resp.status_code == 200 and len(dl_resp.content) > 10_000:
                        out.write_bytes(dl_resp.content)
                        ensure_video_4k(out)
                        return out

        if is_mock_mode() and not force_live:
            return self._fallback_local(Path(video_url), audio_path, out)

        if not self.api_key:
            logger.warning("fal_kling_lipsync: no FAL_KEY — falling back to local passthrough")
            return self._fallback_local(Path(video_url), audio_path, out)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}

        # Normalize video resolution to <=1920x1080 (Kling LipSync rejects >2160px width)
        v_path = Path(video_url)
        eff_video_path = _normalize_video_for_kling(v_path) if v_path.is_file() else v_path

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                vid_fal_url = str(video_url) if str(video_url).startswith("http") else await upload_to_fal(eff_video_path, self.api_key)
                audio_fal_url = str(audio_path) if str(audio_path).startswith("http") else await upload_to_fal(Path(audio_path), self.api_key)
                payload = {"video_url": vid_fal_url, "audio_url": audio_fal_url}

                logger.info(f"fal_kling_lipsync_submit: video={out.name} (input_res={eff_video_path.name})")
                sub_resp = await client.post(_KLING_LIPSYNC_ENDPOINT, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201):
                    raise RuntimeError(f"Kling lipsync submission failed ({sub_resp.status_code}): {sub_resp.text[:200]}")

                sub_data = sub_resp.json()
                status_url: str = sub_data.get("status_url") or ""
                response_url: str = sub_data.get("response_url") or ""

                for attempt in range(1, _POLL_MAX_ATTEMPTS + 1):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    st_resp = await client.get(status_url, headers=headers)
                    if st_resp.status_code != 200:
                        continue
                    st = st_resp.json()
                    status = st.get("status")

                    if status == "COMPLETED":
                        res = (await client.get(response_url, headers=headers)).json()
                        result_video_url = (res.get("video") or {}).get("url") or (res.get("videos") or [{}])[0].get("url")
                        if not result_video_url:
                            raise RuntimeError(f"No video URL in Kling LipSync output: {res}")
                        dl_resp = await client.get(result_video_url, timeout=120.0)
                        out.write_bytes(dl_resp.content)
                        url_file.write_text(result_video_url, encoding="utf-8")
                        ensure_video_4k(out)
                        logger.info(f"fal_kling_lipsync_ok: {out.name} ({out.stat().st_size} B, 4K)")
                        return out

                    if status in ("FAILED", "CANCELLED"):
                        raise RuntimeError(f"Kling LipSync task {status}: {st}")

                raise TimeoutError("Fal Kling LipSync timed out waiting for completion")
            except Exception as ex:
                logger.error(f"fal_kling_lipsync_error: {ex}")
                raise

    def _fallback_local(self, video_path: Path, audio_path: Path, out_path: Path) -> Path:
        from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
        import subprocess
        ffmpeg_bin = get_ffmpeg_binary()
        cmd = [
            ffmpeg_bin, "-y", "-i", str(video_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path),
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_path


fal_kling_lipsync_adapter = FalKlingLipsyncAdapter()
__all__ = ["FalKlingLipsyncAdapter", "fal_kling_lipsync_adapter"]
