import subprocess
import imageio_ffmpeg
from pathlib import Path
from PIL import Image
import numpy as np

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
fonts_dir = Path('storage/fonts/te').resolve().as_posix().replace(':', r'\:')

fonts_to_test = [
    ('Ramabhadra', 'storage/fonts/te/Ramabhadra-Regular.ttf'),
    ('Nirmala UI', 'C:/Windows/Fonts/Nirmala.ttc'),
    ('Gautami', 'C:/Windows/Fonts/gautami.ttf'),
    ('Mandali', 'storage/fonts/te/Mandali-Regular.ttf'),
]

for font_name, fpath in fonts_to_test:
    slug = font_name.replace(" ", "_")
    ass_content = f"""[Script Info]
Title: Font Test
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.0,1.0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,ఎద లోతున మోగిన రాగం నీ చల్లని స్పర్శగా
"""
    ass_path = Path(f"scratch/test_{slug}.ass")
    ass_path.write_text(ass_content, encoding="utf-8")
    clean_sub = ass_path.resolve().as_posix().replace(":", r"\:")

    out_png = f"scratch/out_{slug}.png"
    cmd = [
        ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=1",
        "-vf", f"subtitles={clean_sub}:fontsdir={fonts_dir}",
        "-update", "1", "-vframes", "1", out_png
    ]
    subprocess.run(cmd, capture_output=True)
    if Path(out_png).is_file():
        img = Image.open(out_png)
        arr = np.array(img)
        non_zero = np.where(arr > 0)
        if len(non_zero[0]) > 0:
            ymin, ymax = non_zero[0].min(), non_zero[0].max()
            xmin, xmax = non_zero[1].min(), non_zero[1].max()
            crop = img.crop((max(0, xmin-30), max(0, ymin-30), min(1920, xmax+30), min(1080, ymax+30)))
            crop_path = f"scratch/crop_{slug}.png"
            crop.save(crop_path)
            print(f"{font_name}: rendered! dims={xmax-xmin}x{ymax-ymin} saved to {crop_path}")
        else:
            print(f"{font_name}: black image")
    else:
        print(f"{font_name}: failed")
