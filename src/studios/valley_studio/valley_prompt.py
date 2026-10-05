"""Valley Studio Directorial Prompt Engineering.

Specialized in 4K pastoral valleys, wildflower meadows, and crystal glacial brooks.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

VALLEY_LANDMARK_POOL = [
    "Lauterbrunnen Valley of 72 Waterfalls, Bernese Oberland, Switzerland",
    "Val di Funes Wildflower Pasture & Geisler Peaks, Dolomites, Italy",
    "Yosemite Valley Meadow & El Capitan Reflection, California, USA",
    "Jiuzhaigou Valley Turquoise Lakes & Cascades, Sichuan, China",
    "Glencoe Emerald Valley & River Coe, Scottish Highlands",
    "Cradle Mountain Dove Lake Valley, Tasmania, Australia",
]

VALLEY_SPECIFIC_RULES = """
======================================================================
VALLEY STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. PASTORAL VALLEY PANORAMIC FRAMING:
   - Frame 16:9 panoramic compositions on locked tripod capturing lush blooming wildflower valleys, meandering glacial brooks, and rustic wooden timber barns.
   - Purity Guard: Strictly mandate zero humans, zero tourists, zero asphalt roads, zero modern clutter.
2. NATURAL DAYLIGHT LIGHTING:
   - Default to balanced 5400K-5600K crisp pastoral daylight.
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Valley floor, timber barns, and mountain backdrops remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY gentle wildflower sway, crystal glacial brook current, or delicate morning mist ribbons.
   - Domain: "landscape_solid".
"""


def build_valley_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "valley_wildflower_meadow",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Valley studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["mist", "dawn", "morning"]):
        color_temp = 4200
        cluster = "Misty Valley Morning Sunrise"
        default_topic = "Pastoral green valley awakening at dawn with soft ribbons of morning mist drifting across emerald hills"
    elif any(w in arch_lower for w in ["sunset", "pastoral_sunset"]):
        color_temp = 3000
        cluster = "Pastoral Valley Sunset"
        default_topic = "Golden hour sunset sweeping across pastoral alpine valley, rustic wooden hay barn, long warm shadows"
    elif any(w in arch_lower for w in ["stream", "brook", "glacial"]):
        color_temp = 5500
        cluster = "Glacial Valley Stream"
        default_topic = "Crystal turquoise glacial stream babbling through peaceful valley pasture with snow-capped peaks in distance"
    else:
        color_temp = 5400
        cluster = "Wildflower Meadow Sanctuary"
        default_topic = "Lush Swiss alpine valley meadow blooming with purple lupines and buttercups, crystal stream meandering through"

    return build_base_directorial_prompt(
        genre="relax/valley",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=VALLEY_SPECIFIC_RULES,
        curation_landmarks=VALLEY_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
