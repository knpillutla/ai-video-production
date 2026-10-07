"""Tier-0 CPU Micro-Kinetics & Environmental Atmospheric Motion Engine."""

from __future__ import annotations
import math
import random
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np


def _norm_bbox_to_pixels(bbox: List[float], w: int, h: int) -> Tuple[int, int, int, int]:
    y1 = max(0, min(h - 1, int(bbox[0] * h)))
    y2 = max(y1 + 1, min(h, int(bbox[1] * h)))
    x1 = max(0, min(w - 1, int(bbox[2] * w)))
    x2 = max(x1 + 1, min(w, int(bbox[3] * w)))
    return y1, y2, x1, x2


def auto_detect_environmental_spec(img: np.ndarray) -> Dict[str, Any]:
    """Autonomously detect sun hotspots, horizontal water, vertical waterfalls, and snow."""
    h, w = img.shape[:2]
    spec: Dict[str, Any] = {"water_zones": [], "waterfall_zones": [], "is_snow": False}

    # 1. Celestial / Sun Hotspot (Upper 45%)
    sky_gray = cv2.cvtColor(img[:int(h * 0.45), :], cv2.COLOR_BGR2GRAY)
    _, max_val, _, max_loc = cv2.minMaxLoc(sky_gray)
    if max_val >= 235:
        spec["celestial_zone"] = {"center": [max_loc[1] / float(h), max_loc[0] / float(w)]}

    # 2. Water & Waterfall Detection
    lower_h = int(h * 0.25)
    roi = img[lower_h:, :]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h_chan, s_chan, v_chan = cv2.split(hsv)

    water_mask = (((h_chan >= 80) & (h_chan <= 135) & (s_chan >= 20) & (v_chan >= 40)) |
                  ((s_chan < 50) & (v_chan >= 195))).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(w * 0.02), int(h * 0.02)))
    closed = cv2.morphologyEx(water_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = (w * h) * 0.015
    for cnt in contours:
        if cv2.contourArea(cnt) >= min_area:
            cx, cy, cw, ch = cv2.boundingRect(cnt)
            bbox = [(lower_h + cy) / float(h), (lower_h + cy + ch) / float(h), cx / float(w), (cx + cw) / float(w)]
            if ch > cw * 1.2:
                spec["waterfall_zones"].append(bbox)
            elif (lower_h + cy) > h * 0.45:
                spec["water_zones"].append(bbox)

    # 3. Snow Scene Detection
    snow_pixels = (s_chan < 35) & (v_chan > 210)
    if float(np.mean(snow_pixels)) > 0.22:
        spec["is_snow"] = True

    return spec


def apply_celestial_shimmer(frame: np.ndarray, cel: Dict[str, Any], frame_idx: int) -> None:
    """Apply subtle breathing solar/lunar corona exposure glint."""
    center = cel.get("center")
    if not center or len(center) != 2:
        return
    h, w = frame.shape[:2]
    cy, cx = int(center[0] * h), int(center[1] * w)
    rad = max(10, int(min(w, h) * 0.15))
    pulse = 1.0 + 0.04 * math.sin(frame_idx * 0.08)

    y1, y2 = max(0, cy - rad), min(h, cy + rad)
    x1, x2 = max(0, cx - rad), min(w, cx + rad)
    if y2 <= y1 or x2 <= x1:
        return
    gy, gx = np.ogrid[y1:y2, x1:x2]
    dist_sq = (gx - cx) ** 2 + (gy - cy) ** 2
    mask = np.clip(1.0 - (dist_sq / float(rad * rad)), 0.0, 1.0)[:, :, np.newaxis]
    boost = 1.0 + (pulse - 1.0) * mask
    frame[y1:y2, x1:x2] = np.clip(frame[y1:y2, x1:x2].astype(np.float32) * boost, 0, 255).astype(np.uint8)


def apply_water_surface_ripples(frame: np.ndarray, zones: List[List[float]], frame_idx: int) -> None:
    """Apply harmonic Gerstner sinusoidal wave displacement with specular glint."""
    h, w = frame.shape[:2]
    for bbox in zones:
        y1, y2, x1, x2 = _norm_bbox_to_pixels(bbox, w, h)
        roi = frame[y1:y2, x1:x2]
        rh, rw = roi.shape[:2]
        if rh <= 6 or rw <= 6:
            continue
        gx, gy = np.meshgrid(np.arange(rw, dtype=np.float32), np.arange(rh, dtype=np.float32))
        map_x = gx + (2.2 * np.sin(gx * 0.04 + frame_idx * 0.11)).astype(np.float32)
        map_y = gy + (1.4 * np.cos(gy * 0.05 + frame_idx * 0.09)).astype(np.float32)
        remapped = cv2.remap(roi, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        glint = 1.0 + 0.035 * np.sin(gx * 0.08 - frame_idx * 0.12) * np.cos(gy * 0.06 + frame_idx * 0.10)
        frame[y1:y2, x1:x2] = np.clip(remapped.astype(np.float32) * glint[:, :, np.newaxis], 0, 255).astype(np.uint8)


def apply_waterfall_cascade_flow(frame: np.ndarray, zones: List[List[float]], frame_idx: int) -> None:
    """Apply downward gravitational cascade flow (+Y vector) with micro-turbulence."""
    h, w = frame.shape[:2]
    for bbox in zones:
        y1, y2, x1, x2 = _norm_bbox_to_pixels(bbox, w, h)
        roi = frame[y1:y2, x1:x2]
        rh, rw = roi.shape[:2]
        if rh <= 6 or rw <= 6:
            continue
        gx, gy = np.meshgrid(np.arange(rw, dtype=np.float32), np.arange(rh, dtype=np.float32))
        # Downward acceleration traveling wave
        turb_x = 1.5 * np.sin(gx * 0.12 + gy * 0.04 + frame_idx * 0.18)
        flow_y = gy - (4.0 * np.sin(gy * 0.06 - frame_idx * 0.28))
        map_x = np.clip(gx + turb_x, 0, rw - 1).astype(np.float32)
        map_y = np.clip(flow_y, 0, rh - 1).astype(np.float32)
        frame[y1:y2, x1:x2] = cv2.remap(roi, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


class ProceduralSnowFlakeEngine:
    """Renders soft, circular, fluttering snowflakes with wind oscillation (Zero rain needles)."""
    def __init__(self, width: int, height: int, num_flakes: int = 450):
        self.w, self.h = width, height
        self.flakes = []
        for _ in range(num_flakes):
            x = random.uniform(0, width)
            y = random.uniform(-50, height)
            r = random.choice([1, 1, 2, 2, 3, random.uniform(4, 7)])  # Soft depth layers
            speed_y = random.uniform(1.6, 3.8)
            freq = random.uniform(0.03, 0.06)
            amp = random.uniform(12.0, 28.0)
            phase = random.uniform(0, math.tau)
            alpha = random.uniform(0.45, 0.85)
            self.flakes.append([x, y, r, speed_y, freq, amp, phase, alpha])

    def render(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        snow_layer = np.zeros_like(frame)
        for f in self.flakes:
            bx, by, r, sy, freq, amp, phase, alpha = f
            cur_x = int((bx + amp * math.sin(frame_idx * freq + phase)) % self.w)
            cur_y = int((by + sy * frame_idx) % (self.h + 20)) - 10
            int_r = max(1, int(r))
            cv2.circle(snow_layer, (cur_x, cur_y), int_r, (250, 252, 255), -1)

        # Soft Gaussian blur for organic snowflake fluffiness
        blurred_snow = cv2.GaussianBlur(snow_layer, (3, 3), 0)
        return cv2.addWeighted(frame, 1.0, blurred_snow, 0.70, 0)


def prepare_micro_kinetics(img: np.ndarray, spec: Optional[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """Pre-pass sprite extraction and environmental detection."""
    if not spec:
        spec = auto_detect_environmental_spec(img)
    return img, []


def render_micro_kinetics_frame(
    clean_base: np.ndarray, prepared_sprites: List[Dict[str, Any]], spec: Optional[Dict[str, Any]],
    frame_idx: int, total_frames: int, snow_engine: Optional[ProceduralSnowFlakeEngine] = None,
) -> np.ndarray:
    """Render a single frame with auto-detected sun, water ripples, cascades, and snow."""
    if not spec:
        return clean_base
    frame = clean_base.copy()

    if spec.get("celestial_zone"):
        apply_celestial_shimmer(frame, spec["celestial_zone"], frame_idx)

    water_zones = spec.get("water_zones", [])
    if water_zones:
        apply_water_surface_ripples(frame, water_zones, frame_idx)

    waterfall_zones = spec.get("waterfall_zones", [])
    if waterfall_zones:
        apply_waterfall_cascade_flow(frame, waterfall_zones, frame_idx)

    if spec.get("is_snow") and snow_engine is not None:
        frame = snow_engine.render(frame, frame_idx)

    return frame
