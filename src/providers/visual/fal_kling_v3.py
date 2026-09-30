"""Fal.ai Kling v3 4K Native Image-to-Video Synthesis Adapter.

Features:
- Native 4K UHD video diffusion directly from FAL.ai
- Endpoint: fal-ai/kling-video/v3/4k/image-to-video
- Input parameter: start_image_url
- Unmatched temporal consistency and fluid physical kinematics
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional
import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal

_KLING_V3_4K_ENDPOINT = "https://queue.fal.run/fal-ai/kling-video/v3/4k/image-to-video"
_POLL_INTERVAL_S = 4.0
_POLL_MAX_ATTEMPTS = 120  # 480s max for 4K diffusion


def _extract_video_url(payload: Any) -> Optional[str]:
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


class FalKlingV3Adapter:
    """Kling v3 4K Native Image-to-Video generation adapter on Fal.ai."""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or _fal_api_key()
        self.endpoint = endpoint or _KLING_V3_4K_ENDPOINT

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
        """Synthesize native 4K video motion from a static start image using Kling v3 4K."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 500_000:
            logger.info(f"fal_kling_v3_cache_hit: {out.name} ({out.stat().st_size} B)")
            return f"file://{out}", out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(out, duration)

        if not self.api_key:
            if force_live:
                raise ValueError("FAL_KEY is required for LIVE Kling v3 4K generation")
            logger.warning("fal_kling_v3: no FAL_KEY — using local placeholder")
            return await self._fallback_local(out, duration)

        actual_url = image_url
        if not (actual_url.startswith("http://") or actual_url.startswith("https://")):
            local_p = Path(actual_url.replace("file://", ""))
            actual_url = await upload_to_fal(local_p, api_key=self.api_key)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {
            "prompt": motion_prompt.strip(),
            "start_image_url": actual_url,
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
                        logger.info(f"fal_kling_v3_resuming_job: from {cand.name} response_url={response_url}")
                        break
                except Exception:
                    pass

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            if not status_url or not response_url:
                sub = await client.post(self.endpoint, headers=headers, json=payload)
                if sub.status_code not in (200, 201, 202):
                    raise RuntimeError(f"Kling v3 4K submit failed: {sub.status_code} - {sub.text[:200]}")
                sub_data = sub.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            for i in range(_POLL_MAX_ATTEMPTS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                try:
                    # Check response_url first: if 200, Kling v3 generation is complete and has video URL
                    r_resp = await client.get(response_url, headers=headers)
                    if r_resp.status_code == 200:
                        final_res = r_resp.json()
                        vid_url = _extract_video_url(final_res)
                        if not vid_url:
                            raise RuntimeError(f"Could not extract Kling v3 video url: {final_res}")

                        for attempt in range(5):
                            try:
                                v_bytes = (await client.get(vid_url, timeout=180.0)).content
                                if len(v_bytes) > 5000:
                                    out.write_bytes(v_bytes)
                                    job_sidecar.unlink(missing_ok=True)
                                    logger.info(f"fal_kling_v3_ok: {out.name} ({len(v_bytes)} B)")
                                    return vid_url, out
                            except Exception as dl_err:
                                logger.warning(f"fal_kling_v3_download_retry: attempt {attempt+1}/5 failed ({dl_err}). Retrying...")
                                await asyncio.sleep(3.0)
                        raise RuntimeError(f"Failed to download Kling v3 video after 5 attempts from {vid_url}")

                    # If not yet complete, check status_url for failures
                    s_resp = await client.get(status_url, headers=headers)
                    if s_resp.status_code in (200, 202):
                        res_data = s_resp.json()
                        status = res_data.get("status")
                        if status in ("FAILED", "CANCELLED"):
                            job_sidecar.unlink(missing_ok=True)
                            raise RuntimeError(f"Kling v3 4K task failed: {res_data}")
                except Exception as poll_err:
                    if "Kling v3 4K task failed" in str(poll_err):
                        raise
                    logger.debug(f"fal_kling_v3_poll_status: {poll_err}")
                    continue

            job_sidecar.unlink(missing_ok=True)
            raise TimeoutError("Kling v3 4K generation timed out after 5 minutes")

    async def _fallback_local(self, out: Path, duration: int) -> tuple[str, Path]:
        import subprocess
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            exe, "-y",
            "-f", "lavfi", "-i", f"color=c=0x0f172a:s=3840x2160:d={duration}:r=24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return f"file://{out}", out


fal_kling_v3_adapter = FalKlingV3Adapter()
__all__ = ["FalKlingV3Adapter", "fal_kling_v3_adapter"]
