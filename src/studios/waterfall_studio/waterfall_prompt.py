"""Waterfall Studio Directorial Prompt Engineering.

Specialized exclusively in monumental cascades, cataracts, and plunge waterfalls
with wall-to-wall eye-level framing, dense spray mist, and brown noise foley.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

WATERFALL_LANDMARK_POOL = [
    "Staubbach Falls & Lauterbrunnen Valley Vertical Cliffs, Swiss Alps",
    "Giessbach Falls & Lake Brienz Turquoise Waters, Switzerland",
    "Plitvice Lakes Great Waterfall & Emerald Cascades, Croatia",
    "Skogafoss Glacial Waterfall & Green Cliffs, Iceland",
    "Multnomah Falls & Mossy Basalt Gorge, Oregon",
    "Niagara Falls Horseshoe Cataract & Turquoise Basin",
    "Victoria Falls (Mosi-oa-Tunya) Zambezi Gorge, Zimbabwe",
    "Iguazu Falls Devil's Throat, Argentina & Brazil",
    "Angel Falls (Salto Angel) Auyan-Tepui, Venezuela",
    "Gullfoss Golden Glacial Falls, Iceland",
]

WATERFALL_SPECIFIC_RULES = """
======================================================================
WATERFALL DIRECTORIAL RULES & FRAMING:
======================================================================
1. MONUMENTAL CASCADE & ALPINE CLIFFSIDE FRAMING:
   - Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod.
   - For Monumental Plunge / Cataracts: The falling cataract water curtain spans wall-to-wall into a churning turquoise or emerald basin with rising spray mist plumes.
   - For Alpine Cliffside Waterfalls (e.g. Lauterbrunnen / Staubbach Falls): Towering 300-meter vertical limestone cliff walls with a graceful cascading water veil plunging into a lush emerald green alpine meadow and crystal-clear glacial stream, with distant snow-capped peaks under crisp natural 5400K daylight.
   - Strictly zero humans, zero tourists, zero boats, zero railings, zero bridges, zero modern structures.

2. ACOUSTIC SOUNDSCAPE & NARRATION DIRECTIVE:
   - Audio tags: "432Hz ambient soundscape, peaceful cascading water foley, Celtic harp and acoustic cello, gentle alpine stream murmur, deep relaxation, -14 LUFS".
   - Spoken narration: Poetic, educational commentary exploring the geological hydrology, ancient glacial valleys, and tranquil majesty of the cascading waters.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Flanking canyon rock walls, mountains, and alpine meadows remain 100% frozen, rigid, and static.
   - Animate ONLY the plunging cascading water curtain and gentle rising spray mist plumes.
   - Domain: "water_fluid".
"""


def build_waterfall_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated waterfall directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/waterfall",
        sub_genre="monumental_waterfall",
        archetype="waterfall",
        cluster="Global Monumental Waterfalls",
        custom_prompt=custom_prompt or "Monumental wall-to-wall cascading waterfall with rising mist",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=WATERFALL_SPECIFIC_RULES,
        curation_landmarks=WATERFALL_LANDMARK_POOL,
        color_temp_kelvin=5400,
        channel_id=channel_id or "earth_serenade",
    )
