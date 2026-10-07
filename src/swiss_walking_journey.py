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


def build_xfade_filter(num_clips: int, clip_duration: float, xfade_dur: float = 1.0) -> str:
    """Builds a single-pass FFmpeg xfade filter chain for seamless cross-dissolves."""
    if num_clips == 1:
        return "[0:v]copy[vout]"

    filters = []
    current_label = "0:v"
    offset = clip_duration - xfade_dur

    for i in range(1, num_clips):
        next_label = f"{i}:v"
        out_label = f"v{i}" if i < num_clips - 1 else "vout"
        filters.append(
            f"[{current_label}][{next_label}]xfade=transition=fade:duration={xfade_dur:.2f}:offset={offset:.2f}[{out_label}]"
        )
        current_label = out_label
        offset += (clip_duration - xfade_dur)

    return ";".join(filters)


def render_rigid_4k_dolly_shot(
    img: np.ndarray,
    output_path: str,
    duration_sec: float = 6.0,
    speed: float = 1.2,
    vpx_norm: float = 0.50,
    vpy_norm: float = 0.52,
    target_size: tuple = (3840, 2160),
    fps: float = 30.0,
):
    """Renders a 100% rigid, distortion-free 4K camera dolly push-in.

    Zero morphing, zero liquid warping. Straight architectural lines stay 100% straight.
    """
    h, w = img.shape[:2]
    target_w, target_h = target_size
    target_aspect = target_w / float(target_h)

    total_frames = int(duration_sec * fps)
    start_scale = 1.00
    push_amount = min(0.38, 0.22 * speed)
    end_scale = start_scale - push_amount

    # Target path center biased toward vanishing point
    cx = max(0.35, min(0.65, vpx_norm))
    cy = max(0.40, min(0.60, vpy_norm))

    dst_pts = np.float32([[0.0, 0.0], [float(target_w), 0.0], [0.0, float(target_h)]])
    matrices = []

    for i in range(total_frames):
        t = i / float(max(1, total_frames - 1))
        scale = start_scale + t * (end_scale - start_scale)

        crop_h = h * scale
        crop_w = crop_h * target_aspect
        if crop_w > w:
            crop_w = w
            crop_h = crop_w / target_aspect

        center_x = w * cx
        center_y = h * cy
        half_w, half_h = crop_w / 2.0, crop_h / 2.0

        center_x = max(half_w, min(w - half_w, center_x))
        center_y = max(half_h, min(h - half_h, center_y))

        src_pts = np.float32(
            [
                [center_x - half_w, center_y - half_h],
                [center_x + half_w, center_y - half_h],
                [center_x - half_w, center_y + half_h],
            ]
        )
        matrix = cv2.getAffineTransform(src_pts, dst_pts)
        matrices.append(matrix)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    for i in range(total_frames):
        frame = cv2.warpAffine(img, matrices[i], (target_w, target_h), flags=cv2.INTER_CUBIC)
        writer.write(frame)

    writer.release()


def assemble_multishot_journey(
    input_dir: str,
    output_master: str,
    clip_duration: float = 6.0,
    speed: float = 1.2,
    xfade_duration: float = 0.8,
    max_photos: int = None,
):
    """Renders sequential distortion-free 4K walking shots across Swiss photos and stitches them with crossfades."""
    os.makedirs(os.path.dirname(os.path.abspath(output_master)), exist_ok=True)
    temp_shots_dir = os.path.join(os.path.dirname(output_master), "temp_shots_4k")
    os.makedirs(temp_shots_dir, exist_ok=True)

    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    all_files = sorted([f for f in os.listdir(input_dir) if f.endswith(extensions)])

    # Deduplicate files by file size
    unique_files = []
    seen_sizes = set()
    for f in all_files:
        sz = os.path.getsize(os.path.join(input_dir, f))
        if sz not in seen_sizes:
            seen_sizes.add(sz)
            unique_files.append(f)

    if max_photos:
        unique_files = unique_files[:max_photos]

    if not unique_files:
        print(f"Error: No images found inside: {input_dir}")
        return

    print("================================================================")
    print("   SWISS 4K DISTORTION-FREE MULTI-SHOT WALKING TOUR DIRECTOR   ")
    print("================================================================")
    print(f"Input Directory   : {input_dir}")
    print(f"Total Unique Shots: {len(unique_files)} photos")
    print(f"Master Resolution : 4K UHD (3840x2160)")
    print(f"Clip Duration     : {clip_duration}s per shot")
    print(f"Walking Speed     : {speed}x smooth forward dolly")
    print(f"Crossfade Duration: {xfade_duration}s")
    print(f"Output Master     : {output_master}")
    print("================================================================\n")

    shot_video_paths = []

    for idx, img_name in enumerate(unique_files, start=1):
        stem = os.path.splitext(img_name)[0]
        shot_out_path = os.path.join(temp_shots_dir, f"shot_{idx:02d}_{stem}.mp4")
        shot_video_paths.append(shot_out_path)

        # Rule 3: Tier 1 Disk Check - Skip synthesis if artifact exists and > 1000 bytes
        if os.path.exists(shot_out_path) and os.path.getsize(shot_out_path) > 1000:
            print(f"[{idx}/{len(unique_files)}] Reusing cached 4K shot: {shot_out_path}")
            continue

        print(f"[{idx}/{len(unique_files)}] Rendering distortion-free 4K shot: {img_name}")
        img_path = os.path.join(input_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        vpx_norm, vpy_norm = detect_vanishing_point(img)
        t_start = time.time()

        render_rigid_4k_dolly_shot(
            img=img,
            output_path=shot_out_path,
            duration_sec=clip_duration,
            speed=speed,
            vpx_norm=vpx_norm,
            vpy_norm=vpy_norm,
            target_size=(3840, 2160),
            fps=30.0,
        )
        elapsed = time.time() - t_start
        fps_render = (int(clip_duration * 30.0)) / max(0.001, elapsed)
        print(f" -> 4K Shot finished in {elapsed:.1f}s ({fps_render:.1f} FPS) -> {shot_out_path}")

    # Assemble all shots into 4K master video using single-pass FFmpeg xfade
    print(f"\n[Assembly Engine] Composing {len(shot_video_paths)} 4K shots into single-pass master video...")
    ffmpeg_exe = get_ffmpeg_path()
    filter_complex = build_xfade_filter(len(shot_video_paths), clip_duration, xfade_dur=xfade_duration)

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
    est_duration = (len(shot_video_paths) * clip_duration) - ((len(shot_video_paths) - 1) * xfade_duration)

    print("================================================================")
    print("      4K MASTER WALKING TOUR COMPILATION COMPLETE")
    print("================================================================")
    print(f"Master File : {output_master}")
    print(f"Resolution  : 4K UHD (3840x2160)")
    print(f"Duration    : ~{est_duration:.1f}s")
    print(f"File Size   : {master_size_mb:.2f} MB")
    print(f"Encode Time : {asm_time:.1f}s")
    print("================================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Shot Swiss Alpine 4K Walking Tour Master Producer.")
    parser.add_argument(
        "-i",
        "--input",
        default=r"C:\neel-1\projects\content-generation\storage\swiss-beautiful-photos",
        help="Input folder of Swiss photos",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=r"C:\test\output\swiss_4k_walking_tour_master.mp4",
        help="Output master video file",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=6.0, help="Duration per shot in seconds (default: 6.0)"
    )
    parser.add_argument(
        "-s", "--speed", type=float, default=1.2, help="Walking speed multiplier (default: 1.2)"
    )
    parser.add_argument(
        "--xfade", type=float, default=0.8, help="Crossfade transition duration in seconds (default: 0.8)"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Optional limit on number of photos to include"
    )

    args = parser.parse_args()
    assemble_multishot_journey(
        input_dir=args.input,
        output_master=args.output,
        clip_duration=args.duration,
        speed=args.speed,
        xfade_duration=args.xfade,
        max_photos=args.limit,
    )
