"""Tier-0 CPU Perspective Drone & Camera Homography Motion Engine."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import cv2
import imageio_ffmpeg
import numpy as np


def _get_movement_deltas(movement: str) -> Tuple[float, float, float, float]:
    mov = (movement or "slow_drone_forward").lower().strip()
    if any(k in mov for k in ("left", "sweep_left", "pan_left")):
        return 0.05, -0.08, -0.020, 0.0
    elif any(k in mov for k in ("right", "sweep_right", "pan_right")):
        return 0.05, 0.08, 0.020, 0.0
    elif any(k in mov for k in ("up", "tilt_up", "crane", "ascend", "pedestal_up", "reveal")):
        return 0.06, 0.0, 0.030, -0.05
    elif any(k in mov for k in ("out", "pull_back", "zoom_out", "dolly_out")):
        return -0.07, 0.0, -0.020, 0.02
    elif any(k in mov for k in ("orbit", "wrap", "arc")):
        return 0.06, 0.08, 0.025, -0.02
    elif any(k in mov for k in ("descend", "water_skim", "dive")):
        return 0.07, 0.0, -0.020, 0.04
    return 0.065, 0.015, 0.015, -0.015


def _corners_from_deltas(w: int, h: int, zoom_factor: float, pan_track: float, tilt_skew: float, y_shift: float) -> np.ndarray:
    zoom_factor = min(0.085, max(-0.085, zoom_factor))
    x_left_top = w * (zoom_factor + pan_track + tilt_skew)
    x_right_top = w * (1.0 - zoom_factor + pan_track - tilt_skew)
    x_left_bot = w * (zoom_factor * 1.10 + pan_track * 1.05)
    x_right_bot = w * (1.0 - zoom_factor * 1.10 + pan_track * 1.05)
    y_top_row = h * (zoom_factor + y_shift)
    y_bot_row = h * (1.0 - zoom_factor * 1.10 + y_shift * 1.05)
    return np.float32([[x_left_top, y_top_row], [x_right_top, y_top_row], [x_left_bot, y_bot_row], [x_right_bot, y_bot_row]])


def compute_perspective_corners(w: int, h: int, progress: float, movement: str = "slow_drone_forward", speed_factor: float = 1.0) -> np.ndarray:
    """Compute 4 dynamic destination corner coordinates for 3D camera simulation."""
    t = max(0.0, min(1.0, progress))
    easing = (1.0 - (1.0 - t) ** 3) * speed_factor
    dz, dp, dt, dy = _get_movement_deltas(movement)
    return _corners_from_deltas(w, h, dz * easing, dp * easing, dt * easing, dy * easing)


def compute_waypoint_perspective_corners(w: int, h: int, current_sec: float, total_sec: float, waypoints: Optional[list] = None, default_mov: str = "slow_drone_forward", speed_factor: float = 1.0) -> np.ndarray:
    """Compute 4 dynamic destination corners across multi-phase timed camera waypoints."""
    if not waypoints:
        prog = min(1.0, max(0.0, current_sec / max(0.1, total_sec)))
        return compute_perspective_corners(w, h, prog, default_mov, speed_factor)

    norm_wps = []
    for wp in waypoints:
        m = getattr(wp, "motion", None) or (wp.get("motion") if isinstance(wp, dict) else str(wp))
        d = float(getattr(wp, "duration_seconds", 0.0) or (wp.get("duration_seconds", 0.0) if isinstance(wp, dict) else 5.0))
        norm_wps.append((m or default_mov, max(0.5, d)))

    tot_wp_dur = sum(d for _, d in norm_wps) or total_sec
    scale = total_sec / tot_wp_dur
    scaled_wps = [(m, d * scale) for m, d in norm_wps]

    cum_z, cum_p, cum_t, cum_y = 0.0, 0.0, 0.0, 0.0
    elapsed = 0.0
    active_m, active_tau, active_dur = scaled_wps[-1][0], 1.0, scaled_wps[-1][1]

    for m, d in scaled_wps:
        if elapsed <= current_sec <= elapsed + d:
            active_m, active_tau, active_dur = m, min(1.0, max(0.0, (current_sec - elapsed) / d)), d
            break
        dz, dp, dt, dy = _get_movement_deltas(m)
        w_frac = d / total_sec
        cum_z += dz * w_frac
        cum_p += dp * w_frac
        cum_t += dt * w_frac
        cum_y += dy * w_frac
        elapsed += d

    dz, dp, dt, dy = _get_movement_deltas(active_m)
    active_easing = (1.0 - (1.0 - active_tau) ** 3) * speed_factor
    w_active = active_dur / total_sec
    tot_z, tot_p = cum_z + dz * w_active * active_easing, cum_p + dp * w_active * active_easing
    tot_t, tot_y = cum_t + dt * w_active * active_easing, cum_y + dy * w_active * active_easing
    return _corners_from_deltas(w, h, tot_z, tot_p, tot_t, tot_y)


from src.scripts.local_micro_kinetics import (
    prepare_micro_kinetics,
    render_micro_kinetics_frame,
)


def render_perspective_drone_clip_sync(
    image_path: Path | str, output_path: Path | str, duration_seconds: float = 5.0, fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160), camera_movement: str = "slow_drone_forward",
    speed_factor: float = 1.0, force_rerun: bool = False, camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Render high-precision 4K 2.5D perspective drone shot on CPU via subpixel homography with waypoint choreography and micro-kinetics."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        from src.services.ambient_export_service import get_media_duration
        c_dur = get_media_duration(out) or 0.0
        if abs(c_dur - float(duration_seconds)) <= 2.0:
            return out

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot load image for perspective drone shot: {image_path}")

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


def render_perspective_drone_clip_sync(
    image_path: Path | str, output_path: Path | str, duration_seconds: float = 5.0, fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160), camera_movement: str = "slow_drone_forward",
    speed_factor: float = 1.0, force_rerun: bool = False, camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Render high-precision 4K 2.5D perspective drone shot on CPU via subpixel homography with waypoint choreography and micro-kinetics."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        from src.services.ambient_export_service import get_media_duration
        c_dur = get_media_duration(out) or 0.0
        if abs(c_dur - float(duration_seconds)) <= 2.0:
            return out

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot load image for perspective drone shot: {image_path}")

    target_w, target_h = target_res
    img = enhance_image_ultra_clarity(img, target_w, target_h)

    h, w, _ = img.shape
    total_frames = max(24, int(duration_seconds * fps))
    pts_canvas = np.float32([[0, 0], [target_w, 0], [0, target_h], [target_w, target_h]])
    clean_base, prepared_sprites = prepare_micro_kinetics(img, kinetic_micro_zones)

    temp_raw = out.parent / f"_raw_{out.stem}.mp4"
    temp_raw.unlink(missing_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_raw), fourcc, fps, (target_w, target_h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open OpenCV VideoWriter for {temp_raw}")

    try:
        for i in range(total_frames):
            sec = i / float(fps)
            pts_dst = compute_waypoint_perspective_corners(w, h, sec, duration_seconds, camera_waypoints, camera_movement, speed_factor)
            matrix = cv2.getPerspectiveTransform(pts_dst, pts_canvas)
            canvas = render_micro_kinetics_frame(clean_base, prepared_sprites, kinetic_micro_zones, i, total_frames)
            frame = cv2.warpPerspective(canvas, matrix, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
            writer.write(frame)
    finally:
        writer.release()

    # Convert to broadcast H.264 (yuv420p, CRF 15, -tune film, +faststart) for pristine lossless clarity
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    cmd_h264 = [
        ffmpeg_bin, "-y", "-i", str(temp_raw),
        "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "15", "-tune", "film", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ]
    res = subprocess.run(cmd_h264, capture_output=True, text=True, creationflags=flags)
    temp_raw.unlink(missing_ok=True)

    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg H.264 encode failed for {out.name}: {res.stderr[-300:]}")

    return out


async def render_perspective_drone_clip(
    image_path: Path | str,
    output_path: Path | str,
    duration_seconds: float = 5.0,
    fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160),
    camera_movement: str = "slow_drone_forward",
    speed_factor: float = 1.0,
    force_rerun: bool = False,
    camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Asynchronously render 4K perspective drone shot on a worker thread."""
    return await asyncio.to_thread(
        render_perspective_drone_clip_sync,
        image_path,
        output_path,
        duration_seconds,
        fps,
        target_res,
        camera_movement,
        speed_factor,
        force_rerun,
        camera_waypoints,
        kinetic_micro_zones,
    )
