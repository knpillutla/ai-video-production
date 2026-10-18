"""Autonomous Regional Language Font Downloader & Manager.

Automatically downloads, verifies, and caches broadcast-grade Google Fonts
for regional languages (Telugu, Hindi, Tamil, Kannada, Malayalam, English, etc.)
so subtitle text renders with crisp, modern, standard written letterforms.
"""

from __future__ import annotations
import urllib.request
from pathlib import Path
from src.core.telemetry import logger

# Google Fonts official raw repositories for standard modern written fonts
LANGUAGE_FONT_REGISTRY: dict[str, dict[str, str]] = {
    "te": {
        "family": "Mandali",
        "filename": "Mandali-Regular.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/mandali/Mandali-Regular.ttf",
    },
    "hi": {
        "family": "Noto Sans Devanagari",
        "filename": "NotoSansDevanagari.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    },
    "ta": {
        "family": "Noto Sans Tamil",
        "filename": "NotoSansTamil.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstamil/NotoSansTamil%5Bwdth%2Cwght%5D.ttf",
    },
    "kn": {
        "family": "Noto Sans Kannada",
        "filename": "NotoSansKannada.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskannada/NotoSansKannada%5Bwdth%2Cwght%5D.ttf",
    },
    "ml": {
        "family": "Noto Sans Malayalam",
        "filename": "NotoSansMalayalam.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansmalayalam/NotoSansMalayalam%5Bwdth%2Cwght%5D.ttf",
    },
    "en": {
        "family": "Roboto",
        "filename": "Roboto.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
    },
}


def ensure_language_font(language: str, cache_root: Path | str | None = None) -> tuple[str, Path]:
    """Ensure font for language is downloaded and cached on disk.

    Returns:
        tuple[font_family_name, font_directory_path]
    """
    lang = (language or "en").lower().strip()
    font_spec = LANGUAGE_FONT_REGISTRY.get(lang, LANGUAGE_FONT_REGISTRY["en"])
    family = font_spec["family"]
    filename = font_spec["filename"]
    url = font_spec["url"]

    fonts_dir = Path(cache_root or "storage/fonts") / lang
    fonts_dir.mkdir(parents=True, exist_ok=True)
    font_file = fonts_dir / filename

    if font_file.is_file() and font_file.stat().st_size > 5000:
        return family, fonts_dir

    try:
        logger.info(f"downloading_language_font: lang={lang}, font={family}, url={url}")
        req = urllib.request.Request(url, headers={"User-Agent": "CineAI-Studio/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 5000:
                font_file.write_bytes(content)
                logger.info(f"downloaded_language_font: {font_file} ({len(content)} bytes)")
                return family, fonts_dir
    except Exception as exc:
        logger.warning(f"font_download_failed: lang={lang}, err={exc}. Falling back to system font.")

    # Graceful fallback to Nirmala UI on Windows or Arial
    fallback_family = "Nirmala UI" if lang in ("te", "hi", "ta", "kn", "ml") else "Arial"
    return fallback_family, fonts_dir


__all__ = ["ensure_language_font", "LANGUAGE_FONT_REGISTRY"]
