import cv2
import numpy as np
from pathlib import Path

ep_dir = Path("storage/user-knpillutla-gmail-com/networks/euro_discovery/documentary/top_5_wonders_in_europe/ep-001")
kfs = sorted(ep_dir.glob("stage1_keyframe_p*.jpg"))
print(f"Found {len(kfs)} keyframes in ep-001:")
for k in kfs:
    print(" ", k.name)
