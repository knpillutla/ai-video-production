import subprocess
from pathlib import Path
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Ramabhadra,60,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{\\pos(960,540)}దసరా డప్పు దుమ్ము
"""
ass_path = Path("scratch/test_te.ass").resolve()
ass_path.write_text(ass_content, encoding="utf-8")

# In ffmpeg filters, escape backslashes and colons:
escaped_ass = ass_path.as_posix().replace(":", r"\:")
font_dir = Path("storage/fonts/te").resolve().as_posix().replace(":", r"\:")
out_img = Path("scratch/test_te_ass.png").resolve().as_posix()

cmd = [
    get_ffmpeg_binary(), "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=1",
    "-vf", f"subtitles='{escaped_ass}':fontsdir='{font_dir}'",
    "-frames:v", "1", out_img
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
if res.returncode != 0:
    print("Stderr:", res.stderr[-500:])
print("Output file exists:", Path(out_img).exists())
