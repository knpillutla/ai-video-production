"""Extract sample frame from Hunyuan 4K master for quality evaluation."""

import subprocess
import imageio_ffmpeg
from pathlib import Path

exe = imageio_ffmpeg.get_ffmpeg_exe()
vpath = Path("storage/live_production/wild_canada_hunyuan_test/wild_canada_hunyuan_4k_master.mp4")
frame_path = Path("scratch/analysis/comparison_frames/hunyuan_4k_f2s.jpg")

cmd = [exe, "-y", "-ss", "2.0", "-i", str(vpath), "-vframes", "1", "-q:v", "2", str(frame_path)]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Extracted {frame_path.name} ({frame_path.stat().st_size} bytes)")
