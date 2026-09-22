"""Fal.ai Tencent Hunyuan Video v1.5 Video Motion Synthesis Adapter."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key, upload_to_fal


_DEFAULT_HUNYUAN_ENDPOINT = "https://queue.fal.run/fal-ai/hunyuan-video-v1.5/image-to-video"


def _extract_video_url(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    val = payload.get("video")
    if isinstance(val, dict) and val.get("url"):
        return str(val["url"])
    if isinstance(val, str) and val.startswith("http"):
        return val
    out_val = payload.get("output")
    if isinstance(out_val, dict):
        if isinstance(out_val.get("video"), dict) and out_val["video"].get("url"):
            return str(out_val["video"]["url"])
        if isinstance(out_val.get("video"), str) and out_val["video"].startswith("http"):
            return str(out_val["video"])
        if isinstance(out_val.get("url"), str) and out_val["url"].startswith("http"):
            return str(out_val["url"])
    f_val = payload.get("file")
    if isinstance(f_val, dict) and f_val.get("url"):
        return str(f_val["url"])
    if isinstance(payload.get("url"), str) and payload["url"].startswith("http"):
        return str(payload["url"])
    for v in payload.values():
        if isinstance(v, str) and (v.endswith(".mp4") or "fal.media" in v):
            return v
        if isinstance(v, dict) and isinstance(v.get("url"), str) and ("fal.media" in v["url"] or v["url"].endswith(".mp4")):
            return str(v["url"])
    return None


class FalHunyuanAdapter:
    """Tencent Hunyuan Video v1.5 Image-to-Video generation adapter on Fal.ai.

    Features: High-fidelity open-source video architecture, prompt adherence, physical dynamics.
    """

    def __init__(self, api_key: str | None = None, endpoint: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()
        ep = endpoint or _DEFAULT_HUNYUAN_ENDPOINT
        if not ep.startswith("http"):
            ep = f"https://queue.fal.run/{ep}"
        self.endpoint = ep

    async def generate_video(
        self,
        image_url: str,
        motion_prompt: str,
        output_path: Path | str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        force_live: bool = False,
    ) -> tuple[str, Path]:
        """Synthesize video motion using Tencent Hunyuan Video v1.5."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"fal_hunyuan_cache_hit: {out.name} ({out.stat().st_size} B)")
            return f"file://{out}", out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(image_url, motion_prompt, out, duration)

        if not self.api_key:
            if force_live:
                raise ValueError("FAL_KEY is required for LIVE Hunyuan Video generation")
            logger.warning("fal_hunyuan: no FAL_KEY — falling back to local synthesis")
            return await self._fallback_local(image_url, motion_prompt, out, duration)

        try:
            actual_url = image_url
            if not (image_url.startswith("http://") or image_url.startswith("https://")):
                actual_url = await upload_to_fal(Path(image_url), api_key=self.api_key)

            headers = {
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "prompt": motion_prompt,
                "image_url": actual_url,
            }

            job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
            status_url, response_url = None, None
            if job_sidecar.exists():
                try:
                    import json
                    job_data = json.loads(job_sidecar.read_text(encoding="utf-8"))
                    status_url = job_data.get("status_url")
                    response_url = job_data.get("response_url")
                    print(f"    [i] Fal.ai Hunyuan Video: Resuming existing queue job for {out.name}...")
                except Exception:
                    status_url, response_url = None, None

            async with httpx.AsyncClient(timeout=300.0) as client:
                if not status_url or not response_url:
                    print(f"    [~] Fal.ai Hunyuan Video: Submitting {out.name} to GPU queue...")
                    submit_res = await client.post(self.endpoint, headers=headers, json=payload)
                    if submit_res.status_code not in (200, 201, 202):
                        raise RuntimeError(f"Hunyuan Video submit failed: {submit_res.status_code} - {submit_res.text}")

                    res_json = submit_res.json()
                    video_url = _extract_video_url(res_json)
                    status_url = res_json.get("status_url")
                    response_url = res_json.get("response_url")
                    if status_url and response_url:
                        import json
                        job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")
                else:
                    video_url = None
                    res_json = {}

                if not video_url and (status_url or response_url):
                    for attempt in range(80):
                        if attempt > 0:
                            await asyncio.sleep(2.5)
                        poll_target = status_url or response_url
                        poll_res = await client.get(poll_target, headers=headers, params={"logs": "1"})
                        if poll_res.status_code not in (200, 202):
                            job_sidecar.unlink(missing_ok=True)
                            print(f"    [!] Fal.ai Hunyuan Video: Previous queue job expired ({poll_res.status_code}), resubmitting {out.name}...")
                            submit_res = await client.post(self.endpoint, headers=headers, json=payload)
                            if submit_res.status_code not in (200, 201, 202):
                                raise RuntimeError(f"Hunyuan Video resubmit failed: {submit_res.status_code} - {submit_res.text}")
                            sub_json = submit_res.json()
                            status_url = sub_json.get("status_url")
                            response_url = sub_json.get("response_url")
                            if status_url and response_url:
                                import json
                                job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")
                            continue

                        data = poll_res.json()
                        status = data.get("status", "IN_PROGRESS")
                        logs = data.get("logs") or []
                        if logs and isinstance(logs, list):
                            for lg in logs[-1:]:
                                msg = lg.get("message") if isinstance(lg, dict) else str(lg)
                                if msg:
                                    print(f"    [Fal Queue Log]: {msg}")
                                    logger.info(f"fal_hunyuan_log: {msg}")

                        if status in ("IN_QUEUE", "IN_PROGRESS"):
                            if attempt % 3 == 0:
                                print(f"    [~] Fal.ai Hunyuan Video: Cloud GPU rendering {out.name} ({status}, {int(attempt * 2.5)}s)...")
                                logger.info(f"fal_hunyuan_queue: {out.name} status={status} ({int(attempt * 2.5)}s elapsed)")
                        elif status == "COMPLETED":
                            if response_url:
                                resp_res = await client.get(response_url, headers=headers)
                                if resp_res.status_code == 200:
                                    video_url = _extract_video_url(resp_res.json())
                            if not video_url:
                                video_url = _extract_video_url(data)
                            if video_url:
                                print(f"    [~] Fal.ai Hunyuan Video: GPU synthesis complete for {out.name}! Downloading video...")
                                break
                        elif status in ("FAILED", "CANCELLED"):
                            job_sidecar.unlink(missing_ok=True)
                            raise RuntimeError(f"Hunyuan Video generation failed: {data}")

                if not video_url:
                    job_sidecar.unlink(missing_ok=True)
                    raise RuntimeError(f"No video URL returned by Hunyuan Video: {res_json or data}")

                dl_res = await client.get(video_url, timeout=120.0)
                if dl_res.status_code == 200 and len(dl_res.content) > 1000:
                    out.write_bytes(dl_res.content)
                    job_sidecar.unlink(missing_ok=True)
                    print(f"\n🎉 [SUCCESS] Hunyuan Video finished processing successfully: {out.name}")
                    print(f"🔗 Video Output URL: {video_url}\n")
                    logger.info(f"fal_hunyuan_download_complete: {out.name} ({len(dl_res.content)} B)")
                    return video_url, out
                job_sidecar.unlink(missing_ok=True)
                raise RuntimeError(f"Failed to download video from {video_url}")

        except Exception as ex:
            if force_live:
                raise
            logger.warning(f"fal_hunyuan_failed: {ex} — falling back to local steadycam")
            return await self._fallback_local(image_url, motion_prompt, out, duration)

    async def _fallback_local(self, image_url: str, prompt: str, out: Path, duration: int) -> tuple[str, Path]:
        from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
        from src.scripts.local_pan_zoom import render_steadycam_clip
        src_img = Path(image_url) if Path(image_url).exists() else out.parent / "scene_00.jpg"
        if not src_img.exists():
            from PIL import Image
            img = Image.new("RGB", (1280, 720), color=(30, 45, 60))
            img.save(src_img)
        await render_steadycam_clip(image_path=src_img, output_path=out, duration_seconds=float(duration), fps=30, movement="pan_right", ffmpeg_bin=get_ffmpeg_binary())
        return f"file://{out}", out


fal_hunyuan_adapter = FalHunyuanAdapter()
__all__ = ["FalHunyuanAdapter", "fal_hunyuan_adapter"]
