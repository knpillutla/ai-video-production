"""Fal.ai Z-Image Turbo high-quality, ultra-fast 4K keyframe generator.

Uses Tongyi-MAI Z-Image Turbo on Fal.ai for sub-second, photorealistic keyframes.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import upload_to_fal, _fal_api_key


_FAL_ZIMAGE_ENDPOINT = "https://fal.run/fal-ai/z-image/turbo"
_FAL_QUEUE_ENDPOINT = "https://queue.fal.run/fal-ai/z-image/turbo"
_POLL_INTERVAL_S = 1.0
_POLL_MAX_ATTEMPTS = 40


class FalZImageAdapter:
    """Z-Image Turbo photorealistic keyframe generator via Fal.ai."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path | str,
        aspect_ratio: str = "16:9",
        force_live: bool = False,
        loras: list[dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> tuple[str, Path]:
        """Generate and save a photorealistic keyframe via Z-Image Turbo."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 10_000:
            logger.info(f"fal_zimage_cache_hit: {out.name} ({out.stat().st_size} B)")
            fal_url = await upload_to_fal(out, self.api_key)
            return fal_url, out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(prompt, out, aspect_ratio)

        if not self.api_key:
            logger.warning("fal_zimage: no FAL_KEY — using local placeholder")
            return await self._fallback_local(prompt, out, aspect_ratio)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        image_size = {"width": 1920, "height": 1080} if aspect_ratio == "16:9" else {"width": 1080, "height": 1920}
        payload: dict[str, Any] = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 8,
            "num_images": 1,
            "enable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                # 1. Direct fast-path inference via fal.run
                resp = await client.post(_FAL_ZIMAGE_ENDPOINT, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    images = data.get("images") or []
                    if images and images[0].get("url"):
                        img_url: str = images[0]["url"]
                        img_bytes = (await client.get(img_url, timeout=60.0)).content
                        out.write_bytes(img_bytes)
                        logger.info(f"fal_zimage_ok: {out.name} ({out.stat().st_size} B)")
                        return img_url, out

                # 2. Queue fallback if direct endpoint queued or rate-limited
                sub_resp = await client.post(_FAL_QUEUE_ENDPOINT, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201):
                    raise RuntimeError(f"Fal Z-Image submit failed: {sub_resp.text[:200]}")
                sub_data = sub_resp.json()
                status_url: str = sub_data["status_url"]
                response_url: str = sub_data["response_url"]

                for attempt in range(_POLL_MAX_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    s = (await client.get(status_url, headers=headers)).json()
                    if s.get("status") == "COMPLETED":
                        res = (await client.get(response_url, headers=headers)).json()
                        img_url = res["images"][0]["url"]
                        img_bytes = (await client.get(img_url, timeout=60.0)).content
                        out.write_bytes(img_bytes)
                        logger.info(f"fal_zimage_queue_ok: {out.name} ({out.stat().st_size} B)")
                        return img_url, out
                    if s.get("status") in ("FAILED", "CANCELLED"):
                        raise RuntimeError(f"Fal Z-Image task {s.get('status')}: {s}")

                raise TimeoutError("Fal Z-Image timed out waiting for completion")
            except Exception as ex:
                if force_live:
                    logger.error(f"Fal Z-Image failed in live mode: {ex}")
                    raise
                logger.warning(f"fal_zimage_failed_falling_back: {ex}")
                return await self._fallback_local(prompt, out, aspect_ratio)

    async def _fallback_local(self, prompt: str, out: Path, aspect_ratio: str) -> tuple[str, Path]:
        """Generate deterministic fallback keyframe."""
        from src.services.local_video_producer import create_placeholder_image
        w, h = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
        create_placeholder_image(out, text=prompt[:80], width=w, height=h)
        return f"file://{out}", out


fal_zimage_adapter = FalZImageAdapter()
__all__ = ["FalZImageAdapter", "fal_zimage_adapter"]
