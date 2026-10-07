import os
import argparse
import random
import cv2
import numpy as np
from scipy.interpolate import CubicSpline
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

def generate_cinematic_path(img_shape, total_frames, num_waypoints=6):
    """
    Generates a highly varied, multi-angle random flight path using 
    Cubic Spline interpolation to connect organic camera points.
    """
    h, w, _ = img_shape
    
    # Safe boundaries for the 16:9 crop window
    # 0.40 = Deep architecture zoom, 0.85 = Wide panorama view
    min_scale, max_scale = 0.40, 0.85  
    
    # Generate waypoints spaced evenly across the total video duration
    waypoint_frames = np.linspace(0, total_frames - 1, num_waypoints)
    
    scales = []
    x_pcts = []
    y_pcts = []
    
    # Frame 0: Initialize at a random location
    scales.append(random.uniform(0.70, max_scale))
    x_pcts.append(random.uniform(0.20, 0.40))
    y_pcts.append(random.uniform(0.35, 0.65))
    
    # Generate organic multi-angle waypoints (zooms, pans, tilts, crane movements)
    for i in range(num_waypoints - 1):
        # Force a meaningful zoom change so it never feels flat or static
        next_scale = random.uniform(min_scale, max_scale)
        while abs(next_scale - scales[-1]) < 0.15:
            next_scale = random.uniform(min_scale, max_scale)
            
        scales.append(next_scale)
        # Random wide sweeps across the panorama canvas
        x_pcts.append(random.uniform(0.15, 0.85))
        # Random altitude adjustments (crane up / glide down)
        y_pcts.append(random.uniform(0.25, 0.75))
        
    # Use continuous Cubic Splines with clamped boundaries to eliminate sharp velocity changes
    frames_axis = np.arange(total_frames)
    cs_scale = CubicSpline(waypoint_frames, scales, bc_type='clamped')
    cs_x = CubicSpline(waypoint_frames, x_pcts, bc_type='clamped')
    cs_y = CubicSpline(waypoint_frames, y_pcts, bc_type='clamped')
    
    # Synthesize smooth, fluid timelines for the entire video clip
    smooth_scales = np.clip(cs_scale(frames_axis), min_scale, max_scale)
    smooth_x = np.clip(cs_x(frames_axis), 0.12, 0.88)
    smooth_y = np.clip(cs_y(frames_axis), 0.20, 0.80)
    
    return smooth_scales, smooth_x, smooth_y

def render_stabilized_frame(img, scale, cx_pct, cy_pct, output_size=(1920, 1080)):
    """
    Applies high-precision sub-pixel floating point math to completely 
    eliminate pixel-rounding jitters or shaking.
    """
    h, w, _ = img.shape
    target_w, target_h = output_size
    target_aspect = target_w / target_h
    
    crop_h = h * scale
    crop_w = crop_h * target_aspect
    
    if crop_w > w:
        crop_w = w
        crop_h = crop_w / target_aspect
        
    center_x = w * cx_pct
    center_y = h * cy_pct
    
    # Clamp bounding windows safely within image margins
    half_w, half_h = crop_w / 2.0, crop_h / 2.0
    if center_x - half_w < 0: center_x = half_w
    if center_x + half_w > w: center_x = w - half_w
    if center_y - half_h < 0: center_y = half_h
    if center_y + half_h > h: center_y = h - half_h
    
    # High-precision floating point control matrices
    src_pts = np.array([
        [center_x - half_w, center_y - half_h],
        [center_x + half_w, center_y - half_h],
        [center_x - half_w, center_y + half_h]
    ], dtype=np.float32)
    
    dst_pts = np.array([
        [0.0, 0.0],
        [float(target_w), 0.0],
        [0.0, float(target_h)]
    ], dtype=np.float32)
    
    # Affine matrix transformation creates perfect pixel gliding
    matrix = cv2.getAffineTransform(src_pts, dst_pts)
    return cv2.warpAffine(img, matrix, output_size, flags=cv2.INTER_LANCZOS4)

def process_random_tours(input_dir, output_dir, duration_sec):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    images = [f for f in os.listdir(input_dir) if f.endswith(extensions)]

    if not images:
        print(f"Error: No images found inside: {input_dir}")
        return

    fps = 30
    total_frames = int(duration_sec * fps)
    print(f"--- Stabilized Random Director Loaded ---")
    print(f"Processing {len(images)} files for {duration_sec}s flights...")

    for img_name in images:
        img_path = os.path.join(input_dir, img_name)
        output_path = os.path.join(output_dir, f"{os.path.splitext(img_name)}_stabilized_tour.mp4")
        
        print(f"\n[Mapping Engine] Mapping random paths for: {img_name}")
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        # Call our organic random trajectory engine
        scales, x_pcts, y_pcts = generate_cinematic_path(img.shape, total_frames)
        
        video_frames = []
        print(f" -> Rendering fluid camera motions ({total_frames} frames)...")
        
        for i in range(total_frames):
            frame = render_stabilized_frame(img, scales[i], x_pcts[i], y_pcts[i])
            video_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
        print(f" -> Encoding cinematic stream file...")
        video_clip = ImageSequenceClip(video_frames, fps=fps)
        
        video_clip.write_videofile(
            output_path, 
            fps=fps, 
            codec='libx264', 
            bitrate="18000k", 
            preset="medium"
        )
        print(f"[Done] Video generated smoothly: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smooth multi-angle random drone flights over panoramas.")
    parser.add_argument("-i", "--input", required=True, help="Input folder of panoramic images")
    parser.add_argument("-o", "--output", required=True, help="Output folder for MP4 videos")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Video duration in seconds")
    
    args = parser.parse_args()
    process_random_tours(args.input, args.output, args.duration)
