"""Tier-0 CPU Micro-Kinetics Engine for Wide Architectural & Scenic Shots.

Simulates macroscopic movement (subpixel sprite drift, canopy sway, water surface
harmonic ripples, and celestial corona shimmer) with zero background voids.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np


def _norm_bbox_to_pixels(bbox: List[float], w: int, h: int) -> Tuple[int, int, int, int]:
    """Convert normalized [ymin, ymax, xmin, xmax] (0.0-1.0) to pixel bounds."""
    y1 = max(0, min(h - 1, int(bbox[0] * h)))
    y2 = max(y1 + 1, min(h, int(bbox[1] * h)))
    x1 = max(0, min(w - 1, int(bbox[2] * w)))
    x2 = max(x1 + 1, min(w, int(bbox[3] * w)))
    return y1, y2, x1, x2


def prepare_micro_kinetics(
    img: np.ndarray,
    spec: Optional[Dict[str, Any]],
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """Pre-pass: inpaint sprite footprints once at frame 0 to create a pristine base canvas."""
    if not spec:
        return img, []

    h, w, _ = img.shape
    prepared_sprites: List[Dict[str, Any]] = []
    mask = np.zeros((h, w), dtype=np.uint8)

    sprites_data = spec.get("sprites", []) or []
    for s in sprites_data:
        bbox = s.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        y1, y2, x1, x2 = _norm_bbox_to_pixels(bbox, w, h)
        sh, sw = y2 - y1, x2 - x1
        if sh <= 2 or sw <= 2:
            continue

        sprite_crop = img[y1:y2, x1:x2].copy()
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

        delta_pct = s.get("delta_pct", [0.03, 0.0])
        prepared_sprites.append({
            "sprite": sprite_crop,
            "x1": x1, "y1": y1, "sw": sw, "sh": sh,
            "delta_x": float(delta_pct[0] * w),
            "delta_y": float(delta_pct[1] * h),
            "bobbing": bool(s.get("bobbing", False)),
        })

    if np.any(mask > 0):
        clean_base = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    else:
        clean_base = img

    return clean_base, prepared_sprites


def apply_tree_canopy_sway(frame: np.ndarray, zones: List[List[float]], frame_idx: int) -> None:
    """Apply graduated canopy sway to tree bounding boxes (base locked, upper rows sway)."""
    h, w, _ = frame.shape
    for bbox in zones:
        if len(bbox) != 4:
            continue
        y1, y2, x1, x2 = _norm_bbox_to_pixels(bbox, w, h)
        roi = frame[y1:y2, x1:x2]
        rh = roi.shape[0]
        if rh <= 4:
            continue
        for row in range(rh):
            sway_amp = (1.0 - (row / float(rh))) * 3.5
            shift = int(sway_amp * math.sin(frame_idx * 0.12))
            if shift != 0:
                roi[row] = np.roll(roi[row], shift, axis=0)


def apply_water_surface_ripples(frame: np.ndarray, zones: List[List[float]], frame_idx: int) -> None:
    """Apply harmonic Gerstner-style sinusoidal wave remapping to water surfaces."""
    h, w, _ = frame.shape
    for bbox in zones:
        if len(bbox) != 4:
            continue
        y1, y2, x1, x2 = _norm_bbox_to_pixels(bbox, w, h)
        roi = frame[y1:y2, x1:x2]
        rh, rw = roi.shape[:2]
        if rh <= 4 or rw <= 4:
            continue
        gx, gy = np.meshgrid(np.arange(rw, dtype=np.float32), np.arange(rh, dtype=np.float32))
        map_x = gx + (2.0 * np.sin(gx * 0.05 + frame_idx * 0.10)).astype(np.float32)
        map_y = gy + (1.2 * np.cos(gy * 0.05 + frame_idx * 0.08)).astype(np.float32)
        frame[y1:y2, x1:x2] = cv2.remap(roi, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def apply_celestial_shimmer(frame: np.ndarray, cel: Dict[str, Any], frame_idx: int) -> None:
    """Apply subtle breathing solar/lunar corona exposure glint."""
    center = cel.get("center")
    if not center or len(center) != 2:
        return
    h, w, _ = frame.shape
    cy, cx = int(center[0] * h), int(center[1] * w)
    rad = max(10, int(min(w, h) * 0.12))
    pulse = 1.0 + 0.035 * math.sin(frame_idx * 0.08)

    y1, y2 = max(0, cy - rad), min(h, cy + rad)
    x1, x2 = max(0, cx - rad), min(w, cx + rad)
    if y2 <= y1 or x2 <= x1:
        return

    gy, gx = np.ogrid[y1:y2, x1:x2]
    dist_sq = (gx - cx) ** 2 + (gy - cy) ** 2
    rad_sq = rad * rad
    mask = np.clip(1.0 - (dist_sq / float(rad_sq)), 0.0, 1.0)[:, :, np.newaxis]
    boost = 1.0 + (pulse - 1.0) * mask
    frame[y1:y2, x1:x2] = np.clip(frame[y1:y2, x1:x2].astype(np.float32) * boost, 0, 255).astype(np.uint8)


def render_micro_kinetics_frame(
    clean_base: np.ndarray,
    prepared_sprites: List[Dict[str, Any]],
    spec: Optional[Dict[str, Any]],
    frame_idx: int,
    total_frames: int,
) -> np.ndarray:
    """Render a single 4K frame with all micro-kinetic elements composited."""
    if not spec and not prepared_sprites:
        return clean_base

    frame = clean_base.copy()
    h, w, _ = frame.shape
    t = frame_idx / float(max(1, total_frames - 1))
    easing = 1.0 - (1.0 - t) ** 3

    # 1. Canopy sway
    tree_zones = (spec or {}).get("tree_sway_zones", [])
    if tree_zones:
        apply_tree_canopy_sway(frame, tree_zones, frame_idx)

    # 2. Water ripples
    water_zones = (spec or {}).get("water_zones", [])
    if water_zones:
        apply_water_surface_ripples(frame, water_zones, frame_idx)

    # 3. Celestial shimmer
    cel = (spec or {}).get("celestial_zone")
    if cel:
        apply_celestial_shimmer(frame, cel, frame_idx)

    # 4. Subpixel sprite drift
    for s in prepared_sprites:
        cur_x = s["x1"] + (s["delta_x"] * easing)
        cur_y = s["y1"] + (s["delta_y"] * easing)
        if s["bobbing"]:
            cur_y += 1.5 * math.sin(frame_idx * 0.15)

        ix, iy = int(round(cur_x)), int(round(cur_y))
        sw, sh = s["sw"], s["sh"]
        if 0 <= ix and ix + sw <= w and 0 <= iy and iy + sh <= h:
            frame[iy:iy + sh, ix:ix + sw] = s["sprite"]

    return frame
