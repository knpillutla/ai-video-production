"""Fal.ai Alibaba Wan 2.1 Video Motion Synthesis Adapter.

Features:
- Fast turnaround (~60s generation time)
- Flat rate: $0.40 per 5s clip
- Endpoint: fal-ai/wan-i2v
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal

_WAN21_ENDPOINT = "https://queue.fal.run/fal-ai/wan-i2v"
_POLL_INTERVAL_S = 3.0
_POLL_MAX_ATTEMPTS = 120


def _extract_video_url(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for k in ("video", "output", "file"):
        v = payload.get(k)
        if isinstance(v, dict) and v.get("url"):
            return str(v["url"])
        if isinstance(v, str) and v.startswith("http"):
            return v
    for v in payload.values():
        if isinstance(v, str) and (v.endswith(".mp4") or "fal.media" in v):
            return v
        if isinstance(v, dict) and isinstance(v.get("url"), str) and ("fal.media" in v["url"] or v["url"].endswith(".mp4")):
            return str(v["url"])
    return None


class FalWan21Adapter:
    """Alibaba Wan 2.1 Image-to-Video generation adapter on Fal.ai."""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()
        self.endpoint = endpoint or _WAN21_ENDPOINT

    async def generate_video(
        self,
        image_url: str,
        motion_prompt: str,
        output_path: Path | str,
        duration: int = 5,
        force_live: bool = False,
    ) -> tuple[str, Path]:
        """Synthesize 5s motion using Alibaba Wan 2.1."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 500_000:
            logger.info(f"fal_wan21_cache_hit: {out.name} ({out.stat().st_size} B)")
            return f"file://{out}", out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(out, duration)

        if not self.api_key:
            if force_live:
                raise ValueError("FAL_KEY is required for LIVE Wan 2.1 generation")
            logger.warning("fal_wan21: no FAL_KEY — using local placeholder")
            return await self._fallback_local(out, duration)

        actual_url = image_url
        if not (actual_url.startswith("http://") or actual_url.startswith("https://")):
            local_p = Path(actual_url.replace("file://", ""))
            actual_url = await upload_to_fal(local_p, api_key=self.api_key)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload = {"prompt": motion_prompt, "image_url": actual_url}

        job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
        status_url, response_url = None, None
        if job_sidecar.exists():
            try:
                job_data = json.loads(job_sidecar.read_text(encoding="utf-8"))
                status_url = job_data.get("status_url")
                response_url = job_data.get("response_url")
            except Exception:
                status_url, response_url = None, None

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            if not status_url or not response_url:
                sub = await client.post(self.endpoint, headers=headers, json=payload)
                if sub.status_code not in (200, 201, 202):
                    raise RuntimeError(f"Wan 2.1 submit failed: {sub.status_code} - {sub.text[:200]}")
                sub_data = sub.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            for i in range(_POLL_MAX_ATTEMPTS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                s_resp = await client.get(status_url, headers=headers, params={"logs": "1"})
                res_data = s_resp.json()
                status = res_data.get("status")

                if status == "COMPLETED":
                    r_resp = await client.get(response_url, headers=headers)
                    final_res = r_resp.json()
                    vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                    if not vid_url:
                        raise RuntimeError(f"Could not extract video url: {final_res}")

                    v_bytes = (await client.get(vid_url, timeout=90.0)).content
                    out.write_bytes(v_bytes)
                    job_sidecar.unlink(missing_ok=True)
                    logger.info(f"fal_wan21_ok: {out.name} ({len(v_bytes)} B)")
                    return vid_url, out

                if status in ("FAILED", "CANCELLED"):
                    job_sidecar.unlink(missing_ok=True)
                    raise RuntimeError(f"Wan 2.1 task failed: {res_data}")

            job_sidecar.unlink(missing_ok=True)
            raise TimeoutError("Wan 2.1 generation timed out")

    async def _fallback_local(self, out: Path, duration: int) -> tuple[str, Path]:
        import subprocess
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            exe, "-y",
            "-f", "lavfi", "-i", f"color=c=0x0f172a:s=1280x720:d={duration}:r=24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return f"file://{out}", out


fal_wan21_adapter = FalWan21Adapter()

__all__ = ["FalWan21Adapter", "fal_wan21_adapter"]
