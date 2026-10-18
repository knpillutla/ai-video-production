"""Autonomous Regional Language Font Downloader & Manager with Gemini LLM Curation.

Automatically downloads, verifies, caches, and curates broadcast-grade Google Fonts
for regional languages (Telugu, Hindi, Bengali, Odia, Yoruba, Japanese, etc.)
so subtitle text renders with crisp, modern, standard written letterforms.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

from src.core.telemetry import logger

# Google Fonts official raw repositories for standard modern written fonts
LANGUAGE_FONT_REGISTRY: dict[str, dict[str, str]] = {
    "te": {"family": "Mandali", "filename": "Mandali-Regular.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/mandali/Mandali-Regular.ttf"},
    "hi": {"family": "Noto Sans Devanagari", "filename": "NotoSansDevanagari.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"},
    "mr": {"family": "Noto Sans Devanagari", "filename": "NotoSansDevanagari.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"},
    "bn": {"family": "Noto Sans Bengali", "filename": "NotoSansBengali.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf"},
    "or": {"family": "Noto Sans Oriya", "filename": "NotoSansOriya.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansoriya/NotoSansOriya%5Bwdth%2Cwght%5D.ttf"},
    "gu": {"family": "Noto Sans Gujarati", "filename": "NotoSansGujarati.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansgujarati/NotoSansGujarati%5Bwdth%2Cwght%5D.ttf"},
    "pa": {"family": "Noto Sans Gurmukhi", "filename": "NotoSansGurmukhi.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansgurmukhi/NotoSansGurmukhi%5Bwdth%2Cwght%5D.ttf"},
    "ta": {"family": "Noto Sans Tamil", "filename": "NotoSansTamil.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstamil/NotoSansTamil%5Bwdth%2Cwght%5D.ttf"},
    "kn": {"family": "Noto Sans Kannada", "filename": "NotoSansKannada.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskannada/NotoSansKannada%5Bwdth%2Cwght%5D.ttf"},
    "ml": {"family": "Noto Sans Malayalam", "filename": "NotoSansMalayalam.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansmalayalam/NotoSansMalayalam%5Bwdth%2Cwght%5D.ttf"},
    "as": {"family": "Noto Sans Bengali", "filename": "NotoSansBengali.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf"},
    "ks": {"family": "Noto Sans Devanagari", "filename": "NotoSansDevanagari.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"},
    "sd": {"family": "Noto Sans Devanagari", "filename": "NotoSansDevanagari.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"},
    "yo": {"family": "Noto Sans", "filename": "NotoSans-Regular.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf"},
    "ig": {"family": "Noto Sans", "filename": "NotoSans-Regular.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf"},
    "ha": {"family": "Noto Sans", "filename": "NotoSans-Regular.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf"},
    "ja": {"family": "Noto Sans JP", "filename": "NotoSansJP.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"},
    "ko": {"family": "Noto Sans KR", "filename": "NotoSansKR.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"},
    "ar": {"family": "Noto Sans Arabic", "filename": "NotoSansArabic.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf"},
    "th": {"family": "Noto Sans Thai", "filename": "NotoSansThai.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf"},
    "en": {"family": "Roboto", "filename": "Roboto.ttf", "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf"},
}

FONT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "family": {"type": "STRING"},
        "filename": {"type": "STRING"},
        "url": {"type": "STRING"},
    },
    "required": ["family", "filename", "url"],
}


def _get_font_cache_file() -> Path:
    p = Path("storage/assets/fonts/font_registry_cache.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_font_registry_cache() -> dict[str, dict[str, str]]:
    cf = _get_font_cache_file()
    if cf.is_file() and cf.stat().st_size > 10:
        try:
            return json.loads(cf.read_text("utf-8"))
        except Exception:
            pass
    return {}


def _save_font_registry_cache(cache: dict[str, dict[str, str]]) -> None:
    cf = _get_font_cache_file()
    try:
        cf.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        logger.warning(f"failed_saving_font_registry_cache: {exc}")


def curate_font_spec_via_gemini(language: str) -> dict[str, str]:
    """Ask Gemini LLM for the official Google Fonts raw TTF URL for any world language."""
    lang = language.lower().strip()
    from src.core.config.gemini_key_rotator import get_live_gemini_api_key

    api_key = get_live_gemini_api_key()
    if not api_key:
        logger.info(f"font_curation_offline_fallback: lang='{lang}'")
        return {"family": f"Noto Sans {lang.upper()}", "filename": f"NotoSans-{lang}.ttf", "url": LANGUAGE_FONT_REGISTRY["en"]["url"]}

    prompt = (
        f"You are a master digital typographer.\n"
        f"For language code '{lang}', identify the official Google Fonts raw TTF URL on GitHub.\n"
        f"The URL MUST start with: 'https://raw.githubusercontent.com/google/fonts/main/ofl/' and point to a valid .ttf font file.\n"
        f"Return ONLY a valid JSON object matching the schema."
    )
    try:
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        import asyncio
        llm = GeminiLLMAdapter(api_key=api_key)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                data = pool.submit(asyncio.run, llm.generate_structured(prompt=prompt, schema=FONT_SCHEMA)).result(timeout=20)
        else:
            data = loop.run_until_complete(llm.generate_structured(prompt=prompt, schema=FONT_SCHEMA))

        if data.get("url") and "raw.githubusercontent.com/google/fonts" in data.get("url", ""):
            logger.info(f"gemini_font_curated: lang='{lang}' font='{data.get('family')}'")
            return {
                "family": data.get("family", f"Noto Sans {lang.upper()}"),
                "filename": data.get("filename", f"NotoSans-{lang}.ttf"),
                "url": data.get("url"),
            }
    except Exception as exc:
        logger.warning(f"gemini_font_curation_failed: lang='{lang}' err='{exc}'. Using standard Noto Sans fallback.")

    return {"family": "Noto Sans", "filename": "NotoSans-Regular.ttf", "url": LANGUAGE_FONT_REGISTRY["yo"]["url"]}


def ensure_language_font(language: str, cache_root: Path | str | None = None) -> tuple[str, Path]:
    """Ensure font for language is downloaded, verified, and cached on disk.

    Returns:
        tuple[font_family_name, font_directory_path]
    """
    lang = (language or "en").lower().strip()
    fonts_dir = Path(cache_root or "storage/fonts") / lang
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tier 1: Check if already downloaded on disk
    cached_ttfs = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.ttc"))
    valid_ttfs = [f for f in cached_ttfs if f.stat().st_size > 5000]
    if valid_ttfs:
        return valid_ttfs[0].stem, fonts_dir

    # 2. Tier 2: Check persistent registry cache
    disk_cache = _load_font_registry_cache()
    if lang in disk_cache:
        font_spec = disk_cache[lang]
    elif lang in LANGUAGE_FONT_REGISTRY:
        font_spec = LANGUAGE_FONT_REGISTRY[lang]
    else:
        # 3. Tier 3: Query Gemini LLM for authoritative Google Fonts URL
        font_spec = curate_font_spec_via_gemini(lang)
        disk_cache[lang] = font_spec
        _save_font_registry_cache(disk_cache)

    family = font_spec.get("family", "Noto Sans")
    filename = font_spec.get("filename", f"NotoSans-{lang}.ttf")
    url = font_spec.get("url", LANGUAGE_FONT_REGISTRY["en"]["url"])
    font_file = fonts_dir / filename

    # 4. Download TTF from Google Fonts repository
    try:
        logger.info(f"downloading_language_font: lang='{lang}' family='{family}' url='{url}'")
        req = urllib.request.Request(url, headers={"User-Agent": "CineAI-Studio/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 5000:
                font_file.write_bytes(content)
                logger.info(f"downloaded_language_font: {font_file} ({len(content)} bytes)")
                return family, fonts_dir
    except Exception as exc:
        logger.warning(f"font_download_failed: lang='{lang}' err='{exc}'. Falling back to system fonts.")

    # 5. Native Windows Font Fallbacks
    if lang in ("te", "hi", "mr", "bn", "or", "gu", "pa", "ta", "kn", "ml", "as", "ks", "sd", "ur"):
        for win_path in (Path("C:/Windows/Fonts/Nirmala.ttc"), Path("C:/Windows/Fonts/nirmala.ttf")):
            if win_path.is_file():
                return "Nirmala UI", win_path.parent

    fallback_family = "Nirmala UI" if lang in ("te", "hi", "ta", "kn", "ml", "bn", "or") else "Arial"
    return fallback_family, fonts_dir


__all__ = ["ensure_language_font", "LANGUAGE_FONT_REGISTRY", "curate_font_spec_via_gemini"]
