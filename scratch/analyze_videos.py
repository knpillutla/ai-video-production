import cv2
import numpy as np
import json
from pathlib import Path

def analyze_video(video_path: str, output_prefix: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"=== Analyzing {output_prefix} ===")
    print(f"Path: {video_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps}, Frames: {total_frames}, Duration: {duration:.2f}s")

    out_dir = Path("scratch/analysis") / output_prefix
    out_dir.mkdir(parents=True, exist_ok=True)

    prev_gray = None
    motion_magnitudes = []
    r_means, g_means, b_means = [], [], []

    sample_indices = [int(total_frames * r) for r in [0.1, 0.3, 0.5, 0.7, 0.9] if int(total_frames * r) < total_frames]
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # BGR channels
        b = frame[:, :, 0]
        g = frame[:, :, 1]
        r = frame[:, :, 2]
        r_means.append(np.mean(r))
        g_means.append(np.mean(g))
        b_means.append(np.mean(b))

        # Optical flow / motion speed
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            # Downsample for fast optical flow
            small_prev = cv2.resize(prev_gray, (320, 180))
            small_curr = cv2.resize(gray, (320, 180))
            flow = cv2.calcOpticalFlowFarneback(small_prev, small_curr, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            motion_magnitudes.append(np.mean(mag))
        prev_gray = gray

        if frame_idx in sample_indices:
            # save sample frame for inspection
            cv2.imwrite(str(out_dir / f"frame_{frame_idx:04d}.jpg"), frame)

        frame_idx += 1

    cap.release()

    avg_r = np.mean(r_means)
    avg_g = np.mean(g_means)
    avg_b = np.mean(b_means)
    avg_motion = np.mean(motion_magnitudes) if motion_magnitudes else 0.0
    max_motion = np.max(motion_magnitudes) if motion_magnitudes else 0.0

    # Color cast analysis: warm/yellow has high R and G, lower B
    # Yellow = (R+G)/2 - B
    yellow_index = ((avg_r + avg_g) / 2.0) - avg_b

    print(f"Color Means -> R: {avg_r:.1f}, G: {avg_g:.1f}, B: {avg_b:.1f}")
    print(f"Yellow/Warmth Index: {yellow_index:.2f} (positive = warm/yellow cast, negative = cool/blue cast)")
    print(f"Average Optical Flow Motion Magnitude: {avg_motion:.3f} px/frame (scaled 320x180)")
    print(f"Peak Motion: {max_motion:.3f}")
    print()

if __name__ == "__main__":
    analyze_video("storage/live_production/job_1_swiss_alps/swiss_alps_4k_walk_master.mp4", "swiss_alps")
    analyze_video("storage/live_production/job_2_surrumantadiro/surrumantadiro_4k_dance_master.mp4", "dance_folk")
