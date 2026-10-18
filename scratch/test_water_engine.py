import cv2
import numpy as np
from pathlib import Path

ep_dir = Path("storage/user-knpillutla-gmail-com/networks/euro_discovery/documentary/top_5_wonders_in_europe/ep-001")

for i in range(1, 11):
    kf_path = ep_dir / f"keyframe_p{i}.jpg"
    img = cv2.imread(str(kf_path))
    if img is None:
        continue
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Check old smoke detector
    upper_hsv = hsv[:int(h * 0.40), :]
    upper_gray = gray[:int(h * 0.40), :]
    smoke_candidates = (upper_hsv[:, :, 1] < 45) & (upper_gray > 165) & (upper_gray < 245)
    plume_ratio = float(np.mean(smoke_candidates))
    has_smoke = 0.005 < plume_ratio < 0.10

    # Test new water boundary engine
    # 1. Texture gradient gate (anti-mountain)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(grad_x, grad_y)
    terrain_edges = (grad_mag > 30.0).astype(np.uint8)
    terrain_zone = cv2.dilate(terrain_edges, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))

    # 2. Adaptive water color candidates (lower 75% of image)
    c_classic = (hsv[:, :, 0] >= 85) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] >= 25) & (hsv[:, :, 2] >= 25)
    c_turquoise = (hsv[:, :, 0] >= 72) & (hsv[:, :, 0] <= 90) & (hsv[:, :, 1] >= 25) & (hsv[:, :, 2] >= 30)
    c_dark_ocean = (hsv[:, :, 0] >= 80) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] >= 15) & (hsv[:, :, 2] >= 15) & (hsv[:, :, 2] <= 90)
    c_specular = (hsv[:, :, 0] >= 70) & (hsv[:, :, 0] <= 145) & (hsv[:, :, 1] <= 35) & (hsv[:, :, 2] >= 170)
    water_cand = (c_classic | c_turquoise | c_dark_ocean | c_specular)
    # Mask out terrain & top 25% sky
    water_cand[:int(h * 0.25), :] = False
    water_cand[terrain_zone > 0] = False

    # 3. Morphological cleaning & connected components
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    water_clean = cv2.morphologyEx(water_cand.astype(np.uint8) * 255, cv2.MORPH_OPEN, k_open)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(water_clean)
    min_area = int(0.015 * w * h)
    water_body = np.zeros_like(water_clean)
    for lbl in range(1, num_labels):
        if stats[lbl, cv2.CC_STAT_AREA] >= min_area:
            water_body[labels == lbl] = 255

    # 4. Strict inward safety buffer (19px) + internal distance transform
    k_buffer = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    water_buffered = cv2.erode(water_body, k_buffer)
    dist = cv2.distanceTransform(water_buffered, cv2.DIST_L2, 5)
    max_d = 25.0 * (w / 1920.0)
    water_weight = np.clip(dist / max_d, 0.0, 1.0)
    water_coverage = float(np.mean(water_weight > 0.01))

    print(f"p{i} ({kf_path.name}): old_smoke={has_smoke} (plume_ratio={plume_ratio:.4f}) | new_water_coverage={water_coverage:.4f}")
