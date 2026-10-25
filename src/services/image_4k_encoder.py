"""Deterministic 4K Image Encoder & Resolution Standardizer.

Ensures all visual keyframe models (Z-Image, FLUX.1 [dev], FLUX.1 Pro Ultra, Imagen 3, FLUX LoRA)
and character LoRA training dataset generators automatically upscale to 4K resolution:
- 16:9 Landscape: 3840x2160
- 9:16 Shorts: 2160x3840
- 1:1 Square (LoRA datasets & hero anchors): 3840x3840
- Zero-cost pass-through if image is already 4K resolution
- AI Super-Resolution via Fal AuraSR (GigaGAN) with deterministic local Lanczos4 fallback
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import cv2
from PIL import Image

from src.core.telemetry import logger
from src.providers.base import is_mock_mode


def get_image_resolution(image_path: Path | str) -> Optional[Tuple[int, int]]:
    """Return (width, height) of an image file."""
    p = Path(image_path)
    if not p.is_file() or p.stat().st_size < 100:
        return None
    try:
        with Image.open(p) as img:
            return img.size
    except Exception:
        try:
            arr = cv2.imread(str(p))
            if arr is not None:
                return (arr.shape[1], arr.shape[0])
        except Exception:
            pass
    return None


def is_image_4k(image_path: Path | str) -> bool:
    """Return True if image meets or exceeds 4K dimensions for its aspect ratio."""
    res = get_image_resolution(image_path)
    if not res:
        return False
    w, h = res
    if w == h:
        return w >= 3840 and h >= 3840
    elif h > w:
        return w >= 2160 and h >= 3840
    return w >= 3840 and h >= 2160


async def ensure_image_4k(
    image_path: Path | str,
    output_path: Optional[Path | str] = None,
    aspect_ratio: Optional[str] = None,
    force_live: bool = False,
    api_key: Optional[str] = None,
) -> Path:
    """Upscale image in-place to 4K UHD if not already 4K.

    Guarantees every image generator delivers 4K broadcast masters.
    """
    src = Path(image_path)
    dst = Path(output_path) if output_path else src
    if not src.is_file():
        return src

    # Mock mode & test fixture safety (Rule 8)
    if is_mock_mode() and src.stat().st_size < 1000:
        return dst

    res = get_image_resolution(src)
    if res:
        w, h = res
        # Already 4K check
        if (w == h and w >= 3840) or (h > w and w >= 2160 and h >= 3840) or (w > h and w >= 3840 and h >= 2160):
            if dst != src:
                import shutil
                shutil.copy2(src, dst)
            return dst

    target_res: Tuple[int, int] = (3840, 2160)
    if aspect_ratio == "1:1" or (res and res[0] == res[1]):
        target_res = (3840, 3840)
    elif aspect_ratio == "9:16" or (res and res[1] > res[0]):
        target_res = (2160, 3840)

    from src.providers.visual.fal_aura_sr import FalAuraSRAdapter
    upscaler = FalAuraSRAdapter(api_key=api_key)
    return await upscaler.upscale_image(src, dst, target_res=target_res, force_live=force_live)


__all__ = ["is_image_4k", "ensure_image_4k", "get_image_resolution"]
