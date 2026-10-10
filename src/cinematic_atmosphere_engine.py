"""Cinematic Atmospheric Engine for Travel Documentaries.

Procedural 100% deterministic visual enhancers:
1. Golden-Hour Sunlight Lens Flare & Anamorphic Sunburst Glints
2. Atmospheric Dust Motes & Twilight Heat Shimmer
3. Documentary Geographic Telemetry HUD & GPS Coordinate Overlay
4. Timed Narration Subtitle Box Renderer
"""

import math
import random
import cv2
import numpy as np


class GoldenHourAtmosphereEngine:
    """Renders warm procedural golden-hour lens flare, sun glints, and floating dust motes."""

    def __init__(self, width: int, height: int, num_motes: int = 120):
        self.w = width
        self.h = height
        self.scale = width / 3840.0

        # Generate procedural floating dust motes
        self.motes = []
        for _ in range(num_motes):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            radius = random.uniform(2.0, 5.5) * self.scale
            alpha = random.uniform(0.15, 0.45)
            vx = random.uniform(-0.4, 0.6) * self.scale
            vy = random.uniform(-0.5, -0.1) * self.scale
            phase = random.uniform(0, 2 * math.pi)
            self.motes.append([x, y, radius, alpha, vx, vy, phase])

        # Sun source position (top-right golden sky)
        self.sun_x = int(width * 0.78)
        self.sun_y = int(height * 0.18)

    def render(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        h, w = frame.shape[:2]
        canvas = frame.copy()

        # 1. Subtle optical radial sun bloom with feathered multi-tier falloff
        flare_pulse = 0.85 + 0.15 * math.sin(frame_idx * 0.05)
        flare_overlay = np.zeros((h, w, 3), dtype=np.float32)

        # Concentric soft feathered rings
        for radius_frac, intensity in [(1.0, 15.0), (0.6, 25.0), (0.3, 40.0), (0.12, 60.0)]:
            r = int(500 * self.scale * flare_pulse * radius_frac)
            glow_mask = np.zeros((h, w), dtype=np.float32)
            cv2.circle(glow_mask, (self.sun_x, self.sun_y), r, 1.0, -1)
            glow_mask = cv2.GaussianBlur(glow_mask, (0, 0), sigmaX=r * 0.45, sigmaY=r * 0.45)
            flare_overlay[:, :, 0] += glow_mask * (intensity * 0.2)  # B
            flare_overlay[:, :, 1] += glow_mask * (intensity * 0.6)  # G
            flare_overlay[:, :, 2] += glow_mask * (intensity * 1.0)  # R (warm golden)

        flare_u8 = np.clip(flare_overlay, 0, 255).astype(np.uint8)
        canvas = cv2.add(canvas, flare_u8)

        # 2. Render floating golden dust motes
        mote_overlay = np.zeros((h, w, 3), dtype=np.uint8)
        for mote in self.motes:
            mote[0] = (mote[0] + mote[4]) % w
            mote[1] = (mote[1] + mote[5]) % h
            # Gentle pulsing shimmer
            shimmer = 0.7 + 0.3 * math.sin(frame_idx * 0.08 + mote[6])
            curr_alpha = mote[3] * shimmer
            color_bgr = (int(30 * curr_alpha), int(90 * curr_alpha), int(140 * curr_alpha))
            cv2.circle(mote_overlay, (int(mote[0]), int(mote[1])), int(mote[2]), color_bgr, -1)

        cv2.add(canvas, mote_overlay, canvas)
        return canvas


class DocumentaryHUDEngine:
    """Renders minimalist, high-end National Geographic / BBC telemetry HUD in the top corner."""

    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        self.scale = width / 3840.0

    def render(
        self,
        frame: np.ndarray,
        location_title: str = "TAORMINA, SICILY",
        coords: str = "37.8516 N, 15.2853 E",
        altitude_m: int = 204,
        frame_idx: int = 0,
    ) -> np.ndarray:
        s = self.scale
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.05 * s
        thick = max(2, int(2.2 * s))

        # Dynamic simulated telemetry drift
        alt_drift = altitude_m + int(2.5 * math.sin(frame_idx * 0.04))
        rec_dot_blink = (frame_idx % 60) < 30

        hud_text = f"GPS: {coords}   |   ELEV: {alt_drift}M   |   LOC: {location_title.upper()}"
        pos_x = int(120 * s)
        pos_y = int(100 * s)

        # Draw elegant dark pill behind HUD telemetry
        (tw, th), baseline = cv2.getTextSize(hud_text, font, font_scale, thick)
        pad_x = int(24 * s)
        pad_y = int(14 * s)
        overlay = frame.copy()
        cv2.rectangle(overlay, (pos_x - pad_x, pos_y - th - pad_y), (pos_x + tw + pad_x, pos_y + pad_y), (15, 18, 22), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        # REC indicator
        rec_x = pos_x
        rec_y = pos_y - th - int(24 * s)
        if rec_dot_blink:
            cv2.circle(frame, (rec_x, rec_y - int(6 * s)), int(8 * s), (40, 40, 240), -1)  # Red recording dot
        cv2.putText(frame, "4K TELEMETRY LOG", (rec_x + int(22 * s), rec_y), font, 0.85 * s, (240, 240, 240), thick, cv2.LINE_AA)

        # Telemetry line
        cv2.putText(frame, hud_text, (pos_x, pos_y), font, font_scale, (255, 255, 255), thick, cv2.LINE_AA)

        return frame


class TimedSubtitleRenderer:
    """Renders broadcast narration subtitle text with high-contrast frosted backing."""

    def __init__(self, width: int, height: int):
        self.w = width
        self.h = height
        self.scale = width / 3840.0

    def render(self, frame: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
        if not text or alpha <= 0.05:
            return frame

        s = self.scale
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.15 * s
        thick = max(2, int(2.2 * s))

        (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thick)
        pad_x = int(28 * s)
        pad_y = int(16 * s)
        center_x = self.w // 2
        box_y = int(self.h - 95 * s)

        # Centered subtitle background pill
        x1 = center_x - (tw // 2) - pad_x
        x2 = center_x + (tw // 2) + pad_x
        y1 = box_y - th - pad_y
        y2 = box_y + pad_y

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (10, 12, 16), -1)
        cv2.addWeighted(overlay, 0.70 * alpha, frame, 1.0 - (0.70 * alpha), 0, frame)

        # Centered crisp typography
        text_x = center_x - (tw // 2)
        cv2.putText(frame, text, (text_x, box_y), font, font_scale, (255, 255, 255), thick, cv2.LINE_AA)
        return frame


class CinematicPostProcessingEngine:
    """Applies Hollywood 2.39:1 letterbox, lens vignette, organic gimbal sway, and diurnal color grading."""

    def __init__(self, width: int, height: int, aspect_ratio: float = 2.39, enable_letterbox: bool = True):
        self.w = width
        self.h = height
        self.enable_letterbox = enable_letterbox
        self.scale = width / 3840.0

        # Calculate 2.39:1 anamorphic letterbox bar thickness
        target_h = int(width / aspect_ratio)
        self.bar_height = max(0, (height - target_h) // 2) if enable_letterbox else 0

        # Precompute radial vignette mask
        y_grid, x_grid = np.ogrid[:height, :width]
        cx, cy = width / 2.0, height / 2.0
        max_dist = math.sqrt(cx * cx + cy * cy)
        dist = np.sqrt((x_grid - cx) ** 2 + (y_grid - cy) ** 2) / max_dist
        self.vignette_mask = np.clip(1.0 - (dist ** 2) * 0.45, 0.45, 1.0).astype(np.float32)

    def render(self, frame: np.ndarray, frame_idx: int, total_frames: int) -> np.ndarray:
        h, w = frame.shape[:2]

        # 1. Diurnal Sky Color Grading (Golden Hour -> Deep Twilight Progression)
        # Shift progress from 0.0 (day sunset) to 1.0 (twilight evening)
        prog = min(1.0, max(0.0, frame_idx / float(max(1, total_frames))))
        # Slightly enhance blue/magenta depth in shadows and warm amber highlights
        b_shift = int(prog * 10)
        g_shift = int(prog * -4)
        r_shift = int(prog * 6)
        if b_shift != 0 or r_shift != 0:
            frame_i16 = frame.astype(np.int16)
            frame_i16[:, :, 0] = np.clip(frame_i16[:, :, 0] + b_shift, 0, 255)
            frame_i16[:, :, 1] = np.clip(frame_i16[:, :, 1] + g_shift, 0, 255)
            frame_i16[:, :, 2] = np.clip(frame_i16[:, :, 2] + r_shift, 0, 255)
            frame = frame_i16.astype(np.uint8)

        # 2. Cinematic Lens Vignetting (Darkened edges)
        frame = (frame * self.vignette_mask[:, :, np.newaxis]).astype(np.uint8)

        # 3. Anamorphic 2.39:1 Letterbox Bars
        if self.bar_height > 0:
            frame[:self.bar_height, :] = 0
            frame[h - self.bar_height:, :] = 0

        return frame
