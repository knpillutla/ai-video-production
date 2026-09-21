import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

def extract_and_analyze(video_path: str, name: str):
    ffmpeg_bin = get_ffmpeg_binary()
    out_dir = Path("scratch/analysis") / name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract 5 sample frames
    cmd = [
        ffmpeg_bin, "-y", "-i", video_path,
        "-vf", "fps=1",
        "-vframes", "5",
        str(out_dir / "frame_%02d.jpg")
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Analyze color in extracted frames
    frames = sorted(list(out_dir.glob("frame_*.jpg")))
    r_list, g_list, b_list = [], [], []
    for f in frames:
        img = Image.open(f).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        r = arr[:, :, 0].mean()
        g = arr[:, :, 1].mean()
        b = arr[:, :, 2].mean()
        r_list.append(r)
        g_list.append(g)
        b_list.append(b)
        
    avg_r = np.mean(r_list) if r_list else 0
    avg_g = np.mean(g_list) if g_list else 0
    avg_b = np.mean(b_list) if b_list else 0
    # Yellow cast index = (R + G)/2 - B
    # High positive number indicates strong yellow/warm tint
    yellow_cast = ((avg_r + avg_g) / 2.0) - avg_b
    
    print(f"=== {name} ===")
    print(f"Frames analyzed: {len(frames)}")
    print(f"Average RGB: R={avg_r:.1f}, G={avg_g:.1f}, B={avg_b:.1f}")
    print(f"Warmth / Yellow Cast Index: {yellow_cast:.1f}")
    print(f"R/B Ratio: {avg_r / (avg_b + 1e-5):.2f}, G/B Ratio: {avg_g / (avg_b + 1e-5):.2f}")
    print(f"Frames saved in: {out_dir}")
    print()

if __name__ == "__main__":
    extract_and_analyze("storage/live_production/job_1_swiss_alps/swiss_alps_4k_walk_master.mp4", "swiss_alps")
    extract_and_analyze("storage/live_production/job_2_surrumantadiro/surrumantadiro_4k_dance_master.mp4", "dance_folk")
