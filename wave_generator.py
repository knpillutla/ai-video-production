import os
import glob
import math
import argparse
import cv2
import numpy as np
from ultralytics import YOLO

def detect_water_body(img):
    """Adaptive multi-cue CV water detection (color distribution, gradient smoothness, structural connectivity)."""
    h, w, _ = img.shape
    scale = 540.0 / h
    small_w, small_h = int(w * scale), 540
    small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small_img, cv2.COLOR_BGR2HSV)
    b, g, r = cv2.split(small_img.astype(np.float32))
    blue_dominance = (b >= r * 0.95) & (b + g > 2 * r * 0.9)
    hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    cyan_blue = (hue >= 70) & (hue <= 140) & (sat >= 15) & (val >= 20) & (b > r * 0.9)
    emerald = (hue >= 35) & (hue < 70) & (sat >= 25) & (b >= r * 0.85) & (g > r)
    dark_fjord = (val < 100) & (b >= r) & (hue >= 65) & (hue <= 145) & (val >= 15)
    foam = (val > 190) & (sat < 45) & (blue_dominance | (hue >= 60))
    color_cand = (cyan_blue | emerald | dark_fjord | foam) & blue_dominance
    gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    smooth_grad = cv2.magnitude(sobel_x, sobel_y) < 28.0
    water_cand = (color_cand & smooth_grad) | (foam & (b >= r * 0.9))
    water_cand[:int(small_h * 0.35), :] = False
    if np.mean(water_cand[int(small_h * 0.5):, :]) < 0.05:
        return np.zeros((h, w), dtype=np.uint8)
    kernel_horiz = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
    closed = cv2.morphologyEx(water_cand.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel_horiz)
    cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
    final_small = np.zeros((small_h, small_w), dtype=np.uint8)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > (small_w * small_h * 0.04) and (stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT]) > (small_h * 0.6):
            final_small[labels == i] = 255
    contours, _ = cv2.findContours(final_small, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(final_small)
    for cnt in contours:
        if cv2.contourArea(cnt) > (small_w * small_h * 0.04):
            cv2.drawContours(filled, [cnt], -1, 255, -1)
    full_mask = cv2.resize(filled, (w, h), interpolation=cv2.INTER_LINEAR)
    _, full_mask = cv2.threshold(full_mask, 127, 255, cv2.THRESH_BINARY)
    return full_mask


def process_moving_objects_on_cpu(input_folder, output_folder, fps=30, duration_seconds=10):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)
    
    print("Loading local instance model onto CPU...")
    model = YOLO("yolov8n-seg.pt")
    
    # Strictly filter out file casing duplicates
    extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp', '*.PNG', '*.JPG')
    raw_paths = []
    for ext in extensions:
        raw_paths.extend(glob.glob(os.path.join(input_folder, ext)))
    unique_paths = sorted(list(set(os.path.abspath(p) for p in raw_paths)))
    
    total_frames = fps * duration_seconds
    print(f"Found {len(unique_paths)} unique files to process on CPU...")

    for file_idx, img_path in enumerate(unique_paths):
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        print(f"\n[Processing {file_idx+1}/{len(unique_paths)}]: {os.path.basename(img_path)}")
        
        orig_img = cv2.imread(img_path)
        if orig_img is None:
            continue
        h, w, _ = orig_img.shape
        
        results = model.predict(source=orig_img, device="cpu", verbose=False)
        result = results[0]
        
        human_mask = np.zeros((h, w), dtype=np.uint8)
        if result.masks is not None:
            for mask_data, box_data in zip(result.masks.xy, result.boxes):
                if int(box_data.cls) == 0:  # Person
                    poly = np.array(mask_data, dtype=np.int32)
                    if len(poly) >= 3:
                        cv2.fillPoly(human_mask, [poly], 255)

        # Multi-cue CV Water Body Detection
        raw_water_mask = detect_water_body(orig_img)
        water_mask = cv2.bitwise_and(raw_water_mask, cv2.bitwise_not(human_mask))
        mountain_mask = np.zeros((h, w), dtype=np.uint8)
        if np.sum(water_mask) > 0:
            y_indices, _ = np.where(water_mask > 0)
            water_top = np.min(y_indices) if len(y_indices) > 0 else int(h * 0.6)
            mountain_mask[int(h * 0.3):water_top, :] = 255
            mountain_mask = cv2.bitwise_and(mountain_mask, cv2.bitwise_not(human_mask))
            
        water_contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mountain_contours, _ = cv2.findContours(mountain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        human_contours, _ = cv2.findContours(human_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # --- ASSET 1: Diagnostic Labeled Marking Output ---
        marking_img = orig_img.copy()
        marking_img[water_mask > 100] = (marking_img[water_mask > 100] * 0.6 + np.array([255, 255, 0]) * 0.4).astype(np.uint8)
        marking_img[mountain_mask > 100] = (marking_img[mountain_mask > 100] * 0.6 + np.array([0, 0, 255]) * 0.4).astype(np.uint8)
        marking_img[human_mask > 100] = (marking_img[human_mask > 100] * 0.6 + np.array([0, 255, 0]) * 0.4).astype(np.uint8)
        
        if water_contours:
            cv2.putText(marking_img, "WATER", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        if human_contours:
            cv2.putText(marking_img, "HUMAN DETECTED", (20, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(output_folder, f"{base_name}_water_area_marking.jpg"), marking_img)

        # --- ASSET 2: Clean Boundaries Outlines ---
        boundary_img = orig_img.copy()
        if water_contours: cv2.drawContours(boundary_img, water_contours, -1, (255, 255, 0), 2, cv2.LINE_AA)
        if mountain_contours: cv2.drawContours(boundary_img, mountain_contours, -1, (0, 0, 255), 2, cv2.LINE_AA)
        if human_contours: cv2.drawContours(boundary_img, human_contours, -1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(output_folder, f"{base_name}_water_boundary_only.jpg"), boundary_img)

        # --- ASSET 3: Vectorized Video Engine (Waves + Human Motion) ---
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = os.path.join(output_folder, f"{base_name}_motion_simulation_10s.mp4")
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (w, h))
        
        print(" -> Vectorizing wave space and human walking paths concurrently...")
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x_32 = map_x.astype(np.float32)
        map_y_32 = map_y.astype(np.float32)
        
        water_normalized = cv2.GaussianBlur(water_mask, (11, 11), 0).astype(np.float32) / 255.0
        water_mask_3d = np.expand_dims(water_normalized, axis=2)
        
        amplitude = 6
        frequency = 0.05
        speed = 0.2
        
        # Max horizontal translation path for the person across 10 seconds
        max_walk_pixels = int(w * 0.15) 

        for frame_idx in range(total_frames):
            # 1. Apply procedural wave engine to the water layer
            shift_x = map_x_32 + amplitude * np.sin(2 * math.pi * frequency * map_y_32 + frame_idx * speed)
            distorted_frame = cv2.remap(orig_img, shift_x, map_y_32, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            blended_frame = (distorted_frame * water_mask_3d) + (orig_img * (1.0 - water_mask_3d))
            blended_frame = blended_frame.astype(np.uint8)
            
            # 2. Translate human mask over time (Walking motion)
            if np.sum(human_mask) > 0:
                # Calculate current horizontal translation offset step
                offset = int((frame_idx / total_frames) * max_walk_pixels)
                
                # Generate tracking translation shift matrix
                translation_matrix = np.float32([[1, 0, offset], [0, 1, 0]])
                
                # Shift human pixels across the baseline frame
                shifted_human_pixels = cv2.warpAffine(orig_img, translation_matrix, (w, h))
                shifted_human_mask = cv2.warpAffine(human_mask, translation_matrix, (w, h))
                
                # Feather edges of the moving human
                human_mask_blurred = cv2.GaussianBlur(shifted_human_mask, (7, 7), 0).astype(np.float32) / 255.0
                human_mask_3d = np.expand_dims(human_mask_blurred, axis=2)
                
                # Composite the shifted person back onto the frame with water waves
                blended_frame = ((shifted_human_pixels * human_mask_3d) + (blended_frame * (1.0 - human_mask_3d))).astype(np.uint8)

            # Draw static HUD guide markings on top
            if water_contours: cv2.drawContours(blended_frame, water_contours, -1, (255, 255, 0), 2, cv2.LINE_AA)
            if mountain_contours: cv2.drawContours(blended_frame, mountain_contours, -1, (0, 0, 255), 2, cv2.LINE_AA)
            
            video_writer.write(blended_frame)
            
        video_writer.release()
        print(f" -> Successfully finalized rendering: {video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True)
    parser.add_argument("-o", "--output", type=str, default="output_results")
    args = parser.parse_args()
    process_moving_objects_on_cpu(args.input, args.output)
