import cv2
import numpy as np
from pathlib import Path

img_path = Path("storage/user-knpillutla-gmail-com/networks/euro_discovery/documentary/top_5_wonders_in_europe/ep-001/keyframe_p7.jpg")
img = cv2.imread(str(img_path))
h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 1. Texture gradient gate
grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
grad_mag = cv2.magnitude(grad_x, grad_y)
terrain_edges = (grad_mag > 28.0).astype(np.uint8)
terrain_zone = cv2.dilate(terrain_edges, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))

# 2. Water candidate spectrum
c_classic = (hsv[:, :, 0] >= 85) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] >= 20) & (hsv[:, :, 2] >= 20)
c_turquoise = (hsv[:, :, 0] >= 65) & (hsv[:, :, 0] <= 90) & (hsv[:, :, 1] >= 20) & (hsv[:, :, 2] >= 20)
c_dark_ocean = (hsv[:, :, 0] >= 75) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] >= 10) & (hsv[:, :, 2] >= 15) & (hsv[:, :, 2] <= 100)
c_foam_specular = (hsv[:, :, 0] >= 60) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] <= 45) & (hsv[:, :, 2] >= 150)
water_cand = (c_classic | c_turquoise | c_dark_ocean | c_foam_specular)
water_cand[:int(h * 0.20), :] = False
water_cand[terrain_zone > 0] = False

# 3. Morphological cleaning & connected components
k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
water_clean = cv2.morphologyEx(water_cand.astype(np.uint8) * 255, cv2.MORPH_OPEN, k_open)
num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(water_clean)
min_area = int(0.005 * w * h)
water_body = np.zeros_like(water_clean)
for lbl in range(1, num_labels):
    if stats[lbl, cv2.CC_STAT_AREA] >= min_area:
        water_body[labels == lbl] = 255

# 4. Strict inward safety buffer (15px) + internal distance transform
k_buffer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
water_buffered = cv2.erode(water_body, k_buffer)
dist = cv2.distanceTransform(water_buffered, cv2.DIST_L2, 5)
max_d = 20.0 * (w / 1920.0)
water_weight = np.clip(dist / max_d, 0.0, 1.0).astype(np.float32)

print(f"p7 ocean detected: raw_cand={np.mean(water_cand):.4f}, body={np.mean(water_body > 0):.4f}, buffered={np.mean(water_buffered > 0):.4f}")

# Save visualization overlay (green = water displacement zone, red = buffer boundary)
overlay = img.copy()
overlay[water_body > 0] = overlay[water_body > 0] * 0.5 + np.array([0, 0, 180]) * 0.5 # Red: raw water boundary
overlay[water_buffered > 0] = overlay[water_buffered > 0] * 0.3 + np.array([0, 220, 0]) * 0.7 # Green: safe water motion zone

cv2.imwrite("storage/user-knpillutla-gmail-com/networks/euro_discovery/documentary/top_5_wonders_in_europe/ep-001/verify_p7_water_mask.jpg", overlay)
print("Saved verify_p7_water_mask.jpg")
