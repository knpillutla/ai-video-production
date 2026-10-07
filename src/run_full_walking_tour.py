import os
import argparse
import subprocess
import time
import cv2
import numpy as np
import imageio_ffmpeg

from walking_tour_script import detect_vanishing_point


def get_ffmpeg_path() -> str:
    """Finds imageio-ffmpeg or system ffmpeg binary."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def build_xfade_filter(clip_durations: list[float], xfade_dur: float = 0.8) -> str:
    """Builds a variable-length single-pass FFmpeg xfade filter chain."""
    num_clips = len(clip_durations)
    if num_clips == 1:
        return "[0:v]copy[vout]"

    filters = []
    current_label = "0:v"
    current_offset = clip_durations[0] - xfade_dur

    for i in range(1, num_clips):
        next_label = f"{i}:v"
        out_label = f"v{i}" if i < num_clips - 1 else "vout"
        filters.append(
            f"[{current_label}][{next_label}]xfade=transition=fade:duration={xfade_dur:.2f}:offset={current_offset:.2f}[{out_label}]"
        )
        current_label = out_label
        if i < num_clips - 1:
            current_offset += (clip_durations[i] - xfade_dur)

    return ";".join(filters)


def render_4k_waypoint_shot(
    img: np.ndarray,
    output_path: str,
    duration_sec: float = 6.0,
    shot_type: str = "forward_walk",
    speed: float = 1.2,
    vpx_norm: float = 0.50,
    vpy_norm: float = 0.52,
    target_size: tuple = (3840, 2160),
    fps: float = 30.0,
):
    """Renders a single 4K camera shot: either a forward dolly walk or a panoramic turnaround vista."""
    h, w = img.shape[:2]
    target_w, target_h = target_size
    target_aspect = target_w / float(target_h)
    total_frames = int(duration_sec * fps)

    dst_pts = np.float32([[0.0, 0.0], [float(target_w), 0.0], [0.0, float(target_h)]])
    matrices = []

    if shot_type == "reverse_panorama":
        # Slow sweeping panoramic camera glide across the vast valley
        scale = 0.88
        crop_h = h * scale
        crop_w = crop_h * target_aspect
        half_w, half_h = crop_w / 2.0, crop_h / 2.0

        for i in range(total_frames):
            t = i / float(max(1, total_frames - 1))
            # Smooth left-to-right pan: 0.44 -> 0.56
            pan_cx = 0.44 + t * 0.12
            center_x = max(half_w, min(w - half_w, w * pan_cx))
            center_y = max(half_h, min(h - half_h, h * 0.50))

            src_pts = np.float32(
                [
                    [center_x - half_w, center_y - half_h],
                    [center_x + half_w, center_y - half_h],
                    [center_x - half_w, center_y + half_h],
                ]
            )
            M = cv2.getAffineTransform(src_pts, dst_pts)
            matrices.append(M)
    else:
        # Straightforward 4K camera dolly forward walk down the pathway
        start_scale = 1.00
        push_amount = min(0.35, 0.20 * speed)
        end_scale = start_scale - push_amount

        cx = max(0.38, min(0.62, vpx_norm))
        cy = max(0.42, min(0.58, vpy_norm))

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
            matrices.append(M)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    for i in range(total_frames):
        frame = cv2.warpAffine(img, matrices[i], (target_w, target_h), flags=cv2.INTER_CUBIC)
        writer.write(frame)

    writer.release()


def run_full_walking_tour(
    input_dir: str = r"c:\test\input",
    output_master: str = r"c:\test\output\swiss_full_journey_master_4k.mp4",
    speed: float = 1.2,
    xfade_duration: float = 0.8,
):
    """Executes the complete Swiss walking tour pipeline across sequential waypoints."""
    temp_shots_dir = os.path.join(os.path.dirname(output_master), "temp_tour_shots")
    os.makedirs(temp_shots_dir, exist_ok=True)

    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    all_files = sorted([f for f in os.listdir(input_dir) if f.startswith("wp") and f.endswith(extensions)])

    if not all_files:
        # Fallback to any images
        all_files = sorted([f for f in os.listdir(input_dir) if f.endswith(extensions)])

    if not all_files:
        print(f"Error: No waypoint images found in {input_dir}")
        return

    print("==================================================================")
    print("      SWISS ALPINE COMPLETE 4K WALKING TOUR PIPELINE              ")
    print("==================================================================")
    print(f"Input Directory   : {input_dir}")
    print(f"Discovered Shots  : {len(all_files)} sequential waypoints")
    print(f"Resolution        : 4K UHD (3840x2160)")
    print(f"Output Master     : {output_master}")
    print("==================================================================\n")

    shot_video_paths = []
    shot_durations = []

    for idx, img_name in enumerate(all_files, start=1):
        stem = os.path.splitext(img_name)[0]
        shot_out = os.path.join(temp_shots_dir, f"shot_{idx:02d}_{stem}.mp4")
        shot_video_paths.append(shot_out)

        # Reverse panorama gets an 8-second sweeping view; others get 6 seconds
        is_reverse = "reverse" in img_name.lower() or idx == len(all_files)
        dur = 8.0 if is_reverse else 6.0
        shot_durations.append(dur)
        shot_type = "reverse_panorama" if is_reverse else "forward_walk"

        # Tier 1 disk cache check (Directive 3)
        if os.path.exists(shot_out) and os.path.getsize(shot_out) > 1000:
            print(f"[{idx}/{len(all_files)}] Reusing cached 4K shot: {shot_out}")
            continue

        print(f"[{idx}/{len(all_files)}] Rendering 4K {shot_type} for: {img_name} ({dur}s)...")
        img_path = os.path.join(input_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        vpx_norm, vpy_norm = detect_vanishing_point(img)
        t_start = time.time()

        render_4k_waypoint_shot(
            img=img,
            output_path=shot_out,
            duration_sec=dur,
            shot_type=shot_type,
            speed=speed,
            vpx_norm=vpx_norm,
            vpy_norm=vpy_norm,
            target_size=(3840, 2160),
            fps=30.0,
        )

        elapsed = time.time() - t_start
        fps_val = (int(dur * 30.0)) / max(0.001, elapsed)
        print(f" -> Completed in {elapsed:.1f}s ({fps_val:.1f} FPS) -> {shot_out}")

    # Single-pass FFmpeg transition assembly
    print(f"\n[Master Assembly] Stitching {len(shot_video_paths)} shots via single-pass FFmpeg...")
    ffmpeg_exe = get_ffmpeg_path()
    filter_complex = build_xfade_filter(shot_durations, xfade_dur=xfade_duration)

    cmd = [ffmpeg_exe, "-y", "-loglevel", "error"]
    for path in shot_video_paths:
        cmd.extend(["-i", path])

    cmd.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[vout]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            output_master,
        ]
    )

    t_asm = time.time()
    subprocess.run(cmd, check=True)
    asm_time = time.time() - t_asm

    master_size_mb = os.path.getsize(output_master) / 1024 / 1024
    total_est_dur = sum(shot_durations) - ((len(shot_durations) - 1) * xfade_duration)

    print("\n==================================================================")
    print("      COMPLETE 4K WALKING TOUR JOURNEY ASSEMBLED                  ")
    print("==================================================================")
    print(f"Master File : {output_master}")
    print(f"Resolution  : 4K UHD (3840x2160)")
    print(f"Duration    : ~{total_est_dur:.1f}s")
    print(f"File Size   : {master_size_mb:.2f} MB")
    print(f"Encode Time : {asm_time:.1f}s")
    print("==================================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Swiss Alpine 4K Walking Tour Pipeline.")
    parser.add_argument("-i", "--input", default=r"c:\test\input", help="Input directory of waypoint images")
    parser.add_argument(
        "-o",
        "--output",
        default=r"c:\test\output\swiss_full_journey_master_4k.mp4",
        help="Output 4K master video path",
    )
    parser.add_argument("-s", "--speed", type=float, default=1.2, help="Walking speed multiplier (default: 1.2)")
    parser.add_argument("--xfade", type=float, default=0.8, help="Crossfade transition duration (default: 0.8s)")

    args = parser.parse_args()
    run_full_walking_tour(args.input, args.output, speed=args.speed, xfade_duration=args.xfade)
