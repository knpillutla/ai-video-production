"""Universal Concert Setting & Directorial Environment Catalog.

Provides a 5-axis composable environment for concerts of ANY genre, culture, country, or venue:
1. --venue-type (indoor, outdoor, hybrid)
2. --time-of-day (dawn, morning, noon, golden_hour, sunset, twilight, evening, night)
3. --stage-setting (stadium, festival_stage, rooftop, balcony, beach_platform, temple_hall,
                   cathedral, jazz_club, tiny_desk, warehouse, garden_courtyard, yacht_deck,
                   broadway_theatre, desert_oasis, cavern, opera_house, sofa_lounge, living_room,
                   amphitheatre, club_deck, plaza)
4. --background (arena_crowd, city_skyline, beach_ocean, forest_woods, mountain_peaks,
                desert_dunes, heritage_monument, opera_auditorium, lakefront, tokyo_neon,
                cathedral_nave, botanical_garden, mediterranean_coast, industrial_brick)
5. --weather (clear, cloudy, rain, snow, mist_fog)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConcertSettingPreset:
    """Universal 5-axis concert venue and environmental lighting configuration."""

    setting_id: str
    display_name: str
    venue_type: str
    time_of_day: str
    stage_setting: str
    background: str
    weather: str
    lighting_environment: str
    stage_environment: str
    audience_environment: str
    plate1_desc: str
    plate2_desc: str
    plate3_desc: str


STAGE_DESCRIPTIONS = {
    "stadium": ("monumental proscenium arena deck with steel trusses, LED arrays, and pyro risers", "wide arena deck"),
    "festival_stage": ("open-air festival mainstage under architectural shade sails and acoustic shell", "festival platform"),
    "rooftop": ("sleek penthouse rooftop terrace with glass balustrades overlooking metropolitan skyline", "rooftop deck"),
    "balcony": ("intimate architectural balcony overlooking scenic gardens and ambient lanterns", "balcony stage"),
    "beach_platform": ("rustic-luxury teakwood and weathered driftwood platform directly on coastal ocean shoreline sand", "coastal beach deck"),
    "temple_hall": ("sacred heritage stone hall with carved pillars, brass lamps, and ornate carpets", "carpeted stone dais"),
    "cathedral": ("majestic Gothic cathedral sanctuary with soaring vaulted arches, stained glass windows, and grand organ pipes", "sanctuary chancel"),
    "jazz_club": ("intimate candlelit basement jazz club or speakeasy with exposed brick walls, cabaret tables, and acoustic bass", "jazz club stage"),
    "tiny_desk": ("intimate acoustic broadcasting office desk surrounded by vinyl record shelves, eclectic books, and desk lamps", "acoustic office desk"),
    "warehouse": ("gritty industrial warehouse deck with raw concrete pillars, exposed steel ductwork, and neon laser grids", "warehouse deck"),
    "garden_courtyard": ("European baroque palace courtyard or botanical pavilion surrounded by blooming flora and festoon lights", "courtyard pavilion"),
    "yacht_deck": ("luxury ocean yacht teakwood aft deck stage under open star-filled skies with ocean surf reflections", "yacht aft deck"),
    "broadway_theatre": ("classic Broadway theatrical proscenium with illuminated marquee lights and plush velvet box seating", "theatrical proscenium"),
    "desert_oasis": ("Moroccan Bedouin desert camp stage with low brass tables, rich patterned kilim rugs, and fire lanterns", "desert carpeted dais"),
    "cavern": ("subterranean limestone cavern stage with illuminated stalactites, acoustic rock chambers, and pool reflections", "cavern platform"),
    "opera_house": ("majestic European tiered opera stage with gilded mouldings and grand velvet curtains", "gilded proscenium"),
    "sofa_lounge": ("cozy acoustic unplugged lounge with plush velvet sofas, low amber lamps, and rugs", "intimate lounge"),
    "living_room": ("warm biophilic studio living room with hardwood floors, bookshelf backdrop, and rugs", "living room studio"),
    "amphitheatre": ("monumental open-air stone amphitheatre carved into natural rock and hillside", "stone amphitheatre"),
    "club_deck": ("electronic dance music stage riser with chrome railings, laser cages, and synth decks", "club stage"),
    "plaza": ("historic European cobblestone town square or Latin plaza with festoon fairy lights", "plaza stage"),
}

TIME_DESCRIPTIONS = {
    "dawn": "Crisp cool dawn transitioning to soft morning blue hour, first golden rays piercing morning haze.",
    "morning": "Crisp balanced natural daylight (5500K), clean open sky, authentic daylight skin tones.",
    "noon": "Bright overhead midday sunlight with crisp architectural shadows and vivid color saturation.",
    "golden_hour": "Low-angle warm golden hour amber light (3000K) casting long cinematic shadows and radiant edge rim glow.",
    "sunset": "Deep crimson and orange sunset sky, warm horizontal glow reflecting across surfaces and ocean.",
    "twilight": "Deep violet-indigo twilight sky, stage floodlights and ambient lanterns sparkling into life.",
    "evening": "Atmospheric evening with glowing warm amber stage wash, starry sky, and subtle theatrical accents.",
    "night": "Deep dark night sky, sharp theatrical spotlights, moving beam lights, lasers, and high-contrast stage glow.",
}

BACKGROUND_DESCRIPTIONS = {
    "arena_crowd": "Towering stadium seating tiers packed with roaring spectators waving synchronized lightsticks.",
    "city_skyline": "Dazzling metropolitan skyline of towering glass skyscrapers and glowing city lights in soft bokeh.",
    "beach_ocean": "Crashing turquoise ocean surf, coastal shoreline sands, and distant marine horizon.",
    "forest_woods": "Towering ancient pine and banyan canopies, mossy forest glades, and sunbeams filtering through trees.",
    "mountain_peaks": "Majestic snow-capped alpine granite peaks and dramatic mountain canyon vistas.",
    "desert_dunes": "Sculpted golden sand dunes under an expansive desert sky with ambient fire lanterns.",
    "heritage_monument": "Ancient stone temple architecture, historic medieval castle walls, or royal palace courtyards.",
    "opera_auditorium": "Gilded multi-tiered theatre balconies, private opera boxes, and crimson velvet seating.",
    "lakefront": "Pristine mountain lake reflecting the glowing performance lights with distant wooded shores.",
    "tokyo_neon": "Vibrant futuristic Shibuya or Neo-Tokyo neon streetscape with glowing holographic billboards and cyber lanterns.",
    "cathedral_nave": "Soaring Gothic stone nave, stained glass rose window catching light, and vaulted stone arches.",
    "botanical_garden": "Victorian glass conservatory greenhouse filled with tropical palms, ferns, and cascading orchids.",
    "mediterranean_coast": "Sun-drenched Amalfi or Greek caldera cliffside with whitewashed villas cascading to sapphire sea.",
    "industrial_brick": "Weathered red brick warehouse interior with exposed steel girders, industrial ductwork, and warm edison bulbs.",
}

WEATHER_DESCRIPTIONS = {
    "clear": "Clear crisp atmosphere, zero haze, pristine optical clarity.",
    "cloudy": "Moody diffused cloudscapes, soft diffused ambient lighting.",
    "rain": "Glistening wet stage deck reflections, falling rain droplets catching laser and spotlight beams.",
    "snow": "Gentle winter snow flurries floating through spotlight beams, light frost on stage borders.",
    "mist_fog": "Atmospheric low-lying volumetric ground fog and ethereal rolling haze catching lights.",
}


def _match_key(val: str, catalog: dict[str, Any], aliases: Optional[dict[str, str]] = None) -> Optional[str]:
    v = val.lower().strip()
    if aliases and v in aliases:
        return aliases[v]
    for k in sorted(catalog.keys(), key=len, reverse=True):
        if k in v:
            return k
    return None


def resolve_concert_setting(
    setting_or_venue: Optional[str] = None,
    venue_type: Optional[str] = None,
    time_of_day: Optional[str] = None,
    stage_setting: Optional[str] = None,
    background: Optional[str] = None,
    weather: Optional[str] = None,
) -> ConcertSettingPreset:
    """Resolve 5-axis concert environment with turnkey presets and granular overrides."""
    target = str(setting_or_venue or "").lower().strip()

    # Baseline seed from setting_or_venue
    v_type = venue_type or ("outdoor" if any(k in target for k in ("outdoor", "beach", "day", "plaza", "field", "amphi", "roof", "garden", "yacht", "desert")) else ("hybrid" if any(k in target for k in ("balcony", "veranda", "terrace", "pavilion", "hybrid")) else "indoor"))
    t_day = time_of_day or ("sunset" if "beach" in target else ("morning" if "day" in target else "night"))
    s_stage = stage_setting or ("beach_platform" if "beach" in target else ("rooftop" if "roof" in target else ("temple_hall" if "temple" in target else ("cathedral" if "cathedral" in target or "church" in target else ("jazz_club" if "jazz" in target else ("tiny_desk" if "tiny" in target or "desk" in target else ("warehouse" if "warehouse" in target or "rave" in target else ("garden_courtyard" if "garden" in target else ("yacht_deck" if "yacht" in target else ("sofa_lounge" if "sofa" in target else "stadium"))))))))))
    b_ground = background or ("beach_ocean" if "beach" in target else ("city_skyline" if "roof" in target else ("heritage_monument" if "temple" in target else ("cathedral_nave" if "cathedral" in target else ("industrial_brick" if "warehouse" in target else ("botanical_garden" if "garden" in target else "arena_crowd"))))))
    w_feat = weather or ("clear" if not any(k in target for k in ("rain", "snow", "fog", "mist")) else ("rain" if "rain" in target else "snow"))

    # Granular overrides with rich global aliases
    stage_aliases = {"beach": "beach_platform", "desk": "tiny_desk", "rave": "warehouse", "garden": "garden_courtyard", "yacht": "yacht_deck", "broadway": "broadway_theatre", "oasis": "desert_oasis", "cave": "cavern", "church": "cathedral", "sofa": "sofa_lounge"}
    time_aliases = {"day": "morning", "afternoon": "noon", "midday": "noon", "dusk": "twilight", "dark": "night", "sunrise": "dawn"}
    bg_aliases = {"city": "city_skyline", "crowd": "arena_crowd", "ocean": "beach_ocean", "forest": "forest_woods", "mountains": "mountain_peaks", "desert": "desert_dunes", "tokyo": "tokyo_neon", "neon": "tokyo_neon", "botanical": "botanical_garden", "amalfi": "mediterranean_coast", "brick": "industrial_brick"}
    weather_aliases = {"sunny": "clear", "overcast": "cloudy", "storm": "rain", "drizzle": "rain", "blizzard": "snow", "frost": "snow", "fog": "mist_fog", "haze": "mist_fog"}

    if stage_setting:
        matched = _match_key(stage_setting, STAGE_DESCRIPTIONS, stage_aliases)
        if matched: s_stage = matched
    if time_of_day:
        matched = _match_key(time_of_day, TIME_DESCRIPTIONS, time_aliases)
        if matched: t_day = matched
    if background:
        matched = _match_key(background, BACKGROUND_DESCRIPTIONS, bg_aliases)
        if matched: b_ground = matched
    if weather:
        matched = _match_key(weather, WEATHER_DESCRIPTIONS, weather_aliases)
        if matched: w_feat = matched
    if venue_type:
        v_low = venue_type.lower()
        v_type = "outdoor" if any(k in v_low for k in ("out", "open", "outdoor")) else ("hybrid" if any(k in v_low for k in ("hyb", "semi", "veranda", "terrace", "balcony")) else "indoor")

    stage_full, stage_short = STAGE_DESCRIPTIONS.get(s_stage, STAGE_DESCRIPTIONS["stadium"])
    time_full = TIME_DESCRIPTIONS.get(t_day, TIME_DESCRIPTIONS["night"])
    bg_full = BACKGROUND_DESCRIPTIONS.get(b_ground, BACKGROUND_DESCRIPTIONS["arena_crowd"])
    weather_full = WEATHER_DESCRIPTIONS.get(w_feat, WEATHER_DESCRIPTIONS["clear"])

    stage_title = "Coastal Beach" if "beach" in s_stage else s_stage.replace('_', ' ').title()
    disp_name = f"{v_type.capitalize()} {stage_title} ({t_day.replace('_', ' ').title()})"
    lighting_env = f"{time_full} {weather_full}"
    stage_env = f"{v_type.capitalize()} {stage_full}."
    audience_env = f"Audience gathered facing the {stage_short}. Backdrop features {bg_full.lower()}"

    p1 = f"Eye-level view of lead performer on the {stage_short}, {lighting_env.lower()} Backing musicians on riser, {b_ground.replace('_', ' ')} softly visible."
    p2 = f"Eye-level shot looking toward the glowing {stage_short}, audience in foreground, {bg_full.lower()}"
    p3 = f"Grand wide panoramic view of the {v_type} {stage_short}, capturing the full stage architecture, {lighting_env.lower()} and {bg_full.lower()}"

    setting_slug = f"{v_type}_{s_stage}_{t_day}_{b_ground}_{w_feat}"
    return ConcertSettingPreset(
        setting_id=setting_slug,
        display_name=disp_name,
        venue_type=v_type,
        time_of_day=t_day,
        stage_setting=s_stage,
        background=b_ground,
        weather=w_feat,
        lighting_environment=lighting_env,
        stage_environment=stage_env,
        audience_environment=audience_env,
        plate1_desc=p1,
        plate2_desc=p2,
        plate3_desc=p3,
    )


def list_available_settings() -> list[str]:
    """Return canonical stage setting identifiers."""
    return list(STAGE_DESCRIPTIONS.keys())


__all__ = [
    "ConcertSettingPreset",
    "resolve_concert_setting",
    "list_available_settings",
    "STAGE_DESCRIPTIONS",
    "TIME_DESCRIPTIONS",
    "BACKGROUND_DESCRIPTIONS",
    "WEATHER_DESCRIPTIONS",
]
