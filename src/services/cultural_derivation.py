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
_IN_NORTH = {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"}
_AU = {"culture": "australian", "ethnicity": "australian", "female_costume": "western_modern", "male_costume": "western_modern"}
_IT = {"culture": "italian", "ethnicity": "italian", "female_costume": "italian_tarantella_folk", "male_costume": "italian_tarantella_folk"}
_MX = {"culture": "mexican", "ethnicity": "mexican", "female_costume": "mexican_jalisco_charro", "male_costume": "mexican_jalisco_charro"}
_EA = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "chinese_hanfu_water_sleeves", "male_costume": "chinese_hanfu_water_sleeves"}
_NORDIC = {"culture": "nordic", "ethnicity": "nordic", "female_costume": "western_modern", "male_costume": "western_modern"}
_UK = {"culture": "british_uk", "ethnicity": "british", "female_costume": "western_modern", "male_costume": "western_modern"}
_WEST = {"culture": "western_global", "ethnicity": "caucasian", "female_costume": "western_modern", "male_costume": "western_modern"}
_MID_EAST = {"culture": "egyptian", "ethnicity": "middle_eastern", "female_costume": "western_modern", "male_costume": "western_modern"}

COUNTRY_CULTURE_MAP: dict[str, dict[str, str]] = {
    "in": _IN, "india": _IN, "bharat": _IN, "au": _AU, "australia": _AU, "aus": _AU,
    "it": _IT, "italy": _IT, "mx": _MX, "mexico": _MX, "jp": _EA, "japan": _EA,
    "kr": _EA, "korea": _EA, "south korea": _EA, "cn": _EA, "china": _EA,
    "is": _NORDIC, "iceland": _NORDIC, "se": _NORDIC, "sweden": _NORDIC, "no": _NORDIC, "norway": _NORDIC, "dk": _NORDIC, "denmark": _NORDIC, "fi": _NORDIC, "finland": _NORDIC,
    "uk": _UK, "gb": _UK, "united kingdom": _UK, "england": _UK, "scotland": _UK, "wales": _UK, "britain": _UK,
    "us": _WEST, "usa": _WEST, "united states": _WEST, "fr": _WEST, "france": _WEST, "de": _WEST, "germany": _WEST,
    "ae": _MID_EAST, "uae": _MID_EAST, "dubai": _MID_EAST, "eg": _MID_EAST, "egypt": _MID_EAST, "sa": _MID_EAST, "saudi": _MID_EAST,
}

SCRIPT_CULTURE_KEYWORDS: list[tuple[list[str], dict[str, str]]] = [
    (["iceland", "reykjavik", "sweden", "stockholm", "norway", "oslo", "denmark", "copenhagen", "finland", "helsinki", "nordic", "scandinavia", "fjord", "geysir"], _NORDIC),
    (["london", "england", "scotland", "edinburgh", "britain", "british", "westminster", "thames", "buckingham", "uk"], _UK),
    (["hyderabad", "hyd", "charminar", "chennai", "bengaluru", "bangalore", "kerala", "tirupati", "kanchipuram", "telugu", "tamil", "kannada", "malayalam", "saree", "pattu", "pelli", "lungi", "panche", "kuchipudi", "bharatanatyam", "tollywood", "gongura", "biryani", "dosa", "idli", "andhra", "telangana", "rayalaseema", "vizag", "vijayawada"], _IN),
    (["delhi", "mumbai", "punjab", "bhangra", "garba", "gujarat", "kolkata", "bengal", "varanasi", "ghats", "kathak", "bollywood", "sherwani", "kurta", "lehenga", "anarkali", "dupatta", "taj mahal", "jaipur", "rajasthan", "diwali", "holi"], _IN_NORTH),
    (["italy", "italian", "rome", "tarantella", "pizzica", "florence", "venice", "naples", "sicily"], _IT),
    (["mexico", "mexican", "mariachi", "tapatio", "jarabe", "zapateado", "guadalajara", "oaxaca", "sombrero", "charro", "folklore"], _MX),
    (["water sleeves", "shuixiu", "hanfu", "guzheng", "erhu", "beijing", "shanghai", "china", "chinese"], _EA),
    (["tokyo", "kyoto", "japan", "japanese", "kimono", "yukata", "seoul", "korea", "korean", "hanbok", "anime", "manga", "k-pop"], _EA),
    (["dubai", "uae", "abu dhabi", "egypt", "cairo", "nile", "pyramid", "arab", "arabic", "middle east"], _MID_EAST),
    (["australia", "sydney", "melbourne", "brisbane", "perth", "adelaide", "bondi", "outback", "great barrier reef", "gold coast", "koala", "kangaroo", "aussie"], _AU),
    (["paris", "louvre", "eiffel", "france", "french", "new york", "hollywood", "suit", "tuxedo", "blazer", "cocktail dress", "jeans", "casual"], _WEST),
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
    setting_type: str = "urban_city"
    environment_space: str = "outdoor"  # indoor, outdoor, semi_outdoor
    time_period: str = "contemporary"
    weather_climate: str = "clear_daylight"
    weather_condition: str = "clear_daylight"
    lighting_scheme: str = "natural_open_daylight_5600k"
    props_instruments: str = ""
    venue_architecture: str = ""
    social_context: str = "solo"
    art_style: str = "photorealistic_cinematic"
    art_style_display: str = "Broadcast 4K Photorealistic Cinematic"
    art_style_prompt: str = ""
    art_style_lighting: str = ""
    art_style_palette: str = ""
    architecture_style: str = ""
    recommended_loras: list[dict[str, Any]] = Field(default_factory=list)
    voice_id: str = "en-US-ChristopherNeural"
    voice_provider: str = "Microsoft Azure Speech HD"
    music_style: str = "Cinematic acoustic score"
    sfx_style: str = "Authentic foley and sound design"
    derivation_source: str
    confidence_score: float = 1.0


def _derive_environment(cues: str) -> dict[str, str]:
    """Derive setting, spatial environment (indoor/outdoor), period, climate, lighting, and props."""
    setting = "urban_city"
    if any(k in cues for k in ("alpine", "mountain", "glacier", "everest", "peak", "himalaya")): setting = "alpine_wilderness"
    elif any(k in cues for k in ("forest", "jungle", "savanna", "safari", "wildlife", "rainforest")): setting = "nature_wilderness"
    elif any(k in cues for k in ("village", "rural", "paddy", "jathara", "bazaar", "temple", "panche")): setting = "village_rural"
    elif any(k in cues for k in ("palace", "fort", "kingdom", "dynasty", "monumental", "bahubali")): setting = "historical_palace"
    elif any(k in cues for k in ("beach", "coast", "ocean", "tropical", "island", "sea")): setting = "tropical_coastal"

    space = "outdoor"
    if any(k in cues for k in ("indoor", "inside", "hotel", "ballroom", "living room", "bedroom", "kitchen", "office", "studio", "cafe", "restaurant", "banquet", "interior", "classroom", "gym", "museum", "mansion", "auditorium")):
        space = "indoor"
    elif any(k in cues for k in ("balcony", "veranda", "porch", "patio", "terrace", "gazebo", "courtyard", "awning")):
        space = "semi_outdoor"

    period = "contemporary"
    if any(k in cues for k in ("ancient", "myth", "purana", "dynasty", "kingdom", "vedic", "medieval")): period = "ancient_mythological"
    elif any(k in cues for k in ("scifi", "cyberpunk", "future", "futuristic", "2050")): period = "futuristic_scifi"

    weather = "clear_daylight"
    if any(k in cues for k in ("blizzard", "arctic storm", "heavy snow")): weather = "snow_blizzard"
    elif any(k in cues for k in ("snow", "subzero", "frost", "ice", "winter")): weather = "snowy_subzero"
    elif any(k in cues for k in ("heavy rain", "downpour", "torrential", "storm", "deluge")): weather = "heavy_rain"
    elif any(k in cues for k in ("rain", "monsoon", "thunder", "vanammo")): weather = "monsoon_rain"
    elif any(k in cues for k in ("drizzle", "shower", "rainy")): weather = "gentle_drizzle"
    elif any(k in cues for k in ("hot sun", "fiery sun", "scorching", "heatwave", "desert heat")): weather = "scorching_hot_sun"
    elif any(k in cues for k in ("cloudy evening", "evening clouds", "sunset", "dusk", "twilight")): weather = "cloudy_evening"
    elif any(k in cues for k in ("cloudy", "overcast", "grey sky", "gray sky")): weather = "cloudy_overcast"
    elif any(k in cues for k in ("fog", "mist", "haze")): weather = "misty_fog"
    elif any(k in cues for k in ("golden hour", "warm sunset")): weather = "golden_hour"
    elif any(k in cues for k in ("night", "midnight")): weather = "night_ambient"

    lighting = "natural_open_daylight_5600k"
    if space == "indoor":
        if any(k in cues for k in ("stadium", "arena", "floodlight", "sports")): lighting = "bright_indoor_stadium_lighting"
        elif any(k in cues for k in ("hotel", "ballroom", "banquet", "reception", "wedding", "chandelier")): lighting = "warm_indoor_event_lighting"
        elif any(k in cues for k in ("hearth", "fireplace", "cabin", "shelter", "ember")): lighting = "cozy_hearth_fireplace_lighting"
        elif any(k in cues for k in ("neon", "club", "party", "bar", "cyber")): lighting = "moody_neon_ambient_lighting"
        else: lighting = "soft_indoor_ambient_lighting"
    else:
        if any(k in cues for k in ("stadium", "floodlight", "concert stage", "arena")): lighting = "bright_outdoor_stadium_lighting"
        elif any(k in cues for k in ("sunset", "golden hour", "dusk", "twilight")): lighting = "golden_hour_sunset_lighting"
        elif any(k in cues for k in ("night", "midnight", "neon", "cyberpunk")): lighting = "moody_neon_night_lighting"
        elif any(k in cues for k in ("rain", "storm", "downpour", "monsoon", "cloudy", "overcast", "fog", "snow")): lighting = "diffuse_overcast_daylight_5600k"
        elif any(k in cues for k in ("hot sun", "fiery sun", "scorching", "desert")): lighting = "bright_direct_sunlight_5800k"

    props = ""
    if any(k in cues for k in ("teenmaar", "mass", "dhol", "drum")): props = "dholak, dappu, brass cymbals"
    elif any(k in cues for k in ("kuchipudi", "bharat", "classical")): props = "ghungroo brass bell anklets, brass puja lamps"
    elif any(k in cues for k in ("trek", "walking", "hike", "tour")): props = "walking stick, modern daypack, camera gimbal"
    elif any(k in cues for k in ("survival", "mountain")): props = "climbing ropes, carabiners, alpine snow boots"

    social = "solo"
    if any(k in cues for k in ("mass", "jathara", "festival", "carnival", "troupe", "crowd", "group")): social = "festive_crowd"
    elif any(k in cues for k in ("duet", "romantic", "couple")): social = "intimate_pair"
    elif "walk" in cues or "tour" in cues: social = "solo_walk"

    return {"setting_type": setting, "environment_space": space, "time_period": period, "weather_climate": weather, "lighting_scheme": lighting, "props_instruments": props, "social_context": social}


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
    """Deterministically derive ethnicity, culture, clothing, outfits, and LoRAs."""
    profile: dict[str, str] | None = None
    source = "western_global_fallback"
    confidence = 0.50

    # 1. Match country/cultural keywords directly in script_text / topic / theme / idea FIRST
    if script_text:
        text_lower = script_text.lower()
        for keywords, candidate_profile in SCRIPT_CULTURE_KEYWORDS:
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    profile, source, confidence = candidate_profile, f"script_keyword:{kw}", 0.98
                    break
            if profile:
                break

    # 2. If no location keyword in script_text, check explicit user cultural heritage
    if not profile and user_cultural_heritage:
        heritage_key = user_cultural_heritage.lower().strip()
        if "south" in heritage_key or heritage_key in ("telugu", "tamil", "kannada", "malayalam"):
            profile = {"culture": "indian_south", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_traditional_dhoti"}
            source, confidence = "user_cultural_heritage", 0.90
        elif "north" in heritage_key or heritage_key in ("hindi", "punjabi", "bengali", "gujarati"):
            profile = {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"}
            source, confidence = "user_cultural_heritage", 0.90
        elif "nordic" in heritage_key or heritage_key in ("iceland", "sweden", "norway"):
            profile = {"culture": "nordic", "ethnicity": "nordic", "female_costume": "western_modern", "male_costume": "western_modern"}
            source, confidence = "user_cultural_heritage", 0.90
        elif "british" in heritage_key or heritage_key in ("uk", "london", "england"):
            profile = {"culture": "british_uk", "ethnicity": "british", "female_costume": "western_modern", "male_costume": "western_modern"}
            source, confidence = "user_cultural_heritage", 0.90
        elif "east_asian" in heritage_key:
            profile = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "western_modern", "male_costume": "western_modern"}
            source, confidence = "user_cultural_heritage", 0.90

    # 3. Check user home country
    if not profile and user_home_country:
        cleaned_country = user_home_country.lower().strip()
        if cleaned_country in COUNTRY_CULTURE_MAP:
            profile, source, confidence = COUNTRY_CULTURE_MAP[cleaned_country], f"user_home_country:{cleaned_country}", 0.85

    # 4. Spoken language code
    if not profile:
        lang_code = language.lower().strip().replace("_", "-").split("-")[0]
        if lang_code in ("is", "sv", "no", "nb", "da", "fi"):
            profile, source, confidence = {"culture": "nordic", "ethnicity": "nordic", "female_costume": "western_modern", "male_costume": "western_modern"}, f"language_code:{lang_code}", 0.85
        elif lang_code in ("te", "ta", "kn", "ml"):
            profile, source, confidence = {"culture": "indian_south", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_traditional_dhoti"}, f"language_code:{lang_code}", 0.85
        elif lang_code in ("hi", "pa", "gu", "bn"):
            profile, source, confidence = {"culture": "indian_north", "ethnicity": "south_asian", "female_costume": "indian_traditional_saree", "male_costume": "indian_royal_sherwani"}, f"language_code:{lang_code}", 0.85
        elif lang_code in ("ja", "ko", "zh"):
            profile, source, confidence = {"culture": "east_asian", "ethnicity": "east_asian", "female_costume": "western_modern", "male_costume": "western_modern"}, f"language_code:{lang_code}", 0.85
        else:
            profile, source, confidence = {"culture": "western_global", "ethnicity": "caucasian", "female_costume": "western_modern", "male_costume": "western_modern"}, "default_western_global", 0.60

    combined_cues = f"{genre} {video_format} {dance_type} {script_text}".lower()
    ethnicity = profile["ethnicity"]
    primary_ethnicity = None
    is_indian = "indian" in profile.get("culture", "") or "telugu" in combined_cues or language in ("te", "ta", "kn", "hi")

    # Explicit outfit/cultural overrides in prompt (e.g., "Indian in saree in Norway")
    if any(k in combined_cues for k in ("saree", "pattu", "lehenga", "anarkali")):
        selected_costume, ethnicity, primary_ethnicity = "indian_traditional_saree", "south_asian", "South Asian / Indian"
    elif any(k in combined_cues for k in ("dhoti", "pancha")):
        selected_costume, ethnicity, primary_ethnicity = "indian_traditional_dhoti", "south_asian", "South Asian / Indian"
    elif any(k in combined_cues for k in ("sherwani", "kurta")):
        selected_costume, ethnicity, primary_ethnicity = "indian_royal_sherwani", "south_asian", "South Asian / Indian"
    elif any(k in combined_cues for k in ("hanfu", "water_sleeve", "shuixiu")):
        selected_costume, ethnicity, primary_ethnicity = "chinese_hanfu_water_sleeves", "east_asian", "East Asian"
    elif any(k in combined_cues for k in ("charro", "sombrero")):
        selected_costume, ethnicity, primary_ethnicity = "mexican_jalisco_charro", "mexican", "Mexican"
    elif is_indian and ("rain" in combined_cues or "monsoon" in combined_cues or "vanammo" in combined_cues):
        selected_costume = "telugu_rain_folk_saree"
    elif is_indian and any(re.search(rf"\b{re.escape(k)}\b", combined_cues) for k in ("mass", "jathara", "teenmaar", "dj", "folk")):
        selected_costume = "telugu_mass_festive"
    elif "hip_hop" in combined_cues or "rap" in combined_cues or "trap" in combined_cues:
        selected_costume, ethnicity, primary_ethnicity = "american_hiphop_streetwear", "african_american", "African American / Urban Streetwear"
    elif "rock" in combined_cues or "metal" in combined_cues or "punk" in combined_cues:
        selected_costume, ethnicity, primary_ethnicity = "american_rock_leather", "american_rocker", "American Rock / Alternative"
    elif "pop" in combined_cues or "edm" in combined_cues:
        selected_costume, ethnicity, primary_ethnicity = "american_pop_glam", "american_popstar", "American Pop Star"
    elif "rnb" in combined_cues or "soul" in combined_cues:
        selected_costume, ethnicity, primary_ethnicity = "american_rnb_velvet", "african_american", "African American / R&B Artist"
    elif "line_dance" in combined_cues or "western_swing" in combined_cues or ("country" in combined_cues and "music" in combined_cues):
        selected_costume, ethnicity, primary_ethnicity = "american_western_country", "american_country", "American Country Western"
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

    active_loras: list[dict[str, Any]] = []
    is_scenic_or_walking = any(k in f"{video_format} {genre}".lower() for k in ("walking", "nature", "scenic", "tourist", "travel"))
    if not is_scenic_or_walking:
        if "recommended_lora" in costume_stack: active_loras.append(costume_stack["recommended_lora"])
        if "jewelry_lora" in costume_stack: active_loras.append(costume_stack["jewelry_lora"])
        for lora_name in cultural_stack.get("visual_diffusion", {}).get("recommended_loras", []):
            if not any(al.get("name") == lora_name for al in active_loras):
                active_loras.append({"name": lora_name, "weight": 0.85})

    style_info = lookup_art_style(style_query=art_style or video_format or script_text, country=user_home_country)
    if "recommended_lora" in style_info:
        sl = style_info["recommended_lora"]
        if not any(al.get("path") == sl.get("path") for al in active_loras):
            active_loras.append(sl)

    selected_voice = resolve_cultural_voice(culture=profile["culture"], language=language, gender=gender)
    voice_provider = cultural_stack.get("voice_tts", {}).get("provider", "Microsoft Azure Speech HD")

    audio_info = cultural_stack.get("audio_soundtrack", {})
    selected_music = audio_info.get(genre.lower().strip(), audio_info.get("default", "Cinematic acoustic score"))
    if style_info.get("music_style") and (art_style or any(k in combined_cues for k in ("scenic", "walk", "drive", "lounge", "forest", "alps", "rain"))):
        selected_music = style_info["music_style"]
    selected_sfx = audio_info.get("sfx", "procedural_foley")
    env = _derive_environment(combined_cues)
    lighting_scheme = style_info.get("lighting_scheme") or env["lighting_scheme"]

    logger.info(f"cultural_context_derived: culture={profile['culture']}, costume={selected_costume}, setting={env['setting_type']}, space={env['environment_space']}, weather={env['weather_climate']}, lighting={lighting_scheme}")

    return DerivedCulturalContext(
        culture=profile["culture"], culture_name=cultural_stack.get("culture_name", profile["culture"]),
        ethnicity=ethnicity, primary_ethnicity=primary_ethnicity or cultural_stack.get("primary_ethnicity", ethnicity),
        clothing_style=selected_costume, outfit_description=costume_stack.get("prompt_enhancer", ""),
        jewelry_description=costume_stack.get("jewelry_anchor", ""), setting_type=env["setting_type"],
        environment_space=env["environment_space"], time_period=env["time_period"],
        weather_climate=env["weather_climate"], weather_condition=env["weather_climate"],
        lighting_scheme=lighting_scheme, props_instruments=env["props_instruments"],
        social_context=env["social_context"], art_style=style_info.get("display_name", "photorealistic_cinematic"),
        art_style_display=style_info.get("display_name", "Broadcast 4K Photorealistic Cinematic"),
        art_style_prompt=style_info.get("prompt_decorations", ""), art_style_lighting=lighting_scheme,
        art_style_palette=style_info.get("color_palette", ""), architecture_style=style_info.get("architecture_style", ""),
        recommended_loras=active_loras, voice_id=selected_voice, voice_provider=voice_provider,
        music_style=selected_music, sfx_style=selected_sfx, derivation_source=source, confidence_score=confidence,
    )


__all__ = ["COUNTRY_CULTURE_MAP", "DerivedCulturalContext", "derive_cultural_context"]
