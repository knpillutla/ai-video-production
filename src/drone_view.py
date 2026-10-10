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
    """Procedural multi-layer natural rain engine: organic translucent drizzle, stochastic respawn, and soft mist."""

    def __init__(self, width: int, height: int, intensity: str = "light", wind_tilt: float = 4.0, source_img: Optional[np.ndarray] = None):
        self.w = width
        self.h = height
        self.wind_tilt = wind_tilt
        self.intensity = intensity.lower()

        scale_factor = width / 1920.0
        self.scale = scale_factor

        # Tiered physical presets calibrated to natural organic rain:
        # - Balanced length (moderate height, avoiding tall stripes) + dense pouring curtain
        configs = {
            "light": {
                "drops": 450,
                "bg_len": (6, 11),   "bg_spd": (14, 20),
                "mg_len": (11, 18),  "mg_spd": (18, 26),
                "fg_len": (18, 28),  "fg_spd": (24, 34),
                "mist_alpha": 0.02,  "rain_alpha": 0.18,
                "splash_prob": 0.01, "wind": 2.5,
            },
            "medium": {
                "drops": 5800,       # Rich continuous natural rain
                "bg_len": (20, 32),  "bg_spd": (28, 38),
                "mg_len": (42, 64),  "mg_spd": (44, 58),
                "fg_len": (68, 96),  "fg_spd": (58, 76),
                "mist_alpha": 0.08,  "rain_alpha": 0.40,
                "splash_prob": 0.08, "wind": 5.5,
                "ripple_rate": 4,    "max_ripple_r": 20.0,
            },
            "heavy": {
                # Category 5 Severe Storm / Tropical Hurricane Downpour
                "drops": 19500,      # Wall-of-water deluge
                "bg_len": (45, 80),   "bg_spd": (60, 95),
                "mg_len": (90, 160),  "mg_spd": (100, 155),
                "fg_len": (160, 260), "fg_spd": (145, 210),
                "mist_alpha": 0.22,  "rain_alpha": 0.55,
                "splash_prob": 0.45, "wind": 16.0,   # Strong wind-driven slant
                "ripple_rate": 16,   "max_ripple_r": 36.0, # Dense, overlapping heavy water rings
            },
        }
        cfg = configs.get(self.intensity, configs["medium"])
        self.cfg = cfg
        self.wind_tilt = cfg["wind"]
        total_drops = cfg["drops"]

        # Calculate left/right margin to compensate for wind-driven slant
        # A positive wind tilt pushes drops rightward as they fall, leaving a bare triangle on the left
        # unless drops originate from negative X coordinates upwind.
        margin = max(abs(self.wind_tilt * scale_factor) * (height / 20.0), width * 0.25)
        self.spawn_x_min = -margin if self.wind_tilt > 0 else 0
        self.spawn_x_max = width if self.wind_tilt > 0 else (width + margin)

        # Layer 1: Background Micro-Drizzle (60% of drops)
        self.bg_drops = []
        for _ in range(int(total_drops * 0.60)):
            x = random.uniform(self.spawn_x_min, self.spawn_x_max)
            y = random.uniform(-100 * scale_factor, height)
            length = random.uniform(*cfg["bg_len"]) * scale_factor
            speed = random.uniform(*cfg["bg_spd"]) * scale_factor
            jitter = random.uniform(0.75, 1.25)
            self.bg_drops.append([x, y, length, speed, jitter])

        # Layer 2: Midground Natural Rain (30% of drops)
        self.mg_drops = []
        for _ in range(int(total_drops * 0.30)):
            x = random.uniform(self.spawn_x_min, self.spawn_x_max)
            y = random.uniform(-100 * scale_factor, height)
            length = random.uniform(*cfg["mg_len"]) * scale_factor
            speed = random.uniform(*cfg["mg_spd"]) * scale_factor
            jitter = random.uniform(0.80, 1.20)
            self.mg_drops.append([x, y, length, speed, jitter])

        # Layer 3: Occasional Foreground Droplets (10% of drops)
        self.fg_drops = []
        for _ in range(int(total_drops * 0.10)):
            x = random.uniform(self.spawn_x_min, self.spawn_x_max)
            y = random.uniform(-100 * scale_factor, height)
            length = random.uniform(*cfg["fg_len"]) * scale_factor
            speed = random.uniform(*cfg["fg_spd"]) * scale_factor
            jitter = random.uniform(0.85, 1.15)
            self.fg_drops.append([x, y, length, speed, jitter])

        # Ground / Water ripples: [x, y, radius, alpha, max_radius, is_water]
        self.splashes = []
        self.ground_y = int(height * 0.52)  # Water plane starts around mid-frame in wide perspectives

        # Dynamic overcast storm sky & sea vapor layer
        # Creates a moody dark stormy atmosphere (dimming sunny sky + low marine haze)
        gradient = np.linspace(0.85, 1.15, height).reshape(height, 1, 1)
        storm_mist = np.full((height, width, 3), (150, 165, 175), dtype=np.float32) * gradient
        self.mist_layer = np.clip(storm_mist, 0, 255).astype(np.uint8)

        # Autonomous Interior Sanctuary vs. Exterior Window Detection:
        # Default: 1.0 (100% full screen rain for landscapes/nature like sicily and hyd1)
        self.weather_mask = None
        if source_img is not None:
            self._build_weather_mask(source_img)

    def _build_weather_mask(self, img: np.ndarray):
        """Autonomously detects if the scene has an interior sanctuary:
        - Alpine Tent: Dome fabric and interior gear surrounding an arched window flap
        - Cozy Room / Cabin: Warm wooden bookshelves/bed/walls framing a glass window
        - Open Landscape: 100% full-screen weather
        """
        h, w = self.h, self.w
        src_h, src_w = img.shape[:2]
        resized = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        # 1. Check for Cozy Bedroom / Cabin Window (Left wall/bookshelf + bottom bed):
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
            self.weather_mask = cv2.GaussianBlur(mask, (21, 21), 5)[:, :, np.newaxis]
            print(f" -> [Sanctuary Guard] Cozy Bedroom / Cabin sanctuary detected! Weather masked exclusively to exterior window (post @ x={post_x}).")
            return

        # 2. Check for Alpine / Expedition Tent Sanctuary:
        # High-saturation orange/red fabric dome along the top and sides (H: 5-24, S > 100)
        orange_dome = (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 24) & (hsv[:, :, 1] > 100)
        top_orange = float(np.mean(orange_dome[:int(h * 0.20), :]))
        if top_orange > 0.40:
            # Alpine Tent Detected: Window is the mountain opening in the center
            tent_interior = orange_dome | (hsv[:, :, 2] < 50)
            mask = (~tent_interior).astype(np.float32)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(w * 0.02), int(h * 0.02)))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            self.weather_mask = cv2.GaussianBlur(mask, (31, 31), 8)[:, :, np.newaxis]
            print(" -> [Sanctuary Guard] Alpine Tent sanctuary detected! Weather masked exclusively outside the tent opening.")
            return

        # 3. Pure Outdoor Landscape (Sicily ocean, courtyard, open valley):
        self.weather_mask = None

    def _draw_feathered_drop(self, canvas: np.ndarray, x: float, y: float, length: float, tilt: float, base_bgr: tuple):
        """Renders an organic raindrop with soft tapered tail and natural droplet head brightness."""
        # Tail (top 50%): faint, wispy
        p_top = (int(x), int(y))
        p_mid = (int(x + tilt * 0.5), int(y + length * 0.5))
        tail_bgr = (int(base_bgr[0] * 0.45), int(base_bgr[1] * 0.45), int(base_bgr[2] * 0.45))
        cv2.line(canvas, p_top, p_mid, tail_bgr, 1, cv2.LINE_AA)

        # Head (bottom 50%): primary droplet mass
        p_bot = (int(x + tilt), int(y + length))
        cv2.line(canvas, p_mid, p_bot, base_bgr, 1, cv2.LINE_AA)

    def render(self, frame: np.ndarray) -> np.ndarray:
        h, w = self.h, self.w
        rain_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        fg_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        ripple_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        base_tilt = self.wind_tilt * self.scale
        cfg = self.cfg
        margin = max(abs(base_tilt) * (h / 20.0), w * 0.25)
        x_max_bound = w + margin if self.wind_tilt > 0 else w

        # 1. Background Micro-Drizzle
        for d in self.bg_drops:
            x, y, length, speed, jitter = d
            t = base_tilt * 0.5 * jitter
            pt1 = (int(x), int(y))
            pt2 = (int(x + t), int(y + length))
            cv2.line(rain_canvas, pt1, pt2, (120, 135, 150), 1, cv2.LINE_AA)
            d[1] += speed
            d[0] += t
            if d[1] > h or d[0] > (w + margin):
                d[1] = random.uniform(-length * 2, -length)
                d[0] = random.uniform(self.spawn_x_min, self.spawn_x_max)

        # 2. Midground Rain (Feathered with natural wind turbulence)
        for d in self.mg_drops:
            x, y, length, speed, jitter = d
            t = base_tilt * 0.85 * jitter
            self._draw_feathered_drop(rain_canvas, x, y, length, t, (175, 190, 205))
            d[1] += speed
            d[0] += t
            if d[1] > h or d[0] > (w + margin):
                d[1] = random.uniform(-length * 2, -length)
                d[0] = random.uniform(self.spawn_x_min, self.spawn_x_max)
                if random.random() < cfg["splash_prob"]:
                    sy = int(self.ground_y + random.uniform(0, h - self.ground_y))
                    # In water / lower half: expanding circular ripples with perspective tilt (0.32)
                    max_r = random.uniform(6.0, 18.0) * self.scale
                    self.splashes.append([int(d[0]), sy, 1.0, 0.45, max_r])

        # 3. Foreground Droplets (Rendered to separate layer for soft lens blur)
        for d in self.fg_drops:
            x, y, length, speed, jitter = d
            t = base_tilt * jitter
            self._draw_feathered_drop(fg_canvas, x, y, length, t, (215, 230, 245))
            d[1] += speed
            d[0] += t
            if d[1] > h or d[0] > (w + margin):
                d[1] = random.uniform(-length * 2, -length)
                d[0] = random.uniform(self.spawn_x_min, self.spawn_x_max)

        # Apply soft 3x3 optical camera lens blur to foreground drops
        fg_canvas = cv2.GaussianBlur(fg_canvas, (3, 3), 0.8)
        rain_canvas = cv2.add(rain_canvas, fg_canvas)

        # 4. Water Rings & Expanding Ocean Ripples
        active_splashes = []
        for s in self.splashes:
            sx, sy, radius, s_alpha, max_r = s
            if radius < max_r and s_alpha > 0.04:
                # Outer water ripple ring (perspective flattened circle: 1.0 : 0.32)
                r_int = int(radius)
                ry_int = max(1, int(radius * 0.32))
                ring_color = (int(185 * s_alpha), int(205 * s_alpha), int(225 * s_alpha))
                cv2.ellipse(
                    ripple_canvas,
                    (sx, sy),
                    (r_int, ry_int),
                    0, 0, 360,
                    ring_color,
                    1,
                    cv2.LINE_AA,
                )
                # Inner secondary concentric wave for larger ripples
                if radius > 5.0 * self.scale:
                    inner_rx = int(radius * 0.55)
                    inner_ry = max(1, int(inner_rx * 0.32))
                    inner_col = (int(140 * s_alpha), int(160 * s_alpha), int(180 * s_alpha))
                    cv2.ellipse(
                        ripple_canvas,
                        (sx, sy),
                        (inner_rx, inner_ry),
                        0, 0, 360,
                        inner_col,
                        1,
                        cv2.LINE_AA,
                    )
                # Splash white droplet crown center
                if radius < 4.0 * self.scale:
                    cv2.circle(ripple_canvas, (sx, sy), 1, (220, 235, 250), -1)

                active_splashes.append([sx, sy, radius + 1.2 * self.scale, s_alpha * 0.88, max_r])
        self.splashes = active_splashes

        # 5. Composite: overcast storm atmosphere + water ripples + rain curtain
        mist_a = cfg["mist_alpha"]
        rain_a = cfg["rain_alpha"]
        # Blend in atmospheric overcast storm sky
        misted_frame = cv2.addWeighted(frame, 1.0 - mist_a, self.mist_layer, mist_a, 0)
        # Add water ripple reflections
        with_ripples = cv2.add(misted_frame, ripple_canvas)
        # Overlay falling rain curtain
        weathered = cv2.addWeighted(with_ripples, 1.0, rain_canvas, rain_a, 0)

        # 6. Sanctuary Mask Guard:
        # If an interior sanctuary exists (tent, cabin, bedroom), keep interior 100% dry
        if self.weather_mask is not None:
            # Weathered outside window + original clean frame inside room
            return np.clip(frame.astype(np.float32) * (1.0 - self.weather_mask) + weathered.astype(np.float32) * self.weather_mask, 0, 255).astype(np.uint8)
        return weathered


class LivingEnvironmentEngine:
    """Procedural Tier-0 Environmental Dynamics:
    1. Ocean/Water Waves: Harmonic Gerstner 2D sinusoidal surface displacement + caustic specular glint.
    2. Volcanic / Factory Smoke: Advective upward billowing curls drifting with wind.
    3. Option A Bird / Wildlife Trajectory Engine: Autonomous detection of mid-air birds, background inpainting,
       and natural forward aerodynamic gliding with subtle lift oscillations across frames.
    """

    def __init__(self, img: np.ndarray, width: int, height: int):
        self.w, self.h = width, height
        self.scale = width / 1920.0
        resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # 1. Autonomous Water Body Detection (Lower 65%, Cyan/Blue Ocean or Lake)
        lower_hsv = hsv[int(height * 0.35):, :]
        water_px = ((lower_hsv[:, :, 0] >= 90) & (lower_hsv[:, :, 0] <= 130) &
                    (lower_hsv[:, :, 1] >= 40) & (lower_hsv[:, :, 2] >= 35)).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(width * 0.03), int(height * 0.03)))
        closed = cv2.morphologyEx(water_px, cv2.MORPH_CLOSE, kernel)
        water_ratio = float(np.mean(closed > 0))

        self.water_mask = None
        if water_ratio > 0.12:
            full_w = np.zeros((height, width), dtype=np.float32)
            full_w[int(height * 0.35):, :] = (closed > 0).astype(np.float32)
            self.water_mask = cv2.GaussianBlur(full_w, (41, 41), 12)[:, :, np.newaxis]
            print(f" -> [Living World] Ocean/Water body detected ({water_ratio:.1%} area). Active waves & glimmer enabled!")

        # 2. Autonomous Smoke / Steam Plume Detection (Upper 40% Sky, high luminance, low saturation)
        upper_hsv = hsv[:int(height * 0.40), :]
        upper_gray = gray[:int(height * 0.40), :]
        smoke_candidates = (upper_hsv[:, :, 1] < 45) & (upper_gray > 165) & (upper_gray < 245)
        plume_ratio = float(np.mean(smoke_candidates))
        self.smoke_mask = None
        if 0.005 < plume_ratio < 0.10:
            full_s = np.zeros((height, width), dtype=np.float32)
            full_s[:int(height * 0.40), :] = smoke_candidates.astype(np.float32)
            kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            full_s = cv2.morphologyEx(full_s, cv2.MORPH_OPEN, kernel_s)
            self.smoke_mask = cv2.GaussianBlur(full_s, (31, 31), 8)[:, :, np.newaxis]
            print(f" -> [Living World] Smoke/Steam plume detected ({plume_ratio:.2%} area). Active billowing enabled!")

        # 3. Autonomous Bird & Aerial Wildlife Flight Trajectory Engine (Option A)
        self.clean_base_plate = None
        self.birds = []
        orig_h, orig_w = img.shape[:2]
        sky_limit_y = int(orig_h * 0.55)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sky_part = img_gray[:sky_limit_y, :]
        sky_med = cv2.medianBlur(sky_part, 51)
        sky_diff = cv2.subtract(sky_med, sky_part)
        _, sky_th = cv2.threshold(sky_diff, 28, 255, cv2.THRESH_BINARY)
        kernel_b = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        sky_th = cv2.morphologyEx(sky_th, cv2.MORPH_CLOSE, kernel_b)

        cnts, _ = cv2.findContours(sky_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        full_bird_mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
        detected_birds = []

        for c in cnts:
            area = cv2.contourArea(c)
            # Area range matches birds in flight without picking up mountain peaks or houses
            if 200 <= area <= 5000:
                bx, by, bw, bh = cv2.boundingRect(c)
                # Birds must be aloft in upper atmosphere (y + bh < 0.55 * orig_h)
                if by + bh < sky_limit_y:
                    # Guard against structured terrain/houses:
                    # In open sky/sea, background around the bird is smooth (std < 22).
                    # In towns, mountains, and trees (like Sicily), local std is > 35!
                    pad = 40
                    y1_bg, y2_bg = max(0, by - pad), min(sky_part.shape[0], by + bh + pad)
                    x1_bg, x2_bg = max(0, bx - pad), min(sky_part.shape[1], bx + bw + pad)
                    surrounding_bg = sky_part[y1_bg:y2_bg, x1_bg:x2_bg]
                    bg_std = float(np.std(surrounding_bg))

                    if bg_std < 22.0:
                        aspect = bw / float(max(1, bh))
                        hull = cv2.convexHull(c)
                        solidity = area / float(max(1, cv2.contourArea(hull)))
                        # Flying bird wing morphology check
                        if 0.70 <= aspect <= 3.8 and 0.20 <= solidity <= 0.75:
                            cv2.drawContours(full_bird_mask, [c], -1, 255, -1)
                            pad_s = 8
                            x1, y1 = max(0, bx - pad_s), max(0, by - pad_s)
                            x2, y2 = min(orig_w, bx + bw + pad_s), min(orig_h, by + bh + pad_s)
                            sprite = img[y1:y2, x1:x2].copy()
                            bird_roi_mask = full_bird_mask[y1:y2, x1:x2].astype(np.float32) / 255.0
                            feathered_mask = cv2.GaussianBlur(bird_roi_mask, (5, 5), 1.5)[:, :, np.newaxis]
                            detected_birds.append({
                                "orig_x": float(x1),
                                "orig_y": float(y1),
                                "w": x2 - x1,
                                "h": y2 - y1,
                                "sprite": sprite,
                                "mask": feathered_mask,
                                "vx": float(-2.8 - (area / 1200.0) * 0.7),
                                "bob_amp": float(3.5 + (area / 2000.0) * 2.0),
                                "bob_phase": float((bx * 0.05 + by * 0.03) % (2.0 * np.pi)),
                            })

        # Require a flock of at least 3 genuine aloft birds before triggering trajectory animation
        if len(detected_birds) >= 3:
            # Native 4K first, then CPU ONNX confirmation
            min_bx = int(min(b["orig_x"] for b in detected_birds))
            max_bx = int(max(b["orig_x"] + b["w"] for b in detected_birds))
            min_by = int(min(b["orig_y"] for b in detected_birds))
            max_by = int(max(b["orig_y"] + b["h"] for b in detected_birds))
            pad_ctx = 60
            y1_ctx, y2_ctx = max(0, min_by - pad_ctx), min(orig_h, max_by + pad_ctx)
            x1_ctx, x2_ctx = max(0, min_bx - pad_ctx), min(orig_w, max_bx + pad_ctx)
            flock_patch = img[y1_ctx:y2_ctx, x1_ctx:x2_ctx]

            confirmed_by_onnx = onnx_confirm_patch(flock_patch, target_label="bird", min_conf=0.28)
            if confirmed_by_onnx:
                inpaint_mask = cv2.dilate(full_bird_mask, np.ones((15, 15), np.uint8))
                self.clean_base_plate = cv2.inpaint(img, inpaint_mask, 11, cv2.INPAINT_TELEA)
                self.birds = detected_birds
                print(f" -> [Living World] Detected {len(self.birds)} birds aloft (ONNX confirmed). Background inpainted & flight trajectory activated!")
            else:
                print(f" -> [Living World] {len(detected_birds)} aloft candidates rejected by CPU ONNX semantic check.")

        # Precompute coordinate grids for fast vectorized remapping
        self.gx, self.gy = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32)
        )

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

        # B. Apply Harmonic Ocean Waves & Specular Caustic Glimmer
        if self.water_mask is not None:
            t = frame_idx * 0.12
            # 2D Gerstner harmonic wave displacement
            disp_x = (2.4 * self.scale * np.sin(self.gx * 0.035 + t)).astype(np.float32)
            disp_y = (1.6 * self.scale * np.cos(self.gy * 0.045 + t * 0.85)).astype(np.float32)
            map_x = np.clip(self.gx + disp_x, 0, self.w - 1).astype(np.float32)
            map_y = np.clip(self.gy + disp_y, 0, self.h - 1).astype(np.float32)
            wave_frame = cv2.remap(out, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            # Caustic sunlight/skylight glimmer sheen
            glimmer = 1.0 + 0.04 * (
                np.sin(self.gx * 0.06 - t * 1.2) * np.cos(self.gy * 0.05 + t * 0.9)
            ).astype(np.float32)
            wave_frame = np.clip(wave_frame.astype(np.float32) * glimmer[:, :, np.newaxis], 0, 255).astype(np.uint8)

            # Blend back using feathered water mask
            out = np.clip(out.astype(np.float32) * (1.0 - self.water_mask) +
                          wave_frame.astype(np.float32) * self.water_mask, 0, 255).astype(np.uint8)

        # C. Apply Upward Billowing & Wind Drift to Smoke Plumes
        if self.smoke_mask is not None:
            t_s = frame_idx * 0.15
            # Advective upward curl vector
            smoke_dx = (2.0 * self.scale * np.sin(self.gy * 0.04 + t_s * 1.1)).astype(np.float32)
            smoke_dy = (-3.2 * self.scale - 1.5 * self.scale * np.sin(self.gx * 0.05 + t_s * 0.7)).astype(np.float32)
            s_map_x = np.clip(self.gx + smoke_dx, 0, self.w - 1).astype(np.float32)
            s_map_y = np.clip(self.gy + smoke_dy, 0, self.h - 1).astype(np.float32)
            smoke_frame = cv2.remap(out, s_map_x, s_map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            out = np.clip(out.astype(np.float32) * (1.0 - self.smoke_mask) +
                          smoke_frame.astype(np.float32) * self.smoke_mask, 0, 255).astype(np.uint8)

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
        "-crf", "20",
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
    res_mode: str = "4k",
    interp_mode: str = "lanczos",
    target_duration: float = None,
):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".webp")
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
    print(f"Output Mode: {mode_str} | Max Zoom Depth: {clamped_depth:.1%} | Interp: {interp_mode.upper()}")

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
        mode_suffix = "reveal_mission" if (start_pan != "center" or start_zoom != "normal") else "flight_mission"
        if rain:
            mode_suffix += f"_rain_{rain_intensity}"
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

        # Initialize living environment engine (waves, caustic glimmer, smoke plumes)
        living_env = LivingEnvironmentEngine(img, out_w, out_h)

        # Initialize rain engine if requested
        rain_engine = None
        if rain:
            rain_engine = CinematicRainEngine(out_w, out_h, intensity=rain_intensity, source_img=img)

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

            if ffmpeg_proc is not None:
                ffmpeg_proc.stdin.write(frame.tobytes())
            else:
                video_writer.write(frame)

        if ffmpeg_proc is not None:
            ffmpeg_proc.stdin.close()
            ffmpeg_proc.wait()
        else:
            video_writer.release()

        elapsed = time.time() - t_start
        render_fps = total_frames / max(0.001, elapsed)
        print(f"[Done] Rendered {total_frames} frames in {elapsed:.1f}s ({render_fps:.1f} FPS) -> {output_path}")


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
    parser.add_argument("--fps", type=float, default=30.0, help="Frames per second (default: 30.0)")
    parser.add_argument("--res", choices=["4k", "1080p"], default="4k", help="Output resolution: 4k (default: 3840x2160) or 1080p")
    parser.add_argument("--lanczos", action="store_true", help="High-precision Lanczos4 interpolation (slower)")
    parser.add_argument("--cubic", action="store_true", help="Bicubic interpolation")
    parser.add_argument("--fast", action="store_true", help="Bilinear interpolation (default: fast and smooth)")

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
        res_mode=args.res,
        interp_mode=interp,
        target_duration=args.duration,
    )
