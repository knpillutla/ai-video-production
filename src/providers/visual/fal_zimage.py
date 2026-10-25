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
from src.services.image_4k_encoder import ensure_image_4k


_FAL_ZIMAGE_ENDPOINT = "https://fal.run/fal-ai/z-image/turbo"
_FAL_QUEUE_ENDPOINT = "https://queue.fal.run/fal-ai/z-image/turbo"
_FAL_ZIMAGE_LORA_ENDPOINT = "https://fal.run/fal-ai/z-image/turbo/lora"
_FAL_QUEUE_LORA_ENDPOINT = "https://queue.fal.run/fal-ai/z-image/turbo/lora"
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
        upscale_4k: bool = True,
        **kwargs: Any,
    ) -> tuple[str, Path]:
        """Generate and save a photorealistic keyframe via Z-Image Turbo with optional LoRAs."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 10_000:
            if upscale_4k:
                await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=force_live, api_key=self.api_key)
            logger.info(f"fal_zimage_cache_hit [model=fal-ai/z-image/turbo]: {out.name} ({out.stat().st_size} B)")
            fal_url = await upload_to_fal(out, self.api_key)
            return fal_url, out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(prompt, out, aspect_ratio, upscale_4k=upscale_4k)

        if not self.api_key:
            logger.warning("fal_zimage [model=fal-ai/z-image/turbo]: no FAL_KEY — using local placeholder")
            return await self._fallback_local(prompt, out, aspect_ratio, upscale_4k=upscale_4k)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        if aspect_ratio == "1:1":
            image_size = {"width": 1024, "height": 1024}
        elif aspect_ratio == "9:16":
            image_size = {"width": 1080, "height": 1920}
        else:
            image_size = {"width": 1920, "height": 1080}

        endpoint = _FAL_ZIMAGE_LORA_ENDPOINT if loras else _FAL_ZIMAGE_ENDPOINT
        queue_endpoint = _FAL_QUEUE_LORA_ENDPOINT if loras else _FAL_QUEUE_ENDPOINT

        payload: dict[str, Any] = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 8,
            "num_images": 1,
            "enable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed
        if loras:
            payload["loras"] = [
                {
                    "path": l.get("path") or l.get("lora_url") or l.get("model_name"),
                    "scale": float(l.get("scale", l.get("weight", 0.8))),
                }
                for l in loras
            ]

        m_tag = "fal-ai/z-image/turbo/lora" if loras else "fal-ai/z-image/turbo"
        logger.info(f"generating_image [model={m_tag}]: {out.name} prompt={prompt[:70]}...")
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                # 1. Direct fast-path inference via fal.run
                resp = await client.post(endpoint, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    images = data.get("images") or []
                    if images and images[0].get("url"):
                        img_url: str = images[0]["url"]
                        img_bytes = (await client.get(img_url, timeout=60.0)).content
                        out.write_bytes(img_bytes)
                        if upscale_4k:
                            await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=force_live, api_key=self.api_key)
                        logger.info(f"fal_zimage_ok [model={m_tag}]: {out.name} ({out.stat().st_size} B)")
                        return img_url, out

                # 2. Queue fallback if direct endpoint queued or rate-limited
                sub_resp = await client.post(queue_endpoint, headers=headers, json=payload)
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
                        if upscale_4k:
                            await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=force_live, api_key=self.api_key)
                        logger.info(f"fal_zimage_queue_ok [model=fal-ai/z-image/turbo]: {out.name} ({out.stat().st_size} B)")
                        return img_url, out
                    if s.get("status") in ("FAILED", "CANCELLED"):
                        raise RuntimeError(f"Fal Z-Image task {s.get('status')}: {s}")

                raise TimeoutError("Fal Z-Image timed out waiting for completion")
            except Exception as ex:
                logger.error(f"Fal Z-Image failed: {ex}")
                raise RuntimeError(f"Fal Z-Image failed: {ex}") from ex

    async def _fallback_local(self, prompt: str, out: Path, aspect_ratio: str, upscale_4k: bool = True) -> tuple[str, Path]:
        """Generate deterministic fallback keyframe."""
        from PIL import Image, ImageDraw
        target_size = (1024, 1024) if aspect_ratio == "1:1" else ((1080, 1920) if aspect_ratio == "9:16" else (1920, 1080))
        image = Image.new("RGB", target_size, (15, 23, 42))
        draw = ImageDraw.Draw(image)
        draw.text((40, 40), f"Offline Fallback (Z-Image Turbo)\n{prompt[:100]}", fill=(226, 232, 240))
        image.save(out, format="JPEG", quality=90)
        if upscale_4k:
            await ensure_image_4k(out, aspect_ratio=aspect_ratio, force_live=False, api_key=self.api_key)
        return f"file://{out}", out


fal_zimage_adapter = FalZImageAdapter()
__all__ = ["FalZImageAdapter", "fal_zimage_adapter"]
