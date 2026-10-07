import os
import argparse
import time
import random
import cv2
import numpy as np


class RealisticTorrentialRainEngine:
    """Authentic cinematic torrential rain engine with high-velocity needle streaks, water alpha, and mist."""

    def __init__(self, width: int, height: int, num_drops: int = 2400, wind_tilt: float = 8.0):
        self.w = width
        self.h = height
        self.wind_tilt = wind_tilt

        # Pre-scale parameters for resolution
        scale_factor = width / 1920.0
        self.scale = scale_factor

        # 1. High-Velocity Foreground Layer (Long, ultra-fast needle streaks rushing past camera)
        self.fg_drops = []
        for _ in range(int(num_drops * 0.35)):
            x = random.uniform(-100 * scale_factor, width + 100 * scale_factor)
            y = random.uniform(-300 * scale_factor, height)
            length = random.uniform(160, 280) * scale_factor
            speed = random.uniform(95, 155) * scale_factor
            thick = random.choice([1, 2])
            self.fg_drops.append([x, y, length, speed, thick])

        # 2. Dense Midground Layer (Driving downpour over chalets & road)
        self.mg_drops = []
        for _ in range(int(num_drops * 0.65)):
            x = random.uniform(-100 * scale_factor, width + 100 * scale_factor)
            y = random.uniform(-300 * scale_factor, height)
            length = random.uniform(90, 170) * scale_factor
            speed = random.uniform(70, 115) * scale_factor
            thick = 1
            self.mg_drops.append([x, y, length, speed, thick])

        # 3. Ground Puddle Splashes
        self.splashes = []
        self.ground_y = int(height * 0.58)

        # 4. Atmospheric Mist Overlay
        self.mist_layer = np.full((height, width, 3), (175, 185, 195), dtype=np.uint8)

    def update_and_render_rain(self, frame: np.ndarray) -> np.ndarray:
        """Applies realistic high-speed needle rain streaks and water alpha onto the frame."""
        h, w = self.h, self.w
        rain_canvas = np.zeros((h, w, 3), dtype=np.uint8)

        tilt = self.wind_tilt * self.scale

        # Draw Midground Rain (Sleek needle streaks, subtle water tone)
        for d in self.mg_drops:
            x, y, length, speed, thick = d
            pt1 = (int(x), int(y))
            pt2 = (int(x + tilt * 0.8), int(y + length))
            cv2.line(rain_canvas, pt1, pt2, (180, 195, 210), thick)
            d[0] = (x + tilt * 0.8) % (w + 100) - 50
            d[1] = (y + speed) % (h + length) - length

            # Micro-splash on wet cobblestone pavement
            if y > self.ground_y and random.random() < 0.02:
                self.splashes.append([int(x), int(y), 1.0, 0.6])

        # Draw Foreground Rain (High-velocity motion-blurred streaks)
        for d in self.fg_drops:
            x, y, length, speed, thick = d
            pt1 = (int(x), int(y))
            pt2 = (int(x + tilt), int(y + length))
            cv2.line(rain_canvas, pt1, pt2, (205, 220, 235), thick)
            d[0] = (x + tilt) % (w + 100) - 50
            d[1] = (y + speed) % (h + length) - length

        # Draw Delicate Micro-Splashes
        active_splashes = []
        for s in self.splashes:
            sx, sy, radius, s_alpha = s
            if radius < (8.0 * self.scale) and s_alpha > 0.05:
                cv2.ellipse(
                    rain_canvas,
                    (sx, sy),
                    (int(radius), int(radius * 0.28)),
                    0,
                    0,
                    360,
                    (190, 205, 220),
                    1,
                )
                active_splashes.append([sx, sy, radius + 1.4 * self.scale, s_alpha - 0.15])
        self.splashes = active_splashes

        # Atmospheric mist veil + translucent water streak blend (Zero white chalk / snow look)
        misted_frame = cv2.addWeighted(frame, 0.96, self.mist_layer, 0.04, 0)
        return cv2.addWeighted(misted_frame, 1.0, rain_canvas, 0.65, 0)


def render_heavy_rain_video(
    image_path: str,
    output_path: str,
    duration_sec: float = 10.0,
    mode: str = "stationary",
    speed: float = 1.2,
    fps: float = 30.0,
    force_4k: bool = True,
):
    """Renders authentic 4K torrential heavy rain video (Stationary or 3D Walking Dolly)."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image: {image_path}")
        return

    h, w = img.shape[:2]
    is_4k = force_4k or (w >= 2400 or h >= 1350)
    target_w, target_h = (3840, 2160) if is_4k else (1920, 1080)
    total_frames = int(duration_sec * fps)

    # Initialize Realistic Torrential Rain Engine
    rain_engine = RealisticTorrentialRainEngine(width=target_w, height=target_h, num_drops=2400, wind_tilt=7.0)

    if mode == "stationary":
        base_img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    else:
        # Rigid 4K Dolly Forward Matrices
        target_aspect = target_w / float(target_h)
        start_scale = 1.00
        push_amount = min(0.38, 0.22 * speed)
        end_scale = start_scale - push_amount

        cx, cy = 0.50, 0.54
        dst_pts = np.float32([[0.0, 0.0], [float(target_w), 0.0], [0.0, float(target_h)]])
        dolly_matrices = []

        for i in range(total_frames):
            t = i / float(max(1, total_frames - 1))
            scale = start_scale + t * (end_scale - start_scale)
            crop_h = h * scale
            crop_w = crop_h * target_aspect
            if crop_w > w:
                crop_w = w
                crop_h = crop_w / target_aspect

            center_x = max(crop_w / 2.0, min(w - crop_w / 2.0, w * cx))
            center_y = max(crop_h / 2.0, min(h - crop_h / 2.0, h * cy))
            half_w, half_h = crop_w / 2.0, crop_h / 2.0

            src_pts = np.float32(
                [
                    [center_x - half_w, center_y - half_h],
                    [center_x + half_w, center_y - half_h],
                    [center_x - half_w, center_y + half_h],
                ]
            )
            M = cv2.getAffineTransform(src_pts, dst_pts)
            dolly_matrices.append(M)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    mode_title = "Stationary Ambient Heavy Rain" if mode == "stationary" else "3D Forward Dolly in Downpour"
    print(f"\n[Torrential Rain Engine] Rendering {total_frames} frames ({duration_sec}s) | Mode: {mode_title}")
    print(f" -> Resolution: {target_w}x{target_h} (4K UHD) | Output: {output_path}")

    t_start = time.time()
    for i in range(total_frames):
        if mode == "stationary":
            current_frame = base_img.copy()
        else:
            current_frame = cv2.warpAffine(img, dolly_matrices[i], (target_w, target_h), flags=cv2.INTER_CUBIC)

        final_frame = rain_engine.update_and_render_rain(current_frame)
        writer.write(final_frame)

    writer.release()
    elapsed = time.time() - t_start
    fps_render = total_frames / max(0.001, elapsed)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[Done] Rendered {total_frames} frames in {elapsed:.1f}s ({fps_render:.1f} FPS) | Size: {size_mb:.2f} MB")


def process_heavy_rain(
    input_image: str,
    output_dir: str,
    duration_sec: float = 10.0,
    speed: float = 1.2,
    mode: str = "both",
):
    stem = os.path.splitext(os.path.basename(input_image))[0]

    # 1. Option A: Stationary Ambient Rain
    if mode in ("stationary", "both"):
        out_stationary = os.path.join(output_dir, f"{stem}_ambient_heavy_rain.mp4")
        render_heavy_rain_video(input_image, out_stationary, duration_sec, mode="stationary", speed=speed)

    # 2. Option B: 3D Walking in Heavy Rain
    if mode in ("walking", "both"):
        out_walking = os.path.join(output_dir, f"{stem}_walking_heavy_rain.mp4")
        render_heavy_rain_video(input_image, out_walking, duration_sec, mode="walking", speed=speed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Realistic 4K Torrential Rain Engine (Stationary & Walking).")
    parser.add_argument("-i", "--input", required=True, help="Input rain image path")
    parser.add_argument("-o", "--output", default=r"C:\test\output", help="Output directory")
    parser.add_argument("-d", "--duration", type=float, default=10.0, help="Duration in seconds (default: 10.0)")
    parser.add_argument("-s", "--speed", type=float, default=1.2, help="Walking speed multiplier (default: 1.2)")
    parser.add_argument(
        "--mode",
        default="both",
        choices=["both", "stationary", "walking"],
        help="Rain mode: stationary, walking, or both (default: both)",
    )

    args = parser.parse_args()
    process_heavy_rain(args.input, args.output, duration_sec=args.duration, speed=args.speed, mode=args.mode)
