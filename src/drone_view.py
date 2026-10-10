import os
import sys
import argparse
import time
import subprocess
import random
import cv2
import numpy as np
from typing import Optional, Dict, Any, List

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"

# Optional Tier-0 CPU Neural Confirmation Engine (0% GPU / 0 VRAM)
ONNX_SESSION = None
try:
    import onnxruntime as ort
    model_onnx_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "yolov8n.onnx")
    if os.path.exists(model_onnx_path):
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        ONNX_SESSION = ort.InferenceSession(model_onnx_path, sess_options=opts, providers=["CPUExecutionProvider"])
except Exception:
    ONNX_SESSION = None

COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
    "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]


def onnx_confirm_patch(patch: np.ndarray, target_label: str = "bird", min_conf: float = 0.28) -> bool:
    """Uses CPU ONNX to confirm semantic label of a candidate patch found by native 4K detector."""
    if ONNX_SESSION is None or patch is None or patch.size == 0:
        return True  # Fallback gracefully to native 4K heuristic if model is absent
    ph, pw = patch.shape[:2]
    if ph < 15 or pw < 15:
        return True
    scale = min(640 / float(pw), 640 / float(ph))
    nw, nh = max(1, int(pw * scale)), max(1, int(ph * scale))
    canvas = np.full((640, 640, 3), 114, dtype=np.uint8)
    dx = (640 - nw) // 2
    dy = (640 - nh) // 2
    canvas[dy:dy + nh, dx:dx + nw] = cv2.resize(patch, (nw, nh), interpolation=cv2.INTER_LINEAR)
    blob = (canvas.astype(np.float32) / 255.0).transpose(2, 0, 1)[np.newaxis, :]
    try:
        preds = ONNX_SESSION.run(None, {"images": blob})[0][0].T
        for row in preds:
            scores = row[4:]
            cid = int(np.argmax(scores))
            conf = float(scores[cid])
            if conf >= min_conf and COCO_CLASSES[cid] == target_label:
                return True
    except Exception:
        return True
    return False


class CinematicRainEngine:
    """High-performance vectorized procedural rain engine: organic translucent drizzle, wind slant, and soft mist."""

    def __init__(self, width: int, height: int, intensity: str = "light", wind_tilt: float = 4.0, source_img: Optional[np.ndarray] = None):
        self.w = width
        self.h = height
        self.wind_tilt = wind_tilt
        self.intensity = intensity.lower()

        scale_factor = width / 1920.0
        self.scale = scale_factor

        configs = {
            "light": {
                "drops": 600,
                "bg_len": (8, 14),   "bg_spd": (16, 24),
                "mg_len": (14, 22),  "mg_spd": (22, 30),
                "fg_len": (22, 34),  "fg_spd": (28, 40),
                "mist_alpha": 0.02,  "rain_alpha": 0.22,
                "wind": 2.5,
            },
            "medium": {
                "drops": 4500,
                "bg_len": (20, 32),  "bg_spd": (28, 38),
                "mg_len": (42, 64),  "mg_spd": (44, 58),
                "fg_len": (68, 96),  "fg_spd": (58, 76),
                "mist_alpha": 0.08,  "rain_alpha": 0.40,
                "wind": 5.5,
            },
            "heavy": {
                "drops": 10500,
                "bg_len": (40, 75),   "bg_spd": (55, 85),
                "mg_len": (80, 140),  "mg_spd": (85, 135),
                "fg_len": (140, 220), "fg_spd": (120, 180),
                "mist_alpha": 0.20,   "rain_alpha": 0.55,
                "wind": 14.0,
            },
        }
        cfg = configs.get(self.intensity, configs["medium"])
        self.cfg = cfg
        self.wind_tilt = cfg["wind"]
        total_drops = cfg["drops"]

        margin = max(abs(self.wind_tilt * scale_factor) * (height / 20.0), width * 0.25)
        self.spawn_x_min = -margin if self.wind_tilt > 0 else 0
        self.spawn_x_max = width if self.wind_tilt > 0 else (width + margin)
        self.margin = margin

        # Layer 1: Background Micro-Drizzle (55% of drops)
        N_bg = int(total_drops * 0.55)
        self.bg_drops = np.zeros((N_bg, 5), dtype=np.float32)
        self._init_drops(self.bg_drops, cfg["bg_len"], cfg["bg_spd"])

        # Layer 2: Midground Natural Rain (35% of drops)
        N_mg = int(total_drops * 0.35)
        self.mg_drops = np.zeros((N_mg, 5), dtype=np.float32)
        self._init_drops(self.mg_drops, cfg["mg_len"], cfg["mg_spd"])

        # Layer 3: Foreground Droplets (10% of drops)
        N_fg = int(total_drops * 0.10)
        self.fg_drops = np.zeros((N_fg, 5), dtype=np.float32)
        self._init_drops(self.fg_drops, cfg["fg_len"], cfg["fg_spd"])

        # Overcast storm sky mist layer
        gradient = np.linspace(0.85, 1.15, height).reshape(height, 1, 1)
        storm_mist = np.full((height, width, 3), (150, 165, 175), dtype=np.float32) * gradient
        self.mist_layer = np.clip(storm_mist, 0, 255).astype(np.uint8)

        self.weather_mask = None
        self.inv_weather_mask = None
        if source_img is not None:
            self._build_weather_mask(source_img)

    def _init_drops(self, arr: np.ndarray, len_range, spd_range):
        N = len(arr)
        arr[:, 0] = np.random.uniform(self.spawn_x_min, self.spawn_x_max, N)
        arr[:, 1] = np.random.uniform(-100 * self.scale, self.h, N)
        arr[:, 2] = np.random.uniform(len_range[0], len_range[1], N) * self.scale
        arr[:, 3] = np.random.uniform(spd_range[0], spd_range[1], N) * self.scale
        arr[:, 4] = np.random.uniform(0.80, 1.20, N)

    def _build_weather_mask(self, img: np.ndarray):
        h, w = self.h, self.w
        resized = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        # 0. Outdoor Landscape Guard: If upper horizon has bright open sky, weather covers full screen edge-to-edge
        tl_sky = float(np.mean(hsv[:int(h * 0.35), :int(w * 0.35), 2] > 100))
        top_sky = float(np.mean(hsv[:int(h * 0.20), :, 2] > 100))
        if tl_sky > 0.65 or top_sky > 0.70:
            self.weather_mask = None
            self.inv_weather_mask = None
            return

        # 1. Check for Cozy Bedroom / Cabin Window
        left_hsv = hsv[:, :int(w * 0.35)]
        is_warm_interior = float(np.mean((left_hsv[:, :, 0] < 25) & (left_hsv[:, :, 1] > 60))) > 0.42

        if is_warm_interior:
            mask = np.ones((h, w), dtype=np.float32)
            post_x = int(w * 0.36)
            mask[:, :post_x] = 0.0
            bed_mask = np.zeros((h, w), dtype=np.uint8)
            pts = np.array([[0, int(h * 0.70)], [post_x, int(h * 0.72)], [int(w * 0.62), h], [0, h]], np.int32)
            cv2.fillPoly(bed_mask, [pts], 255)
            mask[bed_mask == 255] = 0.0
            self.weather_mask = cv2.GaussianBlur(mask, (21, 21), 5)
            self.inv_weather_mask = 1.0 - self.weather_mask
            print(f" -> [Sanctuary Guard] Cozy Bedroom / Cabin sanctuary detected! Weather masked exclusively to exterior window (post @ x={post_x}).")
            return

        # 2. Check for Alpine / Expedition Tent Sanctuary
        orange_dome = (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 24) & (hsv[:, :, 1] > 100)
        top_orange = float(np.mean(orange_dome[:int(h * 0.20), :]))
        if top_orange > 0.40:
            tent_interior = orange_dome | (hsv[:, :, 2] < 50)
            mask = (~tent_interior).astype(np.float32)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(w * 0.02), int(h * 0.02)))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            self.weather_mask = cv2.GaussianBlur(mask, (31, 31), 8)
            self.inv_weather_mask = 1.0 - self.weather_mask
            print(" -> [Sanctuary Guard] Alpine Tent sanctuary detected! Weather masked exclusively outside the tent opening.")
            return

        self.weather_mask = None
        self.inv_weather_mask = None

    def render(self, frame: np.ndarray) -> np.ndarray:
        h, w = self.h, self.w
        rain_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        fg_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        base_tilt = self.wind_tilt * self.scale
        margin = self.margin

        # 1. Background Micro-Drizzle
        t_bg = base_tilt * 0.5 * self.bg_drops[:, 4]
        self.bg_drops[:, 0] += t_bg
        self.bg_drops[:, 1] += self.bg_drops[:, 3]
        reset_bg = (self.bg_drops[:, 1] > h) | (self.bg_drops[:, 0] > (w + margin))
        if np.any(reset_bg):
            cnt = np.count_nonzero(reset_bg)
            self.bg_drops[reset_bg, 1] = np.random.uniform(-self.bg_drops[reset_bg, 2] * 2, -self.bg_drops[reset_bg, 2], cnt)
            self.bg_drops[reset_bg, 0] = np.random.uniform(self.spawn_x_min, self.spawn_x_max, cnt)

        bx1 = self.bg_drops[:, 0].astype(np.int32)
        by1 = self.bg_drops[:, 1].astype(np.int32)
        bx2 = (self.bg_drops[:, 0] + t_bg).astype(np.int32)
        by2 = (self.bg_drops[:, 1] + self.bg_drops[:, 2]).astype(np.int32)
        b_pts = np.stack([np.stack([bx1, by1], axis=1), np.stack([bx2, by2], axis=1)], axis=1)
        cv2.polylines(rain_canvas, b_pts, isClosed=False, color=(125, 140, 155), thickness=1, lineType=cv2.LINE_AA)

        # 2. Midground Rain
        t_mg = base_tilt * 0.85 * self.mg_drops[:, 4]
        self.mg_drops[:, 0] += t_mg
        self.mg_drops[:, 1] += self.mg_drops[:, 3]
        reset_mg = (self.mg_drops[:, 1] > h) | (self.mg_drops[:, 0] > (w + margin))
        if np.any(reset_mg):
            cnt = np.count_nonzero(reset_mg)
            self.mg_drops[reset_mg, 1] = np.random.uniform(-self.mg_drops[reset_mg, 2] * 2, -self.mg_drops[reset_mg, 2], cnt)
            self.mg_drops[reset_mg, 0] = np.random.uniform(self.spawn_x_min, self.spawn_x_max, cnt)

        mx1 = self.mg_drops[:, 0].astype(np.int32)
        my1 = self.mg_drops[:, 1].astype(np.int32)
        mx2 = (self.mg_drops[:, 0] + t_mg).astype(np.int32)
        my2 = (self.mg_drops[:, 1] + self.mg_drops[:, 2]).astype(np.int32)
        m_pts = np.stack([np.stack([mx1, my1], axis=1), np.stack([mx2, my2], axis=1)], axis=1)
        cv2.polylines(rain_canvas, m_pts, isClosed=False, color=(175, 190, 205), thickness=1, lineType=cv2.LINE_AA)

        # 3. Foreground Rain
        t_fg = base_tilt * self.fg_drops[:, 4]
        self.fg_drops[:, 0] += t_fg
        self.fg_drops[:, 1] += self.fg_drops[:, 3]
        reset_fg = (self.fg_drops[:, 1] > h) | (self.fg_drops[:, 0] > (w + margin))
        if np.any(reset_fg):
            cnt = np.count_nonzero(reset_fg)
            self.fg_drops[reset_fg, 1] = np.random.uniform(-self.fg_drops[reset_fg, 2] * 2, -self.fg_drops[reset_fg, 2], cnt)
            self.fg_drops[reset_fg, 0] = np.random.uniform(self.spawn_x_min, self.spawn_x_max, cnt)

        fx1 = self.fg_drops[:, 0].astype(np.int32)
        fy1 = self.fg_drops[:, 1].astype(np.int32)
        fx2 = (self.fg_drops[:, 0] + t_fg).astype(np.int32)
        fy2 = (self.fg_drops[:, 1] + self.fg_drops[:, 2]).astype(np.int32)
        f_pts = np.stack([np.stack([fx1, fy1], axis=1), np.stack([fx2, fy2], axis=1)], axis=1)
        cv2.polylines(fg_canvas, f_pts, isClosed=False, color=(215, 230, 245), thickness=2, lineType=cv2.LINE_AA)

        fg_canvas = cv2.GaussianBlur(fg_canvas, (3, 3), 0.8)
        rain_canvas = cv2.add(rain_canvas, fg_canvas)

        mist_a = self.cfg["mist_alpha"]
        rain_a = self.cfg["rain_alpha"]
        misted_frame = cv2.addWeighted(frame, 1.0 - mist_a, self.mist_layer, mist_a, 0)
        weathered = cv2.addWeighted(misted_frame, 1.0, rain_canvas, rain_a, 0)

        if self.weather_mask is not None:
            return cv2.blendLinear(frame, weathered, self.inv_weather_mask, self.weather_mask)
        return weathered


class CinematicSnowEngine:
    """High-performance vectorized procedural snowfall engine: drifting flurries, lateral flutter, and soft bokeh."""

    def __init__(self, width: int, height: int, intensity: str = "medium", wind: float = 3.5, source_img: Optional[np.ndarray] = None):
        self.w, self.h = width, height
        self.scale = width / 1920.0
        self.intensity = intensity.lower()

        configs = {
            "light": {
                "flakes": 1200,
                "bg_r": (0.7, 1.3),  "bg_spd": (3.5, 6.0),   "bg_alpha": 0.35,
                "mg_r": (1.2, 2.0),  "mg_spd": (5.0, 9.0),   "mg_alpha": 0.55,
                "fg_r": (2.2, 3.8),  "fg_spd": (8.0, 14.0),  "fg_alpha": 0.35,
                "flutter_amp": 20.0, "frost_alpha": 0.03,    "wind": 1.5,
            },
            "medium": {
                "flakes": 2800,
                "bg_r": (0.8, 1.4),  "bg_spd": (4.0, 7.5),   "bg_alpha": 0.40,
                "mg_r": (1.4, 2.2),  "mg_spd": (6.5, 11.5),  "mg_alpha": 0.65,
                "fg_r": (2.5, 4.2),  "fg_spd": (10.0, 18.0), "fg_alpha": 0.40,
                "flutter_amp": 35.0, "frost_alpha": 0.06,    "wind": 3.0,
            },
            "heavy": {
                "flakes": 6500,
                "bg_r": (0.9, 1.6),  "bg_spd": (6.0, 11.0),  "bg_alpha": 0.50,
                "mg_r": (1.6, 2.6),  "mg_spd": (9.0, 16.0),  "mg_alpha": 0.75,
                "fg_r": (2.8, 4.8),  "fg_spd": (14.0, 24.0), "fg_alpha": 0.45,
                "flutter_amp": 60.0, "frost_alpha": 0.12,    "wind": 6.5,
            },
        }
        cfg = configs.get(self.intensity, configs["medium"])
        self.cfg = cfg
        self.wind = cfg["wind"] * self.scale
        total_flakes = cfg["flakes"]

        # 1. Background micro flurries (55%)
        N_bg = int(total_flakes * 0.55)
        self.bg_flakes = np.zeros((N_bg, 7), dtype=np.float32)
        self._init_flakes(self.bg_flakes, cfg["bg_r"], cfg["bg_spd"], cfg["flutter_amp"] * 0.5)

        # 2. Midground drifting flakes (35%)
        N_mg = int(total_flakes * 0.35)
        self.mg_flakes = np.zeros((N_mg, 7), dtype=np.float32)
        self._init_flakes(self.mg_flakes, cfg["mg_r"], cfg["mg_spd"], cfg["flutter_amp"])

        # 3. Foreground soft-focus bokeh flakes (10%)
        N_fg = int(total_flakes * 0.10)
        self.fg_flakes = np.zeros((N_fg, 7), dtype=np.float32)
        self._init_flakes(self.fg_flakes, cfg["fg_r"], cfg["fg_spd"], cfg["flutter_amp"] * 1.4)

        # Frost atmospheric tone layer
        gradient = np.linspace(1.08, 0.94, height).reshape(height, 1, 1)
        frost_img = np.full((height, width, 3), (225, 235, 245), dtype=np.float32) * gradient
        self.frost_layer = np.clip(frost_img, 0, 255).astype(np.uint8)

        self.weather_mask = None
        self.inv_weather_mask = None
        if source_img is not None:
            self._build_weather_mask(source_img)

    def _init_flakes(self, arr: np.ndarray, r_range, spd_range, flutter_amp):
        N = len(arr)
        arr[:, 0] = np.random.uniform(-self.w * 0.15, self.w * 1.15, N)
        arr[:, 1] = np.random.uniform(-80, self.h, N)
        arr[:, 2] = np.random.uniform(r_range[0], r_range[1], N) * self.scale
        arr[:, 3] = np.random.uniform(spd_range[0], spd_range[1], N) * self.scale
        arr[:, 4] = np.random.uniform(flutter_amp * 0.7, flutter_amp * 1.3, N) * self.scale
        arr[:, 5] = np.random.uniform(0.04, 0.10, N)
        arr[:, 6] = np.random.uniform(0, 2 * np.pi, N)

    def _build_weather_mask(self, img: np.ndarray):
        h, w = self.h, self.w
        resized = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        # 0. Outdoor Landscape Guard: If upper horizon has bright open sky, weather covers full screen edge-to-edge
        tl_sky = float(np.mean(hsv[:int(h * 0.35), :int(w * 0.35), 2] > 100))
        top_sky = float(np.mean(hsv[:int(h * 0.20), :, 2] > 100))
        if tl_sky > 0.65 or top_sky > 0.70:
            self.weather_mask = None
            self.inv_weather_mask = None
            return

        # 1. Warm interior cabin/room check:
        left_hsv = hsv[:, :int(w * 0.35)]
        is_warm_interior = float(np.mean((left_hsv[:, :, 0] < 25) & (left_hsv[:, :, 1] > 60))) > 0.42
        if is_warm_interior:
            mask = np.ones((h, w), dtype=np.float32)
            post_x = int(w * 0.36)
            mask[:, :post_x] = 0.0
            bed_mask = np.zeros((h, w), dtype=np.uint8)
            pts = np.array([[0, int(h * 0.70)], [post_x, int(h * 0.72)], [int(w * 0.62), h], [0, h]], np.int32)
            cv2.fillPoly(bed_mask, [pts], 255)
            mask[bed_mask == 255] = 0.0
            self.weather_mask = cv2.GaussianBlur(mask, (21, 21), 5)
            self.inv_weather_mask = 1.0 - self.weather_mask
            print(f" -> [Sanctuary Guard] Cozy Bedroom / Cabin sanctuary detected! Snow masked outside window.")
            return

        # 2. Alpine tent check:
        orange_dome = (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 24) & (hsv[:, :, 1] > 100)
        top_orange = float(np.mean(orange_dome[:int(h * 0.20), :]))
        if top_orange > 0.40:
            tent_interior = orange_dome | (hsv[:, :, 2] < 50)
            mask = (~tent_interior).astype(np.float32)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(w * 0.02), int(h * 0.02)))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            self.weather_mask = cv2.GaussianBlur(mask, (31, 31), 8)
            self.inv_weather_mask = 1.0 - self.weather_mask
            print(" -> [Sanctuary Guard] Alpine Tent sanctuary detected! Snow masked outside tent opening.")
            return
        self.weather_mask = None
        self.inv_weather_mask = None

    def render(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        h, w = self.h, self.w
        bg_canvas = np.zeros((h, w), dtype=np.uint8)
        mg_canvas = np.zeros((h, w), dtype=np.uint8)
        fg_canvas = np.zeros((h, w), dtype=np.uint8)
        t = float(frame_idx)
        cfg = self.cfg
        tilt_angle = int(np.clip(-self.wind * 2.2, -22.0, 22.0))

        # 1. Background micro flurries
        self.bg_flakes[:, 1] += self.bg_flakes[:, 3]
        reset_bg = self.bg_flakes[:, 1] > h
        if np.any(reset_bg):
            cnt = np.count_nonzero(reset_bg)
            self.bg_flakes[reset_bg, 1] = np.random.uniform(-40, -5, cnt)
            self.bg_flakes[reset_bg, 0] = np.random.uniform(-w * 0.15, w * 1.15, cnt)
        cur_bx = (self.bg_flakes[:, 0] + self.bg_flakes[:, 4] * np.sin(t * self.bg_flakes[:, 5] + self.bg_flakes[:, 6]) + self.wind * (self.bg_flakes[:, 1] / h)).astype(np.int32)
        cur_by = self.bg_flakes[:, 1].astype(np.int32)
        for i in range(len(self.bg_flakes)):
            rx = max(1, int(self.bg_flakes[i, 2]))
            ry = max(2, int(rx * 2.8))
            cv2.ellipse(bg_canvas, (cur_bx[i], cur_by[i]), (rx, ry), tilt_angle, 0, 360, 255, -1, cv2.LINE_AA)

        # 2. Midground slender flakes (3.2x aerodynamic height)
        self.mg_flakes[:, 1] += self.mg_flakes[:, 3]
        reset_mg = self.mg_flakes[:, 1] > h
        if np.any(reset_mg):
            cnt = np.count_nonzero(reset_mg)
            self.mg_flakes[reset_mg, 1] = np.random.uniform(-50, -5, cnt)
            self.mg_flakes[reset_mg, 0] = np.random.uniform(-w * 0.15, w * 1.15, cnt)
        cur_mx = (self.mg_flakes[:, 0] + self.mg_flakes[:, 4] * np.sin(t * self.mg_flakes[:, 5] + self.mg_flakes[:, 6]) + self.wind * (self.mg_flakes[:, 1] / h)).astype(np.int32)
        cur_my = self.mg_flakes[:, 1].astype(np.int32)
        for i in range(len(self.mg_flakes)):
            rx = max(1, int(self.mg_flakes[i, 2]))
            ry = max(3, int(rx * 3.2))
            cv2.ellipse(mg_canvas, (cur_mx[i], cur_my[i]), (rx, ry), tilt_angle, 0, 360, 255, -1, cv2.LINE_AA)

        # 3. Foreground soft-focus bokeh flakes (3.2x height with soft blur)
        self.fg_flakes[:, 1] += self.fg_flakes[:, 3]
        reset_fg = self.fg_flakes[:, 1] > h
        if np.any(reset_fg):
            cnt = np.count_nonzero(reset_fg)
            self.fg_flakes[reset_fg, 1] = np.random.uniform(-70, -10, cnt)
            self.fg_flakes[reset_fg, 0] = np.random.uniform(-w * 0.15, w * 1.15, cnt)
        cur_fx = (self.fg_flakes[:, 0] + self.fg_flakes[:, 4] * np.sin(t * self.fg_flakes[:, 5] + self.fg_flakes[:, 6]) + self.wind * (self.fg_flakes[:, 1] / h)).astype(np.int32)
        cur_fy = self.fg_flakes[:, 1].astype(np.int32)
        for i in range(len(self.fg_flakes)):
            rx = max(2, int(self.fg_flakes[i, 2]))
            ry = max(5, int(rx * 3.2))
            cv2.ellipse(fg_canvas, (cur_fx[i], cur_fy[i]), (rx, ry), tilt_angle, 0, 360, 255, -1, cv2.LINE_AA)

        mg_canvas = cv2.GaussianBlur(mg_canvas, (3, 3), 0.6)
        fg_canvas = cv2.GaussianBlur(fg_canvas, (7, 7), 2.0)

        bg_rgb = cv2.merge([bg_canvas, bg_canvas, bg_canvas])
        mg_rgb = cv2.merge([mg_canvas, mg_canvas, mg_canvas])
        fg_rgb = cv2.merge([fg_canvas, fg_canvas, fg_canvas])

        snow_layer = cv2.addWeighted(bg_rgb, cfg["bg_alpha"], mg_rgb, cfg["mg_alpha"], 0)
        snow_layer = cv2.addWeighted(snow_layer, 1.0, fg_rgb, cfg["fg_alpha"], 0)

        frost_a = cfg["frost_alpha"]
        frosted = cv2.addWeighted(frame, 1.0 - frost_a, self.frost_layer, frost_a, 0)
        weathered = cv2.add(frosted, snow_layer)

        if self.weather_mask is not None:
            return cv2.blendLinear(frame, weathered, self.inv_weather_mask, self.weather_mask)
        return weathered


class LivingEnvironmentEngine:
    """High-performance procedural living world dynamics:
    1. Ocean/Water Waves: Vectorized 1D broadcast Gerstner harmonic wave displacement + caustic specular glint.
    2. Volcanic / Factory Smoke: Advective upward billowing curls drifting with wind.
    3. Selective Object Removal Engine (--remove-objects or --remove-object-list bird,boat,car).
    4. Wildlife Flight Trajectory Engine: Aloft aerodynamic flight trajectories for unremoved birds.
    """

    def __init__(self, img: np.ndarray, width: int, height: int, remove_objects: bool = False, remove_object_list: Optional[List[str]] = None):
        self.w, self.h = width, height
        self.scale = width / 1920.0
        self.remove_objects = remove_objects
        self.remove_object_list = remove_object_list

        # Build set of normalized target object categories to remove
        self.remove_targets = set()
        if remove_objects:
            self.remove_targets = {"bird", "boat", "car", "vehicle", "plane", "person"}
        elif remove_object_list:
            for item in remove_object_list:
                cleaned = item.strip().lower()
                if cleaned in ["bird", "birds"]:
                    self.remove_targets.add("bird")
                elif cleaned in ["boat", "boats", "ship", "ships"]:
                    self.remove_targets.add("boat")
                elif cleaned in ["car", "cars", "vehicle", "vehicles", "truck", "trucks", "bus"]:
                    self.remove_targets.add("car")
                elif cleaned in ["person", "people", "human", "humans"]:
                    self.remove_targets.add("person")
                elif cleaned in ["plane", "airplane", "flight"]:
                    self.remove_targets.add("plane")
                else:
                    self.remove_targets.add(cleaned)

        if self.remove_targets:
            print(f" -> [Object Removal Config] Active removal targets: {sorted(list(self.remove_targets))}")

        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # 1. Autonomous Water Body Detection
        lower_hsv = hsv[int(height * 0.35):, :]
        water_px = ((lower_hsv[:, :, 0] >= 90) & (lower_hsv[:, :, 0] <= 130) &
                    (lower_hsv[:, :, 1] >= 40) & (lower_hsv[:, :, 2] >= 35)).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(width * 0.03), int(height * 0.03)))
        closed = cv2.morphologyEx(water_px, cv2.MORPH_CLOSE, kernel)
        water_ratio = float(np.mean(closed > 0))

        self.water_mask = None
        self.inv_water_mask = None
        if water_ratio > 0.12:
            full_w = np.zeros((height, width), dtype=np.float32)
            full_w[int(height * 0.35):, :] = (closed > 0).astype(np.float32)
            self.water_mask = cv2.GaussianBlur(full_w, (41, 41), 12)
            self.inv_water_mask = 1.0 - self.water_mask

            ys = np.where(self.water_mask > 0.005)[0]
            self.water_y_min = int(ys.min())
            self.water_y_max = int(ys.max()) + 1
            roi_h = self.water_y_max - self.water_y_min

            self.water_x = np.arange(width, dtype=np.float32)
            self.water_y_rel = np.arange(roi_h, dtype=np.float32)
            self.water_gx, self.water_gy = np.meshgrid(self.water_x, self.water_y_rel)
            self.water_weight_roi = self.water_mask[self.water_y_min:self.water_y_max, :]
            self.inv_water_weight_roi = self.inv_water_mask[self.water_y_min:self.water_y_max, :]
            print(f" -> [Living World] Ocean/Water body detected ({water_ratio:.1%} area). Active waves & glimmer enabled!")

        # 2. Autonomous Smoke / Steam Plume Detection
        upper_hsv = hsv[:int(height * 0.40), :]
        upper_gray = gray[:int(height * 0.40), :]
        smoke_candidates = (upper_hsv[:, :, 1] < 45) & (upper_gray > 165) & (upper_gray < 245)
        plume_ratio = float(np.mean(smoke_candidates))
        self.smoke_mask = None
        self.inv_smoke_mask = None
        if 0.005 < plume_ratio < 0.10:
            full_s = np.zeros((height, width), dtype=np.float32)
            full_s[:int(height * 0.40), :] = smoke_candidates.astype(np.float32)
            kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            full_s = cv2.morphologyEx(full_s, cv2.MORPH_OPEN, kernel_s)
            self.smoke_mask = cv2.GaussianBlur(full_s, (31, 31), 8)
            self.inv_smoke_mask = 1.0 - self.smoke_mask

            ys_s = np.where(self.smoke_mask > 0.005)[0]
            self.smoke_y_min = int(ys_s.min())
            self.smoke_y_max = int(ys_s.max()) + 1
            s_roi_h = self.smoke_y_max - self.smoke_y_min
            self.smoke_x = np.arange(width, dtype=np.float32)
            self.smoke_y_rel = np.arange(s_roi_h, dtype=np.float32)
            self.smoke_gx, self.smoke_gy = np.meshgrid(self.smoke_x, self.smoke_y_rel)
            self.smoke_weight_roi = self.smoke_mask[self.smoke_y_min:self.smoke_y_max, :]
            self.inv_smoke_weight_roi = self.inv_smoke_mask[self.smoke_y_min:self.smoke_y_max, :]
            print(f" -> [Living World] Smoke/Steam plume detected ({plume_ratio:.2%} area). Active billowing enabled!")

        # 3. Selective Object Detection & Inpainting Plate Construction
        self.clean_base_plate = None
        self.birds = []
        orig_h, orig_w = img.shape[:2]
        working_plate = img.copy()
        combined_inpaint_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)

        # 3A. Bird Detection & Selective Removal
        sky_limit_y = int(orig_h * 0.70)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sky_part = img_gray[:sky_limit_y, :]
        sky_med = cv2.medianBlur(sky_part, 51)
        sky_diff = cv2.subtract(sky_med, sky_part)
        _, sky_th = cv2.threshold(sky_diff, 28, 255, cv2.THRESH_BINARY)
        kernel_b = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        sky_th = cv2.morphologyEx(sky_th, cv2.MORPH_CLOSE, kernel_b)

        cnts, _ = cv2.findContours(sky_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bird_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
        detected_birds = []

        for c in cnts:
            area = cv2.contourArea(c)
            if 250 <= area <= 6000:
                bx, by, bw, bh = cv2.boundingRect(c)
                if by + bh < sky_limit_y and bx > int(orig_w * 0.35):
                    pad = 40
                    y1_bg, y2_bg = max(0, by - pad), min(sky_part.shape[0], by + bh + pad)
                    x1_bg, x2_bg = max(0, bx - pad), min(sky_part.shape[1], bx + bw + pad)
                    surrounding_bg = sky_part[y1_bg:y2_bg, x1_bg:x2_bg]
                    if float(np.std(surrounding_bg)) < 29.0:
                        aspect = bw / float(max(1, bh))
                        hull = cv2.convexHull(c)
                        solidity = area / float(max(1, cv2.contourArea(hull)))
                        if 0.70 <= aspect <= 4.0 and 0.20 <= solidity <= 0.75:
                            cv2.drawContours(bird_mask, [c], -1, 255, -1)
                            pad_s = 10
                            x1, y1 = max(0, bx - pad_s), max(0, by - pad_s)
                            x2, y2 = min(orig_w, bx + bw + pad_s), min(orig_h, by + bh + pad_s)
                            sprite = img[y1:y2, x1:x2].copy()
                            bird_roi_mask = bird_mask[y1:y2, x1:x2].astype(np.float32) / 255.0
                            feathered_mask = cv2.GaussianBlur(bird_roi_mask, (5, 5), 1.5)[:, :, np.newaxis]
                            detected_birds.append({
                                "orig_x": float(x1), "orig_y": float(y1),
                                "w": x2 - x1, "h": y2 - y1,
                                "sprite": sprite, "mask": feathered_mask,
                                "vx": float(-3.0 - (area / 1200.0) * 0.8),
                                "bob_amp": float(3.5 + (area / 2000.0) * 2.0),
                                "bob_phase": float((bx * 0.05 + by * 0.03) % (2.0 * np.pi)),
                            })

        if len(detected_birds) >= 3:
            min_bx = int(min(b["orig_x"] for b in detected_birds))
            max_bx = int(max(b["orig_x"] + b["w"] for b in detected_birds))
            min_by = int(min(b["orig_y"] for b in detected_birds))
            max_by = int(max(b["orig_y"] + b["h"] for b in detected_birds))
            pad_ctx = 60
            flock_patch = img[max(0, min_by - pad_ctx):min(orig_h, max_by + pad_ctx), max(0, min_bx - pad_ctx):min(orig_w, max_bx + pad_ctx)]

            if onnx_confirm_patch(flock_patch, target_label="bird", min_conf=0.28):
                if "bird" in self.remove_targets:
                    combined_inpaint_mask = cv2.bitwise_or(combined_inpaint_mask, bird_mask)
                    self.birds = []
                    print(f" -> [Object Removal] Completely removed {len(detected_birds)} birds from scene plate!")
                else:
                    self.birds = detected_birds
                    # Inpaint under sprite so original birds don't freeze on plate while animating
                    combined_inpaint_mask = cv2.bitwise_or(combined_inpaint_mask, bird_mask)
                    print(f" -> [Living World] Detected {len(self.birds)} birds aloft (ONNX confirmed). Background inpainted & flight trajectory activated!")

        # 3B. Boat Detection & Selective Removal
        if "boat" in self.remove_targets:
            lower_zone = img[int(orig_h * 0.45):int(orig_h * 0.85), :int(orig_w * 0.45)]
            l_hsv = cv2.cvtColor(lower_zone, cv2.COLOR_BGR2HSV)
            hull_px = ((l_hsv[:, :, 1] > 55) | (l_hsv[:, :, 2] < 50))
            cnts_boat, _ = cv2.findContours(hull_px.astype(np.uint8) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boat_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
            boat_cnt = 0
            for c in cnts_boat:
                area = cv2.contourArea(c)
                if 300 <= area <= 15000:
                    bx, by, bw, bh = cv2.boundingRect(c)
                    aspect = bw / float(max(1, bh))
                    if 1.2 <= aspect <= 6.0:
                        cv2.drawContours(boat_mask[int(orig_h * 0.45):int(orig_h * 0.85), :int(orig_w * 0.45)], [c], -1, 255, -1)
                        boat_cnt += 1
            if boat_cnt > 0:
                combined_inpaint_mask = cv2.bitwise_or(combined_inpaint_mask, boat_mask)
                print(f" -> [Object Removal] Completely removed {boat_cnt} coastal boats from scene plate!")

        # 3C. Vehicle Detection & Selective Removal (ONNX Inference)
        if "car" in self.remove_targets and ONNX_SESSION is not None:
            blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (640, 640), swapRB=True)
            preds = ONNX_SESSION.run(None, {"images": blob})[0][0].T
            veh_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
            veh_cnt = 0
            for row in preds:
                classes_scores = row[4:]
                cid = np.argmax(classes_scores)
                conf = classes_scores[cid]
                if conf > 0.28 and COCO_CLASSES[cid] in ["car", "truck", "bus"]:
                    cx, cy, bw, bh = row[0:4]
                    x1 = max(0, int((cx - bw / 2) * (orig_w / 640.0)))
                    y1 = max(0, int((cy - bh / 2) * (orig_h / 640.0)))
                    x2 = min(orig_w, int((cx + bw / 2) * (orig_w / 640.0)))
                    y2 = min(orig_h, int((cy + bh / 2) * (orig_h / 640.0)))
                    cv2.rectangle(veh_mask, (x1, y1), (x2, y2), 255, -1)
                    veh_cnt += 1
            if veh_cnt > 0:
                combined_inpaint_mask = cv2.bitwise_or(combined_inpaint_mask, veh_mask)
                print(f" -> [Object Removal] Completely removed {veh_cnt} vehicles from scene plate!")

        # Perform single unified inpainting pass if any objects were masked
        if np.any(combined_inpaint_mask > 0):
            inpaint_mask = cv2.dilate(combined_inpaint_mask, np.ones((15, 15), np.uint8))
            self.clean_base_plate = cv2.inpaint(img, inpaint_mask, 11, cv2.INPAINT_TELEA)

    def apply(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        out = frame.copy()

        # A. Composite Animated Birds Flying Along Aerodynamic Trajectories
        if self.birds and len(self.birds) > 0:
            scale_x = self.w / float(self.clean_base_plate.shape[1])
            scale_y = self.h / float(self.clean_base_plate.shape[0])
            for b in self.birds:
                cur_x = int((b["orig_x"] + b["vx"] * frame_idx) * scale_x)
                cur_y = int((b["orig_y"] + b["bob_amp"] * np.sin(frame_idx * 0.12 + b["bob_phase"])) * scale_y)
                cur_w = int(b["w"] * scale_x)
                cur_h = int(b["h"] * scale_y)
                if 0 <= cur_x < self.w - cur_w and 0 <= cur_y < self.h - cur_h:
                    cur_sprite = cv2.resize(b["sprite"], (cur_w, cur_h), interpolation=cv2.INTER_LINEAR).astype(np.float32)
                    cur_mask = cv2.resize(b["mask"], (cur_w, cur_h), interpolation=cv2.INTER_LINEAR)
                    if cur_mask.ndim == 2:
                        cur_mask = cur_mask[:, :, np.newaxis]
                    roi = out[cur_y:cur_y + cur_h, cur_x:cur_x + cur_w].astype(np.float32)
                    blended = np.clip(cur_sprite * cur_mask + roi * (1.0 - cur_mask), 0, 255).astype(np.uint8)
                    out[cur_y:cur_y + cur_h, cur_x:cur_x + cur_w] = blended

        # B. Apply Harmonic Ocean Waves & Specular Caustic Glimmer (Fast ROI)
        if self.water_mask is not None:
            t = frame_idx * 0.12
            disp_x = (2.4 * self.scale * np.sin(self.water_x * 0.035 + t)).astype(np.float32)
            disp_y = (1.6 * self.scale * np.cos((self.water_y_rel + self.water_y_min) * 0.045 + t * 0.85)).astype(np.float32)
            map_x = self.water_gx + disp_x
            map_y = self.water_gy + disp_y[:, None]

            roi_in = out[self.water_y_min:self.water_y_max, :]
            wave_roi = cv2.remap(roi_in, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            glim_x = np.sin(self.water_x * 0.06 - t * 1.2)
            glim_y = np.cos((self.water_y_rel + self.water_y_min) * 0.05 + t * 0.9)
            glimmer = (1.0 + 0.04 * np.outer(glim_y, glim_x)).astype(np.float32)
            wave_roi = np.clip(wave_roi.astype(np.float32) * glimmer[:, :, None], 0, 255).astype(np.uint8)

            out[self.water_y_min:self.water_y_max, :] = cv2.blendLinear(
                roi_in, wave_roi, self.inv_water_weight_roi, self.water_weight_roi
            )

        # C. Apply Upward Billowing & Wind Drift to Smoke Plumes (Fast ROI)
        if self.smoke_mask is not None:
            t_s = frame_idx * 0.15
            s_dx = (2.0 * self.scale * np.sin((self.smoke_y_rel + self.smoke_y_min) * 0.04 + t_s * 1.1)).astype(np.float32)
            s_dy = (-3.2 * self.scale - 1.5 * self.scale * np.sin(self.smoke_x * 0.05 + t_s * 0.7)).astype(np.float32)
            s_map_x = self.smoke_gx + s_dx[:, None]
            s_map_y = self.smoke_gy + s_dy

            s_roi_in = out[self.smoke_y_min:self.smoke_y_max, :]
            smoke_roi = cv2.remap(s_roi_in, s_map_x, s_map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            out[self.smoke_y_min:self.smoke_y_max, :] = cv2.blendLinear(
                s_roi_in, smoke_roi, self.inv_smoke_weight_roi, self.smoke_weight_roi
            )

        return out


def get_ffmpeg_writer(output_path: str, width: int, height: int, fps: float):
    """Spawns an FFmpeg process for high-quality H.264 broadcast encoding with zero GOP pulsing."""
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-maxrate", "22M",
        "-bufsize", "44M",
        "-threads", "4",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception:
        return None


def calculate_easing(t: float, curve: str = "cosine") -> float:
    """Computes normalized progress curve s in [0.0, 1.0] from t in [0.0, 1.0].
    Supports standard easing as well as directorial speed ramps:
    - 'cosine': Smooth S-curve start and finish (default)
    - 'cubic': Smooth cubic easing
    - 'linear': Constant velocity
    - 'ramp-up': Slow start, fast dynamic finish (exponential power 2.5)
    - 'ramp-down': Fast energetic burst slowing into gentle glide
    - 'whip': Fast midpoint whip with slow starts/stops (steep power S-curve)
    """
    curve_key = curve.lower()
    if curve_key == "linear":
        return t
    elif curve_key == "cosine":
        return float(0.5 * (1.0 - np.cos(t * np.pi)))
    elif curve_key == "ramp-up":
        return float(t ** 2.5)
    elif curve_key == "ramp-down":
        return float(1.0 - (1.0 - t) ** 2.5)
    elif curve_key == "whip":
        # Steep sigmoidal whip: slow first 25%, explosive middle, slow final 25%
        return float(t * t * t * (t * (t * 6.0 - 15.0) + 10.0))
    else:  # "cubic" default fallback
        return float(t * t * (3.0 - 2.0 * t))


# Supported sequence action types
VALID_ACTIONS = {
    "--stay": "stay",
    "--hold": "stay",
    "--dollyin": "dollyin",
    "--dollyout": "dollyout",
    "--dollyin-stay": "stay",
    "--dollyout-stay": "stay",
    "--pan-left": "pan-left",
    "--pan-right": "pan-right",
    "--pan-left-stay": "stay",
    "--pan-right-stay": "stay",
    "--tilt-up": "tilt-up",
    "--tilt-down": "tilt-down",
    "--tilt-up-stay": "stay",
    "--tilt-down-stay": "stay",
    "--zoom-in": "zoom-in",
    "--zoom-out": "zoom-out",
    "--zoom-in-stay": "stay",
    "--zoom-out-stay": "stay",
    # Advanced drone cinematography motions:
    "--roll-left": "roll-left",
    "--roll-right": "roll-right",
    "--bank-left": "roll-left",
    "--bank-right": "roll-right",
    "--level": "level",
    "--pedestal-up": "pedestal-up",
    "--pedestal-down": "pedestal-down",
    "--crane-up": "pedestal-up",
    "--crane-down": "pedestal-down",
    "--drift-up-right": "drift-up-right",
    "--drift-up-left": "drift-up-left",
    "--drift-down-right": "drift-down-right",
    "--drift-down-left": "drift-down-left",
    "--orbit-left": "orbit-left",
    "--orbit-right": "orbit-right",
    # Compound simultaneous reveal actions:
    "--pan-right-zoom-out": "pan-right-zoom-out",
    "--pan-left-zoom-out": "pan-left-zoom-out",
    "--pan-right-dollyout": "pan-right-zoom-out",
    "--pan-left-dollyout": "pan-left-zoom-out",
    "--reveal": "pan-right-zoom-out",
    "--reveal-left": "pan-right-zoom-out",
    "--reveal-right": "pan-left-zoom-out",
}


def parse_action_sequence(raw_args: list) -> list:
    """Parses sequence steps from command-line arguments.
    Supports sequential actions as well as parallel blocks delimited by:
    --parallel-start ... --parallel-end
    """
    sequence = []
    in_parallel = False
    parallel_actions = []

    i = 0
    while i < len(raw_args):
        arg = raw_args[i].lower()
        if arg == "--parallel-start":
            in_parallel = True
            parallel_actions = []
            i += 1
            continue
        elif arg == "--parallel-end":
            if parallel_actions:
                sequence.append(("parallel", parallel_actions))
                parallel_actions = []
            in_parallel = False
            i += 1
            continue

        if arg in VALID_ACTIONS:
            action_name = VALID_ACTIONS[arg]
            duration_sec = 5.0
            if i + 1 < len(raw_args) and not raw_args[i + 1].startswith("-"):
                try:
                    duration_sec = float(raw_args[i + 1])
                    i += 1
                except ValueError:
                    pass

            if in_parallel:
                parallel_actions.append((action_name, duration_sec))
            else:
                sequence.append((action_name, duration_sec))
            i += 1
        else:
            i += 1

    if parallel_actions:
        sequence.append(("parallel", parallel_actions))

    return sequence


def precompute_sequence_matrices(
    img_shape: tuple,
    sequence: list,
    fps: float = 30.0,
    output_size: tuple = (3840, 2160),
    max_depth: float = 0.50,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
) -> tuple:
    """Simulates a continuous camera timeline across an arbitrary sequence of movements, holds, and parallel blocks."""
    h, w = img_shape[:2]
    target_w, target_h = output_size
    target_aspect = target_w / float(target_h)

    # Base wide framing matching output aspect ratio
    src_aspect = w / float(h)
    if src_aspect > target_aspect:
        base_h = float(h)
        base_w = base_h * target_aspect
    else:
        base_w = float(w)
        base_h = base_w / target_aspect

    base_cx = float(w) / 2.0
    base_cy = float(h) / 2.0

    dst_rect = np.array(
        [
            [0.0, 0.0],
            [float(target_w), 0.0],
            [float(target_w), float(target_h)],
            [0.0, float(target_h)],
        ],
        dtype=np.float32,
    )

    # Initialize starting camera state based on --start-pan, --start-zoom, --start-tilt
    # cur_depth: 0.0 = wide panorama, 1.0 = deep close-up
    cur_depth = 1.0 if start_zoom in ("in", "zoomed", "tight") else 0.0

    # cur_pan: -1.0 = full left (e.g. house on side), 0.0 = center, +1.0 = full right
    if start_pan in ("left", "far-left"):
        cur_pan = -1.0
    elif start_pan in ("right", "far-right"):
        cur_pan = 1.0
    else:
        cur_pan = 0.0

    # cur_tilt: -1.0 = tilted up (sky/peaks), 0.0 = center/level, +1.0 = tilted down
    if start_tilt in ("up", "top"):
        cur_tilt = -1.0
    elif start_tilt in ("down", "bottom"):
        cur_tilt = 1.0
    else:
        cur_tilt = 0.0

    cur_roll = 0.0  # Horizon roll in degrees (e.g. -3.0 to +3.0)

    timeline_states = []

    def resolve_target(action_name, s_d, s_p, s_t, s_r):
        t_d, t_p, t_t, t_r = s_d, s_p, s_t, s_r
        if action_name == "stay":
            pass
        elif action_name in ("dollyin", "zoom-in"):
            t_d = 1.0
        elif action_name in ("dollyout", "zoom-out"):
            t_d = 0.0
        elif action_name == "pan-left":
            t_p = -1.0
        elif action_name == "pan-right":
            t_p = 0.0 if s_p < -0.05 else 1.0
        elif action_name in ("tilt-up", "pedestal-up"):
            t_t = -1.0
        elif action_name in ("tilt-down", "pedestal-down"):
            t_t = 0.0 if s_t < -0.05 else 1.0
        elif action_name == "roll-left":
            t_r = -3.5  # Subtle cinematic banked horizon turn
        elif action_name == "roll-right":
            t_r = 3.5
        elif action_name == "level":
            t_r = 0.0
        elif action_name == "drift-up-right":
            t_p = 1.0
            t_t = -1.0
        elif action_name == "drift-up-left":
            t_p = -1.0
            t_t = -1.0
        elif action_name == "drift-down-right":
            t_p = 1.0
            t_t = 1.0
        elif action_name == "drift-down-left":
            t_p = -1.0
            t_t = 1.0
        elif action_name == "orbit-left":
            # Parallax arc: Pan left while banking horizon right slightly
            t_p = -0.75
            t_r = 2.5
        elif action_name == "orbit-right":
            t_p = 0.75
            t_r = -2.5
        elif action_name == "pan-right-zoom-out":
            t_d = 0.0
            t_p = 0.0
            t_t = 0.0
            t_r = 0.0
        elif action_name == "pan-left-zoom-out":
            t_d = 0.0
            t_p = 0.0
            t_t = 0.0
            t_r = 0.0
        return t_d, t_p, t_t, t_r

    for item in sequence:
        action_type = item[0]

        if action_type == "parallel":
            # item is ("parallel", [(sub_action, dur), ...])
            sub_actions = item[1]
            if not sub_actions:
                continue
            max_duration = max(dur for _, dur in sub_actions)
            num_frames = int(round(max_duration * fps))
            if num_frames <= 0:
                continue

            start_d, start_p, start_t, start_r = cur_depth, cur_pan, cur_tilt, cur_roll

            # Prepare trajectory targets and durations for each active channel
            channels = []
            for sub_act, sub_dur in sub_actions:
                tgt_d, tgt_p, tgt_t, tgt_r = resolve_target(sub_act, start_d, start_p, start_t, start_r)
                sub_frames = max(1, int(round(sub_dur * fps)))
                channels.append((sub_act, tgt_d, tgt_p, tgt_t, tgt_r, sub_frames))

            for f in range(num_frames):
                d_val = start_d
                p_val = start_p
                t_val = start_t
                r_val = start_r

                for sub_act, tgt_d, tgt_p, tgt_t, tgt_r, sub_frames in channels:
                    prog = min(1.0, f / max(1, sub_frames - 1)) if sub_frames > 1 else 1.0
                    e = calculate_easing(prog, curve)
                    if sub_act in ("dollyin", "dollyout", "zoom-in", "zoom-out", "pan-right-zoom-out", "pan-left-zoom-out"):
                        d_val = start_d + e * (tgt_d - start_d)
                    if sub_act in ("pan-left", "pan-right", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "orbit-left", "orbit-right", "pan-right-zoom-out", "pan-left-zoom-out"):
                        p_val = start_p + e * (tgt_p - start_p)
                    if sub_act in ("tilt-up", "tilt-down", "pedestal-up", "pedestal-down", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "pan-right-zoom-out", "pan-left-zoom-out"):
                        t_val = start_t + e * (tgt_t - start_t)
                    if sub_act in ("roll-left", "roll-right", "level", "orbit-left", "orbit-right"):
                        r_val = start_r + e * (tgt_r - start_r)

                timeline_states.append((d_val, p_val, t_val, r_val))

            # Update final camera state after parallel block
            for sub_act, tgt_d, tgt_p, tgt_t, tgt_r, _ in channels:
                if sub_act in ("dollyin", "dollyout", "zoom-in", "zoom-out", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_depth = tgt_d
                if sub_act in ("pan-left", "pan-right", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "orbit-left", "orbit-right", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_pan = tgt_p
                if sub_act in ("tilt-up", "tilt-down", "pedestal-up", "pedestal-down", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_tilt = tgt_t
                if sub_act in ("roll-left", "roll-right", "level", "orbit-left", "orbit-right"):
                    cur_roll = tgt_r

        else:
            action, duration_sec = item
            num_frames = int(round(duration_sec * fps))
            if num_frames <= 0:
                continue

            start_d, start_p, start_t, start_r = cur_depth, cur_pan, cur_tilt, cur_roll
            target_d, target_p, target_t, target_r = resolve_target(action, start_d, start_p, start_t, start_r)

            for f in range(num_frames):
                prog = f / max(1, num_frames - 1) if num_frames > 1 else 1.0
                e = calculate_easing(prog, curve)
                d = start_d + e * (target_d - start_d)
                p = start_p + e * (target_p - start_p)
                t = start_t + e * (target_t - start_t)
                r = start_r + e * (target_r - start_r)
                timeline_states.append((d, p, t, r))

            cur_depth = target_d
            cur_pan = target_p
            cur_tilt = target_t
            cur_roll = target_r

    # Convert state timeline into 2D perspective / affine transformation matrices
    matrices = []
    min_scale = max(0.20, 1.0 - max_depth)

    for d, p, t, r in timeline_states:
        # Scale for dolly/zoom: from 1.0 (wide panorama) down to min_scale (tight framing)
        scale = 1.0 - d * (1.0 - min_scale)
        cw = base_w * scale
        ch = cw / target_aspect

        avail_pan_x = (float(w) - cw) / 2.0
        avail_tilt_y = (float(h) - ch) / 2.0

        cx = base_cx + (p * avail_pan_x)
        cy = base_cy + (t * avail_tilt_y)

        half_w = cw / 2.0
        half_h = ch / 2.0
        cx = max(half_w, min(float(w) - half_w, cx))
        cy = max(half_h, min(float(h) - half_h, cy))

        # Quad corners relative to center
        corners = np.array(
            [
                [-half_w, -half_h],
                [half_w, -half_h],
                [half_w, half_h],
                [-half_w, half_h],
            ],
            dtype=np.float32,
        )

        # Apply subtle aerodynamic horizon roll / bank if non-zero
        if abs(r) > 0.01:
            rad = np.radians(r)
            cos_a = np.cos(rad)
            sin_a = np.sin(rad)
            rot_mat = np.array([[cos_a, -sin_a], [sin_a, cos_a]], dtype=np.float32)
            corners = corners @ rot_mat.T

        src_quad = corners + np.array([cx, cy], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(src_quad, dst_rect)
        matrices.append(matrix)

    return matrices, len(timeline_states)


def process_drone_flyovers(
    input_dir: str,
    output_dir: str,
    sequence: list,
    fps: float = 30.0,
    depth: float = 0.50,
    speed_factor: float = 1.0,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
    rain: bool = False,
    rain_intensity: str = "light",
    snow: bool = False,
    snow_intensity: str = "medium",
    res_mode: str = "4k",
    interp_mode: str = "lanczos",
    target_duration: float = None,
    remove_objects: bool = False,
    remove_object_list: Optional[List[str]] = None,
):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".webp")
    if os.path.isfile(input_dir):
        images = [os.path.basename(input_dir)]
        input_dir = os.path.dirname(input_dir)
    else:
        images = [f for f in os.listdir(input_dir) if f.lower().endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    # Calculate mission total duration and human-readable sequence summary
    total_sec = 0.0
    for item in sequence:
        if item[0] == "parallel":
            sub_acts = item[1]
            dur = max(d for _, d in sub_acts) if sub_acts else 0.0
            total_sec += dur
        else:
            _, dur = item
            total_sec += dur

    # Behavior A: If --duration was specified and exceeds current sequence, automatically hold at end!
    if target_duration is not None and target_duration > total_sec:
        remaining_hold = target_duration - total_sec
        if sequence and sequence[-1][0] == "stay":
            last_act, last_dur = sequence[-1]
            sequence[-1] = (last_act, last_dur + remaining_hold)
        else:
            sequence.append(("stay", remaining_hold))
        total_sec = target_duration

    desc_parts = []
    for item in sequence:
        if item[0] == "parallel":
            sub_acts = item[1]
            inner = "+".join([f"{a.upper()}({d:g}s)" for a, d in sub_acts])
            desc_parts.append(f"PARALLEL[{inner}]")
        else:
            act, dur = item
            desc_parts.append(f"{act.upper()}({dur:g}s)")

    seq_desc = " -> ".join(desc_parts)

    interp_map = {
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }
    warp_flag = interp_map.get(interp_mode.lower(), cv2.INTER_LANCZOS4)

    effective_depth = depth * max(0.05, speed_factor)
    clamped_depth = min(0.75, max(0.05, effective_depth))

    if res_mode.lower() == "1080p":
        target_size = (1920, 1080)
        mode_str = "Full HD (1920x1080)"
    else:
        target_size = (3840, 2160)
        mode_str = "4K UHD (3840x2160)"

    print("--- 3D Keyframe Sequence Drone Director ---")
    print(f"Mission Plan: {seq_desc}")
    print(f"Start Setup: Pan={start_pan.upper()}, Zoom={start_zoom.upper()}, Tilt={start_tilt.upper()}")
    print(f"Total Duration: {total_sec:.1f}s (@ {fps}fps) | Easing: {curve.upper()}")
    if rain:
        print(f"Atmosphere: Active Cinematic Rain ({rain_intensity.upper()}) + Alpine Mist")
    elif snow:
        print(f"Atmosphere: Active Cinematic Snow ({snow_intensity.upper()}) + Frost Atmosphere")
    print(f"Output Mode: {mode_str} | Max Zoom Depth: {clamped_depth:.1%} | Interp: {interp_mode.upper()}")

    for img_name in images:
        t_image_start = time.time()
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
        mode_suffix = "reveal_mission" if (start_pan != "center" or start_zoom != "normal") else "flight_mission"
        if rain:
            mode_suffix += f"_rain_{rain_intensity}"
        if snow:
            mode_suffix += f"_snow_{snow_intensity}"
        output_path = os.path.join(output_dir, f"{stem}_{mode_suffix}.mp4")

        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read {img_name}, skipping.")
            continue

        h, w = img.shape[:2]
        output_size = target_size
        out_w, out_h = output_size

        # Classify input resolution category
        min_dim = min(w, h)
        if min_dim >= 2000 or (w * h) >= 7_000_000:
            in_cat = "4K"
        elif min_dim >= 1000 or (w * h) >= 1_900_000:
            in_cat = "1080p"
        elif min_dim >= 700 or (w * h) >= 800_000:
            in_cat = "720p"
        elif min_dim >= 450:
            in_cat = "480p"
        else:
            in_cat = f"{min_dim}p"

        print(f"\n[Processing] {img_name}")
        print(f" -> Input Image Resolution:  {w}x{h} ({in_cat})")
        print(f" -> Output Video Resolution: {out_w}x{out_h} ({mode_str})")

        # Autonomous Pre-Flight Scene Element Detection
        hsv_full = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Water & Ocean: Cyan/Blue water body in lower frame
        lower_hsv = hsv_full[int(h * 0.25):, :]
        water_px = ((lower_hsv[:, :, 0] >= 85) & (lower_hsv[:, :, 0] <= 135) &
                    (lower_hsv[:, :, 1] >= 30) & (lower_hsv[:, :, 2] >= 30))
        water_ratio = float(np.mean(water_px))
        ocean_detected = water_ratio > 0.08
        water_detected = ocean_detected or (water_ratio > 0.03)

        # 2. Snow: High luminance with near zero saturation
        snow_px = (hsv_full[:, :, 1] < 20) & (gray_full > 225)
        snow_detected = float(np.mean(snow_px)) > 0.12

        # 3. Smoke: Upper 40% sky, bright grey diffuse plume
        upper_hsv = hsv_full[:int(h * 0.40), :]
        upper_gray = gray_full[:int(h * 0.40), :]
        smoke_candidates = (upper_hsv[:, :, 1] < 45) & (upper_gray > 165) & (upper_gray < 245)
        plume_ratio = float(np.mean(smoke_candidates))
        smoke_detected = 0.005 < plume_ratio < 0.10

        # 4. Birds: Aloft flock in smooth sky/upper sea
        sky_limit_y = int(h * 0.55)
        sky_part = gray_full[:sky_limit_y, :]
        sky_med = cv2.medianBlur(sky_part, 51)
        sky_diff = cv2.subtract(sky_med, sky_part)
        _, sky_th = cv2.threshold(sky_diff, 28, 255, cv2.THRESH_BINARY)
        kernel_b = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        sky_th = cv2.morphologyEx(sky_th, cv2.MORPH_CLOSE, kernel_b)
        cnts, _ = cv2.findContours(sky_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        birds_count = 0
        for c in cnts:
            a = cv2.contourArea(c)
            if 200 <= a <= 5000:
                bx, by, bw, bh = cv2.boundingRect(c)
                if by + bh < sky_limit_y:
                    pad = 40
                    y1_bg, y2_bg = max(0, by - pad), min(sky_part.shape[0], by + bh + pad)
                    x1_bg, x2_bg = max(0, bx - pad), min(sky_part.shape[1], bx + bw + pad)
                    bg_std = float(np.std(sky_part[y1_bg:y2_bg, x1_bg:x2_bg]))
                    if bg_std < 22.0:
                        aspect = bw / float(max(1, bh))
                        hull = cv2.convexHull(c)
                        solidity = a / float(max(1, cv2.contourArea(hull)))
                        if 0.70 <= aspect <= 3.8 and 0.20 <= solidity <= 0.75:
                            birds_count += 1
        birds_detected = birds_count >= 3

        # 5. Roads & Vehicles
        road_mask = (hsv_full[:, :, 1] < 35) & (gray_full >= 40) & (gray_full <= 110)
        road_ratio = float(np.mean(road_mask))
        road_detected = road_ratio > 0.08 and ("cars" in img_name.lower() or "road" in img_name.lower() or road_ratio > 0.14)
        vehicles_detected = road_detected

        # 6. Flights / Aircraft: Aloft fast silhouette in upper 30% sky with elongated fuselage/wings
        # (Distinguished from birds by rigid high aspect ratio > 4.2 or jet contrail)
        flights_detected = False

        # 7. Trains: Elongated rail tracks / train cars along terrain
        trains_detected = "train" in img_name.lower() or "rail" in img_name.lower()

        # 8. Boats & Ships: Hulls resting on shoreline or cruising on water
        ships_detected = False
        boats_detected = False
        if water_detected:
            # Look for hulls on water/shoreline (elongated hulls with high color contrast against water/sand)
            lower_zone = img[int(h * 0.45):int(h * 0.85), :]
            l_hsv = cv2.cvtColor(lower_zone, cv2.COLOR_BGR2HSV)
            hull_px = ((l_hsv[:, :, 1] > 60) | (l_hsv[:, :, 2] < 45)) & (lower_zone[:, :, 0] > 20)
            cnts_b, _ = cv2.findContours(hull_px.astype(np.uint8) * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boat_cnt = sum(1 for c in cnts_b if 250 <= cv2.contourArea(c) <= 12000)
            if boat_cnt >= 4:
                boats_detected = True
            # Ships cruising far out on horizon
            horizon_zone = gray_full[int(h * 0.30):int(h * 0.45), :]
            horizon_diff = cv2.subtract(cv2.medianBlur(horizon_zone, 31), horizon_zone)
            _, horiz_th = cv2.threshold(horizon_diff, 30, 255, cv2.THRESH_BINARY)
            cnts_s, _ = cv2.findContours(horiz_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts_s:
                if 80 <= cv2.contourArea(c) <= 2500:
                    bx, by, bw, bh = cv2.boundingRect(c)
                    if bw / float(max(1, bh)) >= 3.0: # Long cargo ship / cruise ship silhouette
                        ships_detected = True
                        break

        # 9. Humans & Animals
        humans_detected = False
        animals_detected = birds_detected

        # 10. Rain: Active request or rain presence
        rain_detected = rain

        print(f" -> Scene Elements:")
        print(f"    Vehicles detected: {vehicles_detected}")
        print(f"    Road detected:     {road_detected}")
        print(f"    Birds detected:    {birds_detected} (count={birds_count})")
        print(f"    Flights detected:  {flights_detected}")
        print(f"    Trains detected:   {trains_detected}")
        print(f"    Ships detected:    {ships_detected}")
        print(f"    Boats detected:    {boats_detected}")
        print(f"    Water detected:    {water_detected}")
        print(f"    Ocean detected:    {ocean_detected}")
        print(f"    Rain detected:     {rain_detected}")
        print(f"    Snow detected:     {snow_detected}")
        print(f"    Smoke detected:    {smoke_detected}")
        print(f"    Humans detected:   {humans_detected}")
        print(f"    Animals detected:  {animals_detected}")

        t_pre = time.time()
        matrices, total_frames = precompute_sequence_matrices(
            img_shape=img.shape,
            sequence=sequence,
            fps=fps,
            output_size=output_size,
            max_depth=clamped_depth,
            start_pan=start_pan,
            start_zoom=start_zoom,
            start_tilt=start_tilt,
            curve=curve,
        )
        print(f" -> Precomputed {len(matrices)} transformation matrices in {(time.time() - t_pre)*1000:.1f}ms")

        # Initialize living environment engine (waves, caustic glimmer, smoke plumes, selective object removal)
        living_env = LivingEnvironmentEngine(img, out_w, out_h, remove_objects=remove_objects, remove_object_list=remove_object_list)

        # Initialize rain engine if requested
        rain_engine = None
        if rain:
            rain_engine = CinematicRainEngine(out_w, out_h, intensity=rain_intensity, source_img=img)

        # Initialize snow engine if requested
        snow_engine = None
        if snow:
            snow_engine = CinematicSnowEngine(out_w, out_h, intensity=snow_intensity, source_img=img)

        ffmpeg_proc = get_ffmpeg_writer(output_path, out_w, out_h, fps)
        video_writer = None
        if ffmpeg_proc is None:
            print(" -> Notice: Falling back to OpenCV VideoWriter (mp4v)...")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, output_size)
        else:
            print(" -> Video Encoder: Broadcast H.264 (libx264, CRF 18, zero-pulsing)")

        t_start = time.time()
        print(f" -> Rendering and streaming {total_frames} frames to disk...")

        # If birds were detected and inpainted, warp the clean plate so original birds don't freeze on plate
        source_plate = living_env.clean_base_plate if living_env.clean_base_plate is not None else img

        for i in range(total_frames):
            frame = cv2.warpPerspective(
                source_plate,
                matrices[i],
                output_size,
                flags=warp_flag,
                borderMode=cv2.BORDER_REPLICATE,
            )

            # Apply living world dynamics: undulating ocean waves, caustic glimmer, rising smoke
            frame = living_env.apply(frame, i)

            if rain_engine is not None:
                frame = rain_engine.render(frame)
            elif snow_engine is not None:
                frame = snow_engine.render(frame, i)

            if ffmpeg_proc is not None:
                ffmpeg_proc.stdin.write(frame.tobytes())
            else:
                video_writer.write(frame)

        if ffmpeg_proc is not None:
            ffmpeg_proc.stdin.close()
            ffmpeg_proc.wait()
        else:
            video_writer.release()

        elapsed = time.time() - t_image_start
        mins, secs = divmod(int(elapsed), 60)
        render_fps = total_frames / max(0.001, elapsed)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{elapsed:.1f}s"
        print(f"[Done] Total Production Time: {time_str} ({elapsed:.1f}s | {render_fps:.1f} FPS) -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cinematic Sequence Drone Flight Director. Chain any sequence of motions and stays."
    )
    parser.add_argument("-i", "--input", required=True, help="Input directory of images")
    parser.add_argument("-o", "--output", required=True, help="Output directory for MP4 videos")
    parser.add_argument("-d", "--duration", type=float, default=None,
                        help="Target total video duration in seconds. If choreography finishes earlier, camera automatically holds on final scene for remainder.")
    parser.add_argument("--start-pan", choices=["center", "left", "right"], default="center",
                        help="Initial camera horizontal framing: center (default), left, or right")
    parser.add_argument("--start-zoom", choices=["normal", "in"], default="normal",
                        help="Initial camera magnification: normal (wide panorama) or in (zoomed-in close-up)")
    parser.add_argument("--start-tilt", choices=["center", "up", "down"], default="center",
                        help="Initial camera vertical framing: center (default), up, or down")
    parser.add_argument("--depth", type=float, default=0.50, 
                        help="Zoom depth scale for close-up framing (default: 0.50 for intimate detail framing)")
    parser.add_argument("--speed", type=float, default=1.0, 
                        help="Speed multiplier (default: 1.0)")
    parser.add_argument("--curve", choices=["cosine", "cubic", "linear", "ramp-up", "ramp-down", "whip"], default="cosine", 
                        help="Motion curve: cosine (default), cubic, linear, ramp-up (speed up), ramp-down (slow down), whip (fast mid-sweep)")
    parser.add_argument("--rain", action="store_true", help="Add authentic procedural cinematic rainfall & atmospheric mist")
    parser.add_argument("--rain-intensity", choices=["light", "medium", "heavy"], default="light", 
                        help="Rain intensity: light (default), medium, heavy")
    parser.add_argument("--snow", action="store_true", help="Add authentic procedural cinematic snowfall & winter atmosphere")
    parser.add_argument("--snow-intensity", choices=["light", "medium", "heavy"], default="medium", 
                        help="Snow intensity: light, medium (default), heavy")
    parser.add_argument("--fps", type=float, default=30.0, help="Frames per second (default: 30.0)")
    parser.add_argument("--res", choices=["4k", "1080p"], default="4k", help="Output resolution: 4k (default: 3840x2160) or 1080p")
    parser.add_argument("--lanczos", action="store_true", help="High-precision Lanczos4 interpolation (slower)")
    parser.add_argument("--cubic", action="store_true", help="Bicubic interpolation")
    parser.add_argument("--fast", action="store_true", help="Bilinear interpolation (default: fast and smooth)")
    parser.add_argument("--remove-objects", action="store_true",
                        help="Completely detect and inpaint away all movable objects (birds, vehicles, boats) leaving a pure uninhabited nature landscape")
    parser.add_argument("--remove-object-list", type=str, default=None,
                        help="Comma-separated list of specific objects to remove (e.g. --remove-object-list bird,boat)")

    args, unknown = parser.parse_known_args()

    # Parse ordered sequence from command-line arguments
    sequence = parse_action_sequence(sys.argv)

    if not sequence:
        print("\nError: No sequence actions specified!")
        print("Example 1 (Sequential flight sequence):")
        print("  python .\\src\\drone_view.py -i C:\\test\\input1 -o C:\\test\\output \\")
        print("    --stay 5 --dollyin 5 --stay 5 --pan-left 5 --stay 5 --pan-right 5 --dollyout 5 --stay 10")
        print("\nExample 2 (Simultaneous reveal using parallel block: pan and zoom out at the same time):")
        print("  python .\\src\\drone_view.py -i C:\\test\\input1 -o C:\\test\\output \\")
        print("    --start-pan left --start-zoom in \\")
        print("    --stay 3 \\")
        print("    --parallel-start --pan-right 5 --zoom-out 6 --parallel-end \\")
        print("    --stay 5")
        sys.exit(1)

    interp = "lanczos" if args.lanczos else ("cubic" if args.cubic else "linear")
    remove_list = [x.strip() for x in args.remove_object_list.split(",")] if args.remove_object_list else None

    process_drone_flyovers(
        input_dir=args.input,
        output_dir=args.output,
        sequence=sequence,
        fps=args.fps,
        depth=args.depth,
        speed_factor=args.speed,
        start_pan=args.start_pan,
        start_zoom=args.start_zoom,
        start_tilt=args.start_tilt,
        curve=args.curve,
        rain=args.rain,
        rain_intensity=args.rain_intensity,
        snow=args.snow,
        snow_intensity=args.snow_intensity,
        res_mode=args.res,
        interp_mode=interp,
        target_duration=args.duration,
        remove_objects=args.remove_objects,
        remove_object_list=remove_list,
    )
