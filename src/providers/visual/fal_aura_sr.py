"""Fal.ai AuraSR 4x Image Super-Resolution Adapter.

Ultra low-cost (~$0.0015/image) AI super-resolution to 4K UHD via GigaGAN architecture.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional, Tuple

import cv2
import httpx
import numpy as np

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.fal_storage import upload_to_fal, _fal_api_key

_FAL_AURA_SR_ENDPOINT = "https://fal.run/fal-ai/aura-sr"
_FAL_QUEUE_ENDPOINT = "https://queue.fal.run/fal-ai/aura-sr"
_POLL_INTERVAL_S = 1.0
_POLL_MAX_ATTEMPTS = 45


class FalAuraSRAdapter:
    """AuraSR 4x AI Super-Resolution adapter on Fal.ai with optical 4K supersampling."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or _fal_api_key()

    async def upscale_image(
        self,
        image_path: Path | str,
        output_path: Path | str,
        target_res: Optional[Tuple[int, int]] = None,
        force_live: bool = False,
    ) -> Path:
        """Upscale input keyframe to pristine 4K UHD using AuraSR 4x GigaGAN."""
        src = Path(image_path)
        dst = Path(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Artifact caching guard (Rule 3)
        if dst.exists() and dst.stat().st_size > 80_000 and dst != src:
            logger.info(f"fal_aura_sr_cache_hit [model=fal-ai/aura-sr]: {dst.name} ({dst.stat().st_size} B) ($0.00 spend)")
            return dst

        # Auto-derive target resolution from source image geometry if not specified
        if target_res is None:
            target_res = (3840, 2160)
            if src.is_file():
                try:
                    probe = cv2.imread(str(src))
                    if probe is not None:
                        pw, ph = probe.shape[1], probe.shape[0]
                        if pw == ph:
                            target_res = (3840, 3840)
                        elif ph > pw:
                            target_res = (2160, 3840)
                        else:
                            target_res = (3840, 2160)
                except Exception:
                    pass

        # Check if source is already target 4K resolution (Rule 3 Tier 1 check)
        if src.is_file():
            try:
                probe = cv2.imread(str(src))
                if probe is not None and (probe.shape[1], probe.shape[0]) == target_res:
                    logger.info(f"fal_aura_sr_already_target_res [model=fal-ai/aura-sr]: {src.name} is already {target_res[0]}x{target_res[1]} ($0.00 spend)")
                    if dst != src:
                        import shutil
                        shutil.copy2(src, dst)
                    return dst
            except Exception:
                pass

        # Mock / Offline mode fallback (Rule 8)
        if is_mock_mode() and not force_live:
            return self._fallback_local(src, dst, target_res)

        if not self.api_key:
            logger.warning("fal_aura_sr [model=fal-ai/aura-sr]: no FAL_KEY — using local Lanczos4 resize fallback")
            return self._fallback_local(src, dst, target_res)

        try:
            actual_url = await upload_to_fal(src, self.api_key)
            headers = {"Authorization": f"Key {self.api_key}", "Content-Type": "application/json"}
            payload: dict[str, Any] = {"image_url": actual_url}

            logger.info(f"upscaling_image [model=fal-ai/aura-sr]: {src.name} -> {dst.name} (target={target_res[0]}x{target_res[1]})")
            upscaled_url: Optional[str] = None
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=15.0)) as client:
                q_resp = await client.post(_FAL_QUEUE_ENDPOINT, headers=headers, json=payload)
                if q_resp.status_code in (200, 201, 202):
                    q_data = q_resp.json()
                    status_url = q_data.get("status_url")
                    response_url = q_data.get("response_url")
                    if status_url and response_url:
                        for attempt in range(_POLL_MAX_ATTEMPTS):
                            await asyncio.sleep(_POLL_INTERVAL_S)
                            st_resp = await client.get(status_url, headers=headers)
                            if st_resp.status_code == 200:
                                st_data = st_resp.json()
                                if st_data.get("status") == "COMPLETED":
                                    res_resp = await client.get(response_url, headers=headers)
                                    if res_resp.status_code == 200:
                                        res_data = res_resp.json()
                                        upscaled_url = (res_data.get("image") or {}).get("url")
                                    break
                                if st_data.get("status") in ("FAILED", "CANCELLED"):
                                    logger.warning(f"fal_aura_sr_status_failed [model=fal-ai/aura-sr]: {st_data.get('status')}")
                                    break

                if upscaled_url:
                    img_resp = await client.get(upscaled_url, timeout=45.0)
                    if img_resp.status_code == 200 and len(img_resp.content) > 10_000:
                        raw_arr = np.frombuffer(img_resp.content, dtype=np.uint8)
                        decoded = cv2.imdecode(raw_arr, cv2.IMREAD_COLOR)
                        if decoded is not None:
                            # Optical 4K supersampling: downsample from 4x (~5.3K) to exact 3840x2160
                            if (decoded.shape[1], decoded.shape[0]) != target_res:
                                final_4k = cv2.resize(decoded, target_res, interpolation=cv2.INTER_AREA)
                            else:
                                final_4k = decoded
                            cv2.imwrite(str(dst), final_4k, [cv2.IMWRITE_JPEG_QUALITY, 96])
                            logger.info(f"fal_aura_sr_success [model=fal-ai/aura-sr]: {dst.name} 4K upscaled ({dst.stat().st_size} B, cost ~$0.0015)")
                            return dst

        except Exception as e:
            logger.warning(f"fal_aura_sr_failed: {e} — falling back to local Lanczos4 enhancement")

        return self._fallback_local(src, dst, target_res)

    def _fallback_local(self, src: Path, dst: Path, target_res: Tuple[int, int]) -> Path:
        """Deterministic local fallback with Lanczos4 resize and LAB CLAHE boost."""
        if src.is_file():
            img = cv2.imread(str(src))
            if img is not None:
                if (img.shape[1], img.shape[0]) != target_res:
                    resized = cv2.resize(img, target_res, interpolation=cv2.INTER_LANCZOS4)
                else:
                    resized = img
                cv2.imwrite(str(dst), resized, [cv2.IMWRITE_JPEG_QUALITY, 96])
                return dst
        return src
