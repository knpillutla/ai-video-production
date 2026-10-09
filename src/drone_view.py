import os
import sys
import argparse
import time
import subprocess
import random
import cv2
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


class CinematicRainEngine:
    """Procedural multi-layer cinematic rain engine with motion-blurred streaks, wind tilt, and atmospheric mist."""

    def __init__(self, width: int, height: int, intensity: str = "medium", wind_tilt: float = 8.0):
        self.w = width
        self.h = height
        self.wind_tilt = wind_tilt

        scale_factor = width / 1920.0
        self.scale = scale_factor

        intensity_map = {
            "light": 1200,
            "medium": 2400,
            "heavy": 4200,
        }
        total_drops = intensity_map.get(intensity.lower(), 2400)

        # 1. High-Velocity Foreground Layer
        self.fg_drops = []
        for _ in range(int(total_drops * 0.35)):
            x = random.uniform(-100 * scale_factor, width + 100 * scale_factor)
            y = random.uniform(-300 * scale_factor, height)
            length = random.uniform(160, 280) * scale_factor
            speed = random.uniform(95, 155) * scale_factor
            thick = random.choice([1, 2])
            self.fg_drops.append([x, y, length, speed, thick])

        # 2. Dense Midground Downpour Layer
        self.mg_drops = []
        for _ in range(int(total_drops * 0.65)):
            x = random.uniform(-100 * scale_factor, width + 100 * scale_factor)
            y = random.uniform(-300 * scale_factor, height)
            length = random.uniform(90, 170) * scale_factor
            speed = random.uniform(70, 115) * scale_factor
            thick = 1
            self.mg_drops.append([x, y, length, speed, thick])

        # 3. Ground Micro-Splashes
        self.splashes = []
        self.ground_y = int(height * 0.55)

        # 4. Soft Alpine Mist Veil
        self.mist_layer = np.full((height, width, 3), (175, 185, 195), dtype=np.uint8)

    def render(self, frame: np.ndarray) -> np.ndarray:
        h, w = self.h, self.w
        rain_canvas = np.zeros((h, w, 3), dtype=np.uint8)
        tilt = self.wind_tilt * self.scale

        # Midground streaks
        for d in self.mg_drops:
            x, y, length, speed, thick = d
            pt1 = (int(x), int(y))
            pt2 = (int(x + tilt * 0.8), int(y + length))
            cv2.line(rain_canvas, pt1, pt2, (180, 195, 210), thick)
            d[0] = (x + tilt * 0.8) % (w + 100) - 50
            d[1] = (y + speed) % (h + length) - length

            if y > self.ground_y and random.random() < 0.02:
                self.splashes.append([int(x), int(y), 1.0, 0.6])

        # Foreground high-speed streaks
        for d in self.fg_drops:
            x, y, length, speed, thick = d
            pt1 = (int(x), int(y))
            pt2 = (int(x + tilt), int(y + length))
            cv2.line(rain_canvas, pt1, pt2, (205, 220, 235), thick)
            d[0] = (x + tilt) % (w + 100) - 50
            d[1] = (y + speed) % (h + length) - length

        # Micro-splashes
        active_splashes = []
        for s in self.splashes:
            sx, sy, radius, s_alpha = s
            if radius < (8.0 * self.scale) and s_alpha > 0.05:
                cv2.ellipse(
                    rain_canvas,
                    (sx, sy),
                    (int(radius), int(radius * 0.28)),
                    0, 0, 360,
                    (190, 205, 220),
                    1,
                )
                active_splashes.append([sx, sy, radius + 1.4 * self.scale, s_alpha - 0.15])
        self.splashes = active_splashes

        misted_frame = cv2.addWeighted(frame, 0.96, self.mist_layer, 0.04, 0)
        return cv2.addWeighted(misted_frame, 1.0, rain_canvas, 0.65, 0)


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
        return float(0.5 * (1.0 - np.cos(t * np.pi)))
    else:  # "cubic"
        return float(t * t * (3.0 - 2.0 * t))


# Supported sequence action types
VALID_ACTIONS = {
    "--stay": "stay",
    "--hold": "stay",
    "--dollyin": "dollyin",
    "--dollyout": "dollyout",
    "--dollyin-stay": "stay",
    "--dollyout-stay": "stay",
    "--pan-left": "pan-left",
    "--pan-right": "pan-right",
    "--pan-left-stay": "stay",
    "--pan-right-stay": "stay",
    "--tilt-up": "tilt-up",
    "--tilt-down": "tilt-down",
    "--tilt-up-stay": "stay",
    "--tilt-down-stay": "stay",
    "--zoom-in": "zoom-in",
    "--zoom-out": "zoom-out",
    "--zoom-in-stay": "stay",
    "--zoom-out-stay": "stay",
    # Compound simultaneous reveal actions:
    "--pan-right-zoom-out": "pan-right-zoom-out",
    "--pan-left-zoom-out": "pan-left-zoom-out",
    "--pan-right-dollyout": "pan-right-zoom-out",
    "--pan-left-dollyout": "pan-left-zoom-out",
    "--reveal": "pan-right-zoom-out",
    "--reveal-left": "pan-right-zoom-out",
    "--reveal-right": "pan-left-zoom-out",
}


def parse_action_sequence(raw_args: list) -> list:
    """Parses sequence steps from command-line arguments.
    Supports sequential actions as well as parallel blocks delimited by:
    --parallel-start ... --parallel-end
    """
    sequence = []
    in_parallel = False
    parallel_actions = []

    i = 0
    while i < len(raw_args):
        arg = raw_args[i].lower()
        if arg == "--parallel-start":
            in_parallel = True
            parallel_actions = []
            i += 1
            continue
        elif arg == "--parallel-end":
            if parallel_actions:
                sequence.append(("parallel", parallel_actions))
                parallel_actions = []
            in_parallel = False
            i += 1
            continue

        if arg in VALID_ACTIONS:
            action_name = VALID_ACTIONS[arg]
            duration_sec = 5.0
            if i + 1 < len(raw_args) and not raw_args[i + 1].startswith("-"):
                try:
                    duration_sec = float(raw_args[i + 1])
                    i += 1
                except ValueError:
                    pass

            if in_parallel:
                parallel_actions.append((action_name, duration_sec))
            else:
                sequence.append((action_name, duration_sec))
            i += 1
        else:
            i += 1

    if parallel_actions:
        sequence.append(("parallel", parallel_actions))

    return sequence


def precompute_sequence_matrices(
    img_shape: tuple,
    sequence: list,
    fps: float = 30.0,
    output_size: tuple = (3840, 2160),
    max_depth: float = 0.50,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
) -> tuple:
    """Simulates a continuous camera timeline across an arbitrary sequence of movements, holds, and parallel blocks."""
    h, w = img_shape[:2]
    target_w, target_h = output_size
    target_aspect = target_w / float(target_h)

    # Base wide framing matching output aspect ratio
    src_aspect = w / float(h)
    if src_aspect > target_aspect:
        base_h = float(h)
        base_w = base_h * target_aspect
    else:
        base_w = float(w)
        base_h = base_w / target_aspect

    base_cx = float(w) / 2.0
    base_cy = float(h) / 2.0

    dst_rect = np.array(
        [
            [0.0, 0.0],
            [float(target_w), 0.0],
            [float(target_w), float(target_h)],
            [0.0, float(target_h)],
        ],
        dtype=np.float32,
    )

    # Initialize starting camera state based on --start-pan, --start-zoom, --start-tilt
    # cur_depth: 0.0 = wide panorama, 1.0 = deep close-up
    cur_depth = 1.0 if start_zoom in ("in", "zoomed", "tight") else 0.0

    # cur_pan: -1.0 = full left (e.g. house on side), 0.0 = center, +1.0 = full right
    if start_pan in ("left", "far-left"):
        cur_pan = -1.0
    elif start_pan in ("right", "far-right"):
        cur_pan = 1.0
    else:
        cur_pan = 0.0

    # cur_tilt: -1.0 = tilted up (sky/peaks), 0.0 = center/level, +1.0 = tilted down
    if start_tilt in ("up", "top"):
        cur_tilt = -1.0
    elif start_tilt in ("down", "bottom"):
        cur_tilt = 1.0
    else:
        cur_tilt = 0.0

    timeline_states = []

    def resolve_target(action_name, s_d, s_p, s_t):
        t_d, t_p, t_t = s_d, s_p, s_t
        if action_name == "stay":
            pass
        elif action_name in ("dollyin", "zoom-in"):
            t_d = 1.0
        elif action_name in ("dollyout", "zoom-out"):
            t_d = 0.0
        elif action_name == "pan-left":
            t_p = -1.0
        elif action_name == "pan-right":
            t_p = 0.0 if s_p < -0.05 else 1.0
        elif action_name == "tilt-up":
            t_t = -1.0
        elif action_name == "tilt-down":
            t_t = 0.0 if s_t < -0.05 else 1.0
        elif action_name == "pan-right-zoom-out":
            t_d = 0.0
            t_p = 0.0
            t_t = 0.0
        elif action_name == "pan-left-zoom-out":
            t_d = 0.0
            t_p = 0.0
            t_t = 0.0
        return t_d, t_p, t_t

    for item in sequence:
        action_type = item[0]

        if action_type == "parallel":
            # item is ("parallel", [(sub_action, dur), ...])
            sub_actions = item[1]
            if not sub_actions:
                continue
            max_duration = max(dur for _, dur in sub_actions)
            num_frames = int(round(max_duration * fps))
            if num_frames <= 0:
                continue

            start_d, start_p, start_t = cur_depth, cur_pan, cur_tilt

            # Prepare trajectory targets and durations for each active channel
            channels = []
            for sub_act, sub_dur in sub_actions:
                tgt_d, tgt_p, tgt_t = resolve_target(sub_act, start_d, start_p, start_t)
                sub_frames = max(1, int(round(sub_dur * fps)))
                channels.append((sub_act, tgt_d, tgt_p, tgt_t, sub_frames))

            for f in range(num_frames):
                d_val = start_d
                p_val = start_p
                t_val = start_t

                for sub_act, tgt_d, tgt_p, tgt_t, sub_frames in channels:
                    prog = min(1.0, f / max(1, sub_frames - 1)) if sub_frames > 1 else 1.0
                    e = calculate_easing(prog, curve)
                    if sub_act in ("dollyin", "dollyout", "zoom-in", "zoom-out", "pan-right-zoom-out", "pan-left-zoom-out"):
                        d_val = start_d + e * (tgt_d - start_d)
                    if sub_act in ("pan-left", "pan-right", "pan-right-zoom-out", "pan-left-zoom-out"):
                        p_val = start_p + e * (tgt_p - start_p)
                    if sub_act in ("tilt-up", "tilt-down", "pan-right-zoom-out", "pan-left-zoom-out"):
                        t_val = start_t + e * (tgt_t - start_t)

                timeline_states.append((d_val, p_val, t_val))

            # Update final camera state after parallel block
            for sub_act, tgt_d, tgt_p, tgt_t, _ in channels:
                if sub_act in ("dollyin", "dollyout", "zoom-in", "zoom-out", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_depth = tgt_d
                if sub_act in ("pan-left", "pan-right", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_pan = tgt_p
                if sub_act in ("tilt-up", "tilt-down", "pan-right-zoom-out", "pan-left-zoom-out"):
                    cur_tilt = tgt_t

        else:
            action, duration_sec = item
            num_frames = int(round(duration_sec * fps))
            if num_frames <= 0:
                continue

            start_d, start_p, start_t = cur_depth, cur_pan, cur_tilt
            target_d, target_p, target_t = resolve_target(action, start_d, start_p, start_t)

            for f in range(num_frames):
                prog = f / max(1, num_frames - 1) if num_frames > 1 else 1.0
                e = calculate_easing(prog, curve)
                d = start_d + e * (target_d - start_d)
                p = start_p + e * (target_p - start_p)
                t = start_t + e * (target_t - start_t)
                timeline_states.append((d, p, t))

            cur_depth = target_d
            cur_pan = target_p
            cur_tilt = target_t

    # Convert state timeline into 2D perspective / affine transformation matrices
    matrices = []
    min_scale = max(0.20, 1.0 - max_depth)

    for d, p, t in timeline_states:
        # Scale for dolly/zoom: from 1.0 (wide panorama) down to min_scale (tight framing)
        scale = 1.0 - d * (1.0 - min_scale)
        cw = base_w * scale
        ch = cw / target_aspect

        # Maximum available pan and tilt travel inside the photo
        # When zoomed in (scale is small), we have full room to slide across to the very edge of the image!
        avail_pan_x = (float(w) - cw) / 2.0
        avail_tilt_y = (float(h) - ch) / 2.0

        cx = base_cx + (p * avail_pan_x)
        cy = base_cy + (t * avail_tilt_y)

        # Ensure framing remains strictly within the image boundary
        half_w = cw / 2.0
        half_h = ch / 2.0
        cx = max(half_w, min(float(w) - half_w, cx))
        cy = max(half_h, min(float(h) - half_h, cy))

        src_quad = np.array(
            [
                [cx - half_w, cy - half_h],
                [cx + half_w, cy - half_h],
                [cx + half_w, cy + half_h],
                [cx - half_w, cy + half_h],
            ],
            dtype=np.float32,
        )

        matrix = cv2.getPerspectiveTransform(src_quad, dst_rect)
        matrices.append(matrix)

    return matrices, len(timeline_states)


def process_drone_flyovers(
    input_dir: str,
    output_dir: str,
    sequence: list,
    fps: float = 30.0,
    depth: float = 0.50,
    speed_factor: float = 1.0,
    start_pan: str = "center",
    start_zoom: str = "normal",
    start_tilt: str = "center",
    curve: str = "cosine",
    rain: bool = False,
    rain_intensity: str = "medium",
    res_mode: str = "4k",
    interp_mode: str = "lanczos",
    target_duration: float = None,
):
    os.makedirs(output_dir, exist_ok=True)
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".webp")
    images = [f for f in os.listdir(input_dir) if f.lower().endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    # Calculate mission total duration and human-readable sequence summary
    total_sec = 0.0
    for item in sequence:
        if item[0] == "parallel":
            sub_acts = item[1]
            dur = max(d for _, d in sub_acts) if sub_acts else 0.0
            total_sec += dur
        else:
            _, dur = item
            total_sec += dur

    # Behavior A: If --duration was specified and exceeds current sequence, automatically hold at end!
    if target_duration is not None and target_duration > total_sec:
        remaining_hold = target_duration - total_sec
        if sequence and sequence[-1][0] == "stay":
            last_act, last_dur = sequence[-1]
            sequence[-1] = (last_act, last_dur + remaining_hold)
        else:
            sequence.append(("stay", remaining_hold))
        total_sec = target_duration

    desc_parts = []
    for item in sequence:
        if item[0] == "parallel":
            sub_acts = item[1]
            inner = "+".join([f"{a.upper()}({d:g}s)" for a, d in sub_acts])
            desc_parts.append(f"PARALLEL[{inner}]")
        else:
            act, dur = item
            desc_parts.append(f"{act.upper()}({dur:g}s)")

    seq_desc = " -> ".join(desc_parts)

    interp_map = {
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }
    warp_flag = interp_map.get(interp_mode.lower(), cv2.INTER_LANCZOS4)

    effective_depth = depth * max(0.05, speed_factor)
    clamped_depth = min(0.75, max(0.05, effective_depth))

    if res_mode.lower() == "1080p":
        target_size = (1920, 1080)
        mode_str = "Full HD (1920x1080)"
    else:
        target_size = (3840, 2160)
        mode_str = "4K UHD (3840x2160)"

    print("--- 3D Keyframe Sequence Drone Director ---")
    print(f"Mission Plan: {seq_desc}")
    print(f"Start Setup: Pan={start_pan.upper()}, Zoom={start_zoom.upper()}, Tilt={start_tilt.upper()}")
    print(f"Total Duration: {total_sec:.1f}s (@ {fps}fps) | Easing: {curve.upper()}")
    if rain:
        print(f"Atmosphere: Active Cinematic Rain ({rain_intensity.upper()}) + Alpine Mist")
    print(f"Output Mode: {mode_str} | Max Zoom Depth: {clamped_depth:.1%} | Interp: {interp_mode.upper()}")

    for img_name in images:
        stem = os.path.splitext(img_name)[0]
        img_path = os.path.join(input_dir, img_name)
        mode_suffix = "reveal_mission" if (start_pan != "center" or start_zoom != "normal") else "flight_mission"
        if rain:
            mode_suffix += f"_rain_{rain_intensity}"
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
        matrices, total_frames = precompute_sequence_matrices(
            img_shape=img.shape,
            sequence=sequence,
            fps=fps,
            output_size=output_size,
            max_depth=clamped_depth,
            start_pan=start_pan,
            start_zoom=start_zoom,
            start_tilt=start_tilt,
            curve=curve,
        )
        print(f" -> Precomputed {len(matrices)} transformation matrices in {(time.time() - t_pre)*1000:.1f}ms")

        # Initialize rain engine if requested
        rain_engine = None
        if rain:
            rain_engine = CinematicRainEngine(out_w, out_h, intensity=rain_intensity)

        ffmpeg_proc = get_ffmpeg_writer(output_path, out_w, out_h, fps)
        video_writer = None
        if ffmpeg_proc is None:
            print(" -> Notice: Falling back to OpenCV VideoWriter (mp4v)...")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, output_size)
        else:
            print(" -> Video Encoder: Broadcast H.264 (libx264, CRF 18, zero-pulsing)")

        t_start = time.time()
        print(f" -> Rendering and streaming {total_frames} frames to disk...")

        for i in range(total_frames):
            frame = cv2.warpPerspective(
                img,
                matrices[i],
                output_size,
                flags=warp_flag,
                borderMode=cv2.BORDER_REPLICATE,
            )

            if rain_engine is not None:
                frame = rain_engine.render(frame)

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
        description="Cinematic Sequence Drone Flight Director. Chain any sequence of motions and stays."
    )
    parser.add_argument("-i", "--input", required=True, help="Input directory of images")
    parser.add_argument("-o", "--output", required=True, help="Output directory for MP4 videos")
    parser.add_argument("-d", "--duration", type=float, default=None,
                        help="Target total video duration in seconds. If choreography finishes earlier, camera automatically holds on final scene for remainder.")
    parser.add_argument("--start-pan", choices=["center", "left", "right"], default="center",
                        help="Initial camera horizontal framing: center (default), left, or right")
    parser.add_argument("--start-zoom", choices=["normal", "in"], default="normal",
                        help="Initial camera magnification: normal (wide panorama) or in (zoomed-in close-up)")
    parser.add_argument("--start-tilt", choices=["center", "up", "down"], default="center",
                        help="Initial camera vertical framing: center (default), up, or down")
    parser.add_argument("--depth", type=float, default=0.50, 
                        help="Zoom depth scale for close-up framing (default: 0.50 for intimate detail framing)")
    parser.add_argument("--speed", type=float, default=1.0, 
                        help="Speed multiplier (default: 1.0)")
    parser.add_argument("--curve", choices=["cosine", "cubic", "linear"], default="cosine", 
                        help="Motion easing curve: cosine (default: smoothest glide), cubic, linear")
    parser.add_argument("--rain", action="store_true", help="Add authentic procedural cinematic rainfall & atmospheric mist")
    parser.add_argument("--rain-intensity", choices=["light", "medium", "heavy"], default="medium", 
                        help="Rain intensity: light, medium, heavy")
    parser.add_argument("--fps", type=float, default=30.0, help="Frames per second (default: 30.0)")
    parser.add_argument("--res", choices=["4k", "1080p"], default="4k", help="Output resolution: 4k (default: 3840x2160) or 1080p")
    parser.add_argument("--fast", action="store_true", help="Fast linear interpolation")
    parser.add_argument("--cubic", action="store_true", help="Bicubic interpolation")

    args, unknown = parser.parse_known_args()

    # Parse ordered sequence from command-line arguments
    sequence = parse_action_sequence(sys.argv)

    if not sequence:
        print("\nError: No sequence actions specified!")
        print("Example 1 (Sequential flight sequence):")
        print("  python .\\src\\drone_view.py -i C:\\test\\input1 -o C:\\test\\output \\")
        print("    --stay 5 --dollyin 5 --stay 5 --pan-left 5 --stay 5 --pan-right 5 --dollyout 5 --stay 10")
        print("\nExample 2 (Simultaneous reveal using parallel block: pan and zoom out at the same time):")
        print("  python .\\src\\drone_view.py -i C:\\test\\input1 -o C:\\test\\output \\")
        print("    --start-pan left --start-zoom in \\")
        print("    --stay 3 \\")
        print("    --parallel-start --pan-right 5 --zoom-out 6 --parallel-end \\")
        print("    --stay 5")
        sys.exit(1)

    interp = "linear" if args.fast else ("cubic" if args.cubic else "lanczos")

    process_drone_flyovers(
        input_dir=args.input,
        output_dir=args.output,
        sequence=sequence,
        fps=args.fps,
        depth=args.depth,
        speed_factor=args.speed,
        start_pan=args.start_pan,
        start_zoom=args.start_zoom,
        start_tilt=args.start_tilt,
        curve=args.curve,
        rain=args.rain,
        rain_intensity=args.rain_intensity,
        res_mode=args.res,
        interp_mode=interp,
        target_duration=args.duration,
    )
