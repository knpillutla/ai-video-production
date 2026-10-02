"""Rain Retreat & River ASMR Directorial Prompt Engineering.

Specialized exclusively in tranquil forest rainfall, river droplet ripples,
misty rainforest streams, and soothing nature ASMR soundscapes.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

RAIN_LANDMARK_POOL = [
    "Hoh Rainforest & Mossy Olympic River, Washington",
    "Yakushima Ancient Cedar Forest & Misty Stream, Japan",
    "Jiuzhaigou Emerald Valley & Crystal Stream Rain, Sichuan",
    "Black Forest Glacial Stream & Pine Canopy, Germany",
    "Milford Sound Misty Rainforest Cascade, New Zealand",
    "Plitvice Lakes Forest Rain & Calming Lakes, Croatia",
    "Great Smoky Mountains Misty Stream & Fern Creek, Tennessee",
    "Daintree Ancient Mossy Rainforest & Calming Creek, Australia",
]

RAIN_SPECIFIC_RULES = """
======================================================================
RAIN RETREAT DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. TRANQUIL FOREST RAIN & WATER RIPPLE COMPOSITION:
   - Frame wide 16:9 cinematic landscape vistas shot on a locked tripod.
   - Symmetrical, tranquil perspective of a crystal-clear forest river winding through ancient moss-covered boulders and dense cedar pines.
   - Steady, gentle rainfall continuously falling with expanding circular water ripples on the translucent water surface.
   - Diffused, cool natural daylight (5400K-5600K) filtering through soft atmospheric mist and glistening wet foliage.
   - Strictly zero humans, zero tourists, zero buildings, zero umbrellas, zero vehicles, zero artificial lighting.

2. ACOUSTIC SOUNDSCAPE & VELVET ASMR DIRECTIVE:
   - Suno tags: "432Hz ambient soundscape, gentle steady rain on forest leaves, soothing river water murmur, soft binaural ASMR, deep relaxation, -14 LUFS".
   - Spoken narration: Poetic, calming contemplation on the restorative rhythm of rainfall, misty river ecosystems, and the quiet vitality of the forest.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Forest trees, mossy riverbanks, and granite stones remain 100% frozen, rigid, and static.
   - Animate ONLY the gentle falling raindrops, expanding water surface ripples, and smoothly flowing river current.
   - Domain: "water_fluid".
"""


def build_rain_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "forest_rain",
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated rain retreat directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/rain",
        sub_genre=sub_genre or "forest_rain",
        archetype="rain_forest",
        cluster="Global Temperate Rainforests",
        custom_prompt=custom_prompt or "Lush forest river during gentle steady rain with expanding water ripples",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=RAIN_SPECIFIC_RULES,
        curation_landmarks=RAIN_LANDMARK_POOL,
        color_temp_kelvin=5500,
        channel_id=channel_id or "silent_hearth",
    )
