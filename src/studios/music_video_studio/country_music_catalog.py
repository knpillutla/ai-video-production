"""Country-to-Language Music Catalog and Scenery Presets for Global Music Video Studio."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class LanguageSpec:
    code: str
    name: str
    native_name: str
    culture: str
    script: str

@dataclass(frozen=True)
class CountrySpec:
    name: str
    code: str
    default_language: str
    languages: list[LanguageSpec]
    traditional_instruments: list[str]
    modern_instruments: list[str]
    local_scenery_prompts: dict[str, str]

COUNTRY_CATALOG: dict[str, CountrySpec] = {
    "India": CountrySpec(
        name="India", code="IN", default_language="te",
        languages=[
            LanguageSpec("te", "Telugu", "తెలుగు", "south_indian", "Telugu"),
            LanguageSpec("hi", "Hindi", "हिन्दी", "north_indian", "Devanagari"),
            LanguageSpec("ta", "Tamil", "தமிழ்", "south_indian", "Tamil"),
            LanguageSpec("kn", "Kannada", "ಕನ್ನಡ", "south_indian", "Kannada"),
            LanguageSpec("ml", "Malayalam", "മലയാളം", "south_indian", "Malayalam"),
            LanguageSpec("bn", "Bengali", "বাংলা", "east_indian", "Bengali"),
            LanguageSpec("mr", "Marathi", "मराठी", "west_indian", "Devanagari"),
            LanguageSpec("or", "Odia", "ଓଡ଼ିଆ", "east_indian", "Odia"),
            LanguageSpec("gu", "Gujarati", "ગુજરાતી", "west_indian", "Gujarati"),
            LanguageSpec("pa", "Punjabi", "ਪੰਜਾਬੀ", "north_indian", "Gurmukhi"),
            LanguageSpec("ks", "Kashmiri", "कॉशुर", "north_indian", "Devanagari"),
            LanguageSpec("sd", "Sindhi", "सिंधी", "west_indian", "Devanagari"),
            LanguageSpec("as", "Assamese", "অসমীয়া", "east_indian", "Bengali"),
            LanguageSpec("ur", "Urdu", "اردو", "north_indian", "Arabic"),
        ],
        traditional_instruments=["Veena", "Mridangam", "Bansuri Flute", "Tabla", "Sitar", "Nadaswaram"],
        modern_instruments=["Acoustic Guitar", "Grand Piano", "Strings Section", "Synth Pads", "Bass"],
        local_scenery_prompts={
            "local_riverside_ghats": "Scenic ancient riverbank ghats, morning mist over sacred waters, temple spires reflecting in dawn river",
            "local_heritage_palace": "Grand historic stone palace courtyard, intricately carved jharokhas, marble pillars and fountains",
            "local_lush_countryside": "Lush verdant countryside, swaying emerald paddy fields, coconut palm groves, crystal canal waters",
            "local_nature_waterfall": "Dense tropical forest waterfall, cascading water over mossy boulders, emerald jungle mist glade",
            "local_historic_street": "Vibrant historic town street at twilight, warm glowing brass lanterns, classical heritage architecture",
        },
    ),
    "Japan": CountrySpec(
        name="Japan", code="JP", default_language="ja",
        languages=[LanguageSpec("ja", "Japanese", "日本語", "japanese", "Japanese")],
        traditional_instruments=["Koto", "Shakuhachi", "Shamisen", "Taiko"],
        modern_instruments=["Nylon Guitar", "Upright Piano", "Ambient Synths", "Electric Bass"],
        local_scenery_prompts={
            "local_riverside_ghats": "Kyoto Kamo riverbanks at twilight, willow branches swaying, soft paper lantern glow",
            "local_heritage_palace": "Ancient wooden temple veranda overlooking raked gravel Zen garden and serene pine courtyard",
            "local_lush_countryside": "Pastoral tea plantation hills in Shizuoka, Mount Fuji silhouette, morning mountain mist",
            "local_nature_waterfall": "Kegon falls gorge, crystal mountain waters plunging into deep emerald plunge basin",
            "local_historic_street": "Historic Gion stone-paved lane, traditional machiya wood facades, soft evening lanterns",
        },
    ),
    "France": CountrySpec(
        name="France", code="FR", default_language="fr",
        languages=[LanguageSpec("fr", "French", "Français", "french", "Latin")],
        traditional_instruments=["Accordion", "Acoustic Nylon Guitar", "Violin", "Grand Piano"],
        modern_instruments=["Upright Bass", "Brushed Drums", "Cello Section", "Rhodes Piano"],
        local_scenery_prompts={
            "local_riverside_ghats": "River Seine stone promenade at sunset, Pont Neuf bridge arches, warm evening golden reflection",
            "local_heritage_palace": "Château courtyard in Loire Valley, manicured French gardens, limestone archways and terraces",
            "local_lush_countryside": "Rolling lavender fields in Provence, rustic stone farmhouse, warm Mediterranean dusk breeze",
            "local_nature_waterfall": "Alpine waterfall in Haute-Savoie, crystal glacial runoff cascading down granite gorges",
            "local_historic_street": "Montmartre cobblestone street at dusk, warm outdoor café bistro lighting, Parisian iron balconies",
        },
    ),
    "Spain": CountrySpec(
        name="Spain", code="ES", default_language="es",
        languages=[LanguageSpec("es", "Spanish", "Español", "spanish", "Latin")],
        traditional_instruments=["Flamenco Guitar", "Cajon", "Castanets", "Palmas Handclaps"],
        modern_instruments=["Spanish Cello", "Acoustic Bass", "Warm Brass", "Modern Percussion"],
        local_scenery_prompts={
            "local_riverside_ghats": "Guadalquivir riverbank in Seville, Torre del Oro in background, golden dusk reflection",
            "local_heritage_palace": "Alhambra stone arches and courtyards in Granada, reflecting pools, moorish filigree carving",
            "local_lush_countryside": "Sun-drenched Andalusian olive groves, whitewashed village on distant hill, terracotta rooftops",
            "local_nature_waterfall": "Pyrenees mountain cataract, clear azure pool surrounded by rugged limestone cliffs",
            "local_historic_street": "Vibrant Gothic Quarter stone alleyway in Barcelona, warm wrought-iron lanterns, warm evening breeze",
        },
    ),
    "United States": CountrySpec(
        name="United States", code="US", default_language="en",
        languages=[LanguageSpec("en", "English", "English", "western", "Latin")],
        traditional_instruments=["Steel Acoustic Guitar", "Banjo", "Fiddle", "Harmonica"],
        modern_instruments=["Grand Piano", "Bass Guitar", "Drum Kit", "Analog Synthesizer"],
        local_scenery_prompts={
            "local_riverside_ghats": "Scenic Pacific Coast highway overlook, dramatic sea stacks and golden sunset waves",
            "local_heritage_palace": "Historic Southern veranda with white columns, ancient mossy live oaks, warm evening light",
            "local_lush_countryside": "Appalachian mountain wildflower meadow at sunrise, golden sunbeams cutting through morning mist",
            "local_nature_waterfall": "Yosemite valley waterfall plunge, granite monoliths, misty pine forest glade",
            "local_historic_street": "Historic Boston brownstone lane or Nashville brick alleyway with warm vintage string lights",
        },
    ),
    "South Korea": CountrySpec(
        name="South Korea", code="KR", default_language="ko",
        languages=[LanguageSpec("ko", "Korean", "한국어", "korean", "Hangul")],
        traditional_instruments=["Gayageum", "Daegeum", "Janggu"],
        modern_instruments=["Lush String Orchestra", "Grand Piano", "Modern Pop Synths", "Acoustic Guitar"],
        local_scenery_prompts={
            "local_riverside_ghats": "Han River promenade at twilight, city skyline reflections and illuminated bridges",
            "local_heritage_palace": "Gyeongbokgung palace stone courtyard, traditional hanok pavilions and ancient pine trees",
            "local_lush_countryside": "Boseong green tea field terraces, rolling misty hills, tranquil morning breeze",
            "local_nature_waterfall": "Jeju Island coastal waterfall plunging into turquoise sea, basalt columns",
            "local_historic_street": "Bukchon Hanok village stone alleyway, traditional curved tile rooftops, warm evening lanterns",
        },
    ),
}

SCENERY_ARCHETYPES: dict[str, dict[str, str]] = {
    # Global Iconic Destination Sceneries
    "swiss_alps_snow": {
        "title": "Swiss Alps Snow Peaks & Pines",
        "prompt": "Majestic snow-covered peaks of the Swiss Alps, snow-laden pine forest, cozy wooden chalet terrace in pristine winter daylight",
        "vfx": "snow",
    },
    "dolomites_meadow": {
        "title": "Dolomites Wildflower Meadows & Glacial Streams",
        "prompt": "Dramatic jagged Dolomite granite spires towering over lush alpine wildflower meadow and crystal clear meandering stream",
        "vfx": "light_bokeh",
    },
    "paris_seine_terrace": {
        "title": "Paris Rooftop & Seine Riverfront",
        "prompt": "Elegant Parisian zinc rooftop terrace overlooking River Seine and classic Haussmann architecture in golden sunset hour",
        "vfx": "dust",
    },
    "santorini_cliffside": {
        "title": "Santorini White Cliffside & Aegean Sea",
        "prompt": "Whitewashed Santorini cliffside terrace, blue-domed churches, overlooking deep cobalt Aegean Sea and golden hour horizon",
        "vfx": "light_bokeh",
    },
    "kyoto_bamboo_temple": {
        "title": "Kyoto Bamboo Grove & Lantern Shrines",
        "prompt": "Towering Arashiyama bamboo grove path, soft sunbeams filtering through dense green stalks, wooden stone lantern shrine",
        "vfx": "dust",
    },
    "iceland_waterfall_canyon": {
        "title": "Icelandic Glacial Canyon & Waterfalls",
        "prompt": "Monumental Icelandic roaring waterfall plunging into deep canyon basin, basalt column cliffs and emerald mossy slopes",
        "vfx": "rain",
    },
    "newyork_night_skyline": {
        "title": "Modern Metropolis & Neon Skyline",
        "prompt": "High-rise luxury penthouse balcony overlooking illuminated metropolis skyline, neon city lights and evening twilight glow",
        "vfx": "light_bokeh",
    },
    "tropical_sunset_beach": {
        "title": "Tropical White Sand Beach & Palms",
        "prompt": "Pristine white sand beach, turquoise crystal ocean swells, swaying coconut palms, warm golden sunset horizon",
        "vfx": "dust",
    },
    "desert_sand_dunes": {
        "title": "Desert Sand Dunes & Starlit Camp",
        "prompt": "Undulating golden sand dunes under deep violet dusk sky, glowing Bedouin lanterns, open-air campfire hearth on sand",
        "vfx": "dust",
    },
    "biophilic_rain_cabin": {
        "title": "Biophilic Monsoon Veranda & Glass Cabin",
        "prompt": "Biophilic forest glass cabin veranda, warm torrential rain streaming from eaves, lush tropical foliage and misty glade",
        "vfx": "rain",
    },
    # Cultural & Local Presets
    "local_riverside_ghats": {"title": "Scenic Local Riverbank & Ghats", "prompt": "scenic local riverside", "vfx": "dust"},
    "local_heritage_palace": {"title": "Ancient Stone Palace & Courtyard", "prompt": "ancient historic palace courtyard", "vfx": "dust"},
    "local_lush_countryside": {"title": "Verdant Countryside & Paddy/Vineyard Hills", "prompt": "lush verdant countryside", "vfx": "light_bokeh"},
    "local_nature_waterfall": {"title": "Forest Waterfall & Mist Glade", "prompt": "forest waterfall and mist glade", "vfx": "rain"},
    "local_historic_street": {"title": "Vibrant Historic Town Street & Lanterns", "prompt": "historic town street with lanterns", "vfx": "dust"},
}

MUSIC_PERFORMANCE_TYPES = {
    "music/static_vocal": "🎙️ Static Tripod Vocal (with Particle VFX, ambient effects & dynamic kinetic subtitles)",
    "music/solo_singer": "🎤 Solo Vocalist Performance (Hero/Heroine Centerstage)",
    "music/duet_romance": "👫 Romantic Melodic Duet (Lead Pair Chemistry)",
    "music/concert_live": "🎸 Concert & Live Acoustic Stage (Auditorium/Open-Air)",
    "music/dance_folk": "💃 Mass Folk & Cultural Troupe Dance",
}

SONG_MOODS = {
    "romantic_melody": "💖 Romantic Melody (Soulful Love & Gentle Acoustic)",
    "party_upbeat": "🎉 Party & High-Energy Dance (Upbeat Electronic & Drums)",
    "happy_feelgood": "☀️ Happy & Feel-Good (Uplifting Bright Cadence)",
    "love_ballad": "🌹 Emotional Love Ballad (Deep Strings & Melancholic Swells)",
    "festival_celebration": "🪔 Festive & Cultural Celebration (Traditional Folk Percussion)",
    "spiritual_devotional": "🪷 Spiritual & Devotional (Meditative Sacred Chants & Flute)",
    "soulful_acoustic": "🎸 Soulful Unplugged & Melancholic",
}


def resolve_network_language_and_country(network_slug: str, fallback_country: str = "India") -> tuple[str, str, str]:
    """Resolve (language_code, country_name, culture_name) directly from network identity."""
    slug = str(network_slug or "").lower()
    if any(k in slug for k in ("telugu", "andhra", "tollywood", "manchu")):
        return "te", "India", "south_indian"
    if any(k in slug for k in ("tamil", "kollywood", "chennai")):
        return "ta", "India", "south_indian"
    if any(k in slug for k in ("hindi", "bollywood", "mumbai")):
        return "hi", "India", "north_indian"
    if any(k in slug for k in ("bengali", "kolkata", "bangla")):
        return "bn", "India", "east_indian"
    if any(k in slug for k in ("japan", "tokyo", "kyoto", "sakura", "nihon")):
        return "ja", "Japan", "japanese"
    if any(k in slug for k in ("france", "paris", "chanson", "french")):
        return "fr", "France", "french"
    if any(k in slug for k in ("spain", "flamenco", "madrid", "spanish")):
        return "es", "Spain", "spanish"
    if any(k in slug for k in ("korea", "seoul", "kpop", "kdrama")):
        return "ko", "South Korea", "korean"
    c_spec = COUNTRY_CATALOG.get(fallback_country, COUNTRY_CATALOG["India"])
    return c_spec.default_language, c_spec.name, c_spec.languages[0].culture


def resolve_culture_for_country_and_language(country: str | None = None, language: str | None = None) -> str:
    """Resolve regional cultural heritage key from country and language."""
    if country and country in COUNTRY_CATALOG:
        for lang_spec in COUNTRY_CATALOG[country].languages:
            if language and lang_spec.code == language.lower():
                return lang_spec.culture
        return COUNTRY_CATALOG[country].languages[0].culture
    if language:
        lang_low = language.lower()
        for c_spec in COUNTRY_CATALOG.values():
            for lang_spec in c_spec.languages:
                if lang_spec.code == lang_low:
                    return lang_spec.culture
    return "global"


def build_music_video_prompt_package(
    network_slug: str,
    performance_type: str = "music/static_vocal",
    song_mood: str = "romantic_melody",
    scenery_key: str = "swiss_alps_snow",
    user_prompt: str | None = None,
) -> dict[str, Any]:
    """Compile zero-prompt parameters autonomously using network identity."""
    lang, country, culture = resolve_network_language_and_country(network_slug)
    c_spec = COUNTRY_CATALOG.get(country, COUNTRY_CATALOG["India"])
    scenery_info = SCENERY_ARCHETYPES.get(scenery_key, SCENERY_ARCHETYPES["swiss_alps_snow"])

    scenery_prompt = (
        c_spec.local_scenery_prompts.get(scenery_key)
        if scenery_key.startswith("local_")
        else scenery_info["prompt"]
    ) or scenery_info["prompt"]

    mood_title = SONG_MOODS.get(song_mood, song_mood.replace("_", " ").title())
    perf_title = MUSIC_PERFORMANCE_TYPES.get(performance_type, performance_type)

    autonomous_theme = (
        f"{mood_title} ({perf_title}) set in {scenery_info['title']}. "
        f"Acoustic atmosphere featuring {scenery_prompt}."
    )
    eff_theme = (user_prompt.strip() if user_prompt and user_prompt.strip() else autonomous_theme)

    suno_style = f"{song_mood.replace('_', ' ')}, {', '.join(c_spec.traditional_instruments[:2])}, {c_spec.modern_instruments[0]}"

    return {
        "language": lang,
        "country": country,
        "culture": culture,
        "theme": eff_theme,
        "music_style": suno_style,
        "vfx_type": scenery_info.get("vfx", "dust"),
        "scenery_prompt": scenery_prompt,
    }

__all__ = [
    "LanguageSpec",
    "CountrySpec",
    "COUNTRY_CATALOG",
    "SCENERY_ARCHETYPES",
    "MUSIC_PERFORMANCE_TYPES",
    "SONG_MOODS",
    "resolve_network_language_and_country",
    "resolve_culture_for_country_and_language",
    "build_music_video_prompt_package",
]

