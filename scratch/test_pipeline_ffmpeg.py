import subprocess
import imageio_ffmpeg
from pathlib import Path
from src.compositor.vocal_fx import compile_vocal_filter_complex

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
sub_path = Path("scratch/test_mandali.ass")
fonts_dir = Path("storage/fonts/te")

# Replace line in vocal_fx or test directly
clean_sub = sub_path.resolve().as_posix().replace(":", r"\\:")
clean_font = f":fontsdir={fonts_dir.resolve().as_posix().replace(':', r'\\:')}"
sub_filter = f"subtitles=filename={clean_sub}{clean_font}"

cmd = [
    ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=1",
    "-vf", sub_filter, "-update", "1", "-vframes", "1", "scratch/test_pipeline_filter.png"
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Pipeline filter returncode:", res.returncode)
if res.returncode != 0:
    print(res.stderr[-400:])
else:
    print("SUCCESSFULLY PARSED AND RENDERED!")
