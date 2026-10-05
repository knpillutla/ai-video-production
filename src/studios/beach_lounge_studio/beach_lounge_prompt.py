"""Beach Lounge Studio Directorial Prompt Engineering.

Specialized in 4K luxury beach lounges, ocean cabanas, sunset pergolas, and shoreline living wallpapers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

BEACH_LOUNGE_LANDMARK_POOL = [
    "Anse Source d'Argent Beach Cabana, La Digue, Seychelles",
    "Bora Bora Overwater Teak Terrace & Mt Otemanu, French Polynesia",
    "Grace Bay Luxury Beachfront Pergola, Turks and Caicos",
    "Amalfi Coast Cliffside Lemon Pergola, Positano, Italy",
    "Tulum Private Beachfront Daybed & Turquoise Surf, Mexico",
    "Whitehaven Beach Whispering Palm Lounge, Whitsunday Islands, Australia",
]

BEACH_LOUNGE_SPECIFIC_RULES = """
======================================================================
BEACH LOUNGE STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. INSIDE-OUT LUXURY CABANA FRAMING:
   - Frame 16:9 panoramic compositions on locked tripod looking from inside a luxury beachfront cabana or teak terrace onto turquoise surf.
   - Luxury elements: Billowing sheer white linen drapes, teak daybed with canvas cushions, weathered driftwood table, gentle sea breeze.
   - Purity Guard: Strictly mandate zero crowds, zero tourists, zero plastic beach chairs, zero modern watercraft.
2. NATURAL BALANCED LIGHTING:
   - Default to crisp 5500K natural daylight, warm 2800K sunset, or soft 2000K starlight.
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Cabana structure, daybed, and sand remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY subtle linen curtain flutter, gentle palm sway, and rhythmic rolling ocean wave wash.
   - Domain: "landscape_solid".
"""


def build_beach_lounge_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "beach_luxury_cabana_day",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Beach Lounge studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["sunset", "terrace"]):
        color_temp = 2800
        cluster = "Sunset Beach Terrace"
        default_topic = "Private teakwood beach terrace overlooking golden hour ocean sunset, glowing lanterns, and gentle rolling waves"
    elif any(w in arch_lower for w in ["twilight", "dusk", "pergola"]):
        color_temp = 2200
        cluster = "Twilight Beach Pergola"
        default_topic = "Open-air beach pergola at deep violet twilight, warm amber lanterns, and soothing ocean tide lullaby"
    elif any(w in arch_lower for w in ["night", "starlight", "hammock"]):
        color_temp = 2000
        cluster = "Starlit Beachfront Hammock"
        default_topic = "Starlit beachfront hammock between palms, glowing starlight reflecting on gentle dark turquoise waves, zero fire"
    else:
        color_temp = 5500
        cluster = "Luxury Beach Cabana Daytime"
        default_topic = "Shaded luxury beachfront cabana with billowing sheer linen drapes looking out at pristine turquoise ocean surf in bright 5500K daylight"

    return build_base_directorial_prompt(
        genre="relax/beach_lounge",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=BEACH_LOUNGE_SPECIFIC_RULES,
        curation_landmarks=BEACH_LOUNGE_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
