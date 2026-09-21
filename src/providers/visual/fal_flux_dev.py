"""Fal.ai FLUX.1-dev high-quality 4K keyframe generator (28-step, photorealistic).

Uses the Fal queue system (submit → poll → download) identical to the scratch
production scripts. Falls back to a local placeholder when Fal is unavailable.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import upload_to_fal, _fal_api_key


_FAL_FLUX_ENDPOINT = "https://queue.fal.run/fal-ai/flux/dev"
_POLL_INTERVAL_S = 2.0
_POLL_MAX_ATTEMPTS = 50   # 100 seconds max


class FalFluxDevAdapter:
    """28-step FLUX.1-dev photorealistic 4K keyframe generator via Fal queue.

    Quality and cost:
    - Steps: 28 → high photorealism for broadcast keyframes
    - Cost: ~$0.015/image (vs $0.003) — acceptable for broadcast masters
    - Resolution: landscape_16_9 (1344×768 native, upscaled to 4K in FFmpeg)
    """

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
        """Generate and save a photorealistic keyframe.

        Returns:
            (remote_fal_url, local_path) — the remote URL is needed by Kling.
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Directive 3)
        if out.exists() and out.stat().st_size > 10_000:
            logger.info(f"fal_flux_dev_cache_hit: {out.name} ({out.stat().st_size} B)")
            fal_url = await upload_to_fal(out, self.api_key)
            return fal_url, out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(prompt, out, aspect_ratio, loras, seed)

        if not self.api_key:
            logger.warning("fal_flux_dev: no FAL_KEY — using local placeholder")
            return await self._fallback_local(prompt, out, aspect_ratio, loras, seed)

        headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
        image_size = "landscape_16_9" if aspect_ratio == "16:9" else "portrait_16_9"
        payload: dict[str, Any] = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "num_images": 1,
            "enable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            try:
                sub_resp = await client.post(_FAL_FLUX_ENDPOINT, headers=headers, json=payload)
                if sub_resp.status_code not in (200, 201):
                    raise RuntimeError(f"Fal FLUX submit failed: {sub_resp.text[:200]}")
                sub_data = sub_resp.json()
                status_url: str = sub_data["status_url"]
                response_url: str = sub_data["response_url"]

                for attempt in range(_POLL_MAX_ATTEMPTS):
                    await asyncio.sleep(_POLL_INTERVAL_S)
                    s = (await client.get(status_url, headers=headers)).json()
                    if s.get("status") == "COMPLETED":
                        res = (await client.get(response_url, headers=headers)).json()
                        img_url: str = res["images"][0]["url"]
                        img_bytes = (await client.get(img_url, timeout=60.0)).content
                        out.write_bytes(img_bytes)
                        logger.info(f"fal_flux_dev_ok: {out.name} ({out.stat().st_size} B)")
                        return img_url, out
                    if s.get("status") in ("FAILED", "CANCELLED"):
                        raise RuntimeError(f"Fal FLUX failed: {s}")
                    if attempt % 5 == 0:
                        logger.info(f"fal_flux_dev_poll: status={s.get('status')} ({attempt * _POLL_INTERVAL_S:.0f}s)")

                raise TimeoutError("Fal FLUX.1-dev timed out after 100s")

            except Exception as ex:
                logger.warning(f"fal_flux_dev_failed: {ex} — using local placeholder")
                return await self._fallback_local(prompt, out, aspect_ratio, loras, seed)

    async def _fallback_local(
        self,
        prompt: str,
        out: Path,
        aspect_ratio: str,
        loras: list[dict[str, Any]] | None,
        seed: int | None,
    ) -> tuple[str, Path]:
        """Fallback to a deterministic local placeholder without switching models."""
        from PIL import Image, ImageDraw
        target_size = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
        image = Image.new("RGB", target_size, (15, 23, 42))
        draw = ImageDraw.Draw(image)
        draw.text((60, target_size[1] // 2 - 20), f"[FLUX Dev unavailable] {prompt[:70]}...", fill=(240, 240, 250))
        image.save(out, format="JPEG", quality=90)
        result_path = out
        return f"file://{result_path}", result_path


fal_flux_dev_adapter = FalFluxDevAdapter()

__all__ = ["FalFluxDevAdapter", "fal_flux_dev_adapter"]
