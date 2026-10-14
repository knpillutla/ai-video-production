"""Fal.ai Kling Video Motion Synthesis Adapter.

Features:
- Kling 1.6 Pro (high dynamic dance & action kinematics, ~$0.14-$0.28)
- Kling standard mode (cost-optimized, ~$0.05)
- Endpoint: fal-ai/kling-video/v1.6/pro/image-to-video
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
from src.providers.fal_storage import _fal_api_key

_POLL_INTERVAL_S = 4.0
_POLL_MAX_ATTEMPTS = 150  # 600s max


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
                return True
        except Exception as dl_err:
            logger.warning(f"fal_kling_dl_retry: attempt {attempt+1}/{max_attempts} failed ({dl_err})")
            await asyncio.sleep(3.0)
    return False


class FalKlingAdapter:
    """Kling AI video motion generation adapter on Fal.ai."""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()
        self.endpoint = endpoint

    async def generate_video(
        self,
        image_url: str,
        motion_prompt: str,
        output_path: Path | str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        mode: str = "pro",
        force_live: bool = False,
        negative_prompt: str | None = None,
        req_file: Optional[Path | str] = None,
    ) -> tuple[str, Path]:
        """Synthesize video motion from a reference image URL."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"fal_kling_cache_hit: {out.name} ({out.stat().st_size} B)")
            return f"file://{out}", out

        saved_url = _find_saved_video_url(out, req_file)
        if saved_url:
            logger.info(f"fal_kling_reusing_remote_url: {out.name} downloading from {saved_url} ($0.00 spend)")
            async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0, read=180.0)) as dl_client:
                if await _download_video_stream(dl_client, saved_url, out):
                    logger.info(f"fal_kling_redownload_ok: {out.name} ({out.stat().st_size} B) ($0.00 spend)")
                    return saved_url, out

        if is_mock_mode() and not force_live:
            return await self._fallback_mimic(image_url, motion_prompt, out, duration)

        if not self.api_key:
            if force_live:
                raise ValueError("FAL_KEY is required for LIVE video motion generation")
            return await self._fallback_mimic(image_url, motion_prompt, out, duration)

        kling_dur = "10" if duration >= 8 else "5"
        eff_mode = "standard" if mode.lower() in ("standard", "fast", "low_cost") else "pro"
        endpoint = self.endpoint or (
            "https://queue.fal.run/fal-ai/kling-video/v1/standard/image-to-video"
            if eff_mode == "standard"
            else "https://queue.fal.run/fal-ai/kling-video/v1.6/pro/image-to-video"
        )

        actual_url = image_url
        if not (image_url.startswith("http://") or image_url.startswith("https://")):
            from src.providers.fal_storage import upload_to_fal
            actual_url = await upload_to_fal(Path(image_url), api_key=self.api_key)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {
            "prompt": motion_prompt.strip(),
            "image_url": actual_url,
            "duration": kling_dur,
            "aspect_ratio": aspect_ratio,
            "mode": eff_mode,
            "cfg_scale": 0.55,
        }
        if negative_prompt and negative_prompt.strip():
            payload["negative_prompt"] = negative_prompt.strip()

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
                    logger.info(f"fal_kling_job_resume: from {cand.name} response_url={response_url}")
                    break
            except Exception:
                pass

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            if not status_url or not response_url:
                sub_resp = await client.post(endpoint, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201, 202):
                    raise RuntimeError(f"Kling submit failed: {sub_resp.text[:200]}")
                sub_data = sub_resp.json()
                status_url = sub_data.get("status_url")
                response_url = sub_data.get("response_url")
                _persist_job_tokens(job_sidecar, status_url, response_url, req_file)

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0, read=300.0)) as client:
            for _ in range(_POLL_MAX_ATTEMPTS):
                await asyncio.sleep(_POLL_INTERVAL_S)
                try:
                    r_resp = await client.get(response_url, headers=headers)
                    if r_resp.status_code == 200:
                        r_data = r_resp.json()
                        vid_url = r_data.get("video", {}).get("url") or (r_data.get("video") if isinstance(r_data.get("video"), str) else None)
                        if not vid_url:
                            vid_url = r_data.get("output", {}).get("url")
                        if not vid_url:
                            raise RuntimeError(f"Kling response missing video URL: {r_data}")
                        _persist_video_url(out, vid_url, response_url, status_url, req_file)
                        if await _download_video_stream(client, vid_url, out, max_attempts=5):
                            job_sidecar.unlink(missing_ok=True)
                            logger.info(f"fal_kling_ok: {out.name} ({out.stat().st_size} B)")
                            return vid_url, out
                        raise RuntimeError(f"Failed to download Kling video from {vid_url}. URL saved to sidecar.")

                    poll_resp = await client.get(status_url, headers=headers)
                    if poll_resp.status_code in (200, 202):
                        s = poll_resp.json()
                        status = s.get("status")
                        if status in ("FAILED", "CANCELLED"):
                            job_sidecar.unlink(missing_ok=True)
                            if req_file:
                                Path(req_file).unlink(missing_ok=True)
                            raise RuntimeError(f"Kling generation failed: {s}")
                except Exception as poll_err:
                    if "generation failed" in str(poll_err) or "download" in str(poll_err):
                        raise
                    logger.debug(f"fal_kling_poll_status: {poll_err}")
                    continue

            logger.warning(f"fal_kling_timeout: Job still running in Fal queue. Sidecar preserved at {job_sidecar.name}.")
            raise TimeoutError("Kling video generation timed out in client, but is still processing in Fal cloud. Sidecar preserved; resynthesizing will resume without new charges.")

    async def _fallback_mimic(self, image_url: str, motion_prompt: str, out: Path, duration: int) -> tuple[str, Path]:
        from src.providers.dance.fal_mimicmotion import FalMimicMotionAdapter
        logger.info(f"fal_kling_fallback_mimic: {out.name} via FalMimicMotion")
        return await FalMimicMotionAdapter(api_key=self.api_key).generate_dance_video(
            image_url=image_url, audio_url="", output_path=out, prompt=motion_prompt,
        )


fal_kling_adapter = FalKlingAdapter()
__all__ = ["FalKlingAdapter", "fal_kling_adapter"]
