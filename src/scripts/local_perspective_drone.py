"""Tier-0 CPU Perspective Drone & Camera Homography Motion Engine."""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import cv2
import imageio_ffmpeg
import numpy as np

from src.scripts.local_micro_kinetics import (
    prepare_micro_kinetics,
    render_micro_kinetics_frame,
)


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


def _corners_from_deltas(w: int, h: int, zoom: float, pan: float, tilt: float, ys: float) -> np.ndarray:
    zoom = min(0.085, max(-0.085, zoom))
    return np.float32([
        [w * (zoom + pan + tilt), h * (zoom + ys)],
        [w * (1.0 - zoom + pan - tilt), h * (zoom + ys)],
        [w * (zoom * 1.10 + pan * 1.05), h * (1.0 - zoom * 1.10 + ys * 1.05)],
        [w * (1.0 - zoom * 1.10 + pan * 1.05), h * (1.0 - zoom * 1.10 + ys * 1.05)]
    ])


def compute_perspective_corners(w: int, h: int, progress: float, movement: str = "slow_drone_forward", speed: float = 1.0) -> np.ndarray:
    t = max(0.0, min(1.0, progress))
    easing = (1.0 - (1.0 - t) ** 3) * speed
    dz, dp, dt, dy = _get_movement_deltas(movement)
    return _corners_from_deltas(w, h, dz * easing, dp * easing, dt * easing, dy * easing)


def compute_waypoint_perspective_corners(
    w: int, h: int, sec: float, tot: float, waypoints: Optional[list] = None,
    mov: str = "slow_drone_forward", speed: float = 1.0
) -> np.ndarray:
    if not waypoints:
        return compute_perspective_corners(w, h, min(1.0, max(0.0, sec / max(0.1, tot))), mov, speed)
    norm = [(getattr(wp, "motion", None) or (wp.get("motion") if isinstance(wp, dict) else str(wp)) or mov,
             float(getattr(wp, "duration_seconds", 0.0) or (wp.get("duration_seconds", 0.0) if isinstance(wp, dict) else 5.0)))
            for wp in waypoints]
    scale = tot / (sum(d for _, d in norm) or tot)
    wps = [(m, d * scale) for m, d in norm]
    cum_z = cum_p = cum_t = cum_y = el = 0.0
    act_m, act_tau, act_d = wps[-1][0], 1.0, wps[-1][1]
    for m, d in wps:
        if el <= sec <= el + d:
            act_m, act_tau, act_d = m, min(1.0, max(0.0, (sec - el) / d)), d
            break
        dz, dp, dt, dy = _get_movement_deltas(m)
        cum_z += dz * (d / tot); cum_p += dp * (d / tot); cum_t += dt * (d / tot); cum_y += dy * (d / tot); el += d
    dz, dp, dt, dy = _get_movement_deltas(act_m)
    ea = (1.0 - (1.0 - act_tau) ** 3) * speed * (act_d / tot)
    return _corners_from_deltas(w, h, cum_z + dz * ea, cum_p + dp * ea, cum_t + dt * ea, cum_y + dy * ea)


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
    """Render calm, steady 4K perspective drone shot on CPU via subpixel homography with micro-kinetics and broadcast FFmpeg."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        return out

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot load image for perspective drone shot: {image_path}")

    target_w, target_h = target_res
    total_frames = max(24, int(duration_seconds * fps))
    pts_canvas = np.float32([[0, 0], [target_w, 0], [0, target_h], [target_w, target_h]])

    if kinetic_micro_zones is None:
        from src.scripts.local_micro_kinetics import auto_detect_environmental_spec
        kinetic_micro_zones = auto_detect_environmental_spec(img)

    clean_base, prepared_sprites = prepare_micro_kinetics(img, kinetic_micro_zones)
    has_micro = bool(
        kinetic_micro_zones and (
            kinetic_micro_zones.get("celestial_zone") or
            kinetic_micro_zones.get("water_zones") or
            kinetic_micro_zones.get("waterfall_zones") or
            kinetic_micro_zones.get("is_snow")
        )
    )
    snow_engine = None
    if kinetic_micro_zones and kinetic_micro_zones.get("is_snow"):
        from src.scripts.local_micro_kinetics import ProceduralSnowFlakeEngine
        snow_engine = ProceduralSnowFlakeEngine(clean_base.shape[1], clean_base.shape[0])

    temp_raw = out.parent / f"_raw_{out.stem}.mp4"
    temp_raw.unlink(missing_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_raw), fourcc, fps, (target_w, target_h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open OpenCV VideoWriter for {temp_raw}")

    try:
        h, w = clean_base.shape[:2]
        for i in range(total_frames):
            sec = i / float(fps)
            pts_src = compute_waypoint_perspective_corners(w, h, sec, duration_seconds, camera_waypoints, camera_movement, speed_factor)
            matrix = cv2.getPerspectiveTransform(pts_src, pts_canvas)
            canvas = render_micro_kinetics_frame(clean_base, prepared_sprites, kinetic_micro_zones, i, total_frames, snow_engine=snow_engine) if has_micro else clean_base
            frame = cv2.warpPerspective(canvas, matrix, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
            writer.write(frame)
    finally:
        writer.release()

    # Broadcast H.264 encode via FFmpeg (yuv420p, CRF 15, -tune film, +faststart)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    cmd_h264 = [
        ffmpeg_bin, "-y", "-i", str(temp_raw),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-tune", "film",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ]
    res = subprocess.run(cmd_h264, capture_output=True, text=True, creationflags=flags)
    temp_raw.unlink(missing_ok=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed for {out.name}: {res.stderr[-300:]}")

    return out


async def render_perspective_drone_clip(
    image_path: Path | str, output_path: Path | str, duration_seconds: float = 5.0, fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160), camera_movement: str = "slow_drone_forward",
    speed_factor: float = 1.0, force_rerun: bool = False, camera_waypoints: Optional[list] = None,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Asynchronously render calm 4K perspective drone shot on a worker thread."""
    return await asyncio.to_thread(
        render_perspective_drone_clip_sync,
        image_path, output_path, duration_seconds, fps, target_res,
        camera_movement, speed_factor, force_rerun, camera_waypoints, kinetic_micro_zones,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Studio Calm 4K Perspective Drone Engine")
    parser.add_argument("-i", "--input", required=True, help="Input image path or directory")
    parser.add_argument("-o", "--output", required=True, help="Output MP4 file or directory")
    parser.add_argument("-d", "--duration", type=float, default=5.0, help="Shot duration in seconds")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default 24)")
    parser.add_argument("--movement", default="slow_drone_forward", help="Movement style: slow_drone_forward, pan_left, etc.")
    args = parser.parse_args()

    in_p = Path(args.input)
    out_p = Path(args.output)
    if in_p.is_file():
        render_perspective_drone_clip_sync(in_p, out_p, duration_seconds=args.duration, fps=args.fps, camera_movement=args.movement)
        print(f"[Done] Rendered {out_p}")
    elif in_p.is_dir():
        out_p.mkdir(parents=True, exist_ok=True)
        imgs = [f for f in in_p.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
        for img in imgs:
            target = out_p / f"{img.stem}_perspective.mp4"
            print(f"Rendering {img.name} -> {target.name}...")
            render_perspective_drone_clip_sync(img, target, duration_seconds=args.duration, fps=args.fps, camera_movement=args.movement)
