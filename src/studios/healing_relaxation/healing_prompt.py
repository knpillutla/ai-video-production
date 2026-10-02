"""Global Healing Relaxation & Solfeggio Sanctuary Directorial Prompt Engineering.

Specialized in global restorative healing sanctuaries (Himalayan singing bowl valleys,
Balinese sacred water springs, Nordic geothermal baths, Redwood cathedral groves,
travertine mineral terraces, and 432Hz/528Hz Solfeggio sound therapy).
Distinct from Japanese Zen — spans diverse global sacred nature landscapes.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

HEALING_LANDMARK_POOL = [
    "Himalayan Singing Bowl Sanctuary & Paro Sacred Valley, Bhutan",
    "Tirta Empul Sacred Spring & Emerald Jungle Water Temple, Ubud Bali",
    "Blue Lagoon Geothermal Mineral Springs & Rising Thermal Mist, Iceland",
    "Saturnia Travertine Cascades & Turquoise Thermal Pools, Tuscany Italy",
    "Redwood Cathedral Sanctuary & Fern Canyon, Northern California",
    "Pamukkale Travertine Thermal Terraces & Mineral Waterways, Turkey",
    "Fairy Glen & Crystal Mountain Springs, Isle of Skye Scotland",
    "Sacred Lotus Waters & Floating Water Lilies, Lake Pichola India",
    "Wairakei Geothermal Thermal Stream & Native Fern Sanctuary, New Zealand",
    "Cenote Suytun Sacred Cavern Sunbeam & Still Turquoise Water, Yucatan",
]

HEALING_SPECIFIC_RULES = """
======================================================================
GLOBAL HEALING SANCTUARY DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. SACRED RESTORATIVE LANDSCAPE COMPOSITION:
   - Frame wide 16:9 cinematic landscape perspectives shot on a locked tripod.
   - Diverse global healing geography: Translucent turquoise geothermal mineral pools, sacred jungle springs with stone carvings, ancient giant cathedral redwood groves, or serene lotus waterways beneath mountain peaks.
   - Illumination: Soft, warm ethereal morning light (5200K-5600K) or golden dawn caustics shimmering on crystal-clear mineral water with gentle rising thermal vapors.
   - PURE SANCTUARY PURITY GUARD: Strictly mandate zero humans, zero tourists, zero swimmers, zero modern clutter, zero vehicles, zero man-made trash.

2. ACOUSTIC SOUNDSCAPE & 432Hz/528Hz SOLFEGGIO MASTERING:
   - Suno tags: "432Hz Solfeggio healing resonance, Tibetan singing bowl vibration, warm crystal singing bowls, soothing Celtic harp, gentle sacred spring trickle, velvet anti-fatigue -14 LUFS".
   - Spoken narration: Poetic, restorative contemplation on cellular renewal, spiritual peace, ancient earth energy, and deep body-mind alignment.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Ancient tree trunks, canyon walls, travertine rock terraces, and mountain peaks remain 100% frozen, rigid, and static.
   - Animate ONLY the gentle thermal vapor mist rising, subtle glassy water ripples, and sparkling light glints.
   - Domain: "water_fluid" (springs/thermal pools) or "landscape_solid" (cathedral groves).
"""


def build_healing_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "global_healing",
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated global healing relaxation prompt conforming to RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/healing",
        sub_genre=sub_genre or "global_healing",
        archetype="healing_sanctuary",
        cluster="Global Restorative Nature Sanctuaries",
        custom_prompt=custom_prompt or "Sacred geothermal turquoise mineral springs with rising thermal mist and 432Hz singing bowls",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=HEALING_SPECIFIC_RULES,
        curation_landmarks=HEALING_LANDMARK_POOL,
        color_temp_kelvin=5400,
        channel_id=channel_id or "earth_serenade",
    )
