"""Local Deterministic Image Color Harmonization & Lighting Sanitization Service.

Enforces Tier 0 ($0.00) color temperature, luminance, and white-balance continuity
across multi-scene video keyframes using Reinhard LAB color space transfer.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import cv2
import numpy as np

from src.core.telemetry import logger

LIGHTING_CONFLICT_REGEX = re.compile(
    r"\b(golden\s+(?:sunlight\s+)?flares?|sunset\s+glow|golden\s+hour|dramatic\s+high\s+contrast\s+sunbeams?|"
    r"warm\s+amber\s+saturation|amber\s+tint|dusk\s+lighting|evening\s+glow|sunbeams?\s+slicing[^\.,;]*)\b",
    re.IGNORECASE,
)

MASTER_DAYLIGHT_ANCHOR = (
    "Crisp natural balanced 5500K daylight, high sun in natural blue sky, "
    "realistic balanced skin tones, clean neutral white balance, uniform directional shadows, "
    "zero golden hour flare, zero sunset amber wash, zero color temperature drift"
)


def sanitize_scene_prompt_lighting(prompt: str, master_ambience: str | None = None) -> str:
    """Strip contradictory lighting buzzwords and enforce uniform master ambience anchor."""
    cleaned = LIGHTING_CONFLICT_REGEX.sub("", prompt)
    cleaned = re.sub(r",\s*,+", ",", cleaned).strip(", ")
    if master_ambience and master_ambience.lower() not in cleaned.lower():
        cleaned = f"{cleaned}, {master_ambience}"
    return cleaned


def harmonize_image_colors(target_path: Path, reference_path: Path) -> Path:
    """Harmonize target image color temperature and contrast against reference image (Reinhard LAB transfer)."""
    if not target_path.is_file() or not reference_path.is_file():
        return target_path
    if target_path.resolve() == reference_path.resolve():
        return target_path

    try:
        ref_bgr = cv2.imread(str(reference_path))
        tgt_bgr = cv2.imread(str(target_path))
        if ref_bgr is None or tgt_bgr is None:
            return target_path

        ref_lab = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

        res_lab = np.zeros_like(tgt_lab)
        for i in range(3):
            mu_r, std_r = float(ref_lab[:, :, i].mean()), float(ref_lab[:, :, i].std())
            mu_t, std_t = float(tgt_lab[:, :, i].mean()), float(tgt_lab[:, :, i].std())
            std_scale = std_r / max(std_t, 1e-4)
            # Subtle blend (85% harmonized, 15% original) to preserve intrinsic costume pigments while locking lighting
            harmonized = (tgt_lab[:, :, i] - mu_t) * std_scale + mu_r
            res_lab[:, :, i] = 0.85 * harmonized + 0.15 * tgt_lab[:, :, i]

        res_lab = np.clip(res_lab, 0, 255).astype(np.uint8)
        res_bgr = cv2.cvtColor(res_lab, cv2.COLOR_LAB2BGR)
        cv2.imwrite(str(target_path), res_bgr)
        logger.info(f"color_harmonized: {target_path.name} harmonized against reference {reference_path.name}")
    except Exception as ex:
        logger.warning(f"color_harmonization_skipped: {ex}")

    return target_path


__all__ = ["sanitize_scene_prompt_lighting", "harmonize_image_colors", "MASTER_DAYLIGHT_ANCHOR"]
