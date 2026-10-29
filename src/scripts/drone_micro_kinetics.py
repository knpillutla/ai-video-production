"""Precision Structure-Tensor, SegFormer Road-Constrained & MiDaS Depth Micro-Kinetic Engine.

Uses local CPU ONNX models (`yolov8n.onnx`, `segformer_b0_ade20k.onnx`, `midas_small.onnx`)
plus 2D Sobel Structure Tensors to constrain vehicles to road surfaces (`ADE20K class 6`),
boats to water (`classes 21/26/60/128`), and scale travel speed by true monocular 3D depth.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

_YOLO_SESSION = None


def get_yolo_session():
    """Load cached YOLOv8n ONNX session on CPU."""
    global _YOLO_SESSION
    if _YOLO_SESSION is None:
        try:
            import onnxruntime as ort
            root = Path(__file__).resolve().parent.parent
            for cand in (root / "models" / "yolov8n.onnx", root.parent / "models" / "yolov8n.onnx"):
                if cand.is_file():
                    opts = ort.SessionOptions()
                    opts.intra_op_num_threads = 2
                    _YOLO_SESSION = ort.InferenceSession(str(cand), sess_options=opts, providers=["CPUExecutionProvider"])
                    break
            else:
                _YOLO_SESSION = False
        except Exception:
            _YOLO_SESSION = False
    return _YOLO_SESSION if _YOLO_SESSION is not False else None


def _estimate_lane_or_flow_vector(
    gray: np.ndarray,
    bx1: int,
    by1: int,
    bx2: int,
    by2: int,
    kind: str,
    seg_map: Optional[np.ndarray] = None,
) -> Tuple[float, float]:
    """Estimate local road lane or water flow tangent unit vector (vx, vy) constrained by SegFormer surface masks."""
    if kind in ("bird", "airplane"):
        return 1.0, -0.18
    h, w = gray.shape[:2]
    pw, ph = bx2 - bx1, by2 - by1
    cx1, cy1 = max(0, bx1 - int(pw * 0.9)), max(0, by1 - int(ph * 0.9))
    cx2, cy2 = min(w, bx2 + int(pw * 0.9)), min(h, by2 + int(ph * 0.9))
    roi = gray[cy1:cy2, cx1:cx2].astype(np.float32)
    if roi.size < 64:
        return (1.0, 0.2) if pw >= ph else (0.3, 0.9)

    mask = np.ones_like(roi, dtype=np.float32)
    ix1, iy1 = bx1 - cx1, by1 - cy1
    ix2, iy2 = ix1 + pw, iy1 + ph
    mask[max(0, iy1) : min(roi.shape[0], iy2), max(0, ix1) : min(roi.shape[1], ix2)] = 0.0

    # Constrain structure tensor to SegFormer road (6, 11, 52) or water (21, 26, 60, 128) pixels when available
    if seg_map is not None:
        seg_roi = seg_map[cy1:cy2, cx1:cx2]
        if kind in ("car", "bus", "truck", "motorcycle", "bicycle"):
            surface_mask = np.isin(seg_roi, (6, 11, 52)).astype(np.float32)
            if float(np.mean(surface_mask)) > 0.10:
                mask *= surface_mask
        elif kind == "boat":
            surface_mask = np.isin(seg_roi, (21, 26, 60, 109, 128)).astype(np.float32)
            if float(np.mean(surface_mask)) > 0.10:
                mask *= surface_mask

    gx = cv2.Sobel(roi, cv2.CV_32F, 1, 0, ksize=3) * mask
    gy = cv2.Sobel(roi, cv2.CV_32F, 0, 1, ksize=3) * mask
    j_xx = float(np.sum(gx * gx))
    j_yy = float(np.sum(gy * gy))
    j_xy = float(np.sum(gx * gy))

    theta_grad = 0.5 * np.arctan2(2.0 * j_xy, j_xx - j_yy + 1e-6)
    tx = -np.sin(theta_grad)
    ty = np.cos(theta_grad)

    cx_center = 0.5 * (bx1 + bx2)
    if kind in ("car", "bus", "truck", "motorcycle", "bicycle", "train"):
        if cx_center < w * 0.48 and ty < 0:
            tx, ty = -tx, -ty
        elif cx_center >= w * 0.48 and ty < 0 and abs(ty) > abs(tx):
            tx, ty = -tx, -ty
    elif tx < 0:
        tx, ty = -tx, -ty

    norm = float(np.hypot(tx, ty)) or 1.0
    return float(tx / norm), float(ty / norm)


def _compute_silhouette_alpha(patch: np.ndarray, seg_patch: Optional[np.ndarray] = None, kind: str = "car") -> np.ndarray:
    """Suppress road/water/sky border background pixels using SegFormer object class + LAB color distance."""
    ph, pw = patch.shape[:2]
    lab = cv2.cvtColor(patch, cv2.COLOR_BGR2LAB).astype(np.float32)
    border = np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]], axis=0)
    bg_med = np.median(border, axis=0)
    bg_mad = np.maximum(8.0, np.median(np.abs(border - bg_med), axis=0) * 1.8)
    dist = np.sqrt(np.sum(((lab - bg_med) / bg_mad) ** 2, axis=2))
    fg_prob = np.clip((dist - 1.1) / 2.2, 0.15, 1.0).astype(np.float32)

    # Boost silhouette accuracy when SegFormer identifies vehicle/person/boat vs road/sky/water
    if seg_patch is not None and seg_patch.shape[:2] == (ph, pw):
        bg_classes = (2, 6, 11, 21, 26, 52, 60, 128)
        not_bg = (~np.isin(seg_patch, bg_classes)).astype(np.float32)
        if 0.12 < float(np.mean(not_bg)) < 0.90:
            fg_prob = np.clip(0.55 * fg_prob + 0.45 * not_bg, 0.05, 1.0)

    wy = np.hanning(ph).astype(np.float32)
    wx = np.hanning(pw).astype(np.float32)
    window = np.clip(np.outer(wy, wx) * 1.75, 0.0, 1.0)
    alpha = cv2.GaussianBlur(fg_prob * window, (5, 5), 1.2)
    return np.clip(alpha, 0.0, 1.0)[:, :, None]


class MicroKineticObjectEngine:
    """Sub-pixel, SegFormer + MiDaS + Structure-Tensor micro-kinetic engine on CPU."""

    def __init__(
        self,
        img: np.ndarray,
        width: int,
        height: int,
        seg_map: Optional[np.ndarray] = None,
        depth_map: Optional[np.ndarray] = None,
    ):
        self.has_objects = False
        self.objects: List[dict] = []
        self.clean_bg: Optional[np.ndarray] = None
        self.w, self.h = width, height
        self.scale = width / 1920.0

        sess = get_yolo_session()
        if sess is None:
            return

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (640, 640), swapRB=True, crop=False)
        preds = sess.run(None, {"images": blob})[0][0]
        target_cids = {
            0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
            4: "airplane", 5: "bus", 6: "train", 7: "truck", 8: "boat", 14: "bird",
        }
        boxes, scores, cids = [], [], []
        frame_area = w * h

        for col in range(preds.shape[1]):
            cls_scores = preds[4:, col]
            cid = int(np.argmax(cls_scores))
            score = float(cls_scores[cid])
            if score > 0.18 and cid in target_cids:
                xc, yc, bw, bh = preds[:4, col]
                bx = int((xc - bw / 2) * (w / 640.0))
                by = int((yc - bh / 2) * (h / 640.0))
                bw_px = int(bw * (w / 640.0))
                bh_px = int(bh * (h / 640.0))
                max_frac = 0.030 if cid == 0 else 0.055
                if 0.00005 * frame_area < (bw_px * bh_px) < max_frac * frame_area:
                    boxes.append([bx, by, bw_px, bh_px])
                    scores.append(score)
                    cids.append(cid)

        if not boxes:
            return
        indices = cv2.dnn.NMSBoxes(boxes, scores, 0.18, 0.45)
        if len(indices) == 0:
            return

        inpaint_mask = np.zeros((h, w), dtype=np.uint8)
        for idx in (indices.flatten() if hasattr(indices, "flatten") else indices):
            bx, by, bw_px, bh_px = boxes[idx]
            cid = cids[idx]
            pad = max(4, int(min(bw_px, bh_px) * 0.15))
            bx1, by1 = max(0, bx - pad), max(0, by - pad)
            bx2, by2 = min(w, bx + bw_px + pad), min(h, by + bh_px + pad)
            if bx2 <= bx1 + 8 or by2 <= by1 + 8:
                continue
            patch = img[by1:by2, bx1:bx2].copy()
            ph, pw = patch.shape[:2]
            kind = target_cids[cid]
            seg_patch = seg_map[by1:by2, bx1:bx2] if seg_map is not None else None
            alpha = _compute_silhouette_alpha(patch, seg_patch=seg_patch, kind=kind)
            vx, vy = _estimate_lane_or_flow_vector(gray, bx1, by1, bx2, by2, kind, seg_map=seg_map)
            depth_factor = float(np.clip(0.65 + 0.70 * float(np.mean(depth_map[by1:by2, bx1:bx2])), 0.60, 1.35)) if depth_map is not None else 1.0
            if kind != "person":
                inpaint_mask[by1:by2, bx1:bx2] = (alpha[:, :, 0] > 0.25).astype(np.uint8) * 255
            self.objects.append({
                "patch": patch, "alpha": alpha, "x": bx1, "y": by1, "w": pw, "h": ph,
                "vx": vx, "vy": vy, "kind": kind, "depth_factor": depth_factor,
            })

        if not self.objects:
            return
        dilated = cv2.dilate(inpaint_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        self.clean_bg = cv2.inpaint(img, dilated, 4, cv2.INPAINT_TELEA) if np.any(dilated > 0) else img.copy()
        self.has_objects = True

    def apply_to_plate(self, plate: np.ndarray, frame_idx: int, total_frames: int = 240) -> None:
        if not self.has_objects or self.clean_bg is None:
            return
        prog = (frame_idx / float(max(1, total_frames))) - 0.5
        for i, obj in enumerate(self.objects):
            x0, y0, pw, ph = obj["x"], obj["y"], obj["w"], obj["h"]
            kind = obj["kind"]
            if kind == "person":
                roi = plate[y0 : y0 + ph, x0 : x0 + pw]
                gx, gy = np.meshgrid(np.arange(pw, dtype=np.float32), np.arange(ph, dtype=np.float32))
                upper_weight = np.clip(1.0 - (gy / float(max(1, ph))), 0.0, 1.0) ** 1.4
                sway_x = (1.6 * self.scale * np.sin(frame_idx * 0.14 + i * 1.7) * upper_weight).astype(np.float32)
                sway_y = (0.7 * self.scale * np.cos(frame_idx * 0.28 + i * 1.3) * upper_weight).astype(np.float32)
                warped = cv2.remap(roi, gx + sway_x, gy + sway_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                alpha = obj["alpha"]
                plate[y0 : y0 + ph, x0 : x0 + pw] = (roi.astype(np.float32) * (1.0 - alpha) + warped.astype(np.float32) * alpha).astype(np.uint8)
                continue

            plate[y0 : y0 + ph, x0 : x0 + pw] = self.clean_bg[y0 : y0 + ph, x0 : x0 + pw]
            base_travel = 36.0 * self.scale if kind in ("car", "bus", "truck", "train", "bird", "airplane") else 22.0 * self.scale
            travel = base_travel * obj.get("depth_factor", 1.0)
            bob = 2.8 * self.scale * np.sin(frame_idx * 0.22 + i) if kind == "bird" else (0.8 * self.scale * np.sin(frame_idx * 0.16 + i) if kind == "boat" else 0.0)
            dx = float(prog * travel * obj["vx"])
            dy = float(prog * travel * obj["vy"] + bob)

            persp_scale = float(np.clip(1.0 + (dy / float(self.h)) * 0.55, 0.90, 1.12))
            ix = int(np.floor(x0 + dx))
            iy = int(np.floor(y0 + dy))
            fx = (x0 + dx) - ix
            fy = (y0 + dy) - iy
            if ix < 0 or iy < 0 or ix + pw > self.w or iy + ph > self.h:
                continue

            M = np.array([
                [persp_scale, 0.0, fx + (1.0 - persp_scale) * (pw * 0.5)],
                [0.0, persp_scale, fy + (1.0 - persp_scale) * (ph * 0.5)],
            ], dtype=np.float32)
            warped_patch = cv2.warpAffine(obj["patch"], M, (pw, ph), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            warped_alpha = cv2.warpAffine(obj["alpha"][:, :, 0], M, (pw, ph), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0)[:, :, None]
            roi = plate[iy : iy + ph, ix : ix + pw].astype(np.float32)
            plate[iy : iy + ph, ix : ix + pw] = (roi * (1.0 - warped_alpha) + warped_patch.astype(np.float32) * warped_alpha).astype(np.uint8)
