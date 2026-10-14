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

SWISS_ALPS_RAIN_LANDMARK_POOL = [
    "Lauterbrunnen Valley Traditional Timber Chalet Veranda & Glacial Waterfall Rain, Canton of Bern",
    "Grindelwald Alpine Meadow Chalet & Torrential Rain over Wet Slate Roofs, Bernese Oberland",
    "Zermatt Mountain Chalet Veranda & Summer Rainstorm over Emerald Pastures, Valais",
    "Wengen Hillside Timber Chalet & Glacial River Rain Sanctuary, Bernese Alps",
    "Mürren Cliffside Balcony & Heavy Summer Downpour over Emerald Valley, Switzerland",
]

RAIN_VILLAGE_HUT_LANDMARK_POOL = [
    "Bali Ubud Lush Rice Terrace Bamboo Pavilion & Tropical Eaves Rain, Indonesia",
    "Kerala Backwaters Teak & Thatched Hut Veranda & Monsoon Rain, India",
    "Chiang Mai Tropical Bamboo River Sanctuary & Torrential Rain, Thailand",
    "Costa Rica Osa Peninsula Rainforest Thatched Veranda & Warm Rain, Costa Rica",
    "Vietnam Mu Cang Chai Rustic Bamboo Hut Veranda & Cascading Rain, Vietnam",
]

RAIN_LANDMARK_POOL = SWISS_ALPS_RAIN_LANDMARK_POOL + RAIN_BEDROOM_LANDMARK_POOL + RAIN_FOREST_LANDMARK_POOL + RAIN_VILLAGE_HUT_LANDMARK_POOL

RAIN_SPECIFIC_RULES = """
======================================================================
RAIN RETREAT & RAIN ON WINDOW DIRECTORIAL RULES:
======================================================================
1. SWISS ALPS CHALET, BEDROOM, BAMBOO HUT OR FOREST RAIN FRAMING:
   - For Swiss Alps Chalet Veranda Scenes:
     * Frame symmetrical 16:9 locked tripod vista from the sheltered wooden balcony/veranda of a hillside chalet overlooking an emerald alpine village.
     * Foreground: Hand-hewn dark timber roof eaves pouring rainwater onto wet railings and scarlet red geraniums in balcony planter boxes.
     * Midground & Background: Traditional timber chalets, lush pastures, surging turquoise glacial river, and sheer granite cliffs in rain mist.
     * For Heavy Rain: Dark storm clouds (5000K-5200K), thick vertical sheets of rain, explosive splashing droplets, and churning river rapids. Zero direct sun.
     * For Gentle Rain: Soft cool overcast (5400K), delicate falling droplets, gentle roof drips, and peaceful mirror ripples.
   - For Tropical Bamboo Hut & Village Veranda Scenes:
     * Frame symmetrical 16:9 eye-level locked shot of a rustic bamboo pavilion with thatched eaves pouring water into lush foliage, warm 2700K amber lantern.
   - For Glass Cabin / Bedroom Scenes:
     * Frame symmetrical 16:9 locked tripod shot from inside a cozy bedroom looking through floor-to-ceiling glass with streaming rivulets, warm 2700K lamp, unmade linen bed.
   - For Outdoor Forest Rain:
     * Wide locked tripod vista of a crystal river, mossy boulders, and continuous rain creating concentric surface ripples.

2. ACOUSTIC SOUNDSCAPE & VELVET ASMR DIRECTIVE:
   - For Heavy Rain: "432Hz binaural rain ASMR, heavy torrential rain pouring on roof eaves, splashing water runoff, roaring turquoise glacial river, distant low thunder rumble, -14 LUFS".
   - For Gentle Rain: "432Hz binaural rain ASMR, soft gentle rain on leaves or glass, delicate roof pitter-patter, deep sleep soundscape, -14 LUFS, zero drums".

3. MODEL-SPECIFIC MOTION DIFFUSION PROMPTS ("model_configs"):
   - KLING DIRECTIVE FOR HEAVY RAIN ("kling_v3_4k" and "kling_v1_6_pro"):
     * Kling diffusion models require intense optical density cues to simulate volumetric water and break the keyframe static hold.
     * For Heavy Rain / Storms / Chalet Downpours, "kling_v3_4k" and "kling_v1_6_pro" positive_prompt MUST use vivid kinetic rain descriptors:
       "Cinematic masterpiece shot from a Swiss chalet balcony. A blinding torrential rainstorm, thick solid white sheets of heavy downpour obscuring the view, intense splashing water exploding off timber eaves. Wet, glistening wooden railings dripping with water. Heavy fog and a dense wall of rain completely blurring the distant mountains. High-contrast dramatic mood, photorealistic 8k."
     * STRICT BAN FOR KLING: NEVER use passive phrases like "living wallpaper", "cinemagraph", "steady gentle rain", or "perfectly static structure" inside Kling's positive prompt. Kling interprets these phrases as an instruction to freeze all motion.
   - WAN 2.1 DIRECTIVE ("wan_2_1"):
     * Continuous laminar fluid dynamics: "Heavy vertical sheets of rainfall, continuous cascading water from roof eaves with bouncing splashing droplets, drifting valley mist, locked stationary tripod."
   - DOMAIN: "water_fluid".
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
    p_l = (custom_prompt or "").lower()

    is_swiss = any(k in sub_l or k in arch_l or k in p_l for k in ["swiss", "alps", "chalet", "alpine"])
    is_village = any(k in sub_l or k in arch_l for k in ["village", "bamboo", "thatched", "hut"]) and not is_swiss
    is_bedroom = ("bedroom" in sub_l or "cabin" in sub_l or "bedroom" in arch_l) and not is_swiss and not is_village
    is_heavy = any(k in sub_l or k in arch_l or k in p_l for k in ["heavy", "torrent", "downpour", "storm"])

    if is_swiss:
        eff_archetype = primary_archetype or ("heavy_rain_swiss_alps" if is_heavy else "gentle_rain_swiss_alps")
        landmarks = SWISS_ALPS_RAIN_LANDMARK_POOL
        cluster = "Swiss Alps Glacial Valleys & Timber Chalet Rain Sanctuaries"
        default_prompt = (
            "Sheltered wooden chalet veranda overlooking an emerald green Swiss alpine village during an awesome heavy torrential summer downpour under dramatic dark overcast storm clouds, continuous thick vertical rain sheets cascading off aged timber eaves onto red geraniums, roaring turquoise glacial river below"
            if is_heavy else
            "Sheltered wooden chalet veranda overlooking an emerald green Swiss alpine village during gentle steady rain, soft cool overcast sky, delicate falling raindrops glistening on wet timber railings and red geraniums, misty emerald valley"
        )
        c_temp = 5200 if is_heavy else 5400
    elif is_village:
        eff_archetype = primary_archetype or "tropical_village_rain"
        landmarks = RAIN_VILLAGE_HUT_LANDMARK_POOL
        cluster = "Tropical Village Sanctuaries & Bamboo Rain Retreats"
        default_prompt = "Sheltered rustic bamboo pavilion veranda in a peaceful tropical village during heavy torrential rainfall, thatched roof eaves with water cascading in continuous glassy sheets, warm glowing amber lantern (2700K), raindrops splashing into reflective puddles"
        c_temp = 2700
    elif is_bedroom:
        eff_archetype = primary_archetype or ("heavy_rain_glass_cabin" if is_heavy else "rainy_bedroom")
        landmarks = RAIN_BEDROOM_LANDMARK_POOL
        cluster = "Global Temperate Rainforests & Cozy Glass Cabins"
        default_prompt = "Cozy luxury glass cabin bedroom in a misty fir forest during rainfall with rain streaming on floor-to-ceiling panoramic window, warm 2700K bedside lamp, and plush unmade king bed"
        c_temp = 2700
    else:
        eff_archetype = primary_archetype or ("heavy_rain_forest_river" if is_heavy else "forest_rain")
        landmarks = RAIN_FOREST_LANDMARK_POOL
        cluster = "Global Temperate Rainforests & Pure River Sanctuaries"
        default_prompt = "Pristine temperate rainforest stream cascading over mossy boulders during continuous rainfall"
        c_temp = 5200 if is_heavy else 5400

    return build_base_directorial_prompt(
        genre="relax/rain",
        sub_genre=sub_genre or eff_archetype,
        archetype=eff_archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=RAIN_SPECIFIC_RULES,
        curation_landmarks=landmarks,
        color_temp_kelvin=c_temp,
        channel_id=channel_id or "silent_hearth",
    )


