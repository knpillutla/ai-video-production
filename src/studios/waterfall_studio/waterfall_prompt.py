"""Waterfall Studio Directorial Prompt Engineering.

Specialized exclusively in monumental cascades, cataracts, and plunge waterfalls
with wall-to-wall eye-level framing, dense spray mist, and brown noise foley.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

WATERFALL_LANDMARK_POOL = [
    "Niagara Falls, Horseshoe Falls & American Falls",
    "Victoria Falls (Mosi-oa-Tunya), Zambia & Zimbabwe",
    "Iguazu Falls (Devil's Throat), Argentina & Brazil",
    "Angel Falls (Salto Angel), Canaima Venezuela",
    "Plitvice Lakes Great Waterfall & Cascades, Croatia",
    "Gullfoss Golden Falls, Iceland",
    "Skogafoss Glacial Waterfall, Iceland",
    "Multnomah Falls, Columbia River Gorge Oregon",
    "Snoqualmie Falls, Washington Cascades",
    "Dettifoss Roaring Chasm, Iceland",
]

WATERFALL_SPECIFIC_RULES = """
======================================================================
WATERFALL DIRECTORIAL RULES & FRAMING:
======================================================================
1. EYE-LEVEL WALL-TO-WALL CASCADE FRAMING:
   - Frame the waterfall confronting the plunging water wall directly.
   - Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod.
   - The falling cataract water curtain spans wall-to-wall across 100% of the horizontal screen into a churning turquoise or emerald basin.
   - Billowing vapor mist rises steadily from the plunge basin under moody overcast skies.
   - Strictly zero humans, zero tourists, zero boats, zero railings, zero bridges, zero buildings.

2. ACOUSTIC SOUNDSCAPE & NARRATION DIRECTIVE:
   - Audio tags: "432Hz ambient soundscape, deep brown noise waterfall roar, immersive rushing water foley, velvety low-frequency resonance, binaural relaxation, -14 LUFS".
   - Spoken narration: Poetic, educational voiceover exploring the geological power, river hydrology, and timeless force of the roaring cascade.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Flanking canyon rock walls and horizon remain 100% frozen, rigid, and static.
   - Animate ONLY the plunging water curtain and rising spray mist plumes.
   - Domain: "water_fluid".
"""


def build_waterfall_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dedicated waterfall directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/nature",
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
    )
