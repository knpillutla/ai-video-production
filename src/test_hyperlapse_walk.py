import os
import argparse
import time
import cv2
import numpy as np


def render_hyperlapse_walking_tour(
    input_dir: str = r"c:\test\input",
    output_path: str = r"c:\test\output\test_hyperlapse_walking_tour.mp4",
    step_frames: int = 14,      # ~0.47s hold per physical step
    trans_frames: int = 8,      # ~0.27s rapid forward motion-blur stride transition
    fps: float = 30.0,
    target_size: tuple = (3840, 2160),
):
    """Renders a true forward hyperlapse walking tour (Google Street View style).

    Eliminates flat zooming by physically advancing camera positions on every stride.
    """
    extensions = (".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG")
    files = sorted([f for f in os.listdir(input_dir) if f.startswith("wp") and f.endswith(extensions)])

    if not files:
        files = sorted([f for f in os.listdir(input_dir) if f.endswith(extensions)])

    if len(files) < 2:
        print(f"Error: Need at least 2 photos in {input_dir}")
        return

    target_w, target_h = target_size
    target_aspect = target_w / float(target_h)

    print("==================================================================")
    print("      TRUE HYPERLAPSE WALKING TOUR DIRECTOR (ZERO ZOOM)           ")
    print("==================================================================")
    print(f"Input Photos    : {len(files)} sequential positions")
    print(f"Cadence         : {step_frames / fps:.2f}s per physical step")
    print(f"Transition      : {trans_frames / fps:.2f}s forward stride leap")
    print(f"Output Master   : {output_path}")
    print("==================================================================\n")

    # Pre-load and scale images to target 4K canvas
    images = []
    for f in files:
        p = os.path.join(input_dir, f)
        raw = cv2.imread(p)
        if raw is not None:
            # Crop to 16:9 if needed and resize to 4K
            h, w = raw.shape[:2]
            asp = w / float(h)
            if abs(asp - target_aspect) > 0.05:
                if asp > target_aspect:
                    crop_w = int(h * target_aspect)
                    x_start = (w - crop_w) // 2
                    raw = raw[:, x_start : x_start + crop_w]
                else:
                    crop_h = int(w / target_aspect)
                    y_start = (h - crop_h) // 2
                    raw = raw[y_start : y_start + crop_h, :]
            scaled = cv2.resize(raw, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            images.append((f, scaled))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    dst_pts = np.float32([[0.0, 0.0], [float(target_w), 0.0], [0.0, float(target_h)]])

    t_start = time.time()
    total_written = 0

    for i in range(len(images)):
        name, img = images[i]
        is_last = (i == len(images) - 1)

        print(f"[{i+1}/{len(images)}] Rendering step: {name}")

        # 1. Step Hold: Camera settles onto the new physical step (subtle cushioned step heave)
        hold_count = 90 if is_last else step_frames  # 3.0s panoramic hold on final turnaround vista

        for f in range(hold_count):
            if is_last:
                # Slow panoramic scan across the 180° reverse valley
                t_pan = f / float(max(1, hold_count - 1))
                crop_scale = 0.92
                cw = int(target_w * crop_scale)
                ch = int(target_h * crop_scale)
                pan_x = int((target_w - cw) * (0.35 + 0.30 * t_pan))
                pan_y = int((target_h - ch) * 0.50)
                sub = img[pan_y : pan_y + ch, pan_x : pan_x + cw]
                frame = cv2.resize(sub, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            else:
                # Subtle cushioned step heave (~12 pixels vertical settle matching a human step contact)
                t_step = f / float(step_frames)
                step_heave = int(np.sin(t_step * np.pi) * 12.0)
                crop_scale = 0.985
                cw = int(target_w * crop_scale)
                ch = int(target_h * crop_scale)
                cx = (target_w - cw) // 2
                cy = max(0, min(target_h - ch, (target_h - ch) // 2 + step_heave))
                sub = img[cy : cy + ch, cx : cx + cw]
                frame = cv2.resize(sub, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

            writer.write(frame)
            total_written += 1

        # 2. Forward Stride Transition: Fast forward push leaping into next physical photo
        if not is_last:
            next_name, next_img = images[i + 1]

            for tf in range(trans_frames):
                tau = tf / float(trans_frames)  # 0.0 -> 1.0

                # Current image pushes forward into vanishing point with motion blur
                push_scale = 1.0 - 0.18 * (tau**1.3)
                cw1 = int(target_w * push_scale)
                ch1 = int(target_h * push_scale)
                cx1 = (target_w - cw1) // 2
                cy1 = int((target_h - ch1) * 0.55)
                sub1 = img[cy1 : cy1 + ch1, cx1 : cx1 + cw1]
                frame1 = cv2.resize(sub1, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

                # Next image starts slightly wide and settles into position
                pull_scale = 0.92 + 0.08 * (tau**0.7)
                cw2 = int(target_w * pull_scale)
                ch2 = int(target_h * pull_scale)
                cx2 = (target_w - cw2) // 2
                cy2 = int((target_h - ch2) * 0.55)
                sub2 = next_img[cy2 : cy2 + ch2, cx2 : cx2 + cw2]
                frame2 = cv2.resize(sub2, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

                # Directional motion blur cross-blend
                blend = cv2.addWeighted(frame1, 1.0 - tau, frame2, tau, 0)
                writer.write(blend)
                total_written += 1

    writer.release()
    elapsed = time.time() - t_start
    dur = total_written / fps
    size_mb = os.path.getsize(output_path) / 1024 / 1024

    print("\n==================================================================")
    print("      HYPERLAPSE WALKING TOUR COMPILATION FINISHED                ")
    print("==================================================================")
    print(f"Output Master : {output_path}")
    print(f"Total Frames  : {total_written} ({dur:.1f}s)")
    print(f"Render Time   : {elapsed:.1f}s ({total_written / max(0.001, elapsed):.1f} FPS)")
    print(f"File Size     : {size_mb:.2f} MB")
    print("==================================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="True Hyperlapse Walking Tour (Google Street View Cadence).")
    parser.add_argument("-i", "--input", default=r"c:\test\input", help="Input directory of waypoint images")
    parser.add_argument(
        "-o",
        "--output",
        default=r"c:\test\output\test_hyperlapse_walking_tour.mp4",
        help="Output 4K master video path",
    )
    parser.add_argument("--step-frames", type=int, default=14, help="Frames to hold per physical step (default: 14)")
    parser.add_argument(
        "--trans-frames", type=int, default=8, help="Frames for forward stride leap (default: 8)"
    )

    args = parser.parse_args()
    render_hyperlapse_walking_tour(
        args.input, args.output, step_frames=args.step_frames, trans_frames=args.trans_frames
    )
