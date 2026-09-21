"""Fal.ai Kling 1.5 Pro Image-to-Video motion synthesis adapter.

Calls ``fal-ai/kling-video/v1.5/pro/image-to-video`` — the same model used
by the high-quality scratch scripts — to produce fluid 10-second dance motion
from a static 4K keyframe.

Falls back to FalMimicMotionAdapter when Fal key is absent or for ≤5s clips.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import _fal_api_key


_KLING_ENDPOINT = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"
_POLL_INTERVAL_S = 4.0
_POLL_MAX_ATTEMPTS = 80   # 320 seconds max


class FalKlingAdapter:
    """Kling 1.5 Pro Image-to-Video for broadcast-grade dance motion synthesis.

    Cost: ~$0.14–$0.28 per 10-second clip (Pro tier).
    Quality: State-of-the-art fluid motion, realistic human body kinematics.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def generate_video(
        self,
        image_url: str,
        motion_prompt: str,
        output_path: Path | str,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        force_live: bool = False,
    ) -> tuple[str, Path]:
        """Synthesize video motion from a reference image URL.

        Args:
            image_url:     Remote Fal CDN URL of the keyframe image.
            motion_prompt: Choreography / motion description for the scene.
            output_path:   Local path to save the rendered MP4.
            duration:      Clip duration in seconds — 5 or 10 (Kling constraint).
            aspect_ratio:  ``"16:9"`` or ``"9:16"``.
            force_live:    Bypass mock mode.

        Returns:
            (remote_video_url, local_path)
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"fal_kling_cache_hit: {out.name} ({out.stat().st_size} B)")
            return f"file://{out}", out

        if is_mock_mode() and not force_live:
            return await self._fallback_mimic(image_url, motion_prompt, out, duration)

        if not self.api_key:
            if force_live:
                raise ValueError("FAL_KEY is required for LIVE video motion generation")
            logger.warning("fal_kling: no FAL_KEY — falling back to FalMimicMotion")
            return await self._fallback_mimic(image_url, motion_prompt, out, duration)

        # Kling only accepts 5 or 10; clamp to nearest valid value
        kling_dur = "10" if duration >= 8 else "5"

        try:
            actual_url = image_url
            if not (image_url.startswith("http://") or image_url.startswith("https://")):
                from src.providers.fal_storage import upload_to_fal
                actual_url = await upload_to_fal(Path(image_url), api_key=self.api_key)

            headers = {
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json",
            }

            neg_prompt = (
                "blurry, low quality, distortion, noise, compression artifacts, jitter, flickers, overexposed, oversaturated, "
                "deformed, cartoon, low resolution, pixelated, soft focus, haze, smear, "
                "unrealistic person walking in front, pedestrian in front, human back, walking person in frame, uncanny human figure, mannequin, bad anatomy, CGI character"
                if "scenic" in motion_prompt.lower() or "first-person" in motion_prompt.lower() or "empty" in motion_prompt.lower() or "pov" in motion_prompt.lower()
                else "blurry, low quality, distortion, noise, compression artifacts, jitter, flickers, overexposed, oversaturated, deformed, cartoon, low resolution, pixelated, soft focus, haze, smear"
            )
            payload = {
                "prompt": motion_prompt,
                "negative_prompt": neg_prompt,
                "image_url": actual_url,
                "duration": kling_dur,
                "aspect_ratio": aspect_ratio,
                "mode": "pro",
                "cfg_scale": 0.55,
            }

            job_sidecar = out.with_suffix(out.suffix + ".fal_job.json")
            status_url, response_url = None, None
            if job_sidecar.exists():
                try:
                    job_data = json.loads(job_sidecar.read_text(encoding="utf-8"))
                    status_url = job_data.get("status_url")
                    response_url = job_data.get("response_url")
                    logger.info(f"fal_kling_job_resume: found existing queue job for {out.name}, resuming polling...")
                except Exception:
                    status_url, response_url = None, None

            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
                if not status_url or not response_url:
                    sub_resp = await client.post(_KLING_ENDPOINT, headers=headers, json=payload)
                    if sub_resp.status_code not in (200, 201):
                        raise RuntimeError(f"Kling submit failed: {sub_resp.text[:200]}")
                    sub_data = sub_resp.json()
                    status_url = sub_data["status_url"]
                    response_url = sub_data["response_url"]
                    job_sidecar.write_text(json.dumps({"status_url": status_url, "response_url": response_url}), encoding="utf-8")

                for attempt in range(_POLL_MAX_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    s = (await client.get(status_url, headers=headers)).json()
                    status = s.get("status")
                    if status == "COMPLETED":
                        r = (await client.get(response_url, headers=headers)).json()
                        vid_url: str = r.get("video", {}).get("url", "")
                        if not vid_url:
                            raise RuntimeError(f"Kling response missing video URL: {r}")
                        v_bytes = (await client.get(vid_url, timeout=90.0)).content
                        out.write_bytes(v_bytes)
                        job_sidecar.unlink(missing_ok=True)
                        logger.info(f"fal_kling_ok: {out.name} ({out.stat().st_size} B)")
                        return vid_url, out
                    if status in ("FAILED", "CANCELLED"):
                        job_sidecar.unlink(missing_ok=True)
                        raise RuntimeError(f"Kling generation failed: {s}")
                    if attempt % 3 == 0:
                        logger.info(f"fal_kling_poll: status={status} ({attempt * _POLL_INTERVAL_S:.0f}s)")

                job_sidecar.unlink(missing_ok=True)
                raise TimeoutError("Kling 1.5 Pro timed out after 320s")

        except Exception as ex:
            if force_live:
                logger.error(f"fal_kling_live_failed: {ex}")
                raise RuntimeError(f"Kling video motion generation failed in LIVE mode: {ex}") from ex
            logger.warning(f"fal_kling_failed: {ex} — falling back to FalMimicMotion")
            return await self._fallback_mimic(image_url, motion_prompt, out, duration)

    async def _fallback_mimic(
        self,
        image_url: str,
        motion_prompt: str,
        out: Path,
        duration: int,
    ) -> tuple[str, Path]:
        """Fallback: MimicMotion or local FFmpeg static loop."""
        from src.providers.dance.fal_mimicmotion import FalMimicMotionAdapter
        adapter = FalMimicMotionAdapter()
        # MimicMotion accepts image path; download if remote URL
        if image_url.startswith("file://"):
            img_path = Path(image_url[7:])
        elif Path(image_url).is_file():
            img_path = Path(image_url)
        elif (out.parent / "scene_00.jpg").is_file():
            img_path = out.parent / "scene_00.jpg"
        else:
            img_path = out.parent / "keyframe_fallback.jpg"
            if not img_path.exists():
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(image_url, timeout=30.0)
                    if resp.status_code == 200:
                        img_path.write_bytes(resp.content)
        result = await adapter.transfer_dance_motion(
            character_image_path=img_path,
            motion_or_audio_path=img_path,  # no dedicated pose ref; will use local synth
            output_path=out,
            duration_seconds=float(duration),
        )
        return f"file://{result}", result


fal_kling_adapter = FalKlingAdapter()

__all__ = ["FalKlingAdapter", "fal_kling_adapter"]
