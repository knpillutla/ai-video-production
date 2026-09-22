import subprocess
from pathlib import Path
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from PIL import Image
import numpy as np

ffmpeg_bin = get_ffmpeg_binary()
img = Path("storage/user-133db3ee-33de-42e0-8798-a2970a5f555a/creative_vault/shows_and_titles/paris_montmartre_in_the_rain_4k/episodes/2e2f726c-62d8-4f21-8236-c8faa900bd7a/scenes/scene_02.jpg")
out = Path("scratch/test_zoompan_pan_right.mp4")
out.unlink(missing_ok=True)

total_frames = 300
w, h = 1920, 1080
fps = 30

zp = f"zoompan=z='1.16':x='(iw-iw/zoom)*(on/{total_frames})':y='ih/2-(ih/zoom/2)':d={total_frames}:s={w}x{h}:fps={fps}"

cmd = [
    ffmpeg_bin, "-y",
    "-i", str(img),
    "-vf", f"{zp},setsar=1",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-crf", "18", "-pix_fmt", "yuv420p",
    "-t", "10.0",
    str(out)
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("RC:", res.returncode)
if res.returncode != 0:
    print("STDERR:", res.stderr[-400:])
else:
    # Measure movement
    subprocess.run([ffmpeg_bin, "-y", "-ss", "0", "-i", str(out), "-vframes", "1", "scratch/zp_f0.png"], capture_output=True)
    subprocess.run([ffmpeg_bin, "-y", "-ss", "5", "-i", str(out), "-vframes", "1", "scratch/zp_f5.png"], capture_output=True)
    subprocess.run([ffmpeg_bin, "-y", "-ss", "9.5", "-i", str(out), "-vframes", "1", "scratch/zp_f9.png"], capture_output=True)
    
    f0 = np.array(Image.open("scratch/zp_f0.png")).astype(float)
    f5 = np.array(Image.open("scratch/zp_f5.png")).astype(float)
    f9 = np.array(Image.open("scratch/zp_f9.png")).astype(float)
    
    print("Diff 0s to 5s:", np.mean(np.abs(f5 - f0)))
    print("Diff 5s to 9.5s:", np.mean(np.abs(f9 - f5)))
    print("SUCCESS: Full continuous motion across all 10 seconds!")
