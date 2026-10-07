import os
import argparse
import random
import cv2
import numpy as np
from scipy.interpolate import CubicSpline
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

def generate_cinematic_path(total_frames, num_waypoints=6):
    """
    Generates a highly varied, multi-angle random flight path using 
    Cubic Spline interpolation to map smooth cinematic nodes.
    """
    waypoint_frames = np.linspace(0, total_frames - 1, num_waypoints)
    
    scales = []
    x_pcts = []
    y_pcts = []
    
    # Base zoom bounds: 0.55 ensures sharp texture preservation while zooming
    min_scale, max_scale = 0.55, 0.90  
    
    # Frame 0: Initialize starting flight vectors
    scales.append(random.uniform(0.75, max_scale))
    x_pcts.append(random.uniform(0.25, 0.45))
    y_pcts.append(random.uniform(0.40, 0.60))
    
    for i in range(num_waypoints - 1):
        next_scale = random.uniform(min_scale, max_scale)
        while abs(next_scale - scales[-1]) < 0.12:
            next_scale = random.uniform(min_scale, max_scale)
            
        scales.append(next_scale)
        x_pcts.append(random.uniform(0.18, 0.82))
        y_pcts.append(random.uniform(0.30, 0.70))
        
    timeline = np.arange(total_frames)
    cs_scale = CubicSpline(waypoint_frames, scales, bc_type='clamped')
    cs_x = CubicSpline(waypoint_frames, x_pcts, bc_type='clamped')
    cs_y = CubicSpline(waypoint_frames, y_pcts, bc_type='clamped')
    
    smooth_scales = np.clip(cs_scale(timeline), min_scale, max_scale)
    smooth_x = np.clip(cs_x(timeline), 0.15, 0.85)
    smooth_y = np.clip(cs_y(timeline), 0.25, 0.75)
    
    return smooth_scales, smooth_x, smooth_y

def process_premium_tours(input_dir, output_dir, duration_sec):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    images = [f for f in os.listdir(input_dir) if f.endswith(extensions)]

    if not images:
        print(f"Error: No images located inside: {input_dir}")
        return

    fps = 30
    total_frames = int(duration_sec * fps)
    output_size = (1920, 1080)
    target_w, target_h = output_size
    target_aspect = target_w / target_h

    print(f"--- High-Clarity Multi-Angle Director Engaged ---")

    for img_name in images:
        img_path = os.path.join(input_dir, img_name)
        output_path = os.path.join(output_dir, f"{os.path.splitext(img_name)}_cinematic.mp4")
        
        print(f"\n[Processing] Analyzing Image: {img_name}")
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        h, w, _ = img.shape
        scales, x_pcts, y_pcts = generate_cinematic_path(total_frames)
        
        video_frames = []
        print(f" -> Rendering crisp flight frames ({total_frames} total)...")
        
        for i in range(total_frames):
            scale = scales[i]
            
            # Pure fixed-base layout calculation to protect original resolution
            if (w / h) > target_aspect:
                crop_h = int(h * scale)
                crop_w = int(crop_h * target_aspect)
            else:
                crop_w = int(w * scale)
                crop_h = int(crop_w / target_aspect)
                
            center_x = w * x_pcts[i]
            center_y = h * y_pcts[i]
            
            half_w, half_h = crop_w / 2.0, crop_h / 2.0
            
            # Strict float boundaries layout
            if center_x - half_w < 0: center_x = half_w
            if center_x + half_w > w: center_x = w - half_w
            if center_y - half_h < 0: center_y = half_h
            if center_y + half_h > h: center_y = h - half_h
            
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
            
            # Sub-pixel transformation mapping
            matrix = cv2.getAffineTransform(src_pts, dst_pts)
            frame = cv2.warpAffine(img, matrix, output_size, flags=cv2.INTER_LANCZOS4)
            video_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
        print(f" -> Encoding stream file with master parameters...")
        video_clip = ImageSequenceClip(video_frames, fps=fps)
        
        # High bitrate (24000k) stops compression blur completely
        video_clip.write_videofile(
            output_path, 
            fps=fps, 
            codec='libx264', 
            bitrate="24000k", 
            preset="slow"
        )
        print(f"[Done] Clean cinematic tour ready: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pristine multi-angle drone flights over high-res images.")
    parser.add_argument("-i", "--input", required=True, help="Input directory path")
    parser.add_argument("-o", "--output", required=True, help="Output folder path")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Duration length in seconds")
    
    args = parser.parse_args()
    process_premium_tours(args.input, args.output, args.duration)
