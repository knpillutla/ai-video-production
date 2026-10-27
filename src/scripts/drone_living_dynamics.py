"""Drone Living Dynamics Engine.

Procedural specular water shimmer, atmospheric cloud drift, and micro-kinetic object motion
for local perspective drone shots at $0.00 compute cost.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, List

# Cached YOLO session for micro-kinetic object detection
_YOLO_SESSION = None


def _get_yolo_session():
    global _YOLO_SESSION
    if _YOLO_SESSION is None:
        try:
            import onnxruntime as ort
            model_path = Path(__file__).resolve().parent.parent.parent / "models" / "yolov8n.onnx"
            if model_path.is_file():
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                _YOLO_SESSION = ort.InferenceSession(str(model_path), sess_options=opts, providers=["CPUExecutionProvider"])
            else:
                _YOLO_SESSION = False
        except Exception:
            _YOLO_SESSION = False
    return _YOLO_SESSION if _YOLO_SESSION is not False else None


class SpecularWaterShimmerEngine:
    """Multi-cue water segmentation with dual-harmonic wave displacement and specular caustic shimmer."""

    def __init__(self, img: np.ndarray, width: int, height: int, num_frames: int = 36):
        self.num_frames = num_frames
        self.scale = width / 1920.0
        self.has_water = False
        self.plates: List[np.ndarray] = []

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.magnitude(grad_x, grad_y)
        high_texture = (grad_mag > 55.0).astype(np.uint8)
        hard_terrain = cv2.dilate(high_texture, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))

        c_classic = (hsv[:, :, 0] >= 85) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] >= 18) & (hsv[:, :, 2] >= 18)
        c_turquoise = (hsv[:, :, 0] >= 70) & (hsv[:, :, 0] <= 90) & (hsv[:, :, 1] >= 18) & (hsv[:, :, 2] >= 20)
        c_dark_ocean = (hsv[:, :, 0] >= 80) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] >= 10) & (hsv[:, :, 2] >= 12) & (hsv[:, :, 2] <= 110)
        c_specular = (hsv[:, :, 0] >= 65) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] <= 45) & (hsv[:, :, 2] >= 150)
        water_cand = (c_classic | c_turquoise | c_dark_ocean | c_specular)
        water_cand[:int(height * 0.45), :] = False
        water_cand[hard_terrain > 0] = False

        k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        water_closed = cv2.morphologyEx(water_cand.astype(np.uint8) * 255, cv2.MORPH_CLOSE, k_close)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(water_closed)
        min_area = int(0.005 * width * height)
        water_body = np.zeros_like(water_closed)
        for lbl in range(1, num_labels):
            if stats[lbl, cv2.CC_STAT_AREA] >= min_area:
                water_body[labels == lbl] = 255

        k_buffer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        water_buffered = cv2.erode(water_body, k_buffer)
        dist = cv2.distanceTransform(water_buffered, cv2.DIST_L2, 5)
        max_d = 25.0 * self.scale
        water_mask = np.clip(dist / max_d, 0.0, 1.0).astype(np.float32)
        self.water_mask = water_mask

        if float(np.mean(water_mask > 0.01)) > 0.005:
            ys = np.where(water_mask > 0.005)[0]
            if len(ys) > 0:
                y_min, y_max = int(ys.min()), int(ys.max()) + 1
                self.y_min, self.y_max = y_min, y_max
                roi_h = y_max - y_min
                water_weight_roi = water_mask[y_min:y_max, :]
                inv_water_weight_roi = 1.0 - water_weight_roi
                roi_in = img[y_min:y_max, :]
                gx, gy = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(roi_h, dtype=np.float32))

                for k in range(self.num_frames):
                    t = k * (2.0 * np.pi / self.num_frames)
                    dx = (3.5 * self.scale * np.sin(gx * 0.008 + t) + 1.8 * self.scale * np.sin(gx * 0.020 - 1.3 * t)).astype(np.float32)
                    dy = (2.5 * self.scale * np.cos(gy * 0.010 - t) + 1.2 * self.scale * np.cos(gy * 0.025 + 1.1 * t)).astype(np.float32)
                    wave_roi = cv2.remap(roi_in, gx + dx, gy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                    blended = cv2.blendLinear(roi_in, wave_roi, inv_water_weight_roi, water_weight_roi)
                    self.plates.append(blended)
                self.has_water = True


class AtmosphericCloudDriftEngine:
    """Atmospheric cloud drift with organic harmonic flow and horizon feathering."""

    def __init__(self, img: np.ndarray, width: int, height: int, num_frames: int = 36):
        self.num_frames = num_frames
        self.scale = width / 1920.0
        self.has_clouds = False
        self.plates: List[np.ndarray] = []

        upper_h = int(height * 0.45)
        upper_img = img[:upper_h, :]
        hsv = cv2.cvtColor(upper_img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(upper_img, cv2.COLOR_BGR2GRAY)

        sky_cand = ((hsv[:, :, 1] < 60) & (gray > 130)) | ((hsv[:, :, 0] >= 80) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 2] > 110))
        k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        sky_clean = cv2.morphologyEx(sky_cand.astype(np.uint8) * 255, cv2.MORPH_CLOSE, k_close)
        sky_feather = cv2.GaussianBlur(sky_clean.astype(np.float32) / 255.0, (31, 31), 15)

        if float(np.mean(sky_feather > 0.05)) > 0.10:
            sm_w = 1920
            sm_h = max(16, int(round(upper_h * (1920.0 / width))))
            upper_sm = cv2.resize(upper_img, (sm_w, sm_h), interpolation=cv2.INTER_LINEAR)
            gx_sky, gy_sky = np.meshgrid(np.arange(sm_w, dtype=np.float32), np.arange(sm_h, dtype=np.float32))
            inv_feather = 1.0 - sky_feather

            for k in range(self.num_frames):
                t = k * (2.0 * np.pi / self.num_frames)
                dx = (3.5 * self.scale * np.sin(gx_sky * 0.006 + t) + 1.8 * self.scale * np.sin(t)).astype(np.float32)
                dy = (1.0 * self.scale * np.cos(gy_sky * 0.010 - t)).astype(np.float32)
                cloud_sm = cv2.remap(upper_sm, gx_sky + dx, gy_sky + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                cloud_hi = cv2.resize(cloud_sm, (width, upper_h), interpolation=cv2.INTER_LANCZOS4)
                blended_sky = cv2.blendLinear(upper_img, cloud_hi, inv_feather, sky_feather)
                plate_k = img.copy()
                plate_k[:upper_h, :] = blended_sky
                self.plates.append(plate_k)
            self.has_clouds = True


class MicroKineticObjectEngine:
    """Micro-kinetic object translation for small boats, vehicles, and aircraft with procedural wakes."""

    def __init__(self, img: np.ndarray, width: int, height: int, num_frames: int = 36):
        self.num_frames = num_frames
        self.has_objects = False
        self.plates: List[np.ndarray] = []

        sess = _get_yolo_session()
        if sess is None:
            return

        h, w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (640, 640), swapRB=True, crop=False)
        preds = sess.run(None, {"images": blob})[0][0]
        target_cids = {2: "car", 4: "airplane", 5: "bus", 7: "truck", 8: "boat"}
        boxes, scores, cids = [], [], []
        frame_area = w * h

        for col in range(preds.shape[1]):
            cls_scores = preds[4:, col]
            cid = int(np.argmax(cls_scores))
            score = float(cls_scores[cid])
            if score > 0.28 and cid in target_cids:
                xc, yc, bw, bh = preds[:4, col]
                bx = int((xc - bw / 2) * (w / 640.0))
                by = int((yc - bh / 2) * (h / 640.0))
                bw_px = int(bw * (w / 640.0))
                bh_px = int(bh * (h / 640.0))
                if 0.0001 * frame_area < (bw_px * bh_px) < 0.035 * frame_area:
                    boxes.append([bx, by, bw_px, bh_px])
                    scores.append(score)
                    cids.append(cid)

        if not boxes:
            return

        indices = cv2.dnn.NMSBoxes(boxes, scores, 0.28, 0.45)
        if len(indices) == 0:
            return

        inpaint_mask = np.zeros((h, w), dtype=np.uint8)
        objects = []
        for idx in (indices.flatten() if hasattr(indices, "flatten") else indices):
            bx, by, bw_px, bh_px = boxes[idx]
            cid = cids[idx]
            bx1, by1 = max(0, bx), max(0, by)
            bx2, by2 = min(w, bx + bw_px), min(h, by + bh_px)
            if bx2 <= bx1 or by2 <= by1:
                continue

            patch = img[by1:by2, bx1:bx2].copy()
            inpaint_mask[by1:by2, bx1:bx2] = 255
            vx = 1.0 if bw_px >= bh_px else 0.3
            vy = 0.3 if bw_px >= bh_px else 1.0
            objects.append({"patch": patch, "x": bx1, "y": by1, "w": bx2 - bx1, "h": by2 - by1, "vx": vx, "vy": vy, "is_boat": (cid == 8)})

        if not objects:
            return

        dilated_mask = cv2.dilate(inpaint_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
        clean_bg = cv2.inpaint(img, dilated_mask, 3, cv2.INPAINT_TELEA)

        scale = width / 1920.0
        for k in range(self.num_frames):
            plate_k = clean_bg.copy()
            offset_factor = (k - self.num_frames / 2.0) / self.num_frames
            for obj in objects:
                dx = int(round(offset_factor * 28.0 * scale * obj["vx"]))
                dy = int(round(offset_factor * 12.0 * scale * obj["vy"]))
                ox1 = max(0, min(w - obj["w"], obj["x"] + dx))
                oy1 = max(0, min(h - obj["h"], obj["y"] + dy))
                ox2 = ox1 + obj["w"]
                oy2 = oy1 + obj["h"]

                if obj["is_boat"]:
                    wake_len = int(max(10, obj["w"] * 0.8))
                    wake_x1 = max(0, ox1 - wake_len if obj["vx"] > 0 else ox2)
                    wake_x2 = min(w, ox1 if obj["vx"] > 0 else ox2 + wake_len)
                    wake_y1 = max(0, oy1 - 4)
                    wake_y2 = min(h, oy2 + 4)
                    if wake_x2 > wake_x1 and wake_y2 > wake_y1:
                        wake_roi = plate_k[wake_y1:wake_y2, wake_x1:wake_x2]
                        plate_k[wake_y1:wake_y2, wake_x1:wake_x2] = cv2.addWeighted(wake_roi, 0.82, np.full_like(wake_roi, 235), 0.18, 0)

                plate_k[oy1:oy2, ox1:ox2] = obj["patch"]
            self.plates.append(plate_k)
        self.has_objects = True


class DroneLivingWorld:
    """Unified Orchestrator: Water shimmer, cloud drift, and micro-kinetic objects precomputed into cyclic plates."""

    def __init__(self, img: np.ndarray, width: int, height: int, enable_water: bool = False, enable_clouds: bool = False, enable_objects: bool = False, num_frames: int = 36):
        self.num_frames = num_frames
        self.cycle_plates: List[np.ndarray] = []

        curr = img
        water_eng = SpecularWaterShimmerEngine(curr, width, height, num_frames=num_frames) if enable_water else None
        cloud_eng = AtmosphericCloudDriftEngine(curr, width, height, num_frames=num_frames) if enable_clouds else None
        obj_eng = MicroKineticObjectEngine(curr, width, height, num_frames=num_frames) if enable_objects else None

        has_any = (water_eng and water_eng.has_water) or (cloud_eng and cloud_eng.has_clouds) or (obj_eng and obj_eng.has_objects)
        if has_any:
            for k in range(num_frames):
                frame_k = curr.copy()
                if cloud_eng and cloud_eng.has_clouds:
                    frame_k = cloud_eng.plates[k].copy()
                if water_eng and water_eng.has_water:
                    w_y1, w_y2 = water_eng.y_min, water_eng.y_max
                    frame_k[w_y1:w_y2, :] = water_eng.plates[k]
                if obj_eng and obj_eng.has_objects:
                    frame_k = obj_eng.plates[k]
                self.cycle_plates.append(frame_k)

    def get_source_plate(self, frame_idx: int, default_img: np.ndarray) -> np.ndarray:
        if self.cycle_plates:
            return self.cycle_plates[frame_idx % len(self.cycle_plates)]
        return default_img
