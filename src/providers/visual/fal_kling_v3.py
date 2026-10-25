"""Fal.ai Kling v3 4K Native Image-to-Video Synthesis Adapter.

Features:
- Native 4K UHD video diffusion directly from FAL.ai
- Endpoint: fal-ai/kling-video/v3/4k/image-to-video
- Input parameter: start_image_url
- Universal Artifact Caching & Idempotent Resumption (Rule 3)
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
from src.services.video_4k_encoder import ensure_video_4k

_KLING_V3_4K_ENDPOINT = "https://queue.fal.run/fal-ai/kling-video/v3/4k/image-to-video"
_POLL_INTERVAL_S = 4.0
_POLL_MAX_ATTEMPTS = 150  # 600s (10 min) for 4K video diffusion queues


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


def _find_saved_video_url(out: Path, req_file: Optional[Path | str] = None) -> Optional[str]:
    clean_stem = out.stem.replace("raw_diff_", "")
    candidates = [
        out.with_suffix(out.suffix + ".fal_meta.json"),
        out.with_suffix(".fal_meta.json"),
        out.with_suffix(out.suffix + ".fal_url"),
        out.with_suffix(".fal_url"),
        out.parent / f"raw_diff_{out.name}.fal_meta.json",
        out.parent / f"raw_diff_{out.name}.fal_url",
        out.parent / f"{clean_stem}.mp4.fal_meta.json",
        out.parent / f"{clean_stem}.fal_meta.json",
        out.parent / f"{clean_stem}.fal_url",
        out.parent / f"fal_motion_req_{clean_stem}.json",
        out.parent / f"fal_diff_req_{clean_stem}.json",
    ]
    if req_file:
        candidates.insert(0, Path(req_file))
    for cand in candidates:
        if cand.is_file():
            try:
                txt = cand.read_text(encoding="utf-8").strip()
                if txt.startswith("http://") or txt.startswith("https://"):
                    return txt
                data = json.loads(txt)
                u = data.get("video_url") or data.get("url")
                if u and isinstance(u, str) and (u.startswith("http://") or u.startswith("https://")):
                    return u
            except Exception:
                pass
    return None


def _persist_video_url(out: Path, vid_url: str, response_url: Optional[str] = None, status_url: Optional[str] = None, req_file: Optional[Path | str] = None) -> None:
    data = {"video_url": vid_url, "response_url": response_url, "status_url": status_url}
    dumped = json.dumps(data, indent=2)
    clean_stem = out.stem.replace("raw_diff_", "")
    targets = [
        out.with_suffix(out.suffix + ".fal_meta.json"),
        out.with_suffix(".fal_meta.json"),
        out.parent / f"{clean_stem}.mp4.fal_meta.json",
        out.parent / f"raw_diff_{clean_stem}.mp4.fal_meta.json",
    ]
    if req_file:
        targets.append(Path(req_file))
    for t in targets:
        try:
            t.write_text(dumped, encoding="utf-8")
        except Exception:
            pass
    for u_path in (out.with_suffix(out.suffix + ".fal_url"), out.with_suffix(".fal_url"), out.parent / f"{clean_stem}.fal_url"):
        try:
            u_path.write_text(vid_url.strip(), encoding="utf-8")
        except Exception:
            pass


def _persist_job_tokens(sidecar: Path, status_url: str, response_url: str, req_file: Optional[Path | str] = None) -> None:
    payload = json.dumps({"status_url": status_url, "response_url": response_url}, indent=2)
    for target in (sidecar, req_file):
        if target:
            try:
                Path(target).write_text(payload, encoding="utf-8")
            except Exception:
                pass


async def _download_video_stream(client: httpx.AsyncClient, vid_url: str, out: Path, max_attempts: int = 5) -> bool:
    for attempt in range(max_attempts):
        try:
            v_bytes = (await client.get(vid_url, timeout=180.0)).content
            if len(v_bytes) > 5000:
                out.write_bytes(v_bytes)
                ensure_video_4k(out)
                return True
        except Exception as dl_err:
            logger.warning(f"fal_kling_v3_dl_retry: attempt {attempt+1}/{max_attempts} failed ({dl_err})")
            await asyncio.sleep(3.0)
    return False


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
        req_file: Optional[Path | str] = None,
    ) -> tuple[str, Path]:
        """Synthesize native 4K video motion from a static start image using Kling v3 4K."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 500_000:
            ensure_video_4k(out)
            logger.info(f"fal_kling_v3_cache_hit [model=fal-ai/kling-video/v3/4k/image-to-video]: {out.name} ({out.stat().st_size} B, 4K)")
            return f"file://{out}", out

        saved_url = _find_saved_video_url(out, req_file)
        if saved_url:
            logger.info(f"fal_kling_v3_reusing_remote_url [model=fal-ai/kling-video/v3/4k/image-to-video]: {out.name} downloading from {saved_url} ($0.00 spend)")
            async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0, read=180.0)) as dl_client:
                if await _download_video_stream(dl_client, saved_url, out):
                    logger.info(f"fal_kling_v3_redownload_ok [model=fal-ai/kling-video/v3/4k/image-to-video]: {out.name} ({out.stat().st_size} B) ($0.00 spend)")
                    return saved_url, out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(out, duration)

        if not self.api_key:
            raise ValueError("FAL_KEY is required for Kling v3 4K video motion generation")

        actual_url = image_url
        if not (actual_url.startswith("http://") or actual_url.startswith("https://")):
            local_p = Path(actual_url.replace("file://", ""))
            actual_url = await upload_to_fal(local_p, api_key=self.api_key)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {"prompt": motion_prompt.strip(), "start_image_url": actual_url}
        if negative_prompt and negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt.strip()
        if settings and isinstance(settings, dict):
            for k, v in settings.items():
                if k not in payload and v is not None:
                    payload[k] = v

        job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
        clean_stem = out.stem.replace("raw_diff_", "")
        status_url, response_url = None, None
        candidates = [
            job_sidecar,
            Path(req_file) if req_file else None,
            out.parent / f"raw_diff_{out.name}.fal_job.json",
            out.parent / f"{out.stem}.fal_job.json",
            out.parent / f"fal_motion_req_{clean_stem}.json",
            out.parent / "fal_motion_req_p1.json",
            out.parent / f"fal_diff_req_{clean_stem}.json",
            out.parent / "fal_diff_req_p1.json",
        ]
        for cand in [c for c in candidates if c and c.exists()]:
            try:
                job_data = json.loads(cand.read_text(encoding="utf-8"))
                s_u, r_u = job_data.get("status_url"), job_data.get("response_url")
                if s_u and r_u:
                    status_url, response_url = s_u, r_u
                    logger.info(f"fal_kling_v3_resuming_job [model=fal-ai/kling-video/v3/4k/image-to-video]: from {cand.name} response_url={response_url}")
                    break
            except Exception:
                pass

        logger.info(f"synthesizing_motion [model=fal-ai/kling-video/v3/4k/image-to-video]: {out.name} prompt={motion_prompt[:70]}...")
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            if not status_url or not response_url:
                sub = await client.post(self.endpoint, headers=headers, json=payload)
                if sub.status_code not in (200, 201, 202):
                    raise RuntimeError(f"Kling v3 4K submit failed: {sub.status_code} - {sub.text[:200]}")
                sub_data = sub.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                _persist_job_tokens(job_sidecar, status_url, response_url, req_file)

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            for _ in range(_POLL_MAX_ATTEMPTS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                try:
                    r_resp = await client.get(response_url, headers=headers)
                    if r_resp.status_code == 200:
                        vid_url = _extract_video_url(r_resp.json())
                        if not vid_url:
                            raise RuntimeError(f"Could not extract Kling v3 video url: {r_resp.json()}")
                        _persist_video_url(out, vid_url, response_url, status_url, req_file)
                        if await _download_video_stream(client, vid_url, out, max_attempts=5):
                            job_sidecar.unlink(missing_ok=True)
                            logger.info(f"fal_kling_v3_ok [model=fal-ai/kling-video/v3/4k/image-to-video]: {out.name} ({out.stat().st_size} B)")
                            return vid_url, out
                        raise RuntimeError(f"Failed to download Kling v3 video from {vid_url}. URL saved to sidecar.")

                    s_resp = await client.get(status_url, headers=headers)
                    if s_resp.status_code in (200, 202):
                        status = s_resp.json().get("status")
                        if status in ("FAILED", "CANCELLED"):
                            job_sidecar.unlink(missing_ok=True)
                            if req_file:
                                Path(req_file).unlink(missing_ok=True)
                            raise RuntimeError(f"Kling v3 4K task failed: {s_resp.json()}")
                except Exception as poll_err:
                    if "task failed" in str(poll_err) or "download" in str(poll_err):
                        raise
                    logger.debug(f"fal_kling_v3_poll_status: {poll_err}")
                    continue

            logger.warning(f"fal_kling_v3_timeout: Job still running in Fal queue. Sidecar preserved at {job_sidecar.name}.")
            raise TimeoutError("Kling v3 4K generation timed out in client, but is still processing in Fal cloud. Sidecar preserved; resynthesizing will resume without new charges.")

    async def _fallback_local(self, out: Path, duration: int) -> tuple[str, Path]:
        import subprocess
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [exe, "-y", "-f", "lavfi", "-i", f"color=c=0x0f172a:s=3840x2160:d={duration}:r=24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)]
        subprocess.run(cmd, check=True, capture_output=True)
        ensure_video_4k(out)
        return f"file://{out}", out


fal_kling_v3_adapter = FalKlingV3Adapter()
__all__ = ["FalKlingV3Adapter", "fal_kling_v3_adapter"]
