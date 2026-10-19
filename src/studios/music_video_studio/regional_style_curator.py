"""Regional Musical Style Discovery & LLM Curation Engine for Global Music Videos.

Discovers, structures, and caches authentic regional musical styles, vocal face-offs
(like Jugalbandi, Sawaal-Jawaab, Gaana, Flamenco, Enka), and cultural instruments
per language/region. Checks disk asset cache first, curating via Gemini Flash on demand.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter, get_live_gemini_api_key

_CURATED_STYLES_CACHE: dict[str, list[dict[str, Any]]] = {
    "te": [
        {
            "id": "jugalbandi",
            "name": "Classical Vocal Jugalbandi",
            "native_name": "శాస్త్రీయ సంగీత జుగల్బందీ",
            "performance_mode": "duet_faceoff",
            "description": "Virtuoso classical vocal face-off with rapid sawaal-jawaab call-and-response and swara kalpana.",
            "traditional_instruments": ["Veena", "Mridangam", "Bansuri Flute", "Ghatam"],
            "recommended_bpm": 84,
            "suno_prompt_tags": "vocal jugalbandi, carnatic classical fusion duet, sawaal jawaab call and response, intricate swara trade, 84 bpm, clean broadcast master",
        },
        {
            "id": "dappu_teenmaar",
            "name": "Mass Dappu Teenmaar",
            "native_name": "మాస్ దప్పు తీన్మార్",
            "performance_mode": "troupe_dance",
            "description": "Explosive, high-octane Telangana street folk with relentless polyrhythmic percussion and brass.",
            "traditional_instruments": ["Dappu", "Thavil", "Nadaswaram", "Brass Trumpet"],
            "recommended_bpm": 138,
            "suno_prompt_tags": "mass commercial dance, thumping dappu drums, fast teenmaar rhythm, energetic brass trumpets, whistle drops, 138 bpm",
        },
        {
            "id": "janapada_geetham",
            "name": "Village Janapada Folk",
            "native_name": "పల్లె జానపద గీతం",
            "performance_mode": "solo_or_duet",
            "description": "Heartfelt pastoral storytelling folk celebrating rural life, monsoons, and harvest fields.",
            "traditional_instruments": ["Kinnera", "Dolu", "Flute", "Harmonium"],
            "recommended_bpm": 92,
            "suno_prompt_tags": "pastoral telugu janapada folk, rustic acoustic melody, kinnera strings, village flute, rhythmic dolu, 92 bpm",
        },
        {
            "id": "carnatic_fusion",
            "name": "Carnatic Raga Fusion",
            "native_name": "కర్ణాటక రాగ ఫ్యూజన్",
            "performance_mode": "duet",
            "description": "Lush classical raga paired with modern acoustic strings, delicate ornamentation, and poetic devotion.",
            "traditional_instruments": ["Veena", "Violin", "Mridangam", "Tambura"],
            "recommended_bpm": 78,
            "suno_prompt_tags": "carnatic classical raga fusion, acoustic bansuri, veena, mridangam, lush strings, 78 bpm, broadcast master",
        },
        {
            "id": "kolatam_festive",
            "name": "Kolatam Stick Dance",
            "native_name": "కోలాటం సంబరం",
            "performance_mode": "troupe_dance",
            "description": "Fast-paced festive folk dance where troupe dancers strike colorful wooden sticks in synchronized rhythm.",
            "traditional_instruments": ["Dappu", "Tasha", "Shehnai", "Harmonium"],
            "recommended_bpm": 126,
            "suno_prompt_tags": "festive telugu kolatam folk, wooden stick claps, infectious rhythmic groove, cheerful chorus, 126 bpm",
        },
    ],
    "ta": [
        {
            "id": "gaana_faceoff",
            "name": "Chennai Gaana Duet",
            "native_name": "சென்னை கானா பாடல்",
            "performance_mode": "duet_faceoff",
            "description": "Raw, lively urban Chennai street folk with witty rhyming repartee, acoustic dholak, and clap beats.",
            "traditional_instruments": ["Dholak", "Kanjira", "Harmonium"],
            "recommended_bpm": 130,
            "suno_prompt_tags": "chennai gaana folk duet, witty lyrical faceoff, fast dholak rhythm, energetic clapping, 130 bpm",
        },
        {
            "id": "carnatic_kriti",
            "name": "Carnatic Classical Kriti",
            "native_name": "கர்நாடக சங்கீத கீர்த்தனை",
            "performance_mode": "solo_or_duet",
            "description": "Timeless classical South Indian raga composition with intricate gamakas and divine poetic devotion.",
            "traditional_instruments": ["Saraswati Veena", "Mridangam", "Carnatic Violin", "Ghatam"],
            "recommended_bpm": 76,
            "suno_prompt_tags": "carnatic classical kriti, veena solo, acoustic violin counterpoint, mridangam rhythm, 76 bpm, broadcast master",
        },
        {
            "id": "villu_paattu",
            "name": "Villu Paattu (Bow Song)",
            "native_name": "வில்லுப்பாட்டு",
            "performance_mode": "troupe_dance",
            "description": "Ancient narrative musical tradition played with a long stringed bow struck with wooden rods.",
            "traditional_instruments": ["Villu Bow", "Urumi", "Kattani Sticks", "Jallra"],
            "recommended_bpm": 105,
            "suno_prompt_tags": "villu paattu musical folklore, acoustic bow percussion, call and response storytelling, 105 bpm",
        },
    ],
    "hi": [
        {
            "id": "jugalbandi_khayal",
            "name": "Hindustani Classical Jugalbandi",
            "native_name": "शास्त्रीय जुगलबंदी (ख्याल)",
            "performance_mode": "duet_faceoff",
            "description": "North Indian classical vocal duel trading rapid taans, bol-alaps, and intricate rhythmic swaras.",
            "traditional_instruments": ["Sitar", "Tabla", "Sarangi", "Tanpura"],
            "recommended_bpm": 86,
            "suno_prompt_tags": "hindustani classical vocal jugalbandi, sawaal jawaab taans, sitar, tabla accompaniment, 86 bpm",
        },
        {
            "id": "sufi_qawwali",
            "name": "Sufi Qawwali Duet",
            "native_name": "सूफी कव्वाली",
            "performance_mode": "duet_faceoff",
            "description": "Ecstatic devotional crescendo with rhythmic handclaps, harmonium swells, and spiritual vocal interplay.",
            "traditional_instruments": ["Harmonium", "Tabla", "Dholak", "Handclaps"],
            "recommended_bpm": 112,
            "suno_prompt_tags": "sufi qawwali devotional duet, ecstatic handclaps, passionate vocal crescendos, harmonium, 112 bpm",
        },
        {
            "id": "thumri_dadra",
            "name": "Romantic Thumri & Dadra",
            "native_name": "ठुमरी और दादरा",
            "performance_mode": "solo_or_duet",
            "description": "Soul-stirring romantic semi-classical style celebrating monsoon yearning, love poetry, and subtle nuances.",
            "traditional_instruments": ["Sarangi", "Bansuri", "Tabla", "Harmonium"],
            "recommended_bpm": 80,
            "suno_prompt_tags": "expressive romantic thumri, bansuri flute, sarangi melody, gentle tabla dadra rhythm, 80 bpm",
        },
    ],
    "pa": [
        {
            "id": "bhangra_dhol",
            "name": "High-Energy Bhangra",
            "native_name": "ਭੰਗੜਾ ਢੋਲ",
            "performance_mode": "troupe_dance",
            "description": "World-famous explosive harvest rhythm driven by booming dhol, tumbi riffs, and joyful boli couplets.",
            "traditional_instruments": ["Dhol", "Tumbi", "Chimta", "Algoza"],
            "recommended_bpm": 136,
            "suno_prompt_tags": "energetic punjabi bhangra, booming dhol beats, tumbi riff, festive boli vocal shouts, 136 bpm",
        },
        {
            "id": "jugni_tappe",
            "name": "Jugni & Tappe Face-Off",
            "native_name": "ਜੁਗਨੀ ਅਤੇ ਟੱਪੇ",
            "performance_mode": "duet_faceoff",
            "description": "Playful lyrical duel where male and female vocalists trade rapid, witty Punjabi tappe couplets.",
            "traditional_instruments": ["Tumbi", "Dholki", "Harmonium"],
            "recommended_bpm": 108,
            "suno_prompt_tags": "punjabi tappe duel, male and female witty lyrical faceoff, tumbi melody, rhythmic dholki, 108 bpm",
        },
    ],
}

STYLES_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "id": {"type": "STRING"},
            "name": {"type": "STRING"},
            "native_name": {"type": "STRING"},
            "performance_mode": {"type": "STRING"},
            "description": {"type": "STRING"},
            "traditional_instruments": {"type": "ARRAY", "items": {"type": "STRING"}},
            "recommended_bpm": {"type": "INTEGER"},
            "suno_prompt_tags": {"type": "STRING"},
        },
        "required": [
            "id", "name", "native_name", "performance_mode",
            "description", "traditional_instruments", "recommended_bpm", "suno_prompt_tags",
        ],
    },
}


def _get_styles_cache_dir() -> Path:
    d = Path(storage_service.root_dir) / "assets" / "musical_styles"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sanitize_lang_code(code: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", code.strip()).lower() or "en"


async def get_or_curate_regional_musical_styles(
    language_code: str,
    language_name: str | None = None,
    culture: str | None = None,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve or autonomously curate authentic regional musical styles for any language with disk asset caching."""
    clean_code = _sanitize_lang_code(language_code)
    cache_file = _get_styles_cache_dir() / f"{clean_code}.json"

    # Tier 1: Check Local Disk Asset Cache
    if not force_refresh and cache_file.is_file() and cache_file.stat().st_size > 100:
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"musical_styles_cache_hit: {clean_code} ({len(data)} styles)")
                return data
        except Exception:
            pass

    # Tier 2: Check Pre-Curated Catalog
    if not force_refresh and clean_code in _CURATED_STYLES_CACHE:
        styles = _CURATED_STYLES_CACHE[clean_code]
        try:
            cache_file.write_text(json.dumps(styles, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return styles

    # Tier 3: Autonomous LLM Discovery via Gemini Flash
    if is_mock_mode() and not get_live_gemini_api_key():
        fallback = _CURATED_STYLES_CACHE.get(clean_code, _CURATED_STYLES_CACHE.get("te", []))
        return fallback

    logger.info(f"curating_musical_styles_via_gemini: lang={clean_code}, name={language_name}")
    name_hint = language_name or clean_code.upper()
    culture_hint = f" Culture: {culture}." if culture else ""
    prompt = (
        f"You are a master ethnomusicologist and international music director.\n"
        f"Identify and structure the top 6 to 8 distinct, authentic, and historically celebrated musical styles / "
        f"vocal traditions / performance formats for the language '{name_hint}' (Code: '{clean_code}').{culture_hint}\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. Include virtuoso vocal duels / face-offs if they exist (e.g. Jugalbandi, Sawaal-Jawaab, Tappe, Gaana duel).\n"
        f"2. Include celebration / mass folk dance rhythms, pastoral storytelling songs, and classical traditions.\n"
        f"3. 'id': snake_case unique identifier (e.g., 'jugalbandi', 'mass_teenmaar', 'flamenco_duet').\n"
        f"4. 'name': Evocative English display title.\n"
        f"5. 'native_name': Authentic name written in the native script of {name_hint}.\n"
        f"6. 'performance_mode': one of 'solo_vocal', 'duet_faceoff', 'duet', 'troupe_dance', 'classical_raga', 'pastoral_folk'.\n"
        f"7. 'traditional_instruments': list of 3-5 authentic instruments traditional to this culture.\n"
        f"8. 'recommended_bpm': optimal tempo integer (60 to 150).\n"
        f"9. 'suno_prompt_tags': comma-separated production tags ready for Suno AI audio synthesis."
    )

    try:
        llm = GeminiLLMAdapter()
        res = await llm.generate_structured(prompt, schema=STYLES_SCHEMA)
        if isinstance(res, list) and len(res) > 0:
            cache_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"musical_styles_curated_and_cached: {clean_code} ({len(res)} styles)")
            return res
        elif isinstance(res, dict) and "styles" in res:
            styles_list = res["styles"]
            cache_file.write_text(json.dumps(styles_list, indent=2, ensure_ascii=False), encoding="utf-8")
            return styles_list
    except Exception as exc:
        logger.error(f"failed_to_curate_musical_styles: {exc}")

    # Fallback to generic safe styles if API call fails
    default_styles = [
        {
            "id": "romantic_melody",
            "name": f"{name_hint} Romantic Melody",
            "native_name": name_hint,
            "performance_mode": "duet",
            "description": f"Soulful, heartfelt acoustic love ballad in {name_hint}.",
            "traditional_instruments": ["Acoustic Guitar", "Flute", "Strings"],
            "recommended_bpm": 88,
            "suno_prompt_tags": f"romantic ballad, {clean_code}, acoustic melody, soft strings, 88 bpm, broadcast master",
        },
        {
            "id": "festive_folk",
            "name": f"{name_hint} Festive Folk Celebration",
            "native_name": name_hint,
            "performance_mode": "troupe_dance",
            "description": f"High-energy celebratory folk rhythm with lively traditional percussion in {name_hint}.",
            "traditional_instruments": ["Drums", "Folk Flute", "Percussion"],
            "recommended_bpm": 124,
            "suno_prompt_tags": f"festive folk dance, {clean_code}, joyous rhythm, vibrant percussion, 124 bpm",
        },
    ]
    return default_styles


__all__ = ["get_or_curate_regional_musical_styles"]
