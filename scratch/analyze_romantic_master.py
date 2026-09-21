import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image
import numpy as np
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

def analyze():
    vid = Path("storage/live_production/telangana_romantic_dance_10s/telangana_romantic_dance_10s_4k_master.mp4")
    ffmpeg_bin = get_ffmpeg_binary()
    probe_cmd = [ffmpeg_bin, "-i", str(vid)]
    p_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    print("=== FFmpeg Probe Output ===")
    for line in p_res.stderr.splitlines():
        if any(k in line for k in ("Duration:", "Stream #0:0", "Stream #0:1")):
            print("  ", line.strip())

    sample_dir = Path("scratch/analysis/telangana_romantic_10s")
    sample_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin, "-y", "-i", str(vid),
        "-vf", "fps=1/3",
        "-vframes", "3",
        str(sample_dir / "frame_%02d.jpg")
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frames = list(sample_dir.glob("frame_*.jpg"))
    if frames:
        arr = np.array(Image.open(frames[0]).convert("RGB"), dtype=np.float32)
        r, g, b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
        yellow_cast = ((r + g) / 2.0) - b
        print(f"\nColor Metrics (Frame 1): R={r:.1f}, G={g:.1f}, B={b:.1f}, Yellow Index={yellow_cast:.1f}")

if __name__ == "__main__":
    analyze()
