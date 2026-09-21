import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

exe = get_ffmpeg_binary()
p = Path("storage/user-c33148b6-aab4-4cf7-b9fe-5c8c3ee3c85e/creative_vault/shows_and_titles/porto_walking_tour_exploring_sun/episodes/f86d1d97-a360-4e4b-959b-dd2247fc0840/master_renders")
scenes = sorted(list(p.parent.glob("scenes/*_motion.mp4")))
lines = [f"file '{s.resolve().as_posix()}'" for s in scenes]
txt = p / "concat_inputs.txt"
txt.write_text("\n".join(lines), encoding="utf-8")
out = p / "master_16x9_ep01.mp4"
cmd = [exe, "-y", "-f", "concat", "-safe", "0", "-i", txt.resolve().as_posix(), "-c", "copy", "-movflags", "+faststart", out.resolve().as_posix()]

t0 = time.perf_counter()
res = subprocess.run(cmd, capture_output=True, text=True)
elapsed = round(time.perf_counter() - t0, 3)
print(f"Code: {res.returncode} | Elapsed: {elapsed}s | Size: {out.stat().st_size} bytes")
if res.returncode != 0:
    print("Error:", res.stderr)
