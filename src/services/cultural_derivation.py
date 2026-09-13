"""Deterministic Cultural, Ethnicity, Clothing, Outfit, and LoRA Derivation Engine."""

import re
from typing import Any
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.mcp.model_selector.cultural_catalog import (
    lookup_art_style,
    lookup_costume_stack,
    lookup_cultural_stack,
    resolve_cultural_voice,
)

_IN = {"culture": "indian_south", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_traditional_dhoti"}
_AU = {"culture": "australian", "ethnicity": "australian", "female_costume": "western_modern", "male_costume": "western_modern"}
_IT = {"culture": "italian", "ethnicity": "italian", "female_costume": "italian_tarantella_folk", "male_costume": "italian_tarantella_folk"}
_MX = {"culture": "mexican", "ethnicity": "mexican", "female_costume": "mexican_jalisco_charro", "male_costume": "mexican_jalisco_charro"}
_EA = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "chinese_hanfu_water_sleeves", "male_costume": "chinese_hanfu_water_sleeves"}
_WEST = {"culture": "western_global", "ethnicity": "caucasian", "female_costume": "western_modern", "male_costume": "western_modern"}

COUNTRY_CULTURE_MAP: dict[str, dict[str, str]] = {
    "in": _IN, "india": _IN, "bharat": _IN,
    "au": _AU, "australia": _AU, "aus": _AU,
    "it": _IT, "italy": _IT,
    "mx": _MX, "mexico": _MX,
    "jp": _EA, "japan": _EA, "kr": _EA, "korea": _EA, "south korea": _EA, "cn": _EA, "china": _EA,
    "us": _WEST, "usa": _WEST, "united states": _WEST, "uk": _WEST, "gb": _WEST, "united kingdom": _WEST,
    "fr": _WEST, "france": _WEST, "de": _WEST, "germany": _WEST,
}

SCRIPT_CULTURE_KEYWORDS: list[tuple[list[str], dict[str, str]]] = [
    (
        [
            "hyderabad", "charminar", "chennai", "bengaluru", "bangalore", "kerala", "tirupati",
            "kanchipuram", "telugu", "tamil", "kannada", "malayalam", "saree", "pattu", "pelli",
            "lungi", "panche", "kuchipudi", "bharatanatyam", "tollywood", "gongura", "biryani",
            "dosa", "idli", "andhra", "telangana", "rayalaseema", "vizag", "vijayawada",
        ],
        _IN,
    ),
    (
        [
            "delhi", "mumbai", "punjab", "bhangra", "garba", "gujarat", "kolkata", "bengal",
            "varanasi", "ghats", "kathak", "bollywood", "sherwani", "kurta", "lehenga",
            "anarkali", "dupatta", "taj mahal", "jaipur", "rajasthan", "diwali", "holi",
        ],
        {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"},
    ),
    (["italy", "italian", "rome", "tarantella", "pizzica", "florence", "venice", "naples", "sicily"], _IT),
    (["mexico", "mexican", "mariachi", "tapatio", "jarabe", "zapateado", "guadalajara", "oaxaca", "sombrero", "charro", "folklore"], _MX),
    (["water sleeves", "shuixiu", "hanfu", "guzheng", "erhu", "beijing", "shanghai", "china", "chinese"], _EA),
    (["tokyo", "kyoto", "japan", "japanese", "kimono", "yukata", "seoul", "korea", "korean", "hanbok", "anime", "manga", "k-pop"], _EA),
    (["country line dance", "western swing", "line dance", "cowboy", "nashville", "texas"], {"culture": "western_global", "ethnicity": "caucasian", "female_costume": "american_western_country", "male_costume": "american_western_country"}),
    (["australia", "sydney", "melbourne", "brisbane", "perth", "adelaide", "bondi", "outback", "great barrier reef", "gold coast", "koala", "kangaroo", "aussie"], _AU),
    (["paris", "louvre", "eiffel", "london", "new york", "hollywood", "suit", "tuxedo", "blazer", "cocktail dress", "jeans", "casual"], _WEST),
]


class DerivedCulturalContext(BaseModel):
    """Complete culturally derived context from user profile or script metadata."""

    culture: str
    culture_name: str
    ethnicity: str
    primary_ethnicity: str
    clothing_style: str
    outfit_description: str
    jewelry_description: str
    art_style: str = "photorealistic_cinematic"
    art_style_display: str = "Broadcast 4K Photorealistic Cinematic"
    art_style_prompt: str = ""
    art_style_lighting: str = ""
    art_style_palette: str = ""
    recommended_loras: list[dict[str, Any]] = Field(default_factory=list)
    voice_id: str = "en-US-ChristopherNeural"
    voice_provider: str = "Microsoft Azure Speech HD"
    music_style: str = "Cinematic acoustic score"
    sfx_style: str = "Authentic foley and sound design"
    derivation_source: str
    confidence_score: float = 1.0


def derive_cultural_context(
    script_text: str = "",
    user_home_country: str | None = None,
    user_cultural_heritage: str | None = None,
    language: str = "en",
    gender: str = "female",
    genre: str = "comedy",
    dance_type: str = "",
    video_format: str = "",
    art_style: str = "",
) -> DerivedCulturalContext:
    """Deterministically derive ethnicity, culture, clothing, outfits, and LoRAs.

    Precedence:
    1. Explicit User Cultural Heritage (from user profile)
    2. Script Keywords & Locations (from script title/scenes/dialogue)
    3. User Home Country (from user identity information)
    4. Language Code Mapping (te -> South Indian, hi -> North Indian, etc.)
    5. Western Global Fallback
    """
    profile: dict[str, str] | None = None
    source = "western_global_fallback"
    confidence = 0.50

    # 1. Check explicit user cultural heritage
    if user_cultural_heritage:
        heritage_key = user_cultural_heritage.lower().strip()
        if "south" in heritage_key or heritage_key in ("telugu", "tamil", "kannada", "malayalam"):
            profile = {"culture": "indian_south", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_traditional_dhoti"}
            source = "user_cultural_heritage"
            confidence = 0.98
        elif "north" in heritage_key or heritage_key in ("hindi", "punjabi", "bengali", "gujarati"):
            profile = {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"}
            source = "user_cultural_heritage"
            confidence = 0.98
        elif "east_asian" in heritage_key:
            profile = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "western_modern", "male_costume": "western_modern"}
            source = "user_cultural_heritage"
            confidence = 0.98

    # 2. Check script keywords (highest priority for topic-specific narratives)
    if not profile and script_text:
        text_lower = script_text.lower()
        for keywords, candidate_profile in SCRIPT_CULTURE_KEYWORDS:
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    profile = candidate_profile
                    source = f"script_keyword:{kw}"
                    confidence = 0.95
                    break
            if profile:
                break

    # 3. Check user home country (from user identity information)
    if not profile and user_home_country:
        cleaned_country = user_home_country.lower().strip()
        if cleaned_country in COUNTRY_CULTURE_MAP:
            profile = COUNTRY_CULTURE_MAP[cleaned_country]
            source = f"user_home_country:{cleaned_country}"
            confidence = 0.90

    # 4. Fallback to language code mapping
    if not profile:
        lang_code = language.lower().strip()
        if lang_code in ("te", "ta", "kn", "ml"):
            profile = {"culture": "indian_south", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_traditional_dhoti"}
            source = f"language_code:{lang_code}"
            confidence = 0.85
        elif lang_code in ("hi", "pa", "gu", "bn"):
            profile = {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"}
            source = f"language_code:{lang_code}"
            confidence = 0.85
        elif lang_code in ("ja", "ko", "zh"):
            profile = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "western_modern", "male_costume": "western_modern"}
            source = f"language_code:{lang_code}"
            confidence = 0.85
        else:
            profile = {"culture": "western_global", "ethnicity": "caucasian", "female_costume": "western_modern", "male_costume": "western_modern"}
            source = "default_western_global"
            confidence = 0.60

    # Resolve music video and dance genre-specific costume & ethnicity adaptations
    combined_cues = f"{genre} {video_format} {dance_type} {script_text}".lower()
    ethnicity = profile["ethnicity"]
    primary_ethnicity = None

    if "rain" in combined_cues or "monsoon" in combined_cues or "vanammo" in combined_cues:
        selected_costume = "telugu_rain_folk_saree"
    elif "mass" in combined_cues or "jathara" in combined_cues or "teenmaar" in combined_cues or "dj" in combined_cues:
        selected_costume = "telugu_mass_festive"
    elif "hip_hop" in combined_cues or "rap" in combined_cues or "trap" in combined_cues:
        selected_costume = "american_hiphop_streetwear"
        ethnicity = "african_american"
        primary_ethnicity = "African American / Urban Streetwear"
    elif "rock" in combined_cues or "metal" in combined_cues or "punk" in combined_cues:
        selected_costume = "american_rock_leather"
        ethnicity = "american_rocker"
        primary_ethnicity = "American Rock / Alternative"
    elif "pop" in combined_cues or "edm" in combined_cues:
        selected_costume = "american_pop_glam"
        ethnicity = "american_popstar"
        primary_ethnicity = "American Pop Star"
    elif "rnb" in combined_cues or "soul" in combined_cues:
        selected_costume = "american_rnb_velvet"
        ethnicity = "african_american"
        primary_ethnicity = "African American / R&B Artist"
    elif "line_dance" in combined_cues or "western_swing" in combined_cues or ("country" in combined_cues and "music" in combined_cues):
        selected_costume = "american_western_country"
        ethnicity = "american_country"
        primary_ethnicity = "American Country Western"
    elif "tarantella" in combined_cues or "pizzica" in combined_cues or ("dance" in combined_cues and "ital" in profile["culture"]):
        selected_costume = "italian_tarantella_folk"
    elif "jarabe" in combined_cues or "zapateado" in combined_cues or "folklore" in combined_cues or ("dance" in combined_cues and "mexic" in profile["culture"]):
        selected_costume = "mexican_jalisco_charro"
    elif "water_sleeve" in combined_cues or "shuixiu" in combined_cues or "ribbon" in combined_cues or ("dance" in combined_cues and "east_asian" in profile["culture"]):
        selected_costume = "chinese_hanfu_water_sleeves"
    elif "classic" in combined_cues or "bharat" in combined_cues or "kuchipudi" in combined_cues or "kathak" in combined_cues:
        selected_costume = "indian_traditional_saree"
    else:
        selected_costume = profile["female_costume"] if gender.lower() == "female" else profile["male_costume"]

    costume_stack = lookup_costume_stack(selected_costume, gender=gender)
    cultural_stack = lookup_cultural_stack(profile["culture"], language=language)

    # Collect recommended LoRAs
    active_loras: list[dict[str, Any]] = []
    if "recommended_lora" in costume_stack:
        active_loras.append(costume_stack["recommended_lora"])
    if "jewelry_lora" in costume_stack:
        active_loras.append(costume_stack["jewelry_lora"])
    if "recommended_loras" in cultural_stack.get("visual_diffusion", {}):
        for lora_name in cultural_stack["visual_diffusion"]["recommended_loras"]:
            if not any(al.get("name") == lora_name for al in active_loras):
                active_loras.append({"name": lora_name, "weight": 0.85})

    # Resolve art style intelligence, prompts, and style LoRAs
    style_query = art_style or video_format or script_text
    style_info = lookup_art_style(style_query=style_query, country=user_home_country)
    if "recommended_lora" in style_info:
        sl = style_info["recommended_lora"]
        if not any(al.get("path") == sl.get("path") for al in active_loras):
            active_loras.append(sl)

    # Resolve Voice ID from cultural stack voice_tts mapping
    selected_voice = resolve_cultural_voice(culture=profile["culture"], language=language, gender=gender)
    voice_provider = cultural_stack.get("voice_tts", {}).get("provider", "Microsoft Azure Speech HD")

    # Resolve Music & Soundtrack from cultural stack or art style
    audio_info = cultural_stack.get("audio_soundtrack", {})
    genre_key = genre.lower().strip()
    selected_music = audio_info.get(genre_key, audio_info.get("default", "Cinematic acoustic score"))
    if style_info.get("music_style") and (art_style or any(k in combined_cues for k in ("scenic", "walk", "drive", "lounge", "forest", "alps", "rain"))):
        selected_music = style_info["music_style"]
    selected_sfx = f"Culturally authentic foley and sound design for {profile['culture']}"

    logger.info(
        f"cultural_context_derived: culture={profile['culture']}, ethnicity={ethnicity}, "
        f"costume={selected_costume}, voice={selected_voice}, loras={len(active_loras)}, source={source}"
    )

    return DerivedCulturalContext(
        culture=profile["culture"],
        culture_name=cultural_stack.get("culture_name", profile["culture"]),
        ethnicity=ethnicity,
        primary_ethnicity=primary_ethnicity or cultural_stack.get("primary_ethnicity", ethnicity),
        clothing_style=selected_costume,
        outfit_description=costume_stack.get("prompt_enhancer", ""),
        jewelry_description=costume_stack.get("jewelry_anchor", ""),
        art_style=style_info.get("display_name", "photorealistic_cinematic"),
        art_style_display=style_info.get("display_name", "Broadcast 4K Photorealistic Cinematic"),
        art_style_prompt=style_info.get("prompt_decorations", ""),
        art_style_lighting=style_info.get("lighting_scheme", ""),
        art_style_palette=style_info.get("color_palette", ""),
        recommended_loras=active_loras,
        voice_id=selected_voice,
        voice_provider=voice_provider,
        music_style=selected_music,
        sfx_style=selected_sfx,
        derivation_source=source,
        confidence_score=confidence,
    )


__all__ = ["COUNTRY_CULTURE_MAP", "DerivedCulturalContext", "derive_cultural_context"]
