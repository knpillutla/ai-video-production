import subprocess
from pathlib import Path
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

txt = "దసరా డప్పు దుమ్ము"
txt_file = Path("scratch/test_te.txt")
txt_file.parent.mkdir(parents=True, exist_ok=True)
txt_file.write_text(txt, encoding="utf-8")

font_path = Path("C:/neel-1/projects/content-generation/storage/fonts/te/Ramabhadra-Regular.ttf").as_posix()
txt_path = txt_file.resolve().as_posix()
out_img = Path("scratch/test_te_ffmpeg.png").resolve().as_posix()

cmd = [
    get_ffmpeg_binary(), "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x200:d=1",
    "-vf", f"drawtext=textfile='{txt_path}':fontfile='{font_path}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
    "-frames:v", "1", out_img
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
if res.returncode != 0:
    print("Stderr:", res.stderr[-500:])
print("Output file exists:", Path(out_img).exists())
