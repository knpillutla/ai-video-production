import subprocess
import os
from pathlib import Path
from PIL import Image

def render_indic_text_directwrite(
    text: str,
    font_size: int = 120,
    color: str = "#ffffff",
    max_width: int = 3400,
    shadow: bool = True
) -> Image.Image | None:
    """Render Indic / complex script text using Windows DirectWrite via headless Edge with perfect shaping."""
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge = next((p for p in edge_paths if os.path.exists(p)), None)
    if not edge:
        return None

    # Compute viewport height
    vp_h = max(200, int(font_size * 2.2))
    vp_w = max_width

    shadow_css = "text-shadow: 0 4px 18px rgba(0,0,0,0.9), 0 2px 6px rgba(0,0,0,0.95);" if shadow else ""
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    background: transparent !important;
    margin: 0;
    padding: 0;
    width: {vp_w}px;
    height: {vp_h}px;
    overflow: hidden;
  }}
  .text-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    text-align: center;
    font-family: 'Nirmala UI', 'Mandali', 'Ramabhadra', sans-serif;
    font-size: {font_size}px;
    font-weight: 700;
    color: {color};
    {shadow_css}
    white-space: nowrap;
  }}
</style>
</head>
<body>
  <div class="text-container">{text}</div>
</body>
</html>"""

    scratch_dir = Path("scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    h_file = scratch_dir / "_indic_tmp.html"
    s_file = scratch_dir / "_indic_tmp.png"
    h_file.write_text(html, encoding="utf-8")

    cmd = [
        edge,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={vp_w},{vp_h}",
        "--default-background-color=00000000",
        f"--screenshot={s_file.resolve().as_posix()}",
        f"file:///{h_file.resolve().as_posix()}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=10)
        if res.returncode == 0 and s_file.exists():
            img = Image.open(s_file).convert("RGBA")
            # Auto-crop bounding box of non-transparent pixels
            bbox = img.getbbox()
            if bbox:
                return img.crop(bbox)
            return img
    except Exception as e:
        print("DirectWrite render failed:", e)
    return None

if __name__ == "__main__":
    rendered = render_indic_text_directwrite("దసరా డప్పు దుమ్ము (Dussehra Dappu Dummu)", font_size=110)
    if rendered:
        rendered.save("scratch/test_cropped_indic.png")
        print("Rendered successfully! Size:", rendered.size)
    else:
        print("Failed to render.")
