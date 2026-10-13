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
from src.providers.llm.gemini_adapter import get_live_gemini_api_key


_GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"
_GEMINI_GENERATE_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_IMAGE_MODEL}:generateContent"
)


class GoogleImagen3Adapter:
    """Google Gemini 2.5 Flash Image generator with strict idempotency."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = get_live_gemini_api_key(api_key) or ""

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

        active_key = get_live_gemini_api_key(self.api_key) or ""
        if not active_key:
            if is_mock_mode() or kwargs.get("allow_fallback"):
                logger.warning("gemini_image: no GEMINI_API_KEY / GOOGLE_API_KEY — using local placeholder")
                return await self._fallback_local(prompt, out, aspect_ratio)
            raise RuntimeError("Gemini Image Generation Failed: GEMINI_API_KEY is not configured in .env")

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

        url = f"{_GEMINI_GENERATE_ENDPOINT}?key={active_key}"
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    err_msg = resp.text[:300]
                    logger.error(f"gemini_image_api_error: HTTP {resp.status_code} - {err_msg}")
                    if is_mock_mode() or kwargs.get("allow_fallback"):
                        return await self._fallback_local(prompt, out, aspect_ratio)
                    raise RuntimeError(f"Gemini Image Generation Failed (HTTP {resp.status_code}): {err_msg}")

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

                # Ensure exact target aspect ratio (16:9 / 9:16)
                from io import BytesIO
                from PIL import Image

                with Image.open(BytesIO(img_bytes)) as pil_img:
                    w, h = pil_img.size
                    curr_ratio = w / h
                    target_ratio = (16.0 / 9.0) if aspect_ratio == "16:9" else ((9.0 / 16.0) if aspect_ratio in ("9:16", "portrait") else 1.0)
                    if abs(curr_ratio - target_ratio) > 0.05:
                        if target_ratio > curr_ratio:
                            # Target is wider (e.g. 16:9 from 1:1 square): center-crop top/bottom
                            new_h = int(w / target_ratio)
                            top = (h - new_h) // 2
                            pil_img = pil_img.crop((0, top, w, top + new_h))
                        else:
                            # Target is taller (e.g. 9:16 from 1:1 square): center-crop left/right
                            new_w = int(h * target_ratio)
                            left = (w - new_w) // 2
                            pil_img = pil_img.crop((left, 0, left + new_w, h))
                        pil_img.save(out, format="JPEG", quality=95)
                        logger.info(f"gemini_image_cropped_aspect: {out.name} ({pil_img.size[0]}x{pil_img.size[1]}) target={aspect_ratio}")
                    else:
                        out.write_bytes(img_bytes)

                logger.info(f"gemini_image_success: {out.name} ({out.stat().st_size} B) created via { _GEMINI_IMAGE_MODEL }")
                return str(out), out

            except Exception as ex:
                logger.error(f"gemini_image_failed: {ex}")
                if is_mock_mode() or kwargs.get("allow_fallback"):
                    return await self._fallback_local(prompt, out, aspect_ratio)
                raise RuntimeError(f"Gemini Image Generation Failed: {ex}") from ex

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
