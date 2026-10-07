import os
import argparse
import time
import random
import cv2
import numpy as np


def interpolate_smooth_path(waypoint_frames: np.ndarray, waypoints: list, total_frames: int) -> np.ndarray:
    """Smooth cubic interpolation supporting both SciPy and pure NumPy environments."""
    try:
        from scipy.interpolate import CubicSpline
        return CubicSpline(waypoint_frames, waypoints, bc_type="clamped")(np.arange(total_frames))
    except ImportError:
        frames_axis = np.arange(total_frames)
        raw = np.interp(frames_axis, waypoint_frames, waypoints)
        kernel_len = max(5, int(total_frames * 0.08))
        if kernel_len % 2 == 0:
            kernel_len += 1
        kernel = np.hanning(kernel_len)
        kernel = kernel / kernel.sum()
        padded = np.pad(raw, kernel_len // 2, mode="edge")
        return np.convolve(padded, kernel, mode="valid")[:total_frames]


def generate_cinematic_path(img_shape: tuple, total_frames: int, num_waypoints: int = 6):
    """Generates a varied, multi-angle random flight path using smooth spline interpolation."""
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


def process_random_tours(input_dir: str, output_dir: str, duration_sec: int, interp_mode: str = "cubic"):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    images = [f for f in os.listdir(input_dir) if f.endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    fps = 30.0
    total_frames = int(duration_sec * fps)

    interp_map = {
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }
    warp_flag = interp_map.get(interp_mode.lower(), cv2.INTER_CUBIC)

    print("--- Fast Stabilized Random Drone Director Active ---")
    print(f"Processing {len(images)} file(s) for {duration_sec}s flight(s) | Mode: {interp_mode.upper()}")

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
        output_path = os.path.join(output_dir, f"{stem}_fast_tour.mp4")

        img = cv2.imread(img_path)
        if img is None:
            continue

        h, w = img.shape[:2]
        is_4k = w >= 3000 or h >= 1800
        output_size = (3840, 2160) if is_4k else (1920, 1080)
        mode_str = "4K UHD (3840x2160)" if is_4k else "Full HD (1920x1080)"
        print(f"\n[Drone Engine] {img_name} ({w}x{h}) -> Output: {mode_str}")

        scales, x_pcts, y_pcts = generate_cinematic_path(img.shape, total_frames)

        # Precompute all affine matrices in milliseconds
        t_pre = time.time()
        matrices = precompute_drone_affine_matrices(img.shape, scales, x_pcts, y_pcts, output_size=output_size)
        print(f" -> Precomputed {len(matrices)} affine matrices in {(time.time() - t_pre)*1000:.1f}ms")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, output_size)

        t_start = time.time()
        print(f" -> Rendering and streaming {total_frames} frames to disk...")

        for i in range(total_frames):
            frame = cv2.warpAffine(img, matrices[i], output_size, flags=warp_flag)
            video_writer.write(frame)

        video_writer.release()
        elapsed = time.time() - t_start
        render_fps = total_frames / max(0.001, elapsed)
        print(f"[Done] Rendered {total_frames} frames in {elapsed:.1f}s ({render_fps:.1f} FPS) -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-speed multi-angle random drone flights via pure OpenCV.")
    parser.add_argument("-i", "--input", required=True, help="Input folder of panoramic images")
    parser.add_argument("-o", "--output", required=True, help="Output folder for MP4 videos")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Video duration in seconds")
    parser.add_argument("--fast", action="store_true", help="Ultra-fast linear interpolation for high-speed rendering")
    parser.add_argument("--lanczos", action="store_true", help="Lanczos4 interpolation for sinc anti-aliasing")

    args = parser.parse_args()
    mode = "linear" if args.fast else ("lanczos" if args.lanczos else "cubic")
    process_random_tours(args.input, args.output, args.duration, interp_mode=mode)
