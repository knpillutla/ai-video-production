"""Forest Studio Directorial Prompt Engineering.

Specialized in 4K ancient forests, komorebi sunbeams, mossy boulder glades, and tranquil woodland living wallpapers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

FOREST_LANDMARK_POOL = [
    "Hoh Rain Forest Mossy Glade & Hall of Mosses, Olympic National Park, USA",
    "Yakushima Ancient Cedar Canopy & Shiratani Ravine, Kagoshima, Japan",
    "Redwood National Park Cathedral Grove & Morning Sunbeams, California, USA",
    "Black Forest Mossy Brook & Pine Glade, Baden-Württemberg, Germany",
    "Tarkine Ancient Myrtle Beech Rainforest & Glacial River, Tasmania, Australia",
    "Jiuzhaigou Emerald Forest Stream & Primordial Pines, Sichuan, China",
]

FOREST_SPECIFIC_RULES = """
======================================================================
FOREST STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. CATHEDRAL FOREST PANORAMIC FRAMING:
   - Frame 16:9 panoramic compositions on locked tripod capturing towering ancient tree trunks, lush moss carpets, crystal forest brooks, and dappled sunbeams.
   - Purity Guard: Strictly mandate zero humans, zero tourists, zero hikers, zero asphalt roads, zero modern clutter.
2. NATURAL BALANCED LIGHTING:
   - Default to crisp 5400K natural daylight with morning mist sunbeams (komorebi lighting).
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Ancient tree trunks, boulders, and forest floor remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY crystal water currents, subtle fern sway, and drifting morning mist.
   - Domain: "landscape_solid".
"""


def build_forest_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "forest_mossy_canopy_day",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Forest studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["brook", "stream"]):
        color_temp = 5200
        cluster = "Babbling Forest Brook Sanctuary"
        default_topic = "Tranquil forest brook cascading over small mossy rock ledges, lush emerald ferns, serene nature ASMR"
    elif any(w in arch_lower for w in ["sunbeam", "komorebi", "morning"]):
        color_temp = 4500
        cluster = "Redwood Cathedral Morning Sunbeams"
        default_topic = "Golden morning sunbeams piercing through misty redwood canopy (komorebi effect), dew glistening on forest floor"
    elif any(w in arch_lower for w in ["twilight", "fireflies", "night"]):
        color_temp = 2500
        cluster = "Enchanted Twilight Fireflies Glade"
        default_topic = "Enchanted forest glade at twilight, gentle bioluminescent fireflies dancing among ferns and ancient tree trunks"
    else:
        color_temp = 5400
        cluster = "Emerald Mossy Canopy Daytime"
        default_topic = "Ancient temperate rainforest with moss-draped cedar canopy, crystal forest river flowing over smooth stones"

    return build_base_directorial_prompt(
        genre="relax/forest",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=FOREST_SPECIFIC_RULES,
        curation_landmarks=FOREST_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
