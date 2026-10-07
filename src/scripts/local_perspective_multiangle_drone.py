"""Tier-0 CPU Multi-Angle Skyline Drone Engine (Spline Affine Flight)."""

import argparse
import asyncio
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import imageio_ffmpeg
import numpy as np

from src.scripts.local_micro_kinetics import (
    prepare_micro_kinetics,
    render_micro_kinetics_frame,
)


def interpolate_smooth_path(waypoint_frames: np.ndarray, waypoints: list, total_frames: int) -> np.ndarray:
    """Smooth cubic interpolation supporting both SciPy and pure NumPy environments."""
    try:
        from scipy.interpolate import CubicSpline
        return CubicSpline(waypoint_frames, waypoints, bc_type="clamped")(np.arange(total_frames))
    except ImportError:
        raw = np.interp(np.arange(total_frames), waypoint_frames, waypoints)
        kernel_len = max(5, int(total_frames * 0.08))
        if kernel_len % 2 == 0:
            kernel_len += 1
        kernel = np.hanning(kernel_len)
        kernel = kernel / kernel.sum()
        padded = np.pad(raw, kernel_len // 2, mode="edge")
        return np.convolve(padded, kernel, mode="valid")[:total_frames]


def generate_cinematic_path(img_shape: tuple, total_frames: int, num_waypoints: int = 6):
    """Generates the varied, multi-angle spline flight path from drone_skyline_mission."""
    min_scale, max_scale = 0.65, 0.90
    waypoint_frames = np.linspace(0, total_frames - 1, num_waypoints)

    scales = [random.uniform(0.75, max_scale)]
    x_pcts = [random.uniform(0.20, 0.40)]
    y_pcts = [random.uniform(0.35, 0.65)]

    for _ in range(num_waypoints - 1):
        next_scale = random.uniform(min_scale, max_scale)
        while abs(next_scale - scales[-1]) < 0.10:
            next_scale = random.uniform(min_scale, max_scale)

        scales.append(next_scale)
        x_pcts.append(random.uniform(0.15, 0.85))
        y_pcts.append(random.uniform(0.25, 0.75))

    smooth_scales = np.clip(interpolate_smooth_path(waypoint_frames, scales, total_frames), min_scale, max_scale)
    smooth_x = np.clip(interpolate_smooth_path(waypoint_frames, x_pcts, total_frames), 0.12, 0.88)
    smooth_y = np.clip(interpolate_smooth_path(waypoint_frames, y_pcts, total_frames), 0.20, 0.80)

    return smooth_scales, smooth_x, smooth_y


def precompute_drone_affine_matrices(
    img_shape: tuple, scales: np.ndarray, x_pcts: np.ndarray, y_pcts: np.ndarray, output_size: tuple = (3840, 2160)
) -> list:
    """Precomputes sub-pixel affine transformation matrices for all frames in milliseconds."""
    h, w = img_shape[:2]
    target_w, target_h = output_size
    target_aspect = target_w / target_h

    dst_pts = np.array([[0.0, 0.0], [float(target_w), 0.0], [0.0, float(target_h)]], dtype=np.float32)

    matrices = []
    for scale, cx_pct, cy_pct in zip(scales, x_pcts, y_pcts):
        crop_h = h * scale
        crop_w = crop_h * target_aspect
        if crop_w > w:
            crop_w = w
            crop_h = crop_w / target_aspect

        center_x = w * cx_pct
        center_y = h * cy_pct
        half_w, half_h = crop_w / 2.0, crop_h / 2.0

        center_x = max(half_w, min(w - half_w, center_x))
        center_y = max(half_h, min(h - half_h, center_y))

        src_pts = np.array(
            [
                [center_x - half_w, center_y - half_h],
                [center_x + half_w, center_y - half_h],
                [center_x - half_w, center_y + half_h],
            ],
            dtype=np.float32,
        )
        matrix = cv2.getAffineTransform(src_pts, dst_pts)
        matrices.append(matrix)

    return matrices


def render_multiangle_drone_clip_sync(
    image_path: Path | str, output_path: Path | str, duration_seconds: float = 60.0, fps: int = 30,
    target_res: Tuple[int, int] = (3840, 2160), force_rerun: bool = False,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Render 4K multi-angle skyline drone shot on CPU via pure affine gimbal flight with broadcast FFmpeg."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        return out

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot load image for multi-angle drone shot: {image_path}")

    target_w, target_h = target_res
    total_frames = max(30, int(duration_seconds * fps))
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

    scales, x_pcts, y_pcts = generate_cinematic_path(clean_base.shape, total_frames)
    affine_matrices = precompute_drone_affine_matrices(clean_base.shape, scales, x_pcts, y_pcts, output_size=target_res)

    temp_raw = out.parent / f"_raw_{out.stem}.mp4"
    temp_raw.unlink(missing_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_raw), fourcc, fps, (target_w, target_h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open OpenCV VideoWriter for {temp_raw}")

    try:
        for i in range(total_frames):
            canvas = render_micro_kinetics_frame(clean_base, prepared_sprites, kinetic_micro_zones, i, total_frames, snow_engine=snow_engine) if has_micro else clean_base
            frame = cv2.warpAffine(canvas, affine_matrices[i], (target_w, target_h), flags=cv2.INTER_CUBIC)
            writer.write(frame)
    finally:
        writer.release()

    # Broadcast H.264 encode via FFmpeg (yuv420p, CRF 17, -tune film, +faststart)
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    cmd_h264 = [
        ffmpeg_bin, "-y", "-i", str(temp_raw),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-tune", "film",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ]
    res = subprocess.run(cmd_h264, capture_output=True, text=True, creationflags=flags)
    temp_raw.unlink(missing_ok=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed for {out.name}: {res.stderr[-300:]}")

    return out


async def render_multiangle_drone_clip(
    image_path: Path | str, output_path: Path | str, duration_seconds: float = 60.0, fps: int = 30,
    target_res: Tuple[int, int] = (3840, 2160), force_rerun: bool = False,
    kinetic_micro_zones: Optional[dict] = None,
) -> Path:
    """Asynchronously render 4K multi-angle drone shot on a worker thread."""
    return await asyncio.to_thread(
        render_multiangle_drone_clip_sync,
        image_path, output_path, duration_seconds, fps, target_res, force_rerun, kinetic_micro_zones,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Studio 4K Multi-Angle Skyline Drone Engine")
    parser.add_argument("-i", "--input", required=True, help="Input image path or directory")
    parser.add_argument("-o", "--output", required=True, help="Output MP4 file or directory")
    parser.add_argument("-d", "--duration", type=float, default=60.0, help="Shot duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default 30)")
    args = parser.parse_args()

    in_p = Path(args.input)
    out_p = Path(args.output)
    if in_p.is_file():
        render_multiangle_drone_clip_sync(in_p, out_p, duration_seconds=args.duration, fps=args.fps)
        print(f"[Done] Rendered {out_p}")
    elif in_p.is_dir():
        out_p.mkdir(parents=True, exist_ok=True)
        imgs = [f for f in in_p.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
        for img in imgs:
            target = out_p / f"{img.stem}_multiangle.mp4"
            print(f"Rendering {img.name} -> {target.name}...")
            render_multiangle_drone_clip_sync(img, target, duration_seconds=args.duration, fps=args.fps)
