"""Rain Retreat & Rain on Window ASMR Directorial Prompt Engineering.

Specialized in both cozy rainy glass cabin bedrooms (rain streaming on window glass)
and tranquil temperate forest rain sanctuaries with 3D binaural sleep soundscapes.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

RAIN_BEDROOM_LANDMARK_POOL = [
    "Cozy Pacific Northwest Glass Cabin Bedroom & Misty Fir Forest Rain, Washington",
    "Nordic Timber Pine Cabin Bedroom & Rain Streaming on Panoramic Window, Norway",
    "Kyoto Cedar Forest Glass Retreat Bedroom & Rain on Windowpane, Japan",
    "Swiss Alpine Glass Chalet Bedroom & Mountain Rain, Zermatt",
    "Blue Ridge Mountain Timber Cabin Bedroom & Windowpane Rainfall, North Carolina",
    "Vancouver Island Oceanfront Glass Cabin Bedroom & Temperate Rain, British Columbia",
    "Scottish Highlands Stone & Glass Bothy Bedroom & Heavy Rain, Scotland",
    "Black Forest Timber Glass Bedroom & Fir Canopy Rain, Germany",
]

RAIN_FOREST_LANDMARK_POOL = [
    "Hoh Rainforest & Mossy Olympic River Rain Sanctuary, Washington",
    "Great Smoky Mountains Misty Stream & Fern Creek, Tennessee",
    "Black Forest Glacial Stream & Pine Canopy Rain, Germany",
    "Yakushima Ancient Cedar & Emerald Moss Rain Basin, Japan",
    "Redwood National Park Misty Fern Canyon & River Rain, California",
    "Fiordland Temperate Rainforest Stream & Cascades, New Zealand",
]

RAIN_VILLAGE_HUT_LANDMARK_POOL = [
    "Bali Ubud Lush Rice Terrace Bamboo Pavilion & Tropical Eaves Rain, Indonesia",
    "Kerala Backwaters Teak & Thatched Hut Veranda & Monsoon Rain, India",
    "Chiang Mai Tropical Bamboo River Sanctuary & Torrential Rain, Thailand",
    "Costa Rica Osa Peninsula Rainforest Thatched Veranda & Warm Rain, Costa Rica",
    "Vietnam Mu Cang Chai Rustic Bamboo Hut Veranda & Cascading Rain, Vietnam",
]

RAIN_LANDMARK_POOL = RAIN_BEDROOM_LANDMARK_POOL + RAIN_FOREST_LANDMARK_POOL + RAIN_VILLAGE_HUT_LANDMARK_POOL

RAIN_SPECIFIC_RULES = """
======================================================================
RAIN RETREAT & RAIN ON WINDOW DIRECTORIAL RULES:
======================================================================
1. COZY BEDROOM, TROPICAL BAMBOO HUT VERANDA OR PRISTINE FOREST RAIN FRAMING:
   - For Tropical Bamboo Hut & Village Veranda Scenes:
     * Frame symmetrical 16:9 eye-level locked shot of a rustic bamboo pavilion veranda with thatched roof eaves pouring sheets and streams of rainwater into surrounding lush green foliage.
     * Warm hanging amber lantern (2700K) illuminating woven bamboo walls, sheltered wooden deck with a cozy outdoor sleeping mattress or daybed with soft linen bedding.
     * Foreground: raindrops splashing into reflective puddles and wet garden vegetation with concentric ripples.
     * Cinemagraph kinetics: Animate the vertical roof runoff cascading sheets, dripping droplets, and splashing puddle ripples; the hut structure, wooden deck, bed, and lantern remain 100% frozen and static.
   - For Glass Cabin / Bedroom Scenes (Cabin TrackSound Archetype):
     * Frame symmetrical 16:9 eye-level locked tripod shot from inside a warm cozy bedroom looking through large floor-to-ceiling glass panoramic windows with streaming rivulets.
     * Plush unmade king-sized bed with thick textured warm linen duvet, fluffy pillows, dark natural cedar timber walls, and a warm glowing bedside night lamp (2700K).
     * Strictly zero humans, zero tourists, zero clutter, zero artificial neon, zero modern electronics.
   - For Outdoor Forest Rain:
     * Wide locked tripod vista of a crystal river, mossy boulders, and steady rain creating concentric surface ripples.

2. ACOUSTIC SOUNDSCAPE & VELVET ASMR DIRECTIVE:
   - Suno tags: "432Hz binaural rain ASMR, steady raindrops streaming on glass window or thatched eaves, soft roof rainfall pitter-patter, deep sleep soundscape, -14 LUFS, zero vocals, zero drums".
   - Spoken narration: Poetic, calming contemplation on the soothing rhythm of rain, shelter from the storm, and peaceful nighttime solitude.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Interior bedroom / hut walls, furniture, bed, and window frames remain 100% frozen, rigid, and static.
   - Animate ONLY the vertical raindrops and trickling water rivulets gliding down the glass windowpane or falling from thatched roof eaves, with subtle drifting mist outside.
   - Domain: "water_fluid".
"""


def build_rain_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "rainy_bedroom",
    primary_archetype: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated rain retreat directorial prompt conforming to global RelaxScreenplay schema."""
    sub_l = (sub_genre or "").lower()
    arch_l = (primary_archetype or "").lower()
    is_village = any(k in sub_l or k in arch_l for k in ["village", "bamboo", "thatched", "hut", "veranda"])
    is_bedroom = ("bedroom" in sub_l or "cabin" in sub_l or "bedroom" in arch_l) and not is_village
    eff_archetype = primary_archetype or ("bamboo_hut_veranda" if is_village else ("rainy_cabin_bedroom" if is_bedroom else "rain_forest"))
    landmarks = RAIN_VILLAGE_HUT_LANDMARK_POOL if is_village else (RAIN_BEDROOM_LANDMARK_POOL if is_bedroom else RAIN_FOREST_LANDMARK_POOL)

    if is_village:
        default_prompt = "Sheltered rustic bamboo pavilion veranda in a peaceful tropical village during heavy torrential rainfall, thatched roof eaves with water cascading in continuous glassy sheets, warm glowing amber lantern (2700K), cozy outdoor wooden deck with plush mattress and linen duvet, wet palm fronds, raindrops splashing into reflective puddles with ripples"
    elif is_bedroom:
        default_prompt = "Cozy luxury glass cabin bedroom in a misty fir forest during heavy rainfall with rain streaming on floor-to-ceiling panoramic window, warm 2700K bedside lamp, and plush unmade king bed"
    else:
        default_prompt = "Pristine temperate rainforest stream cascading over mossy boulders during gentle continuous rainfall"

    return build_base_directorial_prompt(
        genre="relax/rain",
        sub_genre=sub_genre or ("tropical_village_rain" if is_village else ("rainy_bedroom" if is_bedroom else "forest_rain")),
        archetype=eff_archetype,
        cluster="Tropical Village Sanctuaries & Bamboo Rain Retreats" if is_village else "Global Temperate Rainforests & Cozy Glass Cabins",
        custom_prompt=custom_prompt or default_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=RAIN_SPECIFIC_RULES,
        curation_landmarks=landmarks,
        color_temp_kelvin=2700 if (is_bedroom or is_village) else 5400,
        channel_id=channel_id or "silent_hearth",
    )


