"""Ocean Studio Directorial Prompt Construction.

Specialized prompt builder enforcing:
1. Strict Diurnal Lighting Calibration (5500K to 2000K).
2. Rule 20 Natural Water Dynamics & Ocean Fluid Alignment (Alibaba Wan 2.1 & Kling v3 Pro).
3. Rule 13 Natural Daylight Standards (no artificial yellow blowouts).
4. Stationary Locked-Tripod Living Wallpaper Cinemagraph Cadence.
"""

from typing import List, Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

OCEAN_LANDMARKS = [
    "Bora Bora Turquoise Lagoon & Mount Otemanu, French Polynesia",
    "Santorini Caldera Cliffside & Aegean Sea, Greece",
    "Maldives Overwater Sanctuary & Coral Reef Atoll",
    "Big Sur Pacific Coastal Highway & McWay Cove, California",
    "Cannon Beach Sea Stacks & Haystack Rock, Oregon",
    "Amalfi Coast Cliffside Villa & Tyrrhenian Sea, Italy",
    "Kauai North Shore Na Pali Coast & Pacific Waves, Hawaii",
    "Turks and Caicos Grace Bay Pristine White Sand & Azure Sea",
]

OCEAN_SPECIFIC_RULES = """
======================================================================
OCEAN RETREAT STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. ARCHITECTURAL LIVING WALLPAPER FRAMING:
   - Symmetrical, balanced 16:9 composition shot looking outward from a luxurious coastal vantage point (shaded overwater villa deck, Mediterranean stone veranda, cliffside terrace, or beach shelter).
   - Crisp architectural foreground (weathered teak columns, sheer white/ivory linen drapes, stone ledges, artisanal beverage on table).
   - Breathtaking natural ocean background (rolling turquoise wave swells, crystal clear reef lagoon, sea spray caustics, endless horizon).
2. RULE 20 NATURAL WATER DYNAMICS (MANDATORY):
   - Align camera motion or view parallel or perpendicular-facing to incoming laminar swells.
   - Mandate smooth glassy laminar wave swells, rhythmic shoreline breakers, and specular water caustics.
   - Negative constraints: "gelatinous water, melting foam, static frozen water, boiling water artifacts, rubbery water, unnatural foam blobs, zero static vertical streaks, zero falling wire artifacts".
3. STATIONARY LOCKED-TRIPOD CINEMAGRAPH CADENCE:
   - Camera motion must be strictly locked tripod. 
   - Animate ONLY natural fluid elements: continuous rhythmic ocean wave swells rolling ashore, sheer linen drapes fluttering in the sea breeze, and subtle water caustics.
   - Structural architecture, daybeds, furniture, and skies remain 100% rigid, frozen, and temporally stable.
4. PURITY & SOLITUDE MANDATE:
   - Strictly ZERO humans, zero tourists, zero boats, zero plastic trash, zero modern clutter.
"""


def build_ocean_prompt(
    custom_prompt: str = "",
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    archetype: str = "ocean_daytime_shore",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[List[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Builds authoritative system instruction for Gemini generating 4K Ocean Living Wallpapers."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["sunrise", "dawn"]):
        color_temp = 3800
        cluster = "Mediterranean Pastel Dawn"
        default_topic = "Luxury coastal veranda dawn looking out at pastel sea horizon"
    elif any(w in arch_lower for w in ["sunset", "golden_hour"]):
        color_temp = 3000
        cluster = "Pacific Cliffside Sunset"
        default_topic = "Cliffside sanctuary golden hour sunset overlooking fiery ocean horizon"
    elif any(w in arch_lower for w in ["bioluminescent", "night"]):
        color_temp = 2200
        cluster = "Bioluminescent Lagoon"
        default_topic = "Starlit beachfront pavilion looking out at electric-blue bioluminescent waves"
    elif any(w in arch_lower for w in ["campfire", "hearth"]):
        color_temp = 2000
        cluster = "Beach Campfire Surf"
        default_topic = "Driftwood campfire in beach stone pit with rhythmic dark ocean surf"
    elif any(w in arch_lower for w in ["rain", "storm"]):
        color_temp = 4500
        cluster = "Tropical Balcony Rain"
        default_topic = "Sheltered teak balcony looking out at gentle tropical ocean rain"
    else:
        color_temp = 5500
        cluster = "Maldives Overwater Lagoon"
        default_topic = "Shaded overwater villa deck looking out at vast turquoise lagoon and rolling waves"

    return build_base_directorial_prompt(
        genre="relax/ocean",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=OCEAN_SPECIFIC_RULES,
        curation_landmarks=OCEAN_LANDMARKS,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
