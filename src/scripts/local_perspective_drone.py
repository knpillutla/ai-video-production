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


def compute_perspective_corners(
    w: int,
    h: int,
    progress: float,
    movement: str = "slow_drone_forward",
    speed_factor: float = 1.0,
) -> np.ndarray:
    """Compute 4 dynamic destination corner coordinates for 3D camera simulation."""
    # Cubic Ease-Out: Organic deceleration matching physical drone flight
    t = max(0.0, min(1.0, progress))
    easing = (1.0 - (1.0 - t) ** 3) * speed_factor

    mov = movement.lower().strip()
    if any(k in mov for k in ("left", "sweep_left", "pan_left")):
        # Drone sweeping left across facade with yaw banking
        zoom_factor = 0.04 * easing
        pan_track = -0.06 * easing
        tilt_skew = -0.020 * easing
        y_shift = 0.0
    elif any(k in mov for k in ("right", "sweep_right", "pan_right")):
        # Drone sweeping right across facade with yaw banking
        zoom_factor = 0.04 * easing
        pan_track = 0.06 * easing
        tilt_skew = 0.020 * easing
        y_shift = 0.0
    elif any(k in mov for k in ("up", "tilt_up", "crane", "ascend", "pedestal_up")):
        # Drone vertical ascent / crane pedestal
        zoom_factor = 0.04 * easing
        pan_track = 0.0
        tilt_skew = 0.030 * easing
        y_shift = -0.05 * easing
    elif any(k in mov for k in ("out", "pull_back", "reveal", "zoom_out")):
        # Drone reveal pull-back: starts closer and recedes backward
        reverse_t = 1.0 - easing
        zoom_factor = 0.08 * reverse_t
        pan_track = 0.0
        tilt_skew = 0.010 * reverse_t
        y_shift = 0.0
    else:
        # Default: slow_drone_forward / dolly_in approach with architectural pitch
        zoom_factor = 0.075 * easing
        pan_track = 0.015 * easing
        tilt_skew = 0.018 * easing
        y_shift = 0.0

    x_left_top = w * (zoom_factor + pan_track + tilt_skew)
    x_right_top = w * (1.0 - zoom_factor + pan_track - tilt_skew)
    x_left_bot = w * (zoom_factor + pan_track)
    x_right_bot = w * (1.0 - zoom_factor + pan_track)

    y_top_row = h * (zoom_factor + y_shift)
    y_bot_row = h * (1.0 - zoom_factor + y_shift)

    pts_dst = np.float32([
        [x_left_top, y_top_row],
        [x_right_top, y_top_row],
        [x_left_bot, y_bot_row],
        [x_right_bot, y_bot_row],
    ])
    return pts_dst


def render_perspective_drone_clip_sync(
    image_path: Path | str,
    output_path: Path | str,
    duration_seconds: float = 5.0,
    fps: int = 24,
    target_res: Tuple[int, int] = (3840, 2160),
    camera_movement: str = "slow_drone_forward",
    speed_factor: float = 1.0,
    force_rerun: bool = False,
) -> Path:
    """Render high-precision 4K 2.5D perspective drone shot on CPU via subpixel homography."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        return out

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot load image for perspective drone shot: {image_path}")

    # Scale source image to target resolution if needed
    target_w, target_h = target_res
    if img.shape[1] != target_w or img.shape[0] != target_h:
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    h, w, _ = img.shape
    total_frames = max(24, int(duration_seconds * fps))
    pts_canvas = np.float32([
        [0, 0],
        [target_w, 0],
        [0, target_h],
        [target_w, target_h],
    ])

    temp_raw = out.parent / f"_raw_{out.stem}.mp4"
    temp_raw.unlink(missing_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_raw), fourcc, fps, (target_w, target_h))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open OpenCV VideoWriter for {temp_raw}")

    try:
        for i in range(total_frames):
            prog = i / float(total_frames - 1) if total_frames > 1 else 0.0
            pts_dst = compute_perspective_corners(w, h, prog, camera_movement, speed_factor)
            matrix = cv2.getPerspectiveTransform(pts_dst, pts_canvas)
            frame = cv2.warpPerspective(img, matrix, (target_w, target_h), flags=cv2.INTER_CUBIC)
            writer.write(frame)
    finally:
        writer.release()

    # Convert to broadcast H.264 (yuv420p, CRF 18, +faststart) for universal browser playback
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    cmd_h264 = [
        ffmpeg_bin, "-y", "-i", str(temp_raw),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "18", "-pix_fmt", "yuv420p",
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
    )
