"""Ocean Studio Directorial Prompt Construction.

Specialized prompt builder enforcing:
1. Strict Diurnal Lighting Calibration (5500K to 2000K).
2. Rule 20 Natural Water Dynamics & Ocean Fluid Alignment (Alibaba Wan 2.1 & Kling v3 Pro).
3. Rule 13 Natural Daylight Standards (no artificial yellow blowouts).
4. Stationary Locked-Tripod Living Wallpaper Cinemagraph Cadence.
"""

from typing import List, Optional
from src.studios.ocean_studio.ocean_catalog import OCEAN_ARCHETYPES

OCEAN_DIURNAL_LIGHTING = {
    "daytime": "Balanced 5500K natural tropical daylight, bright sun illuminating vibrant turquoise lagoon, cerulean blue sky, zero yellow haze.",
    "sunrise": "Soft 3800K pastel dawn radiance, delicate blush-pink and pale lavender horizon, warm golden sun-shafts reflecting across glassy ocean swells.",
    "sunset": "Rich 3000K golden hour terracotta and vermilion sunset, glowing molten gold reflections across rhythmic wave crests, peaceful evening calm.",
    "night_bioluminescent": "Deep 2200K dark indigo midnight canopy, brilliant Milky Way galaxy arch, rhythmic rolling waves glowing with natural electric-blue bioluminescent phytoplankton, strictly zero campfire, zero smoke.",
    "campfire": "Warm 2000K crackling driftwood campfire in rustic beach stone pit on dark sand, glowing orange wood embers, dark rhythmic ocean surf in background under starlit sky.",
    "rain": "Overcast 4500K soft diffuse silver-gray light, soothing tropical rain falling across calm turquoise sea, concentric micro-ripples, sheltered wooden veranda view.",
}

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


def build_ocean_prompt(
    custom_prompt: str = "",
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    archetype: str = "ocean_daytime_shore",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[List[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Builds authoritative system instruction for Gemini Pro generating 4K Ocean Living Wallpapers."""
    arch_data = OCEAN_ARCHETYPES.get(archetype, OCEAN_ARCHETYPES["ocean_daytime_shore"])
    from src.studios.ocean_studio.ocean_cultural_audio import detect_diurnal_timing
    diurnal_key = detect_diurnal_timing(custom_prompt, archetype=archetype)
    lighting_rule = OCEAN_DIURNAL_LIGHTING.get(diurnal_key, OCEAN_DIURNAL_LIGHTING["daytime"])

    excluded_str = ""
    if excluded_topics:
        excluded_str = (
            f"\nTOPIC DEDUPLICATION MANDATE:\n"
            f"The following ocean topics were recently produced for this channel: {excluded_topics}.\n"
            f"You MUST select a completely unique geographic coastline, perspective, or seasonal timing.\n"
        )

    return f"""You are the Master Architectural Director & Blue-Chip Cinematographer for 'Ocean Retreat Studio'.
You specialize in 4K Living Wallpapers of pristine coastal sanctuaries, overwater bungalows, cliffside terraces, and rhythmic ocean surf under genre 'relax/ocean'.

TARGET ARCHETYPE: {arch_data.display_name} (Key: {arch_data.key})
DIURNAL LIGHTING STANDARD: {lighting_rule}

CORE DIRECTORIAL DIRECTIVES:
1. Architectural Living Wallpaper Framing:
   - Symmetrical, balanced 16:9 composition shot looking outward from a luxurious coastal vantage point (shaded overwater villa deck, Mediterranean stone veranda, cliffside terrace, or beach shelter).
   - Crisp architectural foreground (weathered teak columns, sheer white/ivory linen drapes, stone ledges, artisanal beverage on table).
   - Breathtaking natural ocean background (rolling turquoise wave swells, crystal clear reef lagoon, sea spray caustics, endless horizon).

2. Rule 20 Natural Water Dynamics (Mandatory):
   - Align camera motion or view parallel or perpendicular-facing to incoming laminar swells.
   - Mandate smooth glassy laminar wave swells, rhythmic shoreline breakers, and specular water caustics.
   - Negative constraints: "gelatinous water, melting foam, static frozen water, boiling water artifacts, rubbery water, unnatural foam blobs, zero static vertical streaks, zero falling wire artifacts".

3. Stationary Locked-Tripod Cinemagraph Cadence:
   - Camera motion must be strictly locked tripod. 
   - Animate ONLY natural fluid elements: continuous rhythmic ocean wave swells rolling ashore, sheer linen drapes fluttering in the sea breeze, and subtle water caustics.
   - Structural architecture, daybeds, furniture, and skies remain 100% rigid, frozen, and temporally stable.

4. 100% Monetization-Safe & Solitude Mandate:
   - Strictly ZERO humans, zero tourists, zero boats, zero plastic trash, zero modern clutter.
   - Audio tags must enforce 432Hz/528Hz Solfeggio anti-anxiety soundbath, culturally matched instruments, and rhythmic ocean surf foley.

5. Shot Count & Duration:
   - Number of shots: {num_shots} (Master 60s seamless loop).
   - Target duration: {duration_seconds} seconds.
{excluded_str}
OUTPUT SCHEMA:
Generate a valid RelaxScreenplay JSON adhering exactly to the provided schema. Set genre='relax/ocean', primary_archetype='{arch_data.key}'.
"""
