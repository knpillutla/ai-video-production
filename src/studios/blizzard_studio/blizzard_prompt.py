"""Blizzard Studio Directorial Prompt Engineering.

Specialized in 4K alpine blizzards, cozy cabin windows, stone hearth shelters, and winter ASMR living wallpapers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

BLIZZARD_LANDMARK_POOL = [
    "Zermatt Alpine Timber Cabin & Matterhorn Blizzard, Swiss Alps",
    "Banff National Park Timber Refuge & Bow Valley Snowdrift, Canada",
    "Lappland Glass Igloo Cabin & Frosted Pine Forest, Finland",
    "Dolomite Alta Badia Stone Mountain Hearth, South Tyrol, Italy",
    "Hokkaido Niseko Birch Wood Cabin & Heavy Powder Snow, Japan",
    "Telluride High Alpine Refuge & San Juan Mountain Blizzard, Colorado, USA",
]

BLIZZARD_SPECIFIC_RULES = """
======================================================================
BLIZZARD STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. WARMTH VS. FROST CONTRAST FRAMING:
   - Frame 16:9 panoramic compositions on locked tripod contrasting warm, cozy timber interiors with howling sub-zero winter blizzards outside panoramic glass.
   - Elements: Steaming cocoa ceramic mug, frosted window edges, glowing stone hearth, thick wool blankets.
   - Purity Guard: Strictly mandate zero humans, zero tourists, zero modern vehicles, zero snowmobiles.
2. DUAL-ZONE LIGHTING:
   - Warm 2200K-2700K cozy interior amber light contrasting with cool 6500K exterior blizzard snowdrifts.
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Cabin architecture, timber beams, and mugs remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY swirling blizzard snowflakes outside glass, window frost caustics, and hearth embers.
   - Domain: "cozy_hearth".
"""


def build_blizzard_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "blizzard_cozy_cabin_window",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Blizzard studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["forest", "pines"]):
        color_temp = 6500
        cluster = "Frosted Pine Forest Snowstorm"
        default_topic = "Heavy swirling snowstorm sweeping through dense frosted pine forest, thick snowdrifts accumulating"
    elif any(w in arch_lower for w in ["hearth", "shelter", "fire"]):
        color_temp = 2200
        cluster = "Alpine Stone Hearth Refuge"
        default_topic = "Glowing stone fireplace hearth inside rustic mountain shelter, blizzard howling outside thick timber walls"
    elif any(w in arch_lower for w in ["twilight", "evening", "soft"]):
        color_temp = 4500
        cluster = "Twilight Cabin Heavy Snowfall"
        default_topic = "Peaceful heavy snowfall at deep blue twilight settling on alpine cabin roof and evergreen boughs"
    else:
        color_temp = 2700
        cluster = "Cozy Cabin Blizzard Window"
        default_topic = "Warm interior of timber cabin looking out panoramic window at raging alpine blizzard, frosted glass, steaming cocoa mug"

    return build_base_directorial_prompt(
        genre="relax/blizzard",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=BLIZZARD_SPECIFIC_RULES,
        curation_landmarks=BLIZZARD_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
