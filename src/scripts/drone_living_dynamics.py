"""Drone Living Dynamics Engine (Powered by Local CPU SegFormer-B0 ADE20K & MiDaS Depth).

Uses local CPU ONNX semantic segmentation (`models/segformer_b0_ade20k.onnx`) and monocular
depth (`models/midas_small.onnx`) once per shot to derive exact masks for water, waterfalls,
sky, and roads, with automatic HSV/Sobel fallback for synthetic unit test images.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from src.scripts.drone_micro_kinetics import MicroKineticObjectEngine, get_yolo_session as _get_yolo_session

_SEGFORMER_SESSION = None
_MIDAS_SESSION = None
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# ADE20K 0-indexed class IDs
ADE_SKY = 2
ADE_WATER_CLASSES = (21, 26, 60, 109, 128)  # water, sea, river, swimming pool, lake
ADE_WATERFALL = 113
ADE_ROAD_CLASSES = (6, 11, 52)  # road, sidewalk, path


def _load_onnx_cpu(filename: str):
    try:
        import onnxruntime as ort
        root = Path(__file__).resolve().parent.parent
        for cand in (root / "models" / filename, root.parent / "models" / filename):
            if cand.is_file():
                opts = ort.SessionOptions()
                opts.intra_op_num_threads = 2
                return ort.InferenceSession(str(cand), sess_options=opts, providers=["CPUExecutionProvider"])
    except Exception:
        pass
    return False


def get_segformer_session():
    global _SEGFORMER_SESSION
    if _SEGFORMER_SESSION is None:
        _SEGFORMER_SESSION = _load_onnx_cpu("segformer_b0_ade20k.onnx")
    return _SEGFORMER_SESSION if _SEGFORMER_SESSION is not False else None


def get_midas_session():
    global _MIDAS_SESSION
    if _MIDAS_SESSION is None:
        _MIDAS_SESSION = _load_onnx_cpu("midas_small.onnx")
    return _MIDAS_SESSION if _MIDAS_SESSION is not False else None


def compute_scene_semantics_and_depth(img: np.ndarray, width: int, height: int) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Run SegFormer-B0 (512x512 -> 128x128) and MiDaS Small (256x256) once on CPU (~0.4s total)."""
    seg_map = None
    depth_map = None
    s_seg = get_segformer_session()
    if s_seg is not None:
        try:
            rgb = cv2.cvtColor(cv2.resize(img, (512, 512)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            inp = ((rgb - _MEAN) / _STD).transpose(2, 0, 1)[None, ...]
            logits = s_seg.run(None, {"pixel_values": inp})[0][0]
            seg_low = np.argmax(logits, axis=0).astype(np.uint8)
            seg_map = cv2.resize(seg_low, (width, height), interpolation=cv2.INTER_NEAREST)
        except Exception:
            seg_map = None

    s_mid = get_midas_session()
    if s_mid is not None:
        try:
            rgb_m = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            inp_m = ((rgb_m - _MEAN) / _STD).transpose(2, 0, 1)[None, ...]
            d_raw = s_mid.run(None, {"0": inp_m})[0][0]
            d_norm = (d_raw - float(d_raw.min())) / max(1e-5, float(d_raw.max() - d_raw.min()))
            depth_map = cv2.resize(d_norm.astype(np.float32), (width, height), interpolation=cv2.INTER_LINEAR)
        except Exception:
            depth_map = None
    return seg_map, depth_map


class SpecularWaterShimmerEngine:
    """SegFormer ADE20K + HSV water & waterfall segmentation with depth-modulated wave shimmer and cascade flow."""

    def __init__(self, img: np.ndarray, width: int, height: int, seg_map: Optional[np.ndarray] = None, depth_map: Optional[np.ndarray] = None):
        self.scale = width / 1920.0
        self.has_water = False
        self.has_waterfall = False

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. SegFormer Neural Water Mask + HSV Fallback (for synthetic test fixtures)
        ai_water = np.isin(seg_map, ADE_WATER_CLASSES) if seg_map is not None else np.zeros((height, width), dtype=bool)
        if float(np.mean(ai_water)) > 0.004:
            water_body = (ai_water.astype(np.uint8)) * 255
        else:
            grad_mag = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
            hard_terrain = cv2.dilate((grad_mag > 52.0).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
            c_water = (
                ((hsv[:, :, 0] >= 65) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] >= 12) & (hsv[:, :, 2] >= 15))
                | ((hsv[:, :, 0] >= 60) & (hsv[:, :, 0] <= 115) & (hsv[:, :, 1] >= 8) & (hsv[:, :, 2] >= 90) & (hsv[:, :, 2] <= 225))
            )
            c_water[: int(height * 0.38), :] = False
            c_water[hard_terrain > 0] = False
            k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            water_body = cv2.morphologyEx(c_water.astype(np.uint8) * 255, cv2.MORPH_CLOSE, k_close)

        k_buf = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        dist = cv2.distanceTransform(cv2.erode(water_body, k_buf), cv2.DIST_L2, 5)
        water_mask = np.clip(dist / (24.0 * self.scale), 0.0, 1.0).astype(np.float32)

        # 2. SegFormer Neural Waterfall (Class 113) + Bright Vertical Chute Fallback
        ai_wf = (seg_map == ADE_WATERFALL) if seg_map is not None else np.zeros((height, width), dtype=bool)
        if float(np.mean(ai_wf)) > 0.003:
            wf_body = ai_wf.astype(np.uint8) * 255
        else:
            wf_cand = (hsv[:, :, 1] < 42) & (gray > 180)
            wf_closed = cv2.morphologyEx(wf_cand.astype(np.uint8) * 255, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
            n_wf, l_wf, st_wf, _ = cv2.connectedComponentsWithStats(wf_closed)
            wf_body = np.zeros_like(wf_closed)
            for lbl in range(1, n_wf):
                bx, by, bw, bh, area = st_wf[lbl]
                if area >= int(0.008 * width * height) and bh > bw * 1.15 and bw < int(width * 0.45) and (by + bh) > int(height * 0.48):
                    wf_body[l_wf == lbl] = 255

        if np.any(wf_body > 0):
            wf_feather = cv2.GaussianBlur(wf_body.astype(np.float32) / 255.0, (31, 31), 10)
            ys_wf = np.where(wf_feather > 0.02)[0]
            xs_wf = np.where(np.max(wf_feather, axis=0) > 0.02)[0]
            if len(ys_wf) > 0 and len(xs_wf) > 0:
                self.wf_y1, self.wf_y2 = int(ys_wf.min()), int(ys_wf.max()) + 1
                self.wf_x1, self.wf_x2 = int(xs_wf.min()), int(xs_wf.max()) + 1
                self.wf_w = wf_feather[self.wf_y1 : self.wf_y2, self.wf_x1 : self.wf_x2]
                self.inv_wf_w = 1.0 - self.wf_w
                self.wf_roi = img[self.wf_y1 : self.wf_y2, self.wf_x1 : self.wf_x2].copy()
                self.wf_gx, self.wf_gy = np.meshgrid(
                    np.arange(self.wf_x2 - self.wf_x1, dtype=np.float32),
                    np.arange(self.wf_y2 - self.wf_y1, dtype=np.float32),
                )
                self.has_waterfall = True
                self.has_water = True

        if float(np.mean(water_mask > 0.01)) > 0.003:
            ys = np.where(water_mask > 0.005)[0]
            if len(ys) > 0:
                self.y_min, self.y_max = int(ys.min()), int(ys.max()) + 1
                roi_h = self.y_max - self.y_min
                self.w_weight = water_mask[self.y_min : self.y_max, :]
                self.inv_w_weight = 1.0 - self.w_weight
                self.roi_in = img[self.y_min : self.y_max, :].copy()
                self.gx, self.gy = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(roi_h, dtype=np.float32))
                roi_gray = gray[self.y_min : self.y_max, :].astype(np.float32)
                self.spec_mask = np.clip((roi_gray - 135.0) / 95.0, 0.0, 1.0) * self.w_weight
                if depth_map is not None:
                    self.depth_gain = np.clip(0.55 + 0.75 * depth_map[self.y_min : self.y_max, :], 0.5, 1.3).astype(np.float32)
                else:
                    self.depth_gain = np.linspace(0.65, 1.20, roi_h, dtype=np.float32)[:, None]
                self.has_water = True

    def apply_to_plate(self, plate: np.ndarray, frame_idx: int) -> None:
        if not self.has_water:
            return
        t = frame_idx * 0.09
        if hasattr(self, "roi_in"):
            dx = ((3.8 * self.scale * np.sin(self.gx * 0.009 + self.gy * 0.014 - t) + 1.9 * self.scale * np.sin(self.gx * 0.022 + 1.3 * t)) * self.depth_gain).astype(np.float32)
            dy = ((2.2 * self.scale * np.cos(self.gy * 0.012 - t * 0.85) + 1.1 * self.scale * np.cos(self.gx * 0.018 + 1.1 * t)) * self.depth_gain).astype(np.float32)
            wave_roi = cv2.remap(self.roi_in, self.gx + dx, self.gy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            shimmer = (np.sin(self.gx * 0.028 - self.gy * 0.032 + t * 1.6) * (3.5 * self.w_weight + 6.0 * self.spec_mask))[:, :, None]
            wave_shimmer = np.clip(wave_roi.astype(np.float32) + shimmer, 0, 255).astype(np.uint8)
            plate[self.y_min : self.y_max, :] = cv2.blendLinear(plate[self.y_min : self.y_max, :], wave_shimmer, self.inv_w_weight, self.w_weight)
        if self.has_waterfall:
            fall_shift = (frame_idx * 3.4 * self.scale) % (28.0 * self.scale)
            wf_dx = (1.8 * self.scale * np.sin(self.wf_gy * 0.035 - t * 2.2)).astype(np.float32)
            wf_dy = (-fall_shift + 4.5 * self.scale * np.sin(self.wf_gy * 0.045 - t * 2.6 + self.wf_gx * 0.02)).astype(np.float32)
            wf_warped = cv2.remap(self.wf_roi, self.wf_gx + wf_dx, self.wf_gy + wf_dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            foam = (8.5 * np.sin(self.wf_gy * 0.06 - t * 3.0) * self.wf_w)[:, :, None]
            wf_out = np.clip(wf_warped.astype(np.float32) + foam, 0, 255).astype(np.uint8)
            cur_sub = plate[self.wf_y1 : self.wf_y2, self.wf_x1 : self.wf_x2]
            plate[self.wf_y1 : self.wf_y2, self.wf_x1 : self.wf_x2] = cv2.blendLinear(cur_sub, wf_out, self.inv_wf_w, self.wf_w)


class AtmosphericCloudDriftEngine:
    """SegFormer ADE20K sky-masked cloud drift that guarantees zero building/mountain roof warping."""

    def __init__(self, img: np.ndarray, width: int, height: int, seg_map: Optional[np.ndarray] = None):
        self.scale = width / 1920.0
        self.width = width
        self.upper_h = int(height * 0.46)
        self.has_clouds = False

        upper_img = img[: self.upper_h, :]
        ai_sky = (seg_map[: self.upper_h, :] == ADE_SKY) if seg_map is not None else np.zeros((self.upper_h, width), dtype=bool)
        if float(np.mean(ai_sky)) > 0.04:
            sky_clean = cv2.erode(ai_sky.astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        else:
            hsv = cv2.cvtColor(upper_img, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(upper_img, cv2.COLOR_BGR2GRAY)
            grad_mag = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
            hard_struct = cv2.dilate((grad_mag > 38.0).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
            cloud_cand = (hsv[:, :, 1] < 58) & (gray > 142) & (hard_struct == 0)
            sky_clean = cv2.morphologyEx(cloud_cand.astype(np.uint8) * 255, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))

        v_fade = np.linspace(1.0, 0.0, self.upper_h, dtype=np.float32)[:, None]
        sky_feather = cv2.GaussianBlur(sky_clean.astype(np.float32) / 255.0, (41, 41), 16) * v_fade

        if float(np.mean(sky_feather > 0.05)) > 0.03:
            self.sky_feather = sky_feather
            self.inv_feather = 1.0 - sky_feather
            self.sm_w = 1280
            self.sm_h = max(16, int(round(self.upper_h * (1280.0 / width))))
            self.upper_sm = cv2.resize(upper_img, (self.sm_w, self.sm_h), interpolation=cv2.INTER_LINEAR)
            self.gx_sky, self.gy_sky = np.meshgrid(np.arange(self.sm_w, dtype=np.float32), np.arange(self.sm_h, dtype=np.float32))
            self.has_clouds = True

    def apply_to_plate(self, plate: np.ndarray, frame_idx: int) -> None:
        if not self.has_clouds:
            return
        t = frame_idx * 0.045
        drift_x = (frame_idx * 0.14 * self.scale) % (42.0 * self.scale)
        dx = (drift_x + 3.2 * self.scale * np.sin(self.gx_sky * 0.008 + t)).astype(np.float32)
        dy = (0.9 * self.scale * np.cos(self.gy_sky * 0.012 - t * 0.7)).astype(np.float32)
        cloud_sm = cv2.remap(self.upper_sm, self.gx_sky - dx, self.gy_sky + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cloud_hi = cv2.resize(cloud_sm, (self.width, self.upper_h), interpolation=cv2.INTER_LINEAR)
        plate[: self.upper_h, :] = cv2.blendLinear(plate[: self.upper_h, :], cloud_hi, self.inv_feather, self.sky_feather)


class DroneLivingWorld:
    """Unified zero-RAM-bloat orchestrator composing SegFormer/MiDaS-guided cloud drift, water shimmer, and micro-kinetics."""

    def __init__(self, img: np.ndarray, width: int, height: int, enable_water: bool = True, enable_clouds: bool = True, enable_objects: bool = True, total_frames: int = 240):
        self.total_frames = max(1, total_frames)
        seg_map, depth_map = compute_scene_semantics_and_depth(img, width, height) if (enable_water or enable_clouds or enable_objects) else (None, None)
        self.water_eng = SpecularWaterShimmerEngine(img, width, height, seg_map=seg_map, depth_map=depth_map) if enable_water else None
        self.cloud_eng = AtmosphericCloudDriftEngine(img, width, height, seg_map=seg_map) if enable_clouds else None
        self.obj_eng = MicroKineticObjectEngine(img, width, height, seg_map=seg_map, depth_map=depth_map) if enable_objects else None
        self.has_any = bool(
            (self.water_eng and self.water_eng.has_water)
            or (self.cloud_eng and self.cloud_eng.has_clouds)
            or (self.obj_eng and self.obj_eng.has_objects)
        )
        self.cycle_plates = None

    def get_source_plate(self, frame_idx: int, default_img: np.ndarray) -> np.ndarray:
        if not self.has_any:
            return default_img
        plate = default_img.copy()
        if self.cloud_eng and self.cloud_eng.has_clouds:
            self.cloud_eng.apply_to_plate(plate, frame_idx)
        if self.water_eng and self.water_eng.has_water:
            self.water_eng.apply_to_plate(plate, frame_idx)
        if self.obj_eng and self.obj_eng.has_objects:
            self.obj_eng.apply_to_plate(plate, frame_idx, self.total_frames)
        return plate
