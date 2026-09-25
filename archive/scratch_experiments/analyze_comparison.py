"""Extract comparative sample frames and bitrates across the 3 nature documentary masters."""

import subprocess
import imageio_ffmpeg
from pathlib import Path

exe = imageio_ffmpeg.get_ffmpeg_exe()
out_dir = Path("scratch/analysis/comparison_frames")
out_dir.mkdir(parents=True, exist_ok=True)

videos = {
    "kling_10s": Path("storage/live_production/wild_canada_documentary_10s/wild_canada_nature_documentary_4k_master.mp4"),
    "h3_15s": Path("storage/live_production/wild_canada_minimax_h3_test/wild_canada_nature_documentary_4k_h3_master.mp4"),
    "wan21_15s": Path("storage/live_production/wild_canada_wan21_test/wild_canada_nature_documentary_4k_wan21_master.mp4"),
}

for name, vpath in videos.items():
    if not vpath.exists():
        print(f"[!] {name} not found at {vpath}")
        continue
    # Extract frame at 2.0s
    frame_path = out_dir / f"{name}_f2s.jpg"
    cmd = [exe, "-y", "-ss", "2.0", "-i", str(vpath), "-vframes", "1", "-q:v", "2", str(frame_path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Extracted {frame_path.name} ({frame_path.stat().st_size} bytes)")

print("Analysis extraction complete.")
