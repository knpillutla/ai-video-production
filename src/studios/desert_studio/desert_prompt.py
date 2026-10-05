"""Desert Studio Directorial Prompt Engineering.

Specialized exclusively in 4K luxury desert glamping sanctuaries across all 6 diurnal timings:
daytime, sunrise, sunset, starlit night, campfire hearth, and rain on canvas.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

DESERT_LANDMARK_POOL = [
    "Erg Chebbi Grand Dunes Sanctuary, Merzouga, Sahara Desert, Morocco",
    "Rub' al Khali (The Empty Quarter) Luxury Pavilion, Liwa Oasis, UAE",
    "Sossusvlei Symmetrical Dune 45 Ridge, Namib Desert, Namibia",
    "Wadi Rum Valley of the Moon Glamping Retreat, Jordan",
    "White Desert Chalk Sculptures & Starlit Oasis, Farafra, Egypt",
    "Al-Ula Ancient Desert Canyon & Sandstone Sanctuary, Saudi Arabia",
    "Atacama Desert Moon Valley Dune Overlook, San Pedro de Atacama, Chile",
    "Great Sand Dunes National Park & Sangre de Cristo Vista, Colorado, USA",
]

DESERT_SPECIFIC_RULES = """
======================================================================
DESERT STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY (ALL 6 DIURNAL TIMINGS):
======================================================================
1. INSIDE-OUT LUXURY TENT FRAMING & ZERO PURITY MANDATE:
   - Frame 16:9 panoramic compositions on a locked stationary tripod looking from inside an opulent desert glamping tent/pavilion onto boundless dunes.
   - Interior luxury: Hand-carved low teak table, ornate Moroccan engraved brass tea service, rich hand-woven Berber kilim rugs, plush geometric floor cushions.
   - Drapery framing: Sheer cream linen curtains gently billowing at the frame edges.
   - Purity Guard: Strictly mandate zero humans, zero tourists, zero vehicles, zero modern clutter, zero trash, zero footprints.

2. DIURNAL LIGHTING & COLOR TEMPERATURE MATRIX (STRICT ADHERENCE):
   - DAYTIME (desert_daytime_tent): Natural balanced 5500K daylight, clear cerulean blue sky, golden ripples, zero night, zero fire.
   - SUNRISE (desert_sunrise_tent): Soft 3800K pastel peach & amber dawn radiance, first sun rays cresting dune ridges, delicate steam from mint tea glass.
   - SUNSET (desert_sunset_tent): Fiery 2800K terracotta & burnt crimson golden hour, dramatic elongated purple shadows, warm lantern hum.
   - STARLIT NIGHT (desert_night_tent): Deep 2000K velvet indigo sky, glittering Milky Way galaxy, single dim brass candle lantern, STRICTLY ZERO FIRE / CAMPFIRE.
   - CAMPFIRE HEARTH (desert_campfire_hearth): 2200K pulsing golden campfire embers in circular stone hearth, pierced brass lanterns, starlit night.
   - RAIN SANCTUARY (desert_rain_sanctuary): 4800K diffused silver-slate overcast, gentle rain on canvas ASMR, damp sand ripples, cozy dry tent shelter.

3. SENSORY ACOUSTIC SOUNDBATH (432Hz VELVET MASTERING - ZERO GUITAR):
   - Suno tags: "432Hz meditative soundbath, joyful uplifting handpan in major pentatonic mode, Tibetan singing bowls, airy wooden nay flute, warm velvet ambient pads, gentle desert breeze through linen, zero solo guitar, -21 LUFS sleep master".
   - Spoken narration: Optional one-sentence poetic lore celebrating the timeless stillness, vast desert horizons, and restorative peaceful silence.

4. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Sand dunes, furniture, brass teapot, and horizon line remain 100% frozen, rigid, and temporally stable.
   - Animate ONLY subtle sheer linen curtain flutter, delicate tea steam wisps, fine sand skimming distant crests, or gentle rain/embers.
   - Domain: "landscape_solid".
"""


def build_desert_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "desert_daytime_tent",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Desert studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["sunrise", "dawn"]):
        color_temp = 3800
        cluster = "Sahara Sunrise Sanctuary"
        default_topic = "Luxury desert glamping tent sunrise dawn looking out at soft golden dune ridges with steaming mint tea"
    elif any(w in arch_lower for w in ["sunset", "golden_hour"]):
        color_temp = 2800
        cluster = "Namib Sunset Dunes"
        default_topic = "Luxury desert tent golden hour sunset overlooking fiery terracotta sand dunes with warm brass lantern"
    elif any(w in arch_lower for w in ["night_tent", "starlight", "milky_way"]):
        color_temp = 2000
        cluster = "Arabian Starlit Night"
        default_topic = "Luxury desert glamping tent at night looking out at glittering Milky Way galaxy, candle lantern, zero fire"
    elif any(w in arch_lower for w in ["campfire", "hearth", "pavilion"]):
        color_temp = 2200
        cluster = "Erg Chebbi Bedouin Hearth"
        default_topic = "Open-air Bedouin desert pavilion with glowing circular stone hearth campfire under starry midnight sky"
    elif any(w in arch_lower for w in ["rain", "storm"]):
        color_temp = 4800
        cluster = "Wadi Rum Rain Retreat"
        default_topic = "Cozy luxury desert tent shelter during gentle rare desert rain with pitter-patter on canvas roof"
    else:  # Daytime default
        color_temp = 5500
        cluster = "Rub' al Khali Daytime Dunes"
        default_topic = "Luxury desert glamping tent daytime view looking outward onto vast golden sand dunes in natural 5500K sunlight"

    return build_base_directorial_prompt(
        genre="relax/desert",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=DESERT_SPECIFIC_RULES,
        curation_landmarks=DESERT_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
