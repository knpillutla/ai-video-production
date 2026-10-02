"""Zen Studio Directorial Prompt Engineering.

Specialized exclusively in 432Hz Zen rock gardens, Kyoto temple grounds,
ancient moss sanctuaries, sacred lotus ponds, and raked gravel courtyards.
Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

ZEN_LANDMARK_POOL = [
    "Daitoku-ji Zuiho-in Raked Rock Garden, Kyoto, Japan",
    "Tenryu-ji Temple Sogenchi Reflection Pond, Arashiyama, Kyoto, Japan",
    "Ryoan-ji Temple Dry Landscape Rock Garden, Kyoto, Japan",
    "Ginkaku-ji Silver Pavilion Moss Garden & Sand Cone, Kyoto, Japan",
    "Kenkoku-ji Zen Temple Bamboo Grove & Stone Lanterns, Kamakura, Japan",
    "Byodoin Phoenix Temple Sacred Lotus Pond & Reflecting Waters, Uji, Japan",
    "Saiho-ji Kokedera Ancient Moss Temple Sanctuary, Kyoto, Japan",
    "Nanzen-ji Hojo Stone Garden & Cedar Veranda, Kyoto, Japan",
    "Kennin-ji Temple Twin Dragon Courtyard & Pebble Wave Garden, Kyoto, Japan",
    "Tofuku-ji Hojo Checkerboard Moss & Slate Garden, Kyoto, Japan",
]

ZEN_SPECIFIC_RULES = """
======================================================================
ZEN DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. AUTHENTIC JAPANESE GARDEN COMPOSITION & LIVING WALLPAPER:
   - Frame tranquil wide 16:9 compositions shot on a locked tripod with restrained asymmetry.
   - Foreground: Weathered dark cedar or cypress engawa veranda with rich wood grains, carved granite tsukubai water basin, or pristine raked gravel ripple patterns.
   - Midground: Meticulously sculpted Japanese black pines (niwaki), lush emerald moss mounds, and authentic granite toro lanterns with lichen.
   - Background: Weathered white clay temple walls, dark tiled eaves, or bamboo groves shrouded in soft dawn morning mist.
   - Illumination: Soft, ethereal morning sidelight (5400K daylight) with glowing dawn caustics on still reflective water.
   - PURE ZEN NATURE PURITY GUARD: Strictly mandate zero humans, zero tourists, zero monks, zero voices, zero modern buildings, zero vehicles, zero clutter, zero animals.

2. ACOUSTIC SOUNDSCAPE & 432Hz VELVET MASTERING:
   - Suno tags: "432Hz deep meditative soundscape, shakuhachi bamboo flute, warm singing bowl resonance, soft temple bell chime, gentle tsukubai water trickle, velvet -14 LUFS anti-fatigue master".
   - Spoken narration: Poetic, contemplative reflection on Zen philosophy, stillness of the mind, and the tranquil harmony between weathered timber, moss, and stone.

3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Temple verandas, raked gravel patterns, granite boulders, and stone lanterns remain 100% frozen, rigid, and static.
   - Animate ONLY subtle micro-ripples across the glassy water surface and gentle pine needle whispers in the faint morning breeze.
   - Domain: "landscape_solid" (gravel courtyard) or "water_fluid" (lotus pond / tsukubai).
"""


def build_zen_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "zen_healing",
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Zen studio directorial prompt conforming to global RelaxScreenplay schema."""
    return build_base_directorial_prompt(
        genre="relax/zen",
        sub_genre=sub_genre or "zen_healing",
        archetype="zen_garden",
        cluster="Kyoto, Japan",
        custom_prompt=custom_prompt or "Tranquil Kyoto Zen garden with raked gravel, mossy granite stones, and 432Hz bell resonance",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=ZEN_SPECIFIC_RULES,
        curation_landmarks=ZEN_LANDMARK_POOL,
        color_temp_kelvin=5400,
        channel_id=channel_id or "earth_serenade",
    )
