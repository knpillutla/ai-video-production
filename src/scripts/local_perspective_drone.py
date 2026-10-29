"""Cinematic Perspective Drone Flight Director & Ken Burns Motion Engine.

Supports sequential stages, parallel compound movements, continuous holds,
start framing (pan/zoom/tilt), motion curves (cosine, ramp-up, etc.),
procedural weather (cinematic rain and snow), living environment dynamics,
and 4-stage optical ultra-clarity pre-enhancement for 4K broadcast masters.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"

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


def enhance_image_ultra_clarity(img: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """Enhance image with 4-stage optical pipeline: 4K Lanczos resize, bilateral denoising, LAB CLAHE, and dual-band MTF boost."""
    if img.shape[1] != target_w or img.shape[0] != target_h:
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    denoised = cv2.bilateralFilter(img, d=5, sigmaColor=35, sigmaSpace=35)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_enh = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8)).apply(l)
    bgr_clahe = cv2.cvtColor(cv2.merge((l_enh, a, b)), cv2.COLOR_LAB2BGR)
    fine = cv2.addWeighted(bgr_clahe, 1.45, cv2.GaussianBlur(bgr_clahe, (0, 0), 1.0), -0.45, 0)
    return cv2.addWeighted(fine, 1.25, cv2.GaussianBlur(fine, (0, 0), 3.0), -0.25, 0)


def calculate_easing(t: float, curve: str = "cosine") -> float:
    """Computes normalized progress curve s in [0.0, 1.0] from t in [0.0, 1.0]."""
    curve_key = (curve or "cosine").lower()
    if curve_key == "linear":
        return t
    elif curve_key == "cosine":
        return float(0.5 * (1.0 - np.cos(t * np.pi)))
    elif curve_key == "ramp-up":
        return float(t ** 2.5)
    elif curve_key == "ramp-down":
        return float(1.0 - (1.0 - t) ** 2.5)
    elif curve_key == "whip":
        return float(t * t * t * (t * (t * 6.0 - 15.0) + 10.0))
    else:  # cubic fallback
        return float(t * t * (3.0 - 2.0 * t))


class CinematicRainEngine:
    """High-performance vectorized procedural rain engine: organic translucent drizzle, wind slant, and soft mist."""

    def __init__(self, width: int, height: int, intensity: str = "light", wind_tilt: float = 4.0, source_img: Optional[np.ndarray] = None):
        self.w, self.h = width, height
        self.wind_tilt = wind_tilt
        norm_int = intensity.lower()
        if norm_int in ("heavy", "high"):
            norm_int = "heavy"
        self.intensity = norm_int
        scale_factor = width / 1920.0
        self.scale = scale_factor

        configs = {
            "light": {"drops": 600, "bg_len": (8, 14), "bg_spd": (16, 24), "mg_len": (14, 22), "mg_spd": (22, 30), "fg_len": (22, 34), "fg_spd": (28, 40), "mist_alpha": 0.02, "rain_alpha": 0.22, "wind": 2.5},
            "medium": {"drops": 4500, "bg_len": (20, 32), "bg_spd": (28, 38), "mg_len": (42, 64), "mg_spd": (44, 58), "fg_len": (68, 96), "fg_spd": (58, 76), "mist_alpha": 0.08, "rain_alpha": 0.40, "wind": 5.5},
            "heavy": {"drops": 10500, "bg_len": (40, 75), "bg_spd": (55, 85), "mg_len": (80, 140), "mg_spd": (85, 135), "fg_len": (140, 220), "fg_spd": (120, 180), "mist_alpha": 0.20, "rain_alpha": 0.55, "wind": 14.0},
        }
        cfg = configs.get(self.intensity, configs["medium"])
        self.cfg = cfg
        self.wind_tilt = cfg["wind"]
        total_drops = cfg["drops"]

        margin = max(abs(self.wind_tilt * scale_factor) * (height / 20.0), width * 0.25)
        self.spawn_x_min = -margin if self.wind_tilt > 0 else 0
        self.spawn_x_max = width if self.wind_tilt > 0 else (width + margin)
        self.margin = margin

        N_bg = int(total_drops * 0.55)
        self.bg_drops = np.zeros((N_bg, 5), dtype=np.float32)
        self._init_drops(self.bg_drops, cfg["bg_len"], cfg["bg_spd"])

        N_mg = int(total_drops * 0.35)
        self.mg_drops = np.zeros((N_mg, 5), dtype=np.float32)
        self._init_drops(self.mg_drops, cfg["mg_len"], cfg["mg_spd"])

        N_fg = int(total_drops * 0.10)
        self.fg_drops = np.zeros((N_fg, 5), dtype=np.float32)
        self._init_drops(self.fg_drops, cfg["fg_len"], cfg["fg_spd"])

        gradient = np.linspace(0.85, 1.15, height).reshape(height, 1, 1)
        storm_mist = np.full((height, width, 3), (150, 165, 175), dtype=np.float32) * gradient
        self.mist_layer = np.clip(storm_mist, 0, 255).astype(np.uint8)

        self.weather_mask = None
        self.inv_weather_mask = None

    def _init_drops(self, arr: np.ndarray, len_range, spd_range):
        N = len(arr)
        arr[:, 0] = np.random.uniform(self.spawn_x_min, self.spawn_x_max, N)
        arr[:, 1] = np.random.uniform(-100 * self.scale, self.h, N)
        arr[:, 2] = np.random.uniform(len_range[0], len_range[1], N) * self.scale
        arr[:, 3] = np.random.uniform(spd_range[0], spd_range[1], N) * self.scale
        arr[:, 4] = np.random.uniform(0.80, 1.20, N)

    def render(self, frame: np.ndarray) -> np.ndarray:
        h, w = self.h, self.w
        rain_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        base_tilt = self.wind_tilt * self.scale
        margin = self.margin

        # Bg micro-drizzle
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

        # Midground rain
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

        out = cv2.addWeighted(frame, 1.0, rain_canvas, self.cfg["rain_alpha"], 0)
        return cv2.addWeighted(out, 1.0 - self.cfg["mist_alpha"], self.mist_layer, self.cfg["mist_alpha"], 0)


class CinematicSnowEngine:
    """High-performance procedural snowfall engine: 3-depth aerodynamic crystals, wind tilt, and frost mist."""

    def __init__(self, width: int, height: int, intensity: str = "medium", source_img: Optional[np.ndarray] = None):
        self.w, self.h = width, height
        norm_int = intensity.lower()
        if norm_int in ("heavy", "high"):
            norm_int = "heavy"
        self.intensity = norm_int
        scale_factor = width / 1920.0
        self.scale = scale_factor

        configs = {
            "light": {"flakes": 700, "bg_r": (1.0, 1.8), "mg_r": (1.8, 3.0), "fg_r": (3.0, 5.0), "bg_spd": (1.2, 2.2), "mg_spd": (2.2, 3.5), "fg_spd": (3.5, 5.5), "wind": 1.5, "alpha": 0.65},
            "medium": {"flakes": 1800, "bg_r": (1.2, 2.2), "mg_r": (2.2, 4.0), "fg_r": (4.0, 7.0), "bg_spd": (1.8, 3.0), "mg_spd": (3.0, 4.8), "fg_spd": (4.8, 7.5), "wind": 3.0, "alpha": 0.80},
            "heavy": {"flakes": 3500, "bg_r": (1.5, 2.8), "mg_r": (2.8, 5.5), "fg_r": (5.5, 9.5), "bg_spd": (2.5, 4.2), "mg_spd": (4.2, 6.8), "fg_spd": (6.8, 10.5), "wind": 6.5, "alpha": 0.92},
        }
        cfg = configs.get(self.intensity, configs["medium"])
        self.cfg = cfg
        self.wind = cfg["wind"] * scale_factor
        total = cfg["flakes"]

        margin = max(abs(self.wind) * (height / 15.0), width * 0.20)
        self.spawn_min = -margin if self.wind > 0 else 0
        self.spawn_max = width if self.wind > 0 else (width + margin)
        self.margin = margin

        self.flakes = np.zeros((total, 6), dtype=np.float32)
        self._init_all_flakes(cfg)

    def _init_all_flakes(self, cfg):
        N = len(self.flakes)
        self.flakes[:, 0] = np.random.uniform(self.spawn_min, self.spawn_max, N)
        self.flakes[:, 1] = np.random.uniform(-50, self.h, N)
        r_tiers = np.random.choice([0, 1, 2], size=N, p=[0.55, 0.35, 0.10])
        for i in range(N):
            tier = r_tiers[i]
            if tier == 0:
                self.flakes[i, 2] = np.random.uniform(cfg["bg_r"][0], cfg["bg_r"][1]) * self.scale
                self.flakes[i, 3] = np.random.uniform(cfg["bg_spd"][0], cfg["bg_spd"][1]) * self.scale
            elif tier == 1:
                self.flakes[i, 2] = np.random.uniform(cfg["mg_r"][0], cfg["mg_r"][1]) * self.scale
                self.flakes[i, 3] = np.random.uniform(cfg["mg_spd"][0], cfg["mg_spd"][1]) * self.scale
            else:
                self.flakes[i, 2] = np.random.uniform(cfg["fg_r"][0], cfg["fg_r"][1]) * self.scale
                self.flakes[i, 3] = np.random.uniform(cfg["fg_spd"][0], cfg["fg_spd"][1]) * self.scale
        self.flakes[:, 4] = np.random.uniform(0.5, 2.0, N)
        self.flakes[:, 5] = np.random.uniform(0, 2.0 * np.pi, N)

    def render(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        h, w = self.h, self.w
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

        sway = np.sin(frame_idx * 0.08 + self.flakes[:, 5]) * (1.2 * self.scale)
        self.flakes[:, 0] += self.wind * self.flakes[:, 4] + sway
        self.flakes[:, 1] += self.flakes[:, 3]

        reset = (self.flakes[:, 1] > h) | (self.flakes[:, 0] > (w + self.margin))
        if np.any(reset):
            cnt = np.count_nonzero(reset)
            self.flakes[reset, 1] = np.random.uniform(-30, 0, cnt)
            self.flakes[reset, 0] = np.random.uniform(self.spawn_min, self.spawn_max, cnt)

        xs = self.flakes[:, 0].astype(np.int32)
        ys = self.flakes[:, 1].astype(np.int32)
        rads = np.clip(self.flakes[:, 2].astype(np.int32), 1, 15)

        valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
        for x, y, r in zip(xs[valid], ys[valid], rads[valid]):
            cv2.circle(canvas, (int(x), int(y)), int(r), (245, 248, 255), -1, lineType=cv2.LINE_AA)

        return cv2.addWeighted(frame, 1.0, canvas, self.cfg["alpha"], 0)


class LivingEnvironmentEngine:
    """Procedural living world dynamics: water wave displacement, specular caustic shimmer, cloud drift, and smoke plumes."""

    def __init__(
        self,
        img: np.ndarray,
        width: int,
        height: int,
        remove_objects: bool = False,
        remove_object_list: Optional[List[str]] = None,
        enable_water: bool = True,
        enable_smoke: bool = True,
        enable_clouds: bool = True,
        enable_kinetic_objects: bool = True,
        total_frames: int = 240,
    ):
        self.w, self.h = width, height
        self.scale = width / 1920.0
        self.remove_objects = remove_objects
        self.clean_base_plate = None

        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LANCZOS4)
        if remove_objects and ONNX_SESSION is not None:
            try:
                blob = cv2.dnn.blobFromImage(resized, 1 / 255.0, (640, 640), swapRB=True, crop=False)
                preds = ONNX_SESSION.run(None, {"images": blob})[0][0]
                rm_set = set(remove_object_list or ["person", "car", "bicycle", "motorcycle", "bus", "truck"])
                mask = np.zeros((height, width), dtype=np.uint8)
                for col in range(preds.shape[1]):
                    cid = int(np.argmax(preds[4:, col]))
                    if float(preds[4 + cid, col]) > 0.32 and cid < len(COCO_CLASSES) and COCO_CLASSES[cid] in rm_set:
                        xc, yc, bw, bh = preds[:4, col]
                        x1 = max(0, int((xc - bw * 0.6) * (width / 640.0)))
                        y1 = max(0, int((yc - bh * 0.6) * (height / 640.0)))
                        x2 = min(width, int((xc + bw * 0.6) * (width / 640.0)))
                        y2 = min(height, int((yc + bh * 0.6) * (height / 640.0)))
                        if (x2 - x1) * (y2 - y1) < 0.04 * width * height:
                            mask[y1:y2, x1:x2] = 255
                if np.any(mask > 0):
                    self.clean_base_plate = cv2.inpaint(resized, mask, 4, cv2.INPAINT_TELEA)
            except Exception:
                self.clean_base_plate = None

        base_img = self.clean_base_plate if self.clean_base_plate is not None else resized
        self.img_orig = base_img
        hsv = cv2.cvtColor(base_img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)

        # Precision Living Dynamics: specular water shimmer, cloud drift, micro-kinetic objects
        from src.scripts.drone_living_dynamics import DroneLivingWorld
        self.living_world = DroneLivingWorld(
            base_img,
            width,
            height,
            enable_water=enable_water,
            enable_clouds=enable_clouds,
            enable_objects=enable_kinetic_objects,
            total_frames=total_frames,
        )

        # Smoke Detection (Only active when explicitly requested, preventing sky distortion)
        self.smoke_mask = None
        self.inv_smoke_mask = None
        self.has_smoke = False
        if enable_smoke:
            upper_hsv = hsv[:int(height * 0.40), :]
            upper_gray = gray[:int(height * 0.40), :]
            smoke_candidates = (upper_hsv[:, :, 1] < 45) & (upper_gray > 165) & (upper_gray < 245)
            plume_ratio = float(np.mean(smoke_candidates))
            if 0.005 < plume_ratio < 0.10:
                full_s = np.zeros((height, width), dtype=np.float32)
                full_s[:int(height * 0.40), :] = smoke_candidates.astype(np.float32)
                kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
                full_s = cv2.morphologyEx(full_s, cv2.MORPH_OPEN, kernel_s)
                self.smoke_mask = cv2.GaussianBlur(full_s, (31, 31), 8)
                self.inv_smoke_mask = 1.0 - self.smoke_mask

                ys_s = np.where(self.smoke_mask > 0.005)[0]
                if len(ys_s) > 0:
                    self.smoke_y_min = int(ys_s.min())
                    self.smoke_y_max = int(ys_s.max()) + 1
                    s_roi_h = self.smoke_y_max - self.smoke_y_min
                    self.smoke_x = np.arange(width, dtype=np.float32)
                    self.smoke_y_rel = np.arange(s_roi_h, dtype=np.float32)
                    self.smoke_gx, self.smoke_gy = np.meshgrid(self.smoke_x, self.smoke_y_rel)
                    self.smoke_weight_roi = self.smoke_mask[self.smoke_y_min:self.smoke_y_max, :]
                    self.inv_smoke_weight_roi = self.inv_smoke_mask[self.smoke_y_min:self.smoke_y_max, :]
                    self.has_smoke = True

    @property
    def cycle_plates(self) -> Optional[List[np.ndarray]]:
        return self.living_world.cycle_plates if self.living_world.cycle_plates else None

    def get_source_plate(self, frame_idx: int) -> np.ndarray:
        """Returns source plate animated with natural fluid dynamics aligned with 3D camera space."""
        base = self.clean_base_plate if self.clean_base_plate is not None else self.img_orig
        return self.living_world.get_source_plate(frame_idx, base)

    def apply(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        out = frame
        if getattr(self, "has_smoke", False) and self.smoke_mask is not None:
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


VALID_ACTIONS = {
    "--stay": "stay",
    "--hold": "stay",
    "--dollyin": "dollyin",
    "--dollyout": "dollyout",
    "--pan-left": "pan-left",
    "--pan-right": "pan-right",
    "--tilt-up": "tilt-up",
    "--tilt-down": "tilt-down",
    "--zoom-in": "dollyin",
    "--zoomin": "dollyin",
    "--zoom-out": "dollyout",
    "--zoomout": "dollyout",
    "--roll-left": "roll-left",
    "--roll-right": "roll-right",
    "--level": "level",
    "--pedestal-up": "tilt-up",
    "--pedestal-down": "tilt-down",
    "--drift-up-right": "drift-up-right",
    "--drift-up-left": "drift-up-left",
    "--drift-down-right": "drift-down-right",
    "--drift-down-left": "drift-down-left",
    "--orbit-left": "orbit-left",
    "--orbit-right": "orbit-right",
    "--pan-right-zoom-out": "pan-right-zoom-out",
    "--pan-left-zoom-out": "pan-left-zoom-out",
    "--orbit-stage-to-audience": "orbit-stage-to-audience",
    "--stage-audience-split": "stage-audience-split",
    "--sweep-to-crowd": "sweep-to-crowd",
    "--slow-drone-forward": "slow-drone-forward",
    "--drone-forward": "slow-drone-forward",
    "--slow-drone-pullback": "slow-drone-pullback",
    "--drone-pullback": "slow-drone-pullback",
    "--crane-ascend": "crane-ascend",
    "--crane-descent": "crane-descent",
    "--drone-sweep-left": "drone-sweep-left",
    "--drone-sweep-right": "drone-sweep-right",
}


def parse_action_sequence(raw_args: list) -> list:
    """Parses sequence steps from command-line arguments."""
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


def normalize_choreography_sequence(choreography: Union[list, dict, str, None], default_duration: float = 5.0) -> list:
    """Converts structured dicts, tuples, or legacy strings into sequence tuples."""
    if not choreography:
        return [("dollyin", max(2.0, min(14.0, default_duration)))]

    if isinstance(choreography, dict):
        choreography = [choreography]

    if isinstance(choreography, str):
        mov = choreography.lower().strip()
        dur = max(1.0, float(default_duration))
        if any(w in mov for w in ("stay", "hold", "fixed", "locked", "tripod", "static", "cinemagraph", "still")):
            return [("stay", dur)]
        elif any(k in mov for k in ("orbit-stage", "orbit_stage", "stage-audience", "stage_audience", "sweep-to-crowd", "sweep_to_crowd")):
            p1 = round(dur * 0.40, 2)
            p2 = round(dur * 0.35, 2)
            p3 = round(max(0.5, dur - p1 - p2), 2)
            return [
                ("parallel", [("dollyout", p1), ("pan-right", p1), ("orbit-left", p1)]),
                ("parallel", [("pan-right", p2), ("tilt-up", p2)]),
                ("parallel", [("dollyin", p3), ("level", p3)]),
            ]
        elif "orbit-left" in mov or "orbit_left" in mov:
            return [("orbit-left", dur)]
        elif "orbit-right" in mov or "orbit_right" in mov:
            return [("orbit-right", dur)]
        elif "drift-up-right" in mov:
            return [("drift-up-right", dur)]
        elif "drift-up-left" in mov:
            return [("drift-up-left", dur)]
        elif "drift-down-right" in mov:
            return [("drift-down-right", dur)]
        elif "drift-down-left" in mov:
            return [("drift-down-left", dur)]
        elif "left" in mov:
            return [("pan-left", dur)]
        elif "right" in mov:
            return [("pan-right", dur)]
        elif "up" in mov or "crane" in mov or "pedestal" in mov:
            return [("tilt-up", dur)]
        elif "down" in mov:
            return [("tilt-down", dur)]
        elif "out" in mov or "pull" in mov:
            return [("dollyout", dur)]
        return [("dollyin", dur)]

    norm = []
    for item in choreography:
        if isinstance(item, tuple) and len(item) == 2:
            norm.append(item)
        elif isinstance(item, str):
            mov_str = item.lower().replace("_", "-")
            dur = default_duration / max(1, len(choreography))
            if any(k in mov_str for k in ("orbit-stage", "stage-audience", "sweep-to-crowd")):
                p1 = round(dur * 0.40, 2)
                p2 = round(dur * 0.35, 2)
                p3 = round(max(0.5, dur - p1 - p2), 2)
                norm.extend([
                    ("parallel", [("dollyout", p1), ("pan-right", p1), ("orbit-left", p1)]),
                    ("parallel", [("pan-right", p2), ("tilt-up", p2)]),
                    ("parallel", [("dollyin", p3), ("level", p3)]),
                ])
            else:
                norm.append((mov_str, dur))
        elif isinstance(item, dict):
            # Supports Gemini Stage format: {"stage": 1, "duration": 4.0, "movements": ["dollyin", "pan-left"]}
            # Sequential format: {"movement": "dollyin", "duration": 6.0}
            # Waypoint format: {"motion": "dollyin", "duration_seconds": 6.0}
            dur = float(item.get("duration") or item.get("duration_seconds") or (default_duration / max(1, len(choreography))))
            dur = max(0.5, dur)
            moves = item.get("parallel") or item.get("movements") or item.get("movement") or item.get("motion") or item.get("action")
            if isinstance(moves, str) and any(k in moves.lower() for k in ("orbit-stage", "orbit_stage", "stage-audience", "stage_audience", "sweep-to-crowd", "sweep_to_crowd")):
                p1 = round(dur * 0.40, 2)
                p2 = round(dur * 0.35, 2)
                p3 = round(max(0.5, dur - p1 - p2), 2)
                norm.extend([
                    ("parallel", [("dollyout", p1), ("pan-right", p1), ("orbit-left", p1)]),
                    ("parallel", [("pan-right", p2), ("tilt-up", p2)]),
                    ("parallel", [("dollyin", p3), ("level", p3)]),
                ])
            elif isinstance(moves, list):
                if len(moves) == 1:
                    norm.append((str(moves[0]).lower().replace("_", "-"), dur))
                else:
                    norm.append(("parallel", [(str(m).lower().replace("_", "-"), dur) for m in moves]))
            elif isinstance(moves, str):
                norm.append((moves.lower().replace("_", "-"), dur))
            elif "action" in item:
                norm.append((str(item["action"]).lower().replace("_", "-"), dur))
    return norm if norm else [("dollyin", max(1.0, float(default_duration)))]


_ONNX_YOLO_FACE_SESSION = None


def _get_local_yolo_session():
    global _ONNX_YOLO_FACE_SESSION
    if _ONNX_YOLO_FACE_SESSION is None:
        try:
            import onnxruntime as ort
            from pathlib import Path
            model_path = Path(__file__).resolve().parents[2] / "models" / "yolov8n.onnx"
            if model_path.is_file():
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                _ONNX_YOLO_FACE_SESSION = ort.InferenceSession(
                    str(model_path), sess_options=opts, providers=["CPUExecutionProvider"]
                )
        except Exception:
            _ONNX_YOLO_FACE_SESSION = False
    return _ONNX_YOLO_FACE_SESSION if _ONNX_YOLO_FACE_SESSION is not False else None


def detect_lead_face_center(img: np.ndarray) -> Optional[Tuple[float, float]]:
    """Detects lead character face center (cx, cy) in pixels using local lightweight ONNX YOLOv8n."""
    try:
        session = _get_local_yolo_session()
        if session is not None and img is not None:
            h, w = img.shape[:2]
            scale = min(640.0 / w, 640.0 / h)
            nw, nh = int(w * scale), int(h * scale)
            resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
            canvas = np.zeros((640, 640, 3), dtype=np.uint8)
            pad_x = (640 - nw) // 2
            pad_y = (640 - nh) // 2
            canvas[pad_y:pad_y + nh, pad_x:pad_x + nw] = resized
            inp = (canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0)[None, ...]
            out = session.run(None, {"images": inp})[0]
            preds = out[0].T
            boxes, scores = preds[:, :4], preds[:, 4:]
            class_ids, confs = np.argmax(scores, axis=1), np.max(scores, axis=1)
            mask = (class_ids == 0) & (confs > 0.35)
            if np.any(mask):
                p_b, p_c = boxes[mask], confs[mask]
                best_cand, best_score = None, -1.0
                for (bx, by, bw, bh), conf in zip(p_b, p_c):
                    x1 = (bx - bw / 2 - pad_x) / scale
                    y1 = (by - bh / 2 - pad_y) / scale
                    x2 = (bx + bw / 2 - pad_x) / scale
                    y2 = (by + bh / 2 - pad_y) / scale
                    area = (x2 - x1) * (y2 - y1)
                    cx = (x1 + x2) / 2.0
                    dist_c = abs(cx - w / 2.0) / (w / 2.0)
                    score = area * (float(conf) ** 0.5) * (1.0 - 0.25 * dist_c)
                    if score > best_score:
                        best_score = score
                        head_y = y1 + (y2 - y1) * 0.12
                        best_cand = (float(cx), float(head_y))
                if best_cand:
                    return best_cand
    except Exception:
        pass
    return None


def precompute_sequence_matrices(
    img_shape: tuple,
    sequence: list,
    fps: float = 24.0,
    output_size: tuple = (3840, 2160),
    max_depth: float = 0.50,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
    face_target: Optional[Tuple[float, float]] = None,
) -> tuple:
    """Precomputes 2D perspective / homography transformation matrices along camera timeline."""
    h, w = img_shape[:2]
    target_w, target_h = output_size
    target_aspect = target_w / float(target_h)

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
        [[0.0, 0.0], [float(target_w), 0.0], [float(target_w), float(target_h)], [0.0, float(target_h)]],
        dtype=np.float32,
    )

    cw_min = base_w * (1.0 - max_depth)
    ch_min = base_h * (1.0 - max_depth)
    avail_pan_x_min = max(1.0, (float(w) - cw_min) / 2.0)
    avail_tilt_y_min = max(1.0, (float(h) - ch_min) / 2.0)

    if face_target is not None:
        face_x, face_y = face_target
        singer_target_p = max(-0.95, min(0.95, (face_x - base_cx) / avail_pan_x_min))
        singer_target_t = max(-0.95, min(0.95, (face_y - base_cy) / avail_tilt_y_min))
    else:
        # Default stage lead singer center-left framing
        singer_target_p = -0.28
        singer_target_t = -0.68

    has_pan = any(
        any(k in act for k in ("pan", "drift", "orbit", "left", "right"))
        for item in sequence
        for act in ([x[0] for x in item[1]] if item[0] == "parallel" else [item[0]])
        if not any(w in act for w in ("stay", "hold", "fixed", "locked", "tripod", "static"))
    )
    has_tilt = any(
        any(k in act for k in ("tilt", "pedestal", "crane", "drift", "up", "down", "ascend", "descend"))
        for item in sequence
        for act in ([x[0] for x in item[1]] if item[0] == "parallel" else [item[0]])
        if not any(w in act for w in ("stay", "hold", "fixed", "locked", "tripod", "static"))
    )

    cur_depth = 1.0 if start_zoom in ("in", "zoomed", "tight", "face", "closeup") else (0.35 if (has_pan or has_tilt) else 0.0)

    first_act = sequence[0][1][0][0] if (sequence and sequence[0][0] == "parallel" and sequence[0][1]) else (sequence[0][0] if sequence else "")
    first_act = str(first_act).lower()

    if start_pan in ("left", "far-left"):
        cur_pan = -1.0
    elif start_pan in ("right", "far-right"):
        cur_pan = 1.0
    elif start_pan in ("face", "singer", "vocal"):
        cur_pan = singer_target_p
    else:
        if "pan-right" in first_act or "panright" in first_act:
            cur_pan = -0.85
        elif "pan-left" in first_act or "panleft" in first_act:
            cur_pan = 0.85
        elif "orbit-left" in first_act:
            cur_pan = 0.85
        elif "orbit-right" in first_act:
            cur_pan = -0.85
        else:
            cur_pan = 0.0

    if start_tilt in ("up", "top"):
        cur_tilt = -1.0
    elif start_tilt in ("face", "singer", "vocal"):
        cur_tilt = singer_target_t
    elif start_tilt in ("down", "bottom"):
        cur_tilt = 1.0
    else:
        if any(k in first_act for k in ("face", "singer", "vocal", "closeup")):
            if any(w in first_act for w in ("stay", "hold", "steady", "fixed", "tight", "eye")):
                cur_tilt = singer_target_t
                cur_pan = singer_target_p
                cur_depth = 1.0
            else:
                cur_tilt = 0.0
        elif any(k in first_act for k in ("tilt-up", "tiltup", "crane-up", "pedestal-up", "ascend")):
            cur_tilt = 0.85
        elif any(k in first_act for k in ("tilt-down", "tiltdown", "crane-down", "pedestal-down", "descend")):
            cur_tilt = -0.85
        else:
            cur_tilt = 0.0

    cur_roll = 0.0

    timeline_states = []

    def resolve_target(action_name, s_d, s_p, s_t, s_r):
        act = action_name.lower().replace("_", "-").replace(" ", "-")
        t_d, t_p, t_t, t_r = s_d, s_p, s_t, s_r
        if any(w in act for w in ("stay", "hold", "static", "locked", "tripod", "fixed")) and not any(k in act for k in ("face", "singer")):
            pass
        elif act in ("steady-face", "steady-singer", "tight-face", "face-hold", "singer-hold"):
            t_d = 1.0
            t_t = singer_target_t
            t_p = singer_target_p
            t_r = 0.0
        elif act in ("zoom-in-singer", "zoom-in-face", "vocal-close-up", "face-close-up", "tight-face", "singer-close-up", "close-up", "closeup"):
            t_d = 1.0
            t_t = singer_target_t
            t_p = singer_target_p
            t_r = 0.0
        elif act in ("pan-to-guitarist", "guitarist", "lead-guitarist"):
            t_d = 0.65
            t_t = -0.20
            t_p = 0.85
            t_r = 0.0
        elif act in ("pan-to-drummer", "drummer", "drums"):
            t_d = 0.60
            t_t = -0.45
            t_p = 0.0
            t_r = 0.0
        elif act in ("stage-audience-split", "stage-audience", "orbit-stage-to-audience"):
            t_d = 0.35
            t_t = -0.15
            t_p = 0.55
            t_r = 2.0
        elif act in ("sweep-to-crowd", "pan-to-audience", "crowd-sweep", "crowd-cheer"):
            t_d = 0.65
            t_t = -0.35
            t_p = 0.90
            t_r = 0.0
        elif act in ("wide-stage-pullback", "pullback", "zoom-out-stage", "arena-pullback"):
            t_d = 0.0
            t_t = 0.0
            t_p = 0.0
            t_r = 0.0
        elif act in ("steady-eye-level", "eye-level", "steady-stage"):
            t_d = 0.35
            t_t = -0.15
            t_p = 0.0
            t_r = 0.0
        elif act in ("dollyin", "dolly-in", "zoomin", "zoom-in"):
            t_d = 1.0
            if face_target is not None:
                t_p = singer_target_p
                t_t = singer_target_t
        elif act in ("slow-drone-forward", "drone-forward", "slow-push-in", "push-in"):
            t_d = min(1.0, max(0.65, s_d + 0.55))
        elif act in ("dollyout", "dolly-out", "zoomout", "zoom-out", "slow-drone-pullback", "drone-pullback", "dolly-pullback"):
            t_d = 0.0
        elif act in ("crane-ascend", "crane-up-reveal"):
            t_t = -0.85
            t_d = max(0.0, s_d - 0.35) if s_d > 0.35 else 0.42
        elif act in ("crane-descent", "crane-down-push"):
            t_t = 0.75
            t_d = min(1.0, max(0.50, s_d + 0.40))
        elif act in ("drone-sweep-left", "sweep-left"):
            t_p = -0.90; t_r = 1.5
            if t_d < 0.38:
                t_d = 0.42
        elif act in ("drone-sweep-right", "sweep-right"):
            t_p = 0.90; t_r = -1.5
            if t_d < 0.38:
                t_d = 0.42
        elif act in ("pan-left", "panleft"):
            t_p = -1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("pan-right", "panright"):
            t_p = 1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("tilt-up", "tiltup", "pedestal-up", "crane-up", "ascend"):
            t_t = -1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("tilt-down", "tiltdown", "pedestal-down", "crane-down", "descend"):
            t_t = 1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("roll-left", "rollleft"):
            t_r = -3.5
        elif act in ("roll-right", "rollright"):
            t_r = 3.5
        elif act == "level":
            t_r = 0.0
        elif act in ("drift-up-right", "driftupright"):
            t_p = 1.0; t_t = -1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("drift-up-left", "driftupleft"):
            t_p = -1.0; t_t = -1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("drift-down-right", "driftdownright"):
            t_p = 1.0; t_t = 1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("drift-down-left", "driftdownleft"):
            t_p = -1.0; t_t = 1.0
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("orbit-left", "orbitleft"):
            t_p = -0.85; t_r = 2.5
            if t_d < 0.35:
                t_d = 0.42
        elif act in ("orbit-right", "orbitright"):
            t_p = 0.85; t_r = -2.5
            if t_d < 0.35:
                t_d = 0.42
        elif "zoom-out" in act or "zoomout" in act or "dollyout" in act:
            t_d = 0.0; t_p = 1.0 if "right" in act else -1.0; t_t = s_t; t_r = s_r
        elif "zoom-in" in act or "zoomin" in act or "dollyin" in act:
            t_d = 1.0; t_p = 1.0 if "right" in act else -1.0; t_t = s_t; t_r = s_r
        return t_d, t_p, t_t, t_r

    for item in sequence:
        action_type = item[0]

        if action_type == "parallel":
            sub_actions = item[1]
            if not sub_actions:
                continue
            max_duration = max(dur for _, dur in sub_actions)
            num_frames = int(round(max_duration * fps))
            if num_frames <= 0:
                continue

            start_d, start_p, start_t, start_r = cur_depth, cur_pan, cur_tilt, cur_roll
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
                    act = sub_act.lower().replace("_", "-").replace(" ", "-")
                    if any(k in act for k in ("dollyin", "zoom-in", "zoomin", "dollyout", "zoom-out", "zoomout", "drone-forward", "pullback", "push-in", "crane", "singer", "face", "close")):
                        d_val = start_d + e * (tgt_d - start_d)
                    if any(k in act for k in ("pan", "drift", "orbit", "sweep", "left", "right", "guitarist")):
                        p_val = start_p + e * (tgt_p - start_p)
                    if any(k in act for k in ("tilt", "pedestal", "crane", "drift", "up", "down", "ascend", "descend", "descent", "singer", "face", "close", "guitarist", "drummer")):
                        t_val = start_t + e * (tgt_t - start_t)
                    if any(k in act for k in ("roll", "orbit", "sweep", "level")):
                        r_val = start_r + e * (tgt_r - start_r)

                timeline_states.append((d_val, p_val, t_val, r_val))

            for sub_act, tgt_d, tgt_p, tgt_t, tgt_r, _ in channels:
                act = sub_act.lower().replace("_", "-").replace(" ", "-")
                if any(k in act for k in ("dollyin", "zoom-in", "zoomin", "dollyout", "zoom-out", "zoomout", "drone-forward", "pullback", "push-in", "crane", "singer", "face", "close")):
                    cur_depth = tgt_d
                if any(k in act for k in ("pan", "drift", "orbit", "sweep", "left", "right", "guitarist")):
                    cur_pan = tgt_p
                if any(k in act for k in ("tilt", "pedestal", "crane", "drift", "up", "down", "ascend", "descend", "descent", "singer", "face", "close", "guitarist", "drummer")):
                    cur_tilt = tgt_t
                if any(k in act for k in ("roll", "orbit", "sweep", "level")):
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

    matrices = []
    min_scale = max(0.20, 1.0 - max_depth)

    for d, p, t, r in timeline_states:
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

        corners = np.array([[-half_w, -half_h], [half_w, -half_h], [half_w, half_h], [-half_w, half_h]], dtype=np.float32)

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


def get_ffmpeg_writer(output_path: str, width: int, height: int, fps: float):
    """Spawns FFmpeg pipe for high-quality H.264 broadcast encoding with zero GOP pulsing."""
    cmd = [
        FFMPEG_BIN, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "bgr24", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-maxrate", "4.5M", "-bufsize", "9M",
        "-threads", "4", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_path),
    ]
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    except Exception:
        return None


def render_perspective_drone_clip_sync(
    image_path: Path | str,
    output_path: Path | str,
    duration_seconds: float = 5.0,
    fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160),
    camera_movement: Optional[str] = None,
    speed_factor: float = 1.0,
    force_rerun: bool = False,
    camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
    choreography: Optional[Union[list, str]] = None,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
    motion_curve: Optional[str] = None,
    max_depth: Optional[float] = None,
    rain: bool = False,
    rain_intensity: str = "light",
    snow: bool = False,
    snow_intensity: str = "medium",
    remove_objects: bool = False,
    remove_object_list: Optional[List[str]] = None,
    interpolation: str = "cubic",
    lower_third_hud: Optional[dict] = None,
    water: bool = False,
    smoke: bool = False,
    clouds: bool = False,
    kinetic_objects: bool = False,
    **kwargs,
) -> Path:
    """Render calm, cinematic 4K perspective drone shot on CPU via subpixel homography and procedural dynamics."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        return out

    effective_curve = motion_curve or curve or "cosine"

    is_video = str(image_path).lower().endswith((".mp4", ".mov", ".mkv", ".webm"))
    cap = None
    if is_video:
        cap = cv2.VideoCapture(str(image_path))
        ret, img = cap.read()
        if not ret or img is None:
            raise FileNotFoundError(f"Cannot read video frames from: {image_path}")
    else:
        img = cv2.imread(str(image_path))
        if img is None:
            raise FileNotFoundError(f"Cannot load image for perspective drone shot: {image_path}")

    # Enforce duration bounds [2.0s, 60.0s]
    duration_seconds = max(2.0, min(60.0, float(duration_seconds)))

    # Determine sequence actions
    seq_input = choreography if choreography is not None else (camera_waypoints if camera_waypoints is not None else camera_movement)
    sequence = normalize_choreography_sequence(seq_input, default_duration=duration_seconds)

    # Re-normalize sequence to exactly match target duration
    total_seq_dur = sum(max(dur for _, dur in item[1]) if item[0] == "parallel" else item[1] for item in sequence)
    if total_seq_dur > 0 and abs(total_seq_dur - duration_seconds) > 0.05:
        scale = duration_seconds / total_seq_dur
        scaled_seq = []
        for item in sequence:
            if item[0] == "parallel":
                scaled_seq.append(("parallel", [(sub_act, round(sub_d * scale, 3)) for sub_act, sub_d in item[1]]))
            else:
                scaled_seq.append((item[0], round(item[1] * scale, 3)))
        sequence = scaled_seq

    target_w, target_h = target_res
    output_size = (target_w, target_h)

    # 4-stage optical pipeline enhancement
    img_enhanced = enhance_image_ultra_clarity(img, target_w, target_h)

    # Auto-derive max_depth if not specified: face close-ups need 0.72 depth for tight portrait framing
    if max_depth is None:
        has_face_closeup = any(
            any(k in str(act).lower() for k in ("face", "singer", "closeup", "close-up", "vocal"))
            for item in sequence
            for act in ([x[0] for x in item[1]] if item[0] == "parallel" else [item[0]])
        )
        effective_max_depth = 0.72 if has_face_closeup else 0.50
    else:
        effective_max_depth = float(max_depth)

    # Detect lead face center for intelligent auto-framing
    face_center = detect_lead_face_center(img)

    # Matrices precomputation
    matrices, total_frames = precompute_sequence_matrices(
        img_shape=img_enhanced.shape,
        sequence=sequence,
        fps=fps,
        output_size=output_size,
        max_depth=effective_max_depth,
        start_pan=start_pan,
        start_zoom=start_zoom,
        start_tilt=start_tilt,
        curve=effective_curve,
        face_target=face_center,
    )

    is_static_hold = len(sequence) == 1 and sequence[0][0] == "stay"
    living_env = LivingEnvironmentEngine(
        img_enhanced,
        target_w,
        target_h,
        remove_objects=remove_objects,
        remove_object_list=remove_object_list,
        enable_water=water and not is_static_hold,
        enable_smoke=smoke,
        enable_clouds=clouds and not is_static_hold,
        enable_kinetic_objects=kinetic_objects and not is_static_hold,
        total_frames=total_frames,
    )
    rain_engine = CinematicRainEngine(target_w, target_h, intensity=rain_intensity, source_img=img_enhanced) if rain else None
    snow_engine = CinematicSnowEngine(target_w, target_h, intensity=snow_intensity, source_img=img_enhanced) if snow else None

    # Resolve warp interpolation flag (default: INTER_CUBIC for 4x faster 4K rendering)
    inter_lower = (interpolation or "cubic").lower()
    if "lanczos" in inter_lower:
        warp_flag = cv2.INTER_LANCZOS4
    elif "linear" in inter_lower:
        warp_flag = cv2.INTER_LINEAR
    else:
        warp_flag = cv2.INTER_CUBIC

    ffmpeg_proc = get_ffmpeg_writer(str(out), target_w, target_h, fps)
    video_writer = None
    if ffmpeg_proc is None:
        temp_raw = out.parent / f"_raw_{out.stem}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(str(temp_raw), fourcc, fps, output_size)

    hud_bgr = None
    hud_alpha = None
    chap_bgr = None
    chap_alpha = None
    map_bgr = None
    map_alpha = None
    fact_bgr = None
    fact_alpha = None
    qr_bgr = None
    qr_alpha = None
    if lower_third_hud and isinstance(lower_third_hud, dict):
        try:
            if lower_third_hud.get("is_documentary"):
                from src.studios.documentary_studio.doc_overlay_service import (
                    create_documentary_lower_third_overlay,
                    create_documentary_chapter_title_card,
                    create_documentary_fact_badge_overlay,
                )
                rgba = create_documentary_lower_third_overlay(
                    attraction_name=lower_third_hud.get("attraction_name", "Landmark"),
                    sub_location=lower_third_hud.get("sub_location") or lower_third_hud.get("timing_text"),
                    target_res=output_size,
                    position=lower_third_hud.get("position", "bottom_left"),
                )
                if lower_third_hud.get("chapter_title"):
                    c_rgba = create_documentary_chapter_title_card(
                        chapter_title=lower_third_hud.get("chapter_title"),
                        chapter_subtitle=lower_third_hud.get("chapter_subtitle"),
                        key_stats=lower_third_hud.get("chapter_stats"),
                        target_res=output_size,
                    )
                    chap_bgr = cv2.cvtColor(c_rgba, cv2.COLOR_RGBA2BGR)
                    chap_alpha = (c_rgba[:, :, 3] / 255.0).astype(np.float32)

                if lower_third_hud.get("fact_badge"):
                    f_rgba = create_documentary_fact_badge_overlay(lower_third_hud["fact_badge"], target_res=output_size)
                    fact_bgr = cv2.cvtColor(f_rgba, cv2.COLOR_RGBA2BGR)
                    fact_alpha = (f_rgba[:, :, 3] / 255.0).astype(np.float32)
            else:
                from src.services.map_route_engine import create_lower_third_hud_overlay
                rgba = create_lower_third_hud_overlay(
                    attraction_name=lower_third_hud.get("attraction_name", "Landmark"),
                    timing_text=lower_third_hud.get("timing_text", "09:00 AM – 11:30 AM"),
                    day_badge=lower_third_hud.get("day_badge", "DAY 1"),
                    target_res=output_size,
                    cost_text=lower_third_hud.get("cost_text"),
                    transit_text=lower_third_hud.get("transit_text"),
                )

            # Top-Right Cartographic / Route Map Locator (Active for tours or doc geography chapters)
            if lower_third_hud.get("show_map_locator") or (lower_third_hud.get("is_documentary") and any(w in str(lower_third_hud.get("chapter_title", "")).lower() for w in ("geography", "border", "climate", "coast", "area"))):
                from src.studios.documentary_studio.doc_cartography_service import create_cartographic_locator_overlay
                c_query = lower_third_hud.get("country_entity") or lower_third_hud.get("sub_location") or lower_third_hud.get("attraction_name") or "France"
                m_rgba = create_cartographic_locator_overlay(c_query, target_res=output_size)
                map_bgr = cv2.cvtColor(m_rgba, cv2.COLOR_RGBA2BGR)
                map_alpha = (m_rgba[:, :, 3] / 255.0).astype(np.float32)

            # Bottom-Right Scannable QR Code Card (Strictly for Tour Itineraries with active qr_url)
            if lower_third_hud.get("show_itinerary_qr") and lower_third_hud.get("qr_url"):
                from src.studios.documentary_studio.doc_qr_service import create_itinerary_qr_overlay
                qr_url = lower_third_hud.get("qr_url") or "https://maps.google.com"
                dest_title = lower_third_hud.get("attraction_name") or lower_third_hud.get("country_entity") or "Itinerary Route"
                q_rgba = create_itinerary_qr_overlay(route_url=qr_url, destination_name=dest_title, target_res=output_size)
                qr_bgr = cv2.cvtColor(q_rgba, cv2.COLOR_RGBA2BGR)
                qr_alpha = (q_rgba[:, :, 3] / 255.0).astype(np.float32)

            hud_bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)
            hud_alpha = (rgba[:, :, 3] / 255.0).astype(np.float32)
        except Exception:
            hud_bgr = None
            chap_bgr = None
            map_bgr = None
            fact_bgr = None
            qr_bgr = None

    try:
        for i in range(total_frames):
            if is_video and cap is not None:
                ret, v_frame = cap.read()
                if not ret or v_frame is None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, v_frame = cap.read()
                if ret and v_frame is not None:
                    if v_frame.shape[1] != target_w or v_frame.shape[0] != target_h:
                        source_plate = cv2.resize(v_frame, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
                    else:
                        source_plate = v_frame
                else:
                    source_plate = img_enhanced
            else:
                source_plate = living_env.get_source_plate(i)

            frame = cv2.warpPerspective(source_plate, matrices[i], output_size, flags=warp_flag, borderMode=cv2.BORDER_REPLICATE)
            if not is_video:
                frame = living_env.apply(frame, i)
            if rain_engine:
                frame = rain_engine.render(frame)
            elif snow_engine:
                frame = snow_engine.render(frame, i)

            # Centered Chapter Title Card: 3.3s smooth sine fade-in/fade-out
            if chap_bgr is not None and chap_alpha is not None:
                c_fade_in = max(6, int(fps * 0.5))
                c_hold_end = int(fps * 2.7)
                c_fade_out_end = int(fps * 3.3)
                if i < c_fade_in:
                    c_fade = 0.5 * (1.0 - np.cos(np.pi * i / float(c_fade_in)))
                elif i < c_hold_end:
                    c_fade = 1.0
                elif i < c_fade_out_end:
                    c_fade = 0.5 * (1.0 + np.cos(np.pi * (i - c_hold_end) / float(c_fade_out_end - c_hold_end)))
                else:
                    c_fade = 0.0

                if c_fade > 0.001:
                    c_eff_alpha = (chap_alpha * c_fade)[:, :, None]
                    frame = (frame.astype(np.float32) * (1.0 - c_eff_alpha) + chap_bgr.astype(np.float32) * c_eff_alpha).astype(np.uint8)

            # Cartographic Locator Inset: 5.5s smooth sine fade-in/fade-out in upper-right quadrant
            if map_bgr is not None and map_alpha is not None:
                m_fade_in = max(6, int(fps * 0.5))
                m_start = int(fps * 0.8)
                m_hold_end = int(fps * 4.8)
                m_fade_out_end = int(fps * 5.6)
                adj_m = i - m_start
                if adj_m < 0:
                    m_fade = 0.0
                elif adj_m < m_fade_in:
                    m_fade = 0.5 * (1.0 - np.cos(np.pi * adj_m / float(m_fade_in)))
                elif adj_m < (m_hold_end - m_start):
                    m_fade = 1.0
                elif adj_m < (m_fade_out_end - m_start):
                    m_fade = 0.5 * (1.0 + np.cos(np.pi * (adj_m - (m_hold_end - m_start)) / float(m_fade_out_end - m_hold_end)))
                else:
                    m_fade = 0.0

                if m_fade > 0.001:
                    m_eff_alpha = (map_alpha * m_fade)[:, :, None]
                    frame = (frame.astype(np.float32) * (1.0 - m_eff_alpha) + map_bgr.astype(np.float32) * m_eff_alpha).astype(np.uint8)

            # Lower-third HUD display: 6s fade-in/fade-out for documentary, solid for tour itineraries
            if hud_bgr is not None and hud_alpha is not None:
                display_dur = float(lower_third_hud.get("display_duration", 6.0 if lower_third_hud.get("is_documentary") else 0.0))
                # When a chapter card is displayed, start the lower-third as the chapter slate fades out
                hud_delay = int(fps * 3.0) if (chap_bgr is not None) else 0
                adj_i = i - hud_delay

                if adj_i < 0:
                    fade = 0.0
                else:
                    if display_dur > 0:
                        fade_in_frames = max(6, int(fps * 0.5))
                        fade_out_start = int((display_dur - 0.5) * fps)
                        fade_out_frames = max(6, int(fps * 0.5))
                    elif duration_seconds <= 15.0:
                        fade_in_frames = min(12, max(6, int(fps * 0.4)))
                        fade_out_start = total_frames + 999
                        fade_out_frames = 20
                    else:
                        fade_in_frames = min(12, max(6, int(fps * 0.4)))
                        fade_out_start = int(12.5 * fps)
                        fade_out_frames = 20

                    if adj_i < fade_in_frames:
                        fade = adj_i / max(1.0, float(fade_in_frames))
                    elif adj_i < fade_out_start:
                        fade = 1.0
                    elif adj_i < fade_out_start + fade_out_frames:
                        fade = max(0.0, 1.0 - (adj_i - fade_out_start) / float(fade_out_frames))
                    else:
                        fade = 0.0

                if fade > 0.001:
                    eff_alpha = (hud_alpha * fade)[:, :, None]
                    frame = (frame.astype(np.float32) * (1.0 - eff_alpha) + hud_bgr.astype(np.float32) * eff_alpha).astype(np.uint8)

            # Fact Badge: 4.5s smooth sine fade-in/fade-out in middle-right quadrant
            if fact_bgr is not None and fact_alpha is not None:
                f_start = int(fps * 3.5)
                f_fade_in = max(6, int(fps * 0.5))
                f_hold_end = int(fps * 7.5)
                f_fade_out_end = int(fps * 8.2)
                adj_f = i - f_start
                if adj_f < 0:
                    f_fade = 0.0
                elif adj_f < f_fade_in:
                    f_fade = 0.5 * (1.0 - np.cos(np.pi * adj_f / float(f_fade_in)))
                elif adj_f < (f_hold_end - f_start):
                    f_fade = 1.0
                elif adj_f < (f_fade_out_end - f_start):
                    f_fade = 0.5 * (1.0 + np.cos(np.pi * (adj_f - (f_hold_end - f_start)) / float(f_fade_out_end - f_hold_end)))
                else:
                    f_fade = 0.0

                if f_fade > 0.001:
                    f_eff_alpha = (fact_alpha * f_fade)[:, :, None]
                    frame = (frame.astype(np.float32) * (1.0 - f_eff_alpha) + fact_bgr.astype(np.float32) * f_eff_alpha).astype(np.uint8)

            # Itinerary QR Code: displayed during the last 4.5s of the scene
            if qr_bgr is not None and qr_alpha is not None:
                q_start = max(0, total_frames - int(fps * 4.5))
                q_fade_in = max(6, int(fps * 0.6))
                adj_q = i - q_start
                if adj_q < 0:
                    q_fade = 0.0
                elif adj_q < q_fade_in:
                    q_fade = 0.5 * (1.0 - np.cos(np.pi * adj_q / float(q_fade_in)))
                else:
                    q_fade = 1.0

                if q_fade > 0.001:
                    q_eff_alpha = (qr_alpha * q_fade)[:, :, None]
                    frame = (frame.astype(np.float32) * (1.0 - q_eff_alpha) + qr_bgr.astype(np.float32) * q_eff_alpha).astype(np.uint8)

            if ffmpeg_proc:
                ffmpeg_proc.stdin.write(frame.tobytes())
            else:
                video_writer.write(frame)
    finally:
        if cap is not None:
            cap.release()
        if ffmpeg_proc:
            ffmpeg_proc.stdin.close()
            ffmpeg_proc.wait()
        elif video_writer:
            video_writer.release()
            # Transcode fallback
            temp_raw = out.parent / f"_raw_{out.stem}.mp4"
            cmd_h264 = [FFMPEG_BIN, "-y", "-i", str(temp_raw), "-c:v", "libx264", "-crf", "24", "-maxrate", "4.5M", "-bufsize", "9M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
            subprocess.run(cmd_h264, capture_output=True, text=True)
            temp_raw.unlink(missing_ok=True)

    if max(target_w, target_h) >= 3840:
        from src.services.video_4k_encoder import ensure_video_4k
        ensure_video_4k(out)
    return out


async def render_perspective_drone_clip(
    image_path: Path | str,
    output_path: Path | str,
    duration_seconds: float = 5.0,
    fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160),
    camera_movement: Optional[str] = None,
    speed_factor: float = 1.0,
    force_rerun: bool = False,
    camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
    choreography: Optional[Union[list, str]] = None,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
    rain: bool = False,
    rain_intensity: str = "light",
    snow: bool = False,
    snow_intensity: str = "medium",
    remove_objects: bool = False,
    remove_object_list: Optional[List[str]] = None,
    interpolation: str = "cubic",
    lower_third_hud: Optional[dict] = None,
    water: bool = False,
    smoke: bool = False,
    clouds: bool = False,
    kinetic_objects: bool = False,
) -> Path:
    """Asynchronously render calm 4K perspective drone shot on a worker thread."""
    return await asyncio.to_thread(
        render_perspective_drone_clip_sync,
        image_path=image_path,
        output_path=output_path,
        duration_seconds=duration_seconds,
        fps=fps,
        target_res=target_res,
        camera_movement=camera_movement,
        speed_factor=speed_factor,
        force_rerun=force_rerun,
        camera_waypoints=camera_waypoints,
        kinetic_micro_zones=kinetic_micro_zones,
        choreography=choreography,
        start_pan=start_pan,
        start_zoom=start_zoom,
        start_tilt=start_tilt,
        curve=curve,
        rain=rain,
        rain_intensity=rain_intensity,
        snow=snow,
        snow_intensity=snow_intensity,
        remove_objects=remove_objects,
        remove_object_list=remove_object_list,
        interpolation=interpolation,
        lower_third_hud=lower_third_hud,
        water=water,
        smoke=smoke,
        clouds=clouds,
        kinetic_objects=kinetic_objects,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Studio 4K Perspective Drone Engine (Sequential & Parallel Choreography, 2s-60s)")
    parser.add_argument("-i", "--input", required=True, help="Input image file or directory")
    parser.add_argument("-o", "--output", required=True, help="Output MP4 file or directory")
    parser.add_argument("-d", "--duration", type=float, default=5.0, help="Shot duration in seconds (2.0 to 60.0)")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")
    parser.add_argument("--movement", default="dollyin", help="Legacy movement name (dollyin, pan_left, etc.)")
    parser.add_argument("--interpolation", choices=["cubic", "lanczos", "linear"], default="cubic", help="Warp interpolation mode (cubic is default/4x faster, lanczos for ultra-fine, linear for maximum speed)")
    parser.add_argument("--start-pan", choices=["center", "left", "right"], default="center")
    parser.add_argument("--start-zoom", choices=["normal", "in"], default="normal")
    parser.add_argument("--start-tilt", choices=["center", "up", "down"], default="center")
    parser.add_argument("--curve", choices=["cosine", "cubic", "linear", "ramp-up", "ramp-down", "whip"], default="cosine")
    parser.add_argument("--rain", action="store_true", help="Add procedural rainfall")
    parser.add_argument("--rain-intensity", choices=["light", "medium", "heavy", "high"], default="light")
    parser.add_argument("--snow", action="store_true", help="Add procedural snowfall")
    parser.add_argument("--snow-intensity", choices=["light", "medium", "heavy", "high"], default="medium")
    parser.add_argument("--remove-objects", action="store_true")
    parser.add_argument("--water", action="store_true", help="Enable procedural specular water shimmer")
    parser.add_argument("--clouds", action="store_true", help="Enable atmospheric cloud drift")
    parser.add_argument("--kinetic-objects", action="store_true", help="Enable micro-kinetic object motion")
    args, unknown = parser.parse_known_args()

    parsed_seq = parse_action_sequence(sys.argv)
    choreo = parsed_seq if parsed_seq else args.movement

    in_p = Path(args.input)
    out_p = Path(args.output)

    if in_p.is_file():
        render_perspective_drone_clip_sync(
            image_path=in_p,
            output_path=out_p,
            duration_seconds=args.duration,
            fps=args.fps,
            choreography=choreo,
            start_pan=args.start_pan,
            start_zoom=args.start_zoom,
            start_tilt=args.start_tilt,
            curve=args.curve,
            rain=args.rain,
            rain_intensity=args.rain_intensity,
            snow=args.snow,
            snow_intensity=args.snow_intensity,
            remove_objects=args.remove_objects,
            water=args.water,
            clouds=args.clouds,
            kinetic_objects=args.kinetic_objects,
        )
        print(f"[Done] Rendered {out_p}")
    elif in_p.is_dir():
        out_p.mkdir(parents=True, exist_ok=True)
        imgs = [f for f in in_p.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
        for img in imgs:
            target = out_p / f"{img.stem}_drone.mp4"
            print(f"Rendering {img.name} -> {target.name}...")
            render_perspective_drone_clip_sync(
                image_path=img,
                output_path=target,
                duration_seconds=args.duration,
                fps=args.fps,
                choreography=choreo,
                start_pan=args.start_pan,
                start_zoom=args.start_zoom,
                start_tilt=args.start_tilt,
                curve=args.curve,
                rain=args.rain,
                rain_intensity=args.rain_intensity,
                snow=args.snow,
                snow_intensity=args.snow_intensity,
                remove_objects=args.remove_objects,
                water=args.water,
                clouds=args.clouds,
                kinetic_objects=args.kinetic_objects,
            )
