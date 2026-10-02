"""Cozy Ambiance & Fireplace Directorial Prompt Engineering.

Specialized exclusively in biophilic timber living spaces, mountain chalet verandas,
rainy window reading corners, and crackling stone hearth fireplaces.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

COZY_LANDMARK_POOL = [
    "Zermatt Swiss Chalet Timber Terrace & Matterhorn View, Switzerland",
    "Aspen Biophilic Pine Log Cabin Veranda, Colorado Rockies",
    "Kyoto Cedar Engawa Garden Nook & Stone Lantern, Japan",
    "Cotswolds Stone Hearth Fireplace & Rain on Window, England",
    "Banff Mountain Lodge Covered Timber Terrace, Canadian Rockies",
    "Lake Como Rustic Stone Villa Loggia & Rain Mist, Italy",
    "Nordic Pine Forest Cabin & Crackling Hearth, Norway",
]

COZY_SPECIFIC_RULES = """
======================================================================
COZY AMBIANCE DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. BIOPHILIC TIMBER LIVING SPACE & HEARTH COMPOSITION:
   - Frame tranquil wide 16:9 cinematic landscape perspectives shot on a locked tripod.
   - Rich natural textures: Weathered cedar/pine timber logs, natural stacked fieldstone or brick fireplace, crackling golden amber wood fire, and cozy architectural details.
   - Symmetrical architectural depth looking from an open covered terrace or warm timber room toward a pristine misty nature vista through large clear glass windows with rain droplets.
   - Warm, inviting 3200K interior hearth glow balanced against soft cool 5400K natural daylight outside.
   - Strictly zero humans, zero tourists, zero clutter, zero artificial glare, zero modern electronics.

2. ACOUSTIC SOUNDSCAPE & VELVET ASMR DIRECTIVE:
   - Suno tags: "432Hz ambient soundscape, crackling oak fireplace embers, gentle rain on glass windowpane, soft acoustic cello drone, deep sleep ASMR, -14 LUFS".
   - Spoken narration: Poetic, warm reflection on shelter, peace, the primal comfort of firelight, and tranquil sanctuary from the storm.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Timber walls, stone mantel, furniture, and window frames remain 100% frozen, rigid, and static.
   - Animate ONLY the dancing fireplace flames, glowing embers, and gentle rain trickling down the glass windowpane.
   - Domain: "cozy_hearth".
"""


def build_cozy_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "cozy_shelter",
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated cozy ambiance directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/cozy",
        sub_genre=sub_genre or "cozy_shelter",
        archetype="cozy_hearth",
        cluster="Global Mountain Lodges & Biophilic Cabins",
        custom_prompt=custom_prompt or "Cozy biophilic timber chalet with crackling stone fireplace and rain on window",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=COZY_SPECIFIC_RULES,
        curation_landmarks=COZY_LANDMARK_POOL,
        color_temp_kelvin=3200,
        channel_id=channel_id or "silent_hearth",
    )
