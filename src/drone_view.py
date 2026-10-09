import os
import sys
import argparse
import time
import subprocess
import cv2
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


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
        "-preset", "fast",
        "-crf", "18",
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
    """Computes normalized progress curve s in [0.0, 1.0] from t in [0.0, 1.0]."""
    if curve == "linear":
        return t
    elif curve == "cosine":
        # Cosine ease-in-out: ultra-smooth, gentle start and stop
        return float(0.5 * (1.0 - np.cos(t * np.pi)))
    else:  # "cubic" default
        return float(t * t * (3.0 - 2.0 * t))


def precompute_compound_flyover_matrices(
    img_shape: tuple,
    dolly_in_frames: int,
    hold_frames: int,
    dolly_out_frames: int,
    output_size: tuple = (3840, 2160),
    end_scale: float = 0.50,
    pitch_tilt: float = 0.12,
    focal_cx_pct: float = 0.50,
    focal_cy_pct: float = 0.52,
    curve: str = "cosine",
) -> list:
    """Precomputes 3D perspective flyover matrices supporting motion, speed easing, and hover-hold."""
    h, w = img_shape[:2]
    target_w, target_h = output_size
    target_aspect = target_w / float(target_h)

    # Calculate wide start crop matching output aspect ratio
    src_aspect = w / float(h)
    if src_aspect > target_aspect:
        start_h = float(h)
        start_w = start_h * target_aspect
    else:
        start_w = float(w)
        start_h = start_w / target_aspect

    start_cx = float(w) / 2.0
    start_cy = float(h) / 2.0

    dst_rect = np.array(
        [
            [0.0, 0.0],
            [float(target_w), 0.0],
            [float(target_w), float(target_h)],
            [0.0, float(target_h)],
        ],
        dtype=np.float32,
    )

    progress_curves = []

    # Phase 1: Dolly-In
    if dolly_in_frames > 0:
        for i in range(dolly_in_frames):
            t = i / max(1, dolly_in_frames - 1)
            s = calculate_easing(t, curve)
            progress_curves.append(s)

    # Phase 2: Hold / Hover
    if hold_frames > 0:
        hold_val = 1.0 if (dolly_in_frames > 0 or dolly_out_frames > 0 and dolly_in_frames == 0 and len(progress_curves) == 0) else 0.0
        for _ in range(hold_frames):
            progress_curves.append(hold_val)

    # Phase 3: Dolly-Out
    if dolly_out_frames > 0:
        for i in range(dolly_out_frames):
            t = i / max(1, dolly_out_frames - 1)
            s = 1.0 - calculate_easing(t, curve)
            progress_curves.append(s)

    matrices = []
    for s in progress_curves:
        # Scale smoothly down as drone pushes forward into scene
        current_w = start_w * (1.0 - s * (1.0 - end_scale))
        current_h = current_w / target_aspect

        # Natural camera center: stays locked with the scene's optical center
        cx = start_cx + s * (float(w) * focal_cx_pct - start_cx)
        cy = start_cy + s * (float(h) * focal_cy_pct - start_cy)

        half_w = current_w / 2.0
        half_h = current_h / 2.0

        # Pure rectilinear frame - identical view angle, zero tilt/keystoning distortion
        src_quad = np.array(
            [
                [cx - half_w, cy - half_h],  # Top-Left
                [cx + half_w, cy - half_h],  # Top-Right
                [cx + half_w, cy + half_h],  # Bottom-Right
                [cx - half_w, cy + half_h],  # Bottom-Left
            ],
            dtype=np.float32,
        )

        matrix = cv2.getPerspectiveTransform(src_quad, dst_rect)
        matrices.append(matrix)

    return matrices


def process_drone_flyovers(
    input_dir: str,
    output_dir: str,
    dolly_in_sec: float = 0.0,
    dolly_out_sec: float = 0.0,
    total_duration_sec: float = None,
    fps: float = 30.0,
    depth: float = 0.35,
    speed_factor: float = 1.0,
    curve: str = "cosine",
    res_mode: str = "4k",
    interp_mode: str = "lanczos",
):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".webp")
    images = [f for f in os.listdir(input_dir) if f.lower().endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    active_movement_sec = dolly_in_sec + dolly_out_sec
    if total_duration_sec is not None and total_duration_sec > active_movement_sec:
        hold_sec = total_duration_sec - active_movement_sec
        total_sec = total_duration_sec
    else:
        hold_sec = 0.0
        total_sec = active_movement_sec

    in_frames = int(round(dolly_in_sec * fps))
    hold_frames = int(round(hold_sec * fps))
    out_frames = int(round(dolly_out_sec * fps))
    total_frames = in_frames + hold_frames + out_frames

    # Build descriptive flight labels
    parts = []
    if in_frames > 0:
        parts.append(f"Dolly-In: {dolly_in_sec}s")
    if hold_frames > 0:
        parts.append(f"Hover-Hold: {hold_sec:.1f}s")
    if out_frames > 0:
        parts.append(f"Dolly-Out: {dolly_out_sec}s")

    flight_label = " -> ".join(parts)
    mode_suffix = (
        f"in{int(dolly_in_sec)}s" if in_frames > 0 else ""
    ) + (
        f"_hold{int(hold_sec)}s" if hold_frames > 0 else ""
    ) + (
        f"_out{int(dolly_out_sec)}s" if out_frames > 0 else ""
    )
    mode_suffix = f"dolly_{mode_suffix}" if mode_suffix else "dolly_flight"

    interp_map = {
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }
    warp_flag = interp_map.get(interp_mode.lower(), cv2.INTER_LANCZOS4)

    # Scale depth by user speed multiplier (allows micro-crawls like depth 0.05)
    effective_depth = depth * max(0.05, speed_factor)
    clamped_depth = min(0.65, max(0.02, effective_depth))
    target_end_scale = 1.0 - clamped_depth

    if res_mode.lower() == "1080p":
        target_size = (1920, 1080)
        mode_str = "Full HD (1920x1080)"
    else:
        target_size = (3840, 2160)
        mode_str = "4K UHD (3840x2160)"

    print("--- 3D Perspective Drone Flight Director ---")
    print(f"Mission: {flight_label} | Total: {total_sec:.1f}s ({total_frames} frames @ {fps}fps)")
    print(f"Output Mode: {mode_str} | Travel Depth: {clamped_depth:.1%} | Easing: {curve.upper()} | Interp: {interp_mode.upper()}")

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
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

        t_pre = time.time()
        matrices = precompute_compound_flyover_matrices(
            img_shape=img.shape,
            dolly_in_frames=in_frames,
            hold_frames=hold_frames,
            dolly_out_frames=out_frames,
            output_size=output_size,
            end_scale=target_end_scale,
            curve=curve,
        )
        print(f" -> Precomputed {len(matrices)} 3D perspective matrices in {(time.time() - t_pre)*1000:.1f}ms")

        ffmpeg_proc = get_ffmpeg_writer(output_path, out_w, out_h, fps)
        video_writer = None
        if ffmpeg_proc is None:
            print(" -> Notice: Falling back to OpenCV VideoWriter (mp4v)...")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, output_size)
        else:
            print(" -> Video Encoder: Broadcast H.264 (libx264, CRF 18, zero-pulsing)")

        t_start = time.time()
        print(f" -> Rendering and streaming {total_frames} frames...")

        for i in range(total_frames):
            frame = cv2.warpPerspective(
                img,
                matrices[i],
                output_size,
                flags=warp_flag,
                borderMode=cv2.BORDER_REPLICATE,
            )
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
        description="Cinematic 3D drone camera movement. Requires --dollyin <sec>, --dollyout <sec>, or both."
    )
    parser.add_argument("-i", "--input", required=True, help="Input directory of images")
    parser.add_argument("-o", "--output", required=True, help="Output directory for MP4 videos")
    parser.add_argument("--dollyin", type=float, default=None, help="Duration in seconds for 3D forward flight / push-in")
    parser.add_argument("--dollyout", type=float, default=None, help="Duration in seconds for 3D backward flight / pull-out")
    parser.add_argument("-d", "--duration", "--totalduration", dest="duration", type=float, default=None, 
                        help="Total video duration in seconds. If greater than dolly movement, drone holds/hovers for remainder.")
    parser.add_argument("--depth", type=float, default=0.25, 
                        help="Depth travel scale: 0.05-0.15=micro slow crawl, 0.25=gentle push, 0.40=moderate, 0.55=deep (default: 0.25)")
    parser.add_argument("--speed", type=float, default=1.0, 
                        help="Speed multiplier: e.g. 0.3 for slow cinematic glide, 1.0 standard, 1.5 fast (default: 1.0)")
    parser.add_argument("--curve", choices=["cosine", "cubic", "linear"], default="cosine", 
                        help="Motion easing curve: cosine (default: smoothest glide), cubic, linear (constant velocity)")
    parser.add_argument("--fps", type=float, default=30.0, help="Frames per second (default: 30.0)")
    parser.add_argument("--res", choices=["4k", "1080p"], default="4k", help="Output resolution: 4k (default: 3840x2160) or 1080p")
    parser.add_argument("--fast", action="store_true", help="Fast linear interpolation")
    parser.add_argument("--cubic", action="store_true", help="Bicubic interpolation")

    args = parser.parse_args()

    in_val = args.dollyin if args.dollyin is not None and args.dollyin > 0 else 0.0
    out_val = args.dollyout if args.dollyout is not None and args.dollyout > 0 else 0.0

    if in_val <= 0.0 and out_val <= 0.0:
        parser.error(
            "You must specify at least one movement duration: --dollyin <sec> and/or --dollyout <sec> (e.g., --dollyin 4 --duration 10)."
        )

    interp = "linear" if args.fast else ("cubic" if args.cubic else "lanczos")

    process_drone_flyovers(
        input_dir=args.input,
        output_dir=args.output,
        dolly_in_sec=in_val,
        dolly_out_sec=out_val,
        total_duration_sec=args.duration,
        fps=args.fps,
        depth=args.depth,
        speed_factor=args.speed,
        curve=args.curve,
        res_mode=args.res,
        interp_mode=interp,
    )
