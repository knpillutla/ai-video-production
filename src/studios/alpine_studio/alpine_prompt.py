"""Alpine Nature Studio Directorial Prompt Engineering.

Specialized exclusively in panoramic mountain landscapes, Swiss Alps, Dolomites,
snow-capped peaks, wildflower meadows, and crystal-clear glacial streams.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

ALPINE_LANDMARK_POOL = [
    "Lauterbrunnen Valley & Eiger, Jungfrau Peaks, Swiss Alps",
    "Matterhorn & Zermatt Alpine Meadows, Switzerland",
    "Dolomites Val di Funes & Tre Cime di Lavaredo, Italian Alps",
    "Banff National Park & Moraine Lake, Canadian Rockies",
    "Lake Bled & Julian Alps, Slovenia",
    "Mount Fuji & Lake Kawaguchi Spring Meadows, Japan",
    "Hallstatt & Dachstein Mountain Range, Austrian Alps",
    "Yosemite Valley & Half Dome Granite Peaks, California",
    "Grand Teton Cathedral Group & Snake River Valley, Wyoming",
    "Milford Sound & Mitre Peak Alpine Fjord, New Zealand",
]

ALPINE_SPECIFIC_RULES = """
======================================================================
ALPINE NATURE DIRECTORIAL RULES & FRAMING:
======================================================================
1. WIDE PANORAMIC ALPINE LANDSCAPE FRAMING:
   - Frame majestic wide 16:9 panoramic landscape vistas shot on a locked tripod.
   - In the background: Towering snow-capped jagged alpine mountain peaks rising into a crystal-clear cloudless azure sky.
   - In the foreground/midground: Lush green rolling alpine meadows dotted with colorful wildflowers, framed by a tranquil crystal-clear glacial mountain stream gently flowing over rounded river pebbles.
   - Crisp, balanced natural daylight illumination (5500K-6000K) with pure blue sky.
   - STRICTLY PROHIBIT: Clouds, overcast skies, close-up waterfall plunge walls, dark desaturated rainy clouds, gray mist walls, buildings, tourists, vehicles, ski lifts, roads, and human structures.

2. ACOUSTIC SOUNDSCAPE & NARRATION DIRECTIVE:
   - Audio tags: "432Hz ambient soundscape, gentle mountain breeze, distant acoustic folk strings, crystal glacial stream murmur, deep relaxation, -14 LUFS".
   - Spoken narration: Poetic, educational commentary exploring the geological formation, alpine flora, glacial streams, and serene majesty of the mountain sanctuary.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Snow peaks, granite cliffs, mountain ridgelines, and meadows remain 100% frozen, rigid, and static.
   - Animate ONLY the gentle crystal stream water and subtle flower tip sway. The sky remains completely static and cloudless.
   - Domain: "landscape_solid" or "water_fluid" for stream.
"""


def build_alpine_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    channel_id: Optional[str] = None,
    tier: str = "balanced",
) -> str:
    """Build dedicated alpine nature directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/nature",
        sub_genre="alpine_mountains",
        archetype="alpine_meadow",
        cluster="Swiss Alps, Dolomites, Rockies",
        custom_prompt=custom_prompt or "Majestic Swiss Alps panoramic peaks and wildflower meadows",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=ALPINE_SPECIFIC_RULES,
        curation_landmarks=ALPINE_LANDMARK_POOL,
        color_temp_kelvin=5800,
        channel_id=channel_id or "earth_serenade",
        tier=tier,
    )
