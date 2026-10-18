"""Country-to-Languages Discovery & LLM Curation Engine for Global Music Videos.

Maintains curated regional language registries for world countries and dynamically
curates new country language ecosystems via Gemini Flash with disk caching.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter, get_live_gemini_api_key

CURATED_COUNTRY_LANGUAGES: dict[str, list[dict[str, str]]] = {
    "India": [
        {"code": "te", "name": "Telugu (South India - Tollywood)", "native_name": "తెలుగు", "script": "Telugu", "culture": "south_indian"},
        {"code": "hi", "name": "Hindi (North India - Bollywood)", "native_name": "हिन्दी", "script": "Devanagari", "culture": "north_indian"},
        {"code": "ta", "name": "Tamil (South India - Kollywood)", "native_name": "தமிழ்", "script": "Tamil", "culture": "south_indian"},
        {"code": "kn", "name": "Kannada (South India - Sandalwood)", "native_name": "ಕನ್ನಡ", "script": "Kannada", "culture": "south_indian"},
        {"code": "ml", "name": "Malayalam (South India - Mollywood)", "native_name": "മലയാളം", "script": "Malayalam", "culture": "south_indian"},
        {"code": "bn", "name": "Bengali (East India - Tollywood Bengal / Baul)", "native_name": "বাংলা", "script": "Bengali", "culture": "east_indian"},
        {"code": "mr", "name": "Marathi (West India - Natya Sangeet / Bhavgeet / Lavani)", "native_name": "मराठी", "script": "Devanagari", "culture": "west_indian"},
        {"code": "or", "name": "Odia (East India - Sambalpuri / Odissi / Bhakti)", "native_name": "ଓଡ଼ିଆ", "script": "Odia", "culture": "east_indian"},
        {"code": "gu", "name": "Gujarati (West India - Garba / Sugam Sangeet)", "native_name": "ગુજરાતી", "script": "Gujarati", "culture": "west_indian"},
        {"code": "pa", "name": "Punjabi (North India - Bhangra / Sufi)", "native_name": "ਪੰਜਾਬੀ", "script": "Gurmukhi", "culture": "north_indian"},
        {"code": "ks", "name": "Kashmiri (North India - Sufiyana Kalam / Rouf / Chakri)", "native_name": "कॉशुर / کٲشُر", "script": "Devanagari", "culture": "north_indian"},
        {"code": "sd", "name": "Sindhi (West/North India - Sufi Kalaam / Jhulelal)", "native_name": "سنڌي / सिंधी", "script": "Devanagari", "culture": "west_indian"},
        {"code": "as", "name": "Assamese (East India - Bihu / Folk)", "native_name": "অসমীয়া", "script": "Bengali", "culture": "east_indian"},
        {"code": "ur", "name": "Urdu (North India - Ghazal / Qawwali)", "native_name": "اردو", "script": "Arabic", "culture": "north_indian"},
        {"code": "kok", "name": "Konkani (West India - Goan Mandó / Dulpod)", "native_name": "कोंकणी", "script": "Devanagari", "culture": "west_indian"},
    ],
    "Japan": [
        {"code": "ja", "name": "Japanese (Nihongo - J-Pop / Enka / Traditional)", "native_name": "日本語", "script": "Japanese", "culture": "japanese"},
    ],
    "France": [
        {"code": "fr", "name": "French (Chanson / Modern Pop / Acoustic)", "native_name": "Français", "script": "Latin", "culture": "french"},
    ],
    "Spain": [
        {"code": "es", "name": "Spanish (Flamenco / Latin Pop / Acoustic)", "native_name": "Español", "script": "Latin", "culture": "spanish"},
        {"code": "ca", "name": "Catalan (Rumba Catalana / Folk)", "native_name": "Català", "script": "Latin", "culture": "spanish"},
        {"code": "gl", "name": "Galician (Celtic Cantigas / Folk)", "native_name": "Galego", "script": "Latin", "culture": "spanish"},
    ],
    "United States": [
        {"code": "en", "name": "English (Country / Pop / R&B / Acoustic)", "native_name": "English", "script": "Latin", "culture": "western"},
        {"code": "es", "name": "Spanish (Latin Urban / Tejano)", "native_name": "Español", "script": "Latin", "culture": "spanish"},
    ],
    "South Korea": [
        {"code": "ko", "name": "Korean (K-Pop / Ballad / Traditional Trot)", "native_name": "한국어", "script": "Hangul", "culture": "korean"},
    ],
    "Nigeria": [
        {"code": "en", "name": "English (Afrobeats / Highlife)", "native_name": "English", "script": "Latin", "culture": "african"},
        {"code": "yo", "name": "Yoruba (Fuji / Jùjú / Afrobeats)", "native_name": "Èdè Yorùbá", "script": "Latin", "culture": "african"},
        {"code": "ig", "name": "Igbo (Ogene / Highlife)", "native_name": "Ásụ̀sụ́ Ìgbò", "script": "Latin", "culture": "african"},
        {"code": "ha", "name": "Hausa (Traditional / Arewa Pop)", "native_name": "Harshen Hausa", "script": "Latin", "culture": "african"},
    ],
    "Brazil": [
        {"code": "pt", "name": "Portuguese (Bossa Nova / Samba / MPB)", "native_name": "Português", "script": "Latin", "culture": "latin_american"},
    ],
    "Italy": [
        {"code": "it", "name": "Italian (Canzone / Opera / Melodic Pop)", "native_name": "Italiano", "script": "Latin", "culture": "italian"},
    ],
    "Germany": [
        {"code": "de", "name": "German (Schlager / Liedermacher / Electronic)", "native_name": "Deutsch", "script": "Latin", "culture": "german"},
    ],
}

LANGUAGES_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "code": {"type": "STRING"},
            "name": {"type": "STRING"},
            "native_name": {"type": "STRING"},
            "script": {"type": "STRING"},
            "culture": {"type": "STRING"},
        },
        "required": ["code", "name", "native_name", "script", "culture"],
    },
}


def _get_cache_dir() -> Path:
    d = Path(storage_service.root_dir) / "assets" / "country_languages"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sanitize_country_key(country: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", country.strip()).lower().strip("_") or "world"


async def get_or_curate_country_languages(country: str, force_refresh: bool = False) -> list[dict[str, str]]:
    """Retrieve curated list of regional/national languages for any country, dynamically curating via Gemini."""
    clean_name = country.strip() if country else "India"
    slug = _sanitize_country_key(clean_name)

    # 1. Check in-memory catalog
    for c_name, langs in CURATED_COUNTRY_LANGUAGES.items():
        if c_name.lower() == clean_name.lower():
            return langs

    # 2. Check local disk cache (Universal Artifact Caching Rule 3)
    cache_file = _get_cache_dir() / f"{slug}.json"
    if cache_file.is_file() and cache_file.stat().st_size > 100 and not force_refresh:
        try:
            cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
            if isinstance(cached_data, list) and len(cached_data) > 0:
                return cached_data
        except Exception as e:
            logger.warning(f"failed_reading_country_language_cache: {e}")

    # 3. Dynamic LLM Curation via Gemini Flash (Tier 1 per Rule 1)
    api_key = get_live_gemini_api_key()
    if api_key and not is_mock_mode():
        prompt = (
            f"You are an international ethnomusicologist and cultural linguist.\n"
            f"List all prominent national, regional, and indigenous languages spoken or sung in '{clean_name}'.\n"
            f"For each language, return:\n"
            f"- 'code': ISO 639-1 two-letter code\n"
            f"- 'name': English name with musical/regional heritage hint (e.g. 'Odia (East India - Sambalpuri / Odissi)')\n"
            f"- 'native_name': Name written in its own native script (e.g. 'ଓଡ଼ିଆ')\n"
            f"- 'script': Alphabet/script system (e.g. 'Odia', 'Devanagari', 'Bengali', 'Latin', 'Arabic', 'Cyrillic')\n"
            f"- 'culture': Standard cultural key (e.g. 'east_indian', 'west_indian', 'celtic', 'nordic', 'latin_american')"
        )
        try:
            adapter = GeminiLLMAdapter(api_key=api_key)
            curated_list = await adapter.generate_structured(prompt=prompt, schema=LANGUAGES_SCHEMA)
            if isinstance(curated_list, list) and len(curated_list) > 0:
                cache_file.write_text(json.dumps(curated_list, indent=2, ensure_ascii=False), encoding="utf-8")
                logger.info(f"curated_country_languages_via_llm: country='{clean_name}' count={len(curated_list)}")
                return curated_list
        except Exception as exc:
            logger.warning(f"llm_language_curation_failed: country='{clean_name}' err={exc}")

    # 4. Fallback: generic national language entry
    fallback = [
        {"code": "en", "name": f"English ({clean_name})", "native_name": "English", "script": "Latin", "culture": "western"},
    ]
    return fallback


__all__ = ["CURATED_COUNTRY_LANGUAGES", "get_or_curate_country_languages"]
