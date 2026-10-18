import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
sub_path = Path("scratch/test_mandali.ass").resolve().as_posix()
fonts_dir = Path("storage/fonts/te").resolve().as_posix()

tests = [
    # 1. Double backslash escaped colon:
    f"subtitles=filename={sub_path.replace(':', r'\\:')}:fontsdir={fonts_dir.replace(':', r'\\:')}",
    # 2. Single quoted with forward slashes and colon escaped:
    f"subtitles='{sub_path.replace(':', r'\\:')}':fontsdir='{fonts_dir.replace(':', r'\\:')}'",
    # 3. Without escaping colon inside quotes:
    f"subtitles='{sub_path}':fontsdir='{fonts_dir}'",
    # 4. filename= keyword with quotes:
    f"subtitles=filename='{sub_path}':fontsdir='{fonts_dir}'",
    # 5. Double escaped backslash without quotes:
    f"subtitles={sub_path.replace(':', r'\:')}:fontsdir={fonts_dir.replace(':', r'\:')}",
]

for idx, t in enumerate(tests):
    cmd = [
        ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=1",
        "-vf", t, "-update", "1", "-vframes", "1", "scratch/test_esc.png"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Test {idx + 1}: {t} -> Code: {res.returncode}")
    if res.returncode != 0:
        for line in res.stderr.splitlines():
            if "Error parsing" in line or "No option name" in line:
                print("   ", line)
