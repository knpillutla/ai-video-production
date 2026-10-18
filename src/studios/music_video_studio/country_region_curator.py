"""Country Sub-Regions & Linguistic Hierarchy Curator with Disk Caching.

Manages 4-Tier Geographic & Linguistic Selection:
Continent -> Country -> Country Sub-Region -> Region-Specific Language & Heritage.
Caches LLM-curated responses to storage/assets/geographic_hierarchy/{country_slug}.json.
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

# Pre-curated high-fidelity catalogs for continuous series production
CURATED_COUNTRY_HIERARCHIES: dict[str, dict[str, Any]] = {
    "India": {
        "country": "India",
        "continent": "Asia",
        "flag": "🇮🇳",
        "sub_regions": [
            {
                "id": "south_india",
                "name": "South India (Tollywood, Kollywood, Sandalwood, Mollywood)",
                "culture": "south_indian",
                "languages": [
                    {"code": "te", "name": "Telugu (Andhra & Telangana - Tollywood)", "native_name": "తెలుగు", "script": "Telugu", "culture": "south_indian"},
                    {"code": "ta", "name": "Tamil (Tamil Nadu - Kollywood)", "native_name": "தமிழ்", "script": "Tamil", "culture": "south_indian"},
                    {"code": "kn", "name": "Kannada (Karnataka - Sandalwood)", "native_name": "ಕನ್ನಡ", "script": "Kannada", "culture": "south_indian"},
                    {"code": "ml", "name": "Malayalam (Kerala - Mollywood)", "native_name": "മലയാളം", "script": "Malayalam", "culture": "south_indian"},
                ],
            },
            {
                "id": "east_india",
                "name": "East India (Bengal, Odisha & Assam)",
                "culture": "east_indian",
                "languages": [
                    {"code": "bn", "name": "Bengali (West Bengal - Baul & Tollywood)", "native_name": "বাংলা", "script": "Bengali", "culture": "east_indian"},
                    {"code": "or", "name": "Odia (Odisha - Sambalpuri & Odissi)", "native_name": "ଓଡ଼ିଆ", "script": "Odia", "culture": "east_indian"},
                    {"code": "as", "name": "Assamese (Assam - Bihu & Lokageet)", "native_name": "অসমীয়া", "script": "Bengali", "culture": "east_indian"},
                ],
            },
            {
                "id": "west_india",
                "name": "West India (Maharashtra, Gujarat, Goa & Sindh Heritage)",
                "culture": "west_indian",
                "languages": [
                    {"code": "mr", "name": "Marathi (Maharashtra - Natya Sangeet & Lavani)", "native_name": "मराठी", "script": "Devanagari", "culture": "west_indian"},
                    {"code": "gu", "name": "Gujarati (Gujarat - Garba & Sugam Sangeet)", "native_name": "ગુજરાતી", "script": "Gujarati", "culture": "west_indian"},
                    {"code": "kok", "name": "Konkani (Goa & Konkan - Mandó & Dulpod)", "native_name": "कोंकणी", "script": "Devanagari", "culture": "west_indian"},
                    {"code": "sd", "name": "Sindhi (Sindh Heritage - Sufi Kalaam & Jhulelal)", "native_name": "سنڌي / सिंधी", "script": "Devanagari", "culture": "west_indian"},
                ],
            },
            {
                "id": "north_india",
                "name": "North India (Punjab, Kashmir, Hindi Heartland & Urdu)",
                "culture": "north_indian",
                "languages": [
                    {"code": "hi", "name": "Hindi (Bollywood & Classical Hindustani)", "native_name": "हिन्दी", "script": "Devanagari", "culture": "north_indian"},
                    {"code": "pa", "name": "Punjabi (Punjab - Bhangra & Sufi)", "native_name": "ਪੰਜਾਬੀ", "script": "Gurmukhi", "culture": "north_indian"},
                    {"code": "ks", "name": "Kashmiri (Kashmir Valley - Rouf & Sufiyana)", "native_name": "कॉशुर / کٲشُر", "script": "Devanagari", "culture": "north_indian"},
                    {"code": "ur", "name": "Urdu (Ghazal & Qawwali)", "native_name": "اردو", "script": "Arabic", "culture": "north_indian"},
                ],
            },
        ],
    },
    "Spain": {
        "country": "Spain",
        "continent": "Europe",
        "flag": "🇪🇸",
        "sub_regions": [
            {
                "id": "andalusia",
                "name": "Andalusia (Flamenco & Cante Jondo)",
                "culture": "spanish",
                "languages": [
                    {"code": "es", "name": "Spanish (Andalusian Flamenco & Acoustic)", "native_name": "Español", "script": "Latin", "culture": "spanish"},
                ],
            },
            {
                "id": "catalonia",
                "name": "Catalonia (Rumba Catalana & Nova Cançó)",
                "culture": "spanish",
                "languages": [
                    {"code": "ca", "name": "Catalan (Rumba Catalana & Pop)", "native_name": "Català", "script": "Latin", "culture": "spanish"},
                    {"code": "es", "name": "Spanish (Barcelona Modern Pop)", "native_name": "Español", "script": "Latin", "culture": "spanish"},
                ],
            },
            {
                "id": "galicia",
                "name": "Galicia (Celtic Cantigas & Alalá)",
                "culture": "spanish",
                "languages": [
                    {"code": "gl", "name": "Galician (Celtic Folk & Cantigas)", "native_name": "Galego", "script": "Latin", "culture": "spanish"},
                ],
            },
        ],
    },
    "United States": {
        "country": "United States",
        "continent": "North America",
        "flag": "🇺🇸",
        "sub_regions": [
            {
                "id": "american_south",
                "name": "American South (Country, Blues & Gospel)",
                "culture": "western",
                "languages": [
                    {"code": "en", "name": "English (Southern Country & Delta Blues)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
            {
                "id": "appalachia",
                "name": "Appalachia (Bluegrass & Mountain Folk)",
                "culture": "western",
                "languages": [
                    {"code": "en", "name": "English (Appalachian Bluegrass & Old-Time)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
            {
                "id": "southwest",
                "name": "Southwest & Border (Tejano, Mariachi & Latin)",
                "culture": "spanish",
                "languages": [
                    {"code": "es", "name": "Spanish (Tejano & Border Ballad)", "native_name": "Español", "script": "Latin", "culture": "spanish"},
                    {"code": "en", "name": "English (Desert Acoustic & Folk)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
        ],
    },
    "United Kingdom": {
        "country": "United Kingdom",
        "continent": "Europe",
        "flag": "🇬🇧",
        "sub_regions": [
            {
                "id": "scotland",
                "name": "Scotland (Highland Celtic & Folk Ballads)",
                "culture": "western",
                "languages": [
                    {"code": "gd", "name": "Scottish Gaelic (Gàidhlig - Celtic)", "native_name": "Gàidhlig", "script": "Latin", "culture": "western"},
                    {"code": "en", "name": "English (Scottish Ballads & Acoustic)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
            {
                "id": "wales",
                "name": "Wales (Cerdd Dant & Choral Folk)",
                "culture": "western",
                "languages": [
                    {"code": "cy", "name": "Welsh (Cymraeg - Choral & Folk)", "native_name": "Cymraeg", "script": "Latin", "culture": "western"},
                    {"code": "en", "name": "English (Welsh Acoustic & Hymns)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
            {
                "id": "england",
                "name": "England (Acoustic Folk & Classical Pop)",
                "culture": "western",
                "languages": [
                    {"code": "en", "name": "English (Traditional Folk & Modern Pop)", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            },
        ],
    },
    "Japan": {
        "country": "Japan",
        "continent": "Asia",
        "flag": "🇯🇵",
        "sub_regions": [
            {
                "id": "kanto_tokyo",
                "name": "Kanto (Tokyo - Modern J-Pop & City Pop)",
                "culture": "japanese",
                "languages": [
                    {"code": "ja", "name": "Japanese (Tokyo J-Pop & City Pop)", "native_name": "日本語", "script": "Japanese", "culture": "japanese"},
                ],
            },
            {
                "id": "kansai_kyoto",
                "name": "Kansai (Kyoto & Osaka - Traditional Gagaku & Folk)",
                "culture": "japanese",
                "languages": [
                    {"code": "ja", "name": "Japanese (Koto Classical & Min'yo)", "native_name": "日本語", "script": "Japanese", "culture": "japanese"},
                ],
            },
            {
                "id": "okinawa",
                "name": "Okinawa (Ryukyu - Sanshin Island Folk)",
                "culture": "japanese",
                "languages": [
                    {"code": "ja", "name": "Japanese / Ryukyu (Sanshin Island Folk)", "native_name": "日本語", "script": "Japanese", "culture": "japanese"},
                ],
            },
        ],
    },
    "France": {
        "country": "France",
        "continent": "Europe",
        "flag": "🇫🇷",
        "sub_regions": [
            {
                "id": "paris_ile_de_france",
                "name": "Île-de-France (Paris - Chanson Française & Pop)",
                "culture": "french",
                "languages": [
                    {"code": "fr", "name": "French (Chanson Française & Parisian Pop)", "native_name": "Français", "script": "Latin", "culture": "french"},
                ],
            },
            {
                "id": "brittany",
                "name": "Brittany (Celtic Fest-Noz & Folk)",
                "culture": "french",
                "languages": [
                    {"code": "fr", "name": "French / Breton (Celtic Folk Ballad)", "native_name": "Français / Brezhoneg", "script": "Latin", "culture": "french"},
                ],
            },
        ],
    },
    "Nigeria": {
        "country": "Nigeria",
        "continent": "Africa",
        "flag": "🇳🇬",
        "sub_regions": [
            {
                "id": "yorubaland",
                "name": "South-West (Yorubaland - Fuji, Jùjú & Afrobeats)",
                "culture": "african",
                "languages": [
                    {"code": "yo", "name": "Yoruba (Fuji, Jùjú & Afrobeats)", "native_name": "Èdè Yorùbá", "script": "Latin", "culture": "african"},
                    {"code": "en", "name": "English (Lagos Afrobeats)", "native_name": "English", "script": "Latin", "culture": "african"},
                ],
            },
            {
                "id": "igboland",
                "name": "South-East (Igboland - Ogene & Highlife)",
                "culture": "african",
                "languages": [
                    {"code": "ig", "name": "Igbo (Ogene & Highlife)", "native_name": "Ásụ̀sụ́ Ìgbò", "script": "Latin", "culture": "african"},
                ],
            },
            {
                "id": "northern_nigeria",
                "name": "Northern Nigeria (Hausa Folk & Arewa Pop)",
                "culture": "african",
                "languages": [
                    {"code": "ha", "name": "Hausa (Traditional & Arewa Pop)", "native_name": "Harshen Hausa", "script": "Latin", "culture": "african"},
                ],
            },
        ],
    },
}

COUNTRY_HIERARCHY_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "country": {"type": "STRING"},
        "continent": {"type": "STRING"},
        "flag": {"type": "STRING"},
        "sub_regions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING"},
                    "name": {"type": "STRING"},
                    "culture": {"type": "STRING"},
                    "languages": {
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
                    },
                },
                "required": ["id", "name", "culture", "languages"],
            },
        },
    },
    "required": ["country", "continent", "flag", "sub_regions"],
}


def _get_hierarchy_cache_dir() -> Path:
    d = Path(storage_service.root_dir) / "assets" / "geographic_hierarchy"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sanitize_slug(val: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", str(val).strip()).lower().strip("_") or "world"


async def get_or_curate_country_hierarchy(country: str, force_refresh: bool = False) -> dict[str, Any]:
    """Retrieve 4-tier hierarchy for country: Continent -> Country -> Sub-Regions -> Languages.
    
    Strictly adheres to Universal Artifact Caching:
    1. Check storage/assets/geographic_hierarchy/{country_slug}.json
    2. Check in-memory CURATED_COUNTRY_HIERARCHIES (saves to cache)
    3. Call Gemini Flash Tier 1 LLM, save response to cache
    4. Deterministic fallback
    """
    clean_name = country.strip() if country else "India"
    slug = _sanitize_slug(clean_name)
    cache_file = _get_hierarchy_cache_dir() / f"{slug}.json"

    # 1. Tier 1 Local Disk Check
    if cache_file.is_file() and cache_file.stat().st_size > 100 and not force_refresh:
        try:
            cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
            if isinstance(cached_data, dict) and "sub_regions" in cached_data:
                return cached_data
        except Exception as e:
            logger.warning(f"failed_reading_geographic_cache: {e}")

    # 2. Check in-memory catalog
    for c_name, hier in CURATED_COUNTRY_HIERARCHIES.items():
        if c_name.lower() == clean_name.lower():
            try:
                cache_file.write_text(json.dumps(hier, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            return hier

    # 3. Dynamic LLM Curation via Gemini Flash (Tier 1 per Rule 1)
    api_key = get_live_gemini_api_key()
    if api_key and not is_mock_mode():
        prompt = (
            f"You are an international ethnomusicologist and cultural geographer.\n"
            f"Break down '{clean_name}' into 2 to 5 distinct cultural/musical sub-regions "
            f"(e.g. for continuous video series production).\n"
            f"For each sub-region, list all prominent regional/local languages and musical traditions.\n"
            f"Return valid JSON matching the schema with country, continent, flag emoji, and sub_regions."
        )
        try:
            adapter = GeminiLLMAdapter(api_key=api_key)
            curated_hier = await adapter.generate_structured(prompt=prompt, schema=COUNTRY_HIERARCHY_SCHEMA)
            if isinstance(curated_hier, dict) and curated_hier.get("sub_regions"):
                cache_file.write_text(json.dumps(curated_hier, indent=2, ensure_ascii=False), encoding="utf-8")
                logger.info(f"curated_country_hierarchy_via_llm: country='{clean_name}' subregions={len(curated_hier['sub_regions'])}")
                return curated_hier
        except Exception as exc:
            logger.warning(f"llm_hierarchy_curation_failed: country='{clean_name}' err={exc}")

    # 4. Deterministic fallback
    fallback: dict[str, Any] = {
        "country": clean_name,
        "continent": "Global",
        "flag": "🌐",
        "sub_regions": [
            {
                "id": "nationwide",
                "name": f"Nationwide & Regional Traditions ({clean_name})",
                "culture": "western",
                "languages": [
                    {"code": "en", "name": f"English ({clean_name})", "native_name": "English", "script": "Latin", "culture": "western"},
                ],
            }
        ],
    }
    return fallback


def get_all_country_languages_flat(hierarchy: dict[str, Any]) -> list[dict[str, str]]:
    """Flatten all sub-region languages for backward compatibility."""
    seen_codes = set()
    flat: list[dict[str, str]] = []
    for sub in hierarchy.get("sub_regions", []):
        for lang in sub.get("languages", []):
            code = lang.get("code")
            if code and code not in seen_codes:
                seen_codes.add(code)
                flat.append(lang)
    return flat


__all__ = [
    "CURATED_COUNTRY_HIERARCHIES",
    "get_or_curate_country_hierarchy",
    "get_all_country_languages_flat",
]
