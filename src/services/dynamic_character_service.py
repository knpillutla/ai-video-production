"""Dynamic Language-Aware Character Archetype Service with Just-In-Time Gemini Synthesis."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.services.character_archetype_catalog import ArchetypeSpec, TELUGU_FEMALE_ARCHETYPES, TELUGU_MALE_ARCHETYPES

ARCHETYPE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "language": {"type": "STRING"},
        "culture": {"type": "STRING"},
        "females": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "age": {"type": "INTEGER"},
                    "face": {"type": "STRING"},
                    "hair": {"type": "STRING"},
                    "skin": {"type": "STRING"},
                    "palette": {"type": "STRING"},
                    "seed_offset": {"type": "INTEGER"},
                },
                "required": ["name", "age", "face", "hair", "skin", "palette", "seed_offset"],
            },
        },
        "males": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "age": {"type": "INTEGER"},
                    "face": {"type": "STRING"},
                    "hair": {"type": "STRING"},
                    "skin": {"type": "STRING"},
                    "palette": {"type": "STRING"},
                    "seed_offset": {"type": "INTEGER"},
                },
                "required": ["name", "age", "face", "hair", "skin", "palette", "seed_offset"],
            },
        },
    },
    "required": ["language", "culture", "females", "males"],
}


def get_archetypes_storage_dir(network: str | None = None, user_id: str | None = None) -> Path:
    """Return local disk storage directory under assets/character_archetypes."""
    if user_id and network:
        net_dir = storage_service.get_network_path(user_id, network) / "assets" / "character_archetypes"
        net_dir.mkdir(parents=True, exist_ok=True)
        return net_dir
    base = Path(storage_service.root_dir) / "assets" / "character_archetypes"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_archetypes_file_path(language: str, network: str | None = None, user_id: str | None = None) -> Path:
    """Return the JSON file path for a given language's archetypes under assets/character_archetypes."""
    clean_lang = str(language or "en").lower().strip()
    if user_id and network:
        net_file = storage_service.get_network_path(user_id, network) / "assets" / "character_archetypes" / f"{clean_lang}_archetypes.json"
        if net_file.is_file() and net_file.stat().st_size > 500:
            return net_file
    base = Path(storage_service.root_dir) / "assets" / "character_archetypes"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{clean_lang}_archetypes.json"


def _spec_from_dict(d: dict[str, Any], default_seed: int = 10000) -> ArchetypeSpec:
    return ArchetypeSpec(
        name=str(d.get("name", "Lead")),
        age=int(d.get("age", 24)),
        face=str(d.get("face", "expressive eyes, graceful jawline")),
        hair=str(d.get("hair", "wavy dark hair")),
        skin=str(d.get("skin", "warm wheatish skin")),
        palette=str(d.get("palette", "royal blue and cream")),
        seed_offset=int(d.get("seed_offset", default_seed)),
    )


def _build_deterministic_fallback(language: str, culture: str, count: int = 50) -> tuple[list[ArchetypeSpec], list[ArchetypeSpec]]:
    """Deterministic offline fallback generating culturally authentic archetypes without live API calls."""
    lang_clean = language.lower()
    if lang_clean in ("te", "ta", "kn", "ml"):
        return TELUGU_FEMALE_ARCHETYPES[:count], TELUGU_MALE_ARCHETYPES[:count]
    if lang_clean in ("hi", "pa", "ur", "mr", "gu"):
        from src.services.character_archetypes_north_india import NORTH_INDIAN_FEMALE_ARCHETYPES, NORTH_INDIAN_MALE_ARCHETYPES
        return NORTH_INDIAN_FEMALE_ARCHETYPES[:count], NORTH_INDIAN_MALE_ARCHETYPES[:count]
    if lang_clean in ("bn", "as", "or"):
        from src.services.character_archetypes_east_india import EAST_INDIAN_FEMALE_ARCHETYPES, EAST_INDIAN_MALE_ARCHETYPES
        return EAST_INDIAN_FEMALE_ARCHETYPES[:count], EAST_INDIAN_MALE_ARCHETYPES[:count]
    if lang_clean == "ja":
        from src.services.character_archetypes_global import JAPANESE_FEMALE_ARCHETYPES, JAPANESE_MALE_ARCHETYPES
        return JAPANESE_FEMALE_ARCHETYPES[:count], JAPANESE_MALE_ARCHETYPES[:count]
    if lang_clean == "fr":
        from src.services.character_archetypes_global import FRENCH_FEMALE_ARCHETYPES, FRENCH_MALE_ARCHETYPES
        return FRENCH_FEMALE_ARCHETYPES[:count], FRENCH_MALE_ARCHETYPES[:count]
    if lang_clean == "es":
        from src.services.character_archetypes_global import SPANISH_FEMALE_ARCHETYPES, SPANISH_MALE_ARCHETYPES
        return SPANISH_FEMALE_ARCHETYPES[:count], SPANISH_MALE_ARCHETYPES[:count]
    if lang_clean == "ko":
        from src.services.character_archetypes_global import KOREAN_FEMALE_ARCHETYPES, KOREAN_MALE_ARCHETYPES
        return KOREAN_FEMALE_ARCHETYPES[:count], KOREAN_MALE_ARCHETYPES[:count]

    from src.services.character_archetypes_global import WESTERN_FEMALE_ARCHETYPES, WESTERN_MALE_ARCHETYPES
    return WESTERN_FEMALE_ARCHETYPES[:count], WESTERN_MALE_ARCHETYPES[:count]


async def generate_language_archetypes_with_gemini(
    language: str,
    culture: str = "",
    count: int = 50,
) -> tuple[list[ArchetypeSpec], list[ArchetypeSpec]]:
    """Synthesize 50 distinct female and male character archetypes for any language via Gemini call."""
    from src.providers.llm.gemini_adapter import GeminiLLMAdapter, get_live_gemini_api_key

    eff_culture = culture or language
    prompt = (
        f"You are an acclaimed cultural anthropologist and international film casting director.\n"
        f"Generate exactly {count} distinct female and {count} distinct male lead character archetypes "
        f"native to the language '{language}' and regional culture '{eff_culture}'.\n\n"
        f"MANDATORY SPECIFICATIONS (Strict Rule 12 Compliance):\n"
        f"1. Age: Strictly mid-20s (ages 23–27).\n"
        f"2. Physicality & Charm:\n"
        f"   - Female Leads: Strikingly beautiful, naturally fit medium-slender build, slender waist, natural graceful curves.\n"
        f"   - Male Leads: Strikingly handsome, lean-athletic fit build, confident posture.\n"
        f"3. Culturally Authentic Regional Anatomy:\n"
        f"   - 'name': 100% culturally authentic, widely recognized name in '{language}'. All {count} names MUST be unique.\n"
        f"   - 'face': Anatomically authentic regional facial structure, eye shape, and bone structure for '{eff_culture}'.\n"
        f"   - 'hair': Authentic regional hair texture and modern/cultural styling.\n"
        f"   - 'skin': Authentic regional skin undertones (e.g. glowing golden-wheatish / warm honey / dusky bronze / porcelain-ivory / warm olive).\n"
        f"   - 'palette': Curated wardrobe color combination (e.g. 'ruby crimson and ivory', 'sapphire blue and cream').\n"
        f"   - 'seed_offset': Unique integer offset between 10000 and 99000.\n"
    )

    api_key = get_live_gemini_api_key()
    if not api_key or is_mock_mode():
        logger.info(f"dynamic_archetype_offline_fallback: language='{language}' culture='{eff_culture}'")
        return _build_deterministic_fallback(language, eff_culture, count)

    try:
        adapter = GeminiLLMAdapter(api_key=api_key)
        data = await adapter.generate_structured(prompt=prompt, schema=ARCHETYPE_SCHEMA)
        females = [_spec_from_dict(f, 10000 + i * 1000) for i, f in enumerate(data.get("females", []))]
        males = [_spec_from_dict(m, 15000 + i * 1000) for i, m in enumerate(data.get("males", []))]
        if len(females) >= 5 and len(males) >= 5:
            return females, males
    except Exception as e:
        logger.warning(f"gemini_archetype_call_failed: {e}. Falling back to deterministic local catalog.")

    return _build_deterministic_fallback(language, eff_culture, count)


def get_or_create_language_archetypes_sync(
    language: str,
    culture: str = "",
    count: int = 50,
    force_refresh: bool = False,
) -> tuple[list[ArchetypeSpec], list[ArchetypeSpec]]:
    """Synchronous entry point: Loads cached JSON if present; otherwise runs async synthesis."""
    cache_file = get_archetypes_file_path(language)
    if not force_refresh and cache_file.is_file() and cache_file.stat().st_size > 1000:
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            females = [_spec_from_dict(f) for f in data.get("females", [])]
            males = [_spec_from_dict(m) for m in data.get("males", [])]
            if females and males:
                logger.info(f"dynamic_archetype_cached: loaded {len(females)} females, {len(males)} males from {cache_file.name}")
                return females, males
        except Exception as e:
            logger.warning(f"failed_reading_archetype_cache: {e}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                females, males = executor.submit(
                    lambda: asyncio.run(generate_language_archetypes_with_gemini(language, culture, count))
                ).result()
        else:
            females, males = loop.run_until_complete(
                generate_language_archetypes_with_gemini(language, culture, count)
            )
    except Exception:
        females, males = _build_deterministic_fallback(language, culture, count)

    # Persist dynamically synthesized catalog to disk (Tier 1 Local Disk Check for future runs)
    try:
        cache_data = {
            "language": language,
            "culture": culture or language,
            "females": [f.__dict__ for f in females],
            "males": [m.__dict__ for m in males],
        }
        cache_file.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")
        logger.info(f"dynamic_archetype_saved: persisted {len(females)} archetypes to {cache_file.name}")
    except Exception as e:
        logger.warning(f"failed_saving_archetype_cache: {e}")

    return females, males


__all__ = [
    "get_archetypes_storage_dir",
    "get_archetypes_file_path",
    "generate_language_archetypes_with_gemini",
    "get_or_create_language_archetypes_sync",
]
