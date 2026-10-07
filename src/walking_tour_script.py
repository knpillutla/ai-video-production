import os
import argparse
import time
import urllib.request
import cv2
import numpy as np


def ensure_midas_model() -> str:
    """Ensures the lightweight MiDaS v2.1 small ONNX model exists locally (~66 MB)."""
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "midas_small.onnx")

    if not os.path.exists(model_path) or os.path.getsize(model_path) < 10000000:
        url = "https://github.com/isl-org/MiDaS/releases/download/v2_1/model-small.onnx"
        print(f" -> Downloading MiDaS small ONNX model from: {url}")
        urllib.request.urlretrieve(url, model_path)
        print(f" -> Download complete ({os.path.getsize(model_path)} bytes).")

    return model_path


def get_midas_depth(img: np.ndarray, model_path: str) -> np.ndarray:
    """Runs a single-pass CPU depth estimation via OpenCV DNN in ~90ms."""
    net = cv2.dnn.readNetFromONNX(model_path)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    h, w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(
        img, 1.0 / 255.0, (256, 256), mean=(123.675, 116.28, 103.53), swapRB=True, crop=False
    )
    net.setInput(blob)
    output = net.forward()
    raw_depth = output[0]

    # Resize depth map to original image resolution
    depth = cv2.resize(raw_depth, (w, h), interpolation=cv2.INTER_CUBIC)
    # Normalize depth: 1.0 = closest to camera, 0.0 = furthest/sky
    depth_norm = cv2.normalize(depth, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return depth_norm


def detect_vanishing_point(img: np.ndarray) -> tuple:
    """Automatically detects road/path perspective line convergence."""
    small = cv2.resize(img, (960, 540))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=15)

    if lines is None:
        return 0.50, 0.45

    slopes_and_lines = []
    for line in lines:
        x1, y1, x2, y2 = line
        if abs(x2 - x1) < 1e-3:
            continue
        slope = (y2 - y1) / float(x2 - x1)
        if 0.15 < abs(slope) < 3.0:
            slopes_and_lines.append((slope, line))

    intersections = []
    step = max(1, len(slopes_and_lines) // 100)
    sampled = slopes_and_lines[::step]
    for i in range(len(sampled)):
        for j in range(i + 1, min(i + 20, len(sampled))):
            s1, l1 = sampled[i]
            s2, l2 = sampled[j]
            if abs(s1 - s2) > 0.35 and (s1 * s2 < 0):
                A = np.array([[s1, -1.0], [s2, -1.0]])
                b = np.array([s1 * l1[0] - l1[1], s2 * l2[0] - l2[1]])
                try:
                    pt = np.linalg.solve(A, b)
                    if 0.15 * 960 < pt[0] < 0.85 * 960 and 0.20 * 540 < pt[1] < 0.65 * 540:
                        intersections.append(pt)
                except Exception:
                    pass

    if intersections:
        pts = np.array(intersections)
        vpx = float(np.median(pts[:, 0])) / 960.0
        vpy = float(np.median(pts[:, 1])) / 540.0
        return max(0.20, min(0.80, vpx)), max(0.25, min(0.60, vpy))

    return 0.50, 0.45


def render_walking_video(
    img: np.ndarray,
    output_path: str,
    depth_power: np.ndarray,
    vpx: float,
    vpy: float,
    duration_sec: int,
    speed: float,
    interp_flag: int,
    force_4k: bool = False,
):
    """Renders a walking tour video using a 2D depth displacement map."""
    img_h, img_w = img.shape[:2]
    is_4k = force_4k or (img_w >= 2400 or img_h >= 1350)
    target_w, target_h = (3840, 2160) if is_4k else (1920, 1080)
    fps = 30.0
    total_frames = int(duration_sec * fps)

    grid_y, grid_x = np.indices((target_h, target_w), dtype=np.float32)
    grid_x *= img_w / float(target_w)
    grid_y *= img_h / float(target_h)

    # Sample depth map directly at target grid
    if depth_power.shape[:2] != (target_h, target_w):
        depth_sampled = cv2.resize(depth_power, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    else:
        depth_sampled = depth_power

    dx = grid_x - vpx
    dy = grid_y - vpy

    map_x = np.empty((target_h, target_w), dtype=np.float32)
    map_y = np.empty((target_h, target_w), dtype=np.float32)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    max_fwd = min(0.48, 0.28 * max(0.1, speed))
    t_start = time.time()

    for i in range(total_frames):
        fwd = (i / float(max(1, total_frames - 1))) * max_fwd
        scale = 1.0 - (fwd * depth_sampled)
        np.multiply(dx, scale, out=map_x)
        map_x += vpx
        np.multiply(dy, scale, out=map_y)
        map_y += vpy

        frame = cv2.remap(img, map_x, map_y, interp_flag)
        video_writer.write(frame)

    video_writer.release()
    elapsed = time.time() - t_start
    render_fps = total_frames / max(0.001, elapsed)
    print(f" -> Rendered {total_frames} frames in {elapsed:.1f}s ({render_fps:.1f} FPS) -> {output_path}")


def process_walking_tours(
    input_dir: str,
    output_dir: str,
    duration_sec: int,
    speed: float = 1.0,
    engine: str = "both",
    interp_mode: str = "linear",
    force_4k: bool = False,
):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    images = [f for f in os.listdir(input_dir) if f.endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    interp_flag = cv2.INTER_CUBIC if interp_mode == "cubic" else cv2.INTER_LINEAR
    model_path = ensure_midas_model() if engine in ("midas", "both") else None

    print(f"--- Walking Tour Director Active | Engine: {engine.upper()} | Speed: {speed}x ---")

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        img_h, img_w = img.shape[:2]
        vpx_norm, vpy_norm = detect_vanishing_point(img)
        vpx, vpy = float(img_w * vpx_norm), float(img_h * vpy_norm)
        print(f"\n[Processing {img_name}] VP: ({vpx_norm*100:.1f}%, {vpy_norm*100:.1f}%)")

        # 1. MiDaS Neural Depth Engine (Default & Preferred)
        if engine in ("midas", "both"):
            print(" -> Computing MiDaS AI Neural Depth Walk...")
            t0 = time.time()
            midas_norm = get_midas_depth(img, model_path)
            print(f"    Inference completed in {(time.time()-t0)*1000:.1f}ms")
            # Apply gamma curve to focus displacement on foreground & midground
            midas_clamped = np.clip(midas_norm, 0.0, 1.0)
            midas_depth = np.power(midas_clamped, 1.25)
            out_midas = (
                os.path.join(output_dir, f"{stem}_midas_walk.mp4")
                if engine == "both"
                else os.path.join(output_dir, f"{stem}_slow_walk.mp4")
            )
            render_walking_video(
                img, out_midas, midas_depth, vpx, vpy, duration_sec, speed, interp_flag, force_4k=force_4k
            )

        # 2. Geometric Ground Depth Engine (Optional comparison)
        if engine in ("geometric", "both"):
            print(" -> Computing Geometric Ground-Perspective Walk...")
            grid_y, _ = np.indices((img_h, img_w), dtype=np.float32)
            geom_depth = np.maximum(0.0, (grid_y - vpy) / float(max(1.0, img_h - vpy))) ** 1.30
            out_geom = os.path.join(output_dir, f"{stem}_geometric_walk.mp4")
            render_walking_video(
                img, out_geom, geom_depth, vpx, vpy, duration_sec, speed, interp_flag, force_4k=force_4k
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D Walking Tour generator using MiDaS AI Neural Depth.")
    parser.add_argument("-i", "--input", required=True, help="Input folder of high-res images")
    parser.add_argument("-o", "--output", required=True, help="Output folder for MP4 videos")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Video duration in seconds")
    parser.add_argument("-s", "--speed", type=float, default=1.5, help="Walking speed multiplier (default: 1.5)")
    parser.add_argument(
        "--engine",
        default="midas",
        choices=["midas", "geometric", "both"],
        help="Depth engine to run (default: midas)",
    )
    parser.add_argument("--cubic", action="store_true", help="Use cubic interpolation instead of linear")
    parser.add_argument("--4k", dest="force_4k", action="store_true", help="Force 4K UHD (3840x2160) master output")

    args = parser.parse_args()
    interp = "cubic" if args.cubic else "linear"
    process_walking_tours(
        args.input,
        args.output,
        args.duration,
        speed=args.speed,
        engine=args.engine,
        interp_mode=interp,
        force_4k=args.force_4k,
    )
