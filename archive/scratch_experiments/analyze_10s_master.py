import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

def analyze_new_master():
    vid = Path("storage/live_production/job_mass_dance_10s/telugu_mass_dance_10s_4k_master.mp4")
    sample_dir = Path("scratch/analysis/mass_dance_10s_master")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    ffmpeg_bin = get_ffmpeg_binary()
    # Extract 3 sample frames across the 10 seconds
    cmd = [
        ffmpeg_bin, "-y", "-i", str(vid),
        "-vf", "fps=1/3",
        "-vframes", "3",
        str(sample_dir / "frame_%02d.jpg")
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Probe video metadata
    probe_cmd = [
        ffmpeg_bin, "-i", str(vid)
    ]
    p_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    print("=== FFmpeg Probe Output ===")
    for line in p_res.stderr.splitlines():
        if any(k in line for k in ("Duration:", "Stream #0:0", "Stream #0:1")):
            print("  ", line.strip())
            
    frames = list(sample_dir.glob("frame_*.jpg"))
    if frames:
        arr = np.array(Image.open(frames[0]).convert("RGB"), dtype=np.float32)
        r, g, b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
        yellow_cast = ((r + g) / 2.0) - b
        print(f"\nColor Metrics (Frame 1): R={r:.1f}, G={g:.1f}, B={b:.1f}, Yellow Index={yellow_cast:.1f}")

if __name__ == "__main__":
    analyze_new_master()
