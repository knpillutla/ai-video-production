import asyncio
from pathlib import Path
import cv2
import subprocess
import imageio_ffmpeg
from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync

ep_dir = Path("storage/user-knpillutla-gmail-com/networks/euro_discovery/documentary/top_5_wonders_in_europe/ep-001")
kf6 = ep_dir / "keyframe_p6.jpg"
out_clip = ep_dir / "motion_p6.mp4"

print("Re-rendering motion_p6.mp4 with updated engine (no sky smoke, clean perspective)...")
render_perspective_drone_clip_sync(
    image_path=kf6,
    output_path=out_clip,
    duration_seconds=12.0,
    fps=24,
    target_res=(3840, 2160),
    choreography="dollyin",
    curve="cosine",
    force_rerun=True,
    water=False,
    smoke=False,
)
print("Rendered motion_p6.mp4! Extracting test frame 50...")
ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
verify_img = ep_dir / "verify_p6_frame50.jpg"
cmd = [ffmpeg_bin, "-y", "-ss", "00:00:02.00", "-i", str(out_clip), "-vframes", "1", str(verify_img)]
subprocess.run(cmd, check=True)
print(f"Extracted {verify_img.name} (size: {verify_img.stat().st_size} bytes)")
