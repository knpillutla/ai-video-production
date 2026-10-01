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
        negative_prompt: str | None = None,
        settings: dict[str, Any] | None = None,
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
            raise ValueError("FAL_KEY is required for Wan 2.1 video motion generation")

        actual_url = image_url
        if not (actual_url.startswith("http://") or actual_url.startswith("https://")):
            local_p = Path(actual_url.replace("file://", ""))
            actual_url = await upload_to_fal(local_p, api_key=self.api_key)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {
            "prompt": motion_prompt.strip(),
            "image_url": actual_url,
        }
        if negative_prompt and negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt.strip()
        if settings and isinstance(settings, dict):
            for k, v in settings.items():
                if k not in payload and v is not None:
                    payload[k] = v

        job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
        status_url, response_url = None, None
        
        candidates = [
            job_sidecar,
            out.parent / f"raw_diff_{out.name}.fal_job.json",
            out.parent / f"{out.stem}.fal_job.json",
            out.parent / f"fal_diff_req_{out.stem}.json",
            out.parent / "fal_diff_req_p1.json",
            out.parent / "raw_diff_motion_p1.mp4.fal_job.json",
            out.parent / "motion_p1.mp4.fal_job.json",
        ]
        active_sidecar = job_sidecar
        for cand in candidates:
            if cand.exists():
                try:
                    job_data = json.loads(cand.read_text(encoding="utf-8"))
                    s_u = job_data.get("status_url")
                    r_u = job_data.get("response_url")
                    if s_u and r_u:
                        status_url, response_url = s_u, r_u
                        active_sidecar = cand
                        logger.info(f"fal_wan21_resuming_job: from {cand.name} response_url={response_url}")
                        break
                except Exception:
                    pass

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            if not status_url or not response_url:
                sub = await client.post(self.endpoint, headers=headers, json=payload)
                if sub.status_code not in (200, 201, 202):
                    raise RuntimeError(f"Wan 2.1 submit failed: {sub.status_code} - {sub.text[:200]}")
                sub_data = sub.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            for i in range(_POLL_MAX_ATTEMPTS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                try:
                    # Check response_url first: if 200, Fal generation is complete and has video URL
                    r_resp = await client.get(response_url, headers=headers)
                    if r_resp.status_code == 200:
                        final_res = r_resp.json()
                        vid_url = _extract_video_url(final_res)
                        if not vid_url:
                            raise RuntimeError(f"Could not extract video url: {final_res}")

                        for attempt in range(5):
                            try:
                                v_bytes = (await client.get(vid_url, timeout=180.0)).content
                                if len(v_bytes) > 5000:
                                    out.write_bytes(v_bytes)
                                    job_sidecar.unlink(missing_ok=True)
                                    logger.info(f"fal_wan21_ok: {out.name} ({len(v_bytes)} B)")
                                    return vid_url, out
                            except Exception as dl_err:
                                logger.warning(f"fal_wan21_download_retry: attempt {attempt+1}/5 failed ({dl_err}). Retrying...")
                                await asyncio.sleep(3.0)
                        raise RuntimeError(f"Failed to download Wan 2.1 video after 5 attempts from {vid_url}")

                    # If not yet complete, check status_url for failures
                    s_resp = await client.get(status_url, headers=headers)
                    if s_resp.status_code in (200, 202):
                        res_data = s_resp.json()
                        status = res_data.get("status")
                        if status in ("FAILED", "CANCELLED"):
                            job_sidecar.unlink(missing_ok=True)
                            raise RuntimeError(f"Wan 2.1 task failed: {res_data}")
                except Exception as poll_err:
                    if "Wan 2.1 task failed" in str(poll_err):
                        raise
                    logger.debug(f"fal_wan21_poll_status: {poll_err}")
                    continue

            job_sidecar.unlink(missing_ok=True)
            raise TimeoutError("Wan 2.1 generation timed out after 5 minutes")

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
