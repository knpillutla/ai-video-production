"""Deterministic DirectWrite / HarfBuzz Indic Text Renderer for 4K Compositor.

Renders complex Indic scripts (Telugu, Hindi, Tamil, Bengali, Kannada, etc.)
with 100% authentic ligatures (vattulu/matras) using Windows DirectWrite via headless Edge.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from PIL import Image

_EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def is_complex_indic_script(text: str) -> bool:
    """Detect if text contains Indic / Brahmic characters needing complex HarfBuzz shaping."""
    return any(
        0x0900 <= ord(c) <= 0x0D7F  # Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada, Malayalam
        for c in text
    )


def render_indic_text_directwrite(
    text: str,
    font_size: int = 120,
    color: str = "#ffffff",
    max_width: int = 3400,
    shadow: bool = True,
) -> Image.Image | None:
    """Render Indic script text via Windows DirectWrite for authentic typography."""
    edge = next((p for p in _EDGE_PATHS if os.path.exists(p)), None)
    if not edge or not text.strip():
        return None

    vp_h = max(220, int(font_size * 2.2))
    vp_w = max_width
    shadow_css = "text-shadow: 0 4px 18px rgba(0,0,0,0.95), 0 2px 8px rgba(0,0,0,0.98);" if shadow else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    background: transparent !important;
    margin: 0; padding: 0;
    width: {vp_w}px; height: {vp_h}px;
    overflow: hidden;
  }}
  .text-container {{
    display: flex; justify-content: center; align-items: center;
    width: 100%; height: 100%; box-sizing: border-box; text-align: center;
    font-family: 'Nirmala UI', 'Mandali', 'Ramabhadra', sans-serif;
    font-size: {font_size}px; font-weight: 700; color: {color};
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
    h_file = scratch_dir / "_indic_card_tmp.html"
    s_file = scratch_dir / "_indic_card_tmp.png"
    h_file.write_text(html, encoding="utf-8")

    cmd = [
        edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={vp_w},{vp_h}", "--default-background-color=00000000",
        f"--screenshot={s_file.resolve().as_posix()}", f"file:///{h_file.resolve().as_posix()}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=12)
        if res.returncode == 0 and s_file.exists():
            with Image.open(s_file) as s_img:
                img = s_img.convert("RGBA")
                bbox = img.getbbox()
                return img.crop(bbox) if bbox else img
    except Exception:
        return None
    return None
