"""Silent Hearth & Campfire Studio Directorial Prompt Engineering.

Specialized exclusively in 100% open-air outdoor beach campfires, ocean shore stone hearths,
glowing wood embers, rhythmic rolling ocean surf, and deep sleep ASMR.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

HEARTH_LANDMARK_POOL = [
    "Big Sur Secluded Pebble Beach Cove, California",
    "Cannon Beach Ocean Shoreline & Sea Stacks, Oregon",
    "Rialto Beach Driftwood Coastline, Washington",
    "Amalfi Coastline Secluded Pebble Cove, Italy",
    "Black Sand Beach & Basalt Shoreline, Vik Iceland",
    "Kailua Ocean Shoreline Twilight Breeze, Hawaii",
    "Cape Kiwanda Pacific Sand Dunes & Ocean Waves, Oregon",
]

HEARTH_SPECIFIC_RULES = """
======================================================================
SILENT HEARTH & BEACH CAMPFIRE DIRECTORIAL RULES:
======================================================================
1. 100% OPEN-AIR OUTDOOR BEACH SHORELINE FRAMING:
   - Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod at eye level.
   - In the foreground: A cozy natural stone campfire / rock fire ring burning with rich glowing wood logs and crackling amber embers sitting directly on the wet sand / smooth pebble shore.
   - In the immediate background: Gentle rhythmic ocean waves roll and surge along the coastline under a dark indigo twilight or night sky with soft coastal mist.
   - STRICT NEGATIVE DIRECTIVE: Strictly prohibit indoor rooms, living rooms, interior walls, ceilings, indoor sofas, couches, cushions, rugs, indoor tables, and glass window frames.

2. ACOUSTIC SOUNDSCAPE & NARRATION DIRECTIVE:
   - Audio tags: "432Hz ambient soundscape, deep crackling oak campfire foley, gentle rhythmic ocean surf, soft acoustic drone, velvety low-frequency resonance, binaural relaxation, -14 LUFS".
   - Spoken narration: Poetic, soothing reflection on the nocturnal rhythm of coastal waves, primal warmth of firelight, and tranquil cosmic solitude.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Sand, pebble shore, coastal rock stacks, and horizon remain 100% frozen, rigid, and static.
   - Animate ONLY the crackling campfire flames, glowing embers, and rolling ocean surf.
   - Domain: "cozy_hearth".
"""


def build_hearth_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dedicated silent hearth & beach campfire directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/nature",
        sub_genre="beach_campfire",
        archetype="campfire",
        cluster="Global Pacific & Atlantic Coastlines",
        custom_prompt=custom_prompt or "Open-air beach campfire with glowing wood embers and rolling ocean waves",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=HEARTH_SPECIFIC_RULES,
        curation_landmarks=HEARTH_LANDMARK_POOL,
        color_temp_kelvin=3200,
    )
