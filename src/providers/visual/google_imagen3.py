"""Google Gemini 2.5 Flash Image keyframe generator.

Uses Google Gemini API key via the official generateContent endpoint with
responseModalities: ["IMAGE"] (model: gemini-2.5-flash-image).
This is Google's fastest and most cost-effective image generation model.
Enforces strict idempotency and Tier-1 disk cache checks.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import is_mock_mode


_GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"
_GEMINI_GENERATE_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_IMAGE_MODEL}:generateContent"
)


class GoogleImagen3Adapter:
    """Google Gemini 2.5 Flash Image generator with strict idempotency."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.llm.google_api_key or settings.llm.gemini_api_key or ""

    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path | str,
        aspect_ratio: str = "16:9",
        force_live: bool = False,
        **kwargs: Any,
    ) -> tuple[str, Path]:
        """Generate a keyframe photo using Google Gemini with strict idempotency."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # IDEMPOTENCY GUARD: If artifact exists on disk and is > 1000 bytes, reuse it ($0 spend)
        if out.exists() and out.stat().st_size > 1000:
            logger.info(f"gemini_image_cache_hit: {out.name} ({out.stat().st_size} B) — reusing artifact ($0.00 spend)")
            return str(out), out

        if is_mock_mode() and not force_live:
            return await self._fallback_local(prompt, out, aspect_ratio)

        if not self.api_key:
            logger.warning("gemini_image: no GEMINI_API_KEY / GOOGLE_API_KEY — using local placeholder")
            return await self._fallback_local(prompt, out, aspect_ratio)

        aspect_text = "16:9 widescreen landscape aspect ratio"
        if aspect_ratio in ("9:16", "portrait"):
            aspect_text = "9:16 vertical smartphone portrait aspect ratio"
        elif aspect_ratio in ("1:1", "square"):
            aspect_text = "1:1 square aspect ratio"

        full_prompt = f"{prompt.strip()}. Framing: {aspect_text}, ultra-high resolution, photorealistic clarity."

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        url = f"{_GEMINI_GENERATE_ENDPOINT}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    err_msg = resp.text[:300]
                    logger.error(f"gemini_image_api_error: HTTP {resp.status_code} - {err_msg}")
                    return await self._fallback_local(prompt, out, aspect_ratio)

                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Gemini returned empty candidates")

                parts = candidates[0].get("content", {}).get("parts", [])
                img_data_b64 = None
                for p in parts:
                    inline = p.get("inlineData")
                    if inline and inline.get("data"):
                        img_data_b64 = inline.get("data")
                        break

                if not img_data_b64:
                    raise RuntimeError("Gemini response missing inline image data")

                img_bytes = base64.b64decode(img_data_b64)
                out.write_bytes(img_bytes)
                logger.info(f"gemini_image_success: {out.name} ({out.stat().st_size} B) created via { _GEMINI_IMAGE_MODEL }")
                return str(out), out

            except Exception as ex:
                logger.error(f"gemini_image_failed: {ex}")
                return await self._fallback_local(prompt, out, aspect_ratio)

    async def _fallback_local(
        self,
        prompt: str,
        out: Path,
        aspect_ratio: str,
    ) -> tuple[str, Path]:
        from PIL import Image, ImageDraw
        target_size = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
        image = Image.new("RGB", target_size, (15, 23, 42))
        draw = ImageDraw.Draw(image)
        draw.text((60, 60), f"Gemini Image [Offline Fallback]\n{prompt[:120]}...", fill=(241, 245, 249))
        image.save(out, format="JPEG", quality=92)
        return str(out), out


__all__ = ["GoogleImagen3Adapter"]
