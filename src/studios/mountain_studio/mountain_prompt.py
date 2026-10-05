"""Mountain Studio Directorial Prompt Engineering.

Specialized in 4K high alpine peaks, granite spires, and glacial mountain living wallpapers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

MOUNTAIN_LANDMARK_POOL = [
    "Matterhorn & Gornergrat Glacial Ridge, Zermatt, Swiss Alps",
    "Tre Cime di Lavaredo Monumental Towers, Dolomites, Italy",
    "Mount Rainier High Alpine Paradise Ridge, Washington, USA",
    "Aoraki Mount Cook Hooker Valley Glacial Vista, Southern Alps, New Zealand",
    "Fitz Roy Granite Spires & Laguna de los Tres, Patagonia, Argentina",
    "Eiger, Mönch and Jungfrau High Alpine Pass, Grindelwald, Switzerland",
]

MOUNTAIN_SPECIFIC_RULES = """
======================================================================
MOUNTAIN STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. HIGH-ALTITUDE MONUMENTAL FRAMING:
   - Frame 16:9 panoramic compositions on a locked stationary tripod looking from alpine ridges or viewpoints onto majestic summits.
   - Purity Guard: Strictly mandate zero humans, zero tourists, zero mountaineers, zero climbing ropes, zero modern clutter.
2. NATURAL DAYLIGHT LIGHTING:
   - Default to balanced 5400K-5600K crisp mountain daylight. Zero artificial yellow haze, zero lens flares.
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Mountains, rocky ridges, and viewpoints remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY subtle high-altitude mist drifts or gentle lake ripples.
   - Domain: "landscape_solid".
"""


def build_mountain_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "mountain_daytime_vista",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Mountain studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if any(w in arch_lower for w in ["sunrise", "dawn"]):
        color_temp = 3800
        cluster = "Alpine Summit Sunrise Dawn"
        default_topic = "High alpine mountain summit at sunrise dawn, pastel rose alpenglow lighting jagged granite crags"
    elif any(w in arch_lower for w in ["sunset", "alpenglow"]):
        color_temp = 2800
        cluster = "Dolomite Sunset Alpenglow"
        default_topic = "Fiery alpenglow sunset bathing towering jagged granite peaks, deep purple valley shadows"
    elif any(w in arch_lower for w in ["night", "starlight", "milky_way"]):
        color_temp = 2000
        cluster = "Midnight Alpine Ridge"
        default_topic = "Midnight alpine pass under crystal velvet indigo sky with brilliant Milky Way galaxy over snow peaks"
    else:
        color_temp = 5500
        cluster = "Swiss Alpine Daytime Vista"
        default_topic = "Panoramic high alpine mountain pass in crisp 5500K daylight, snow-capped granite spires, mirror glacial lake"

    return build_base_directorial_prompt(
        genre="relax/mountain",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=MOUNTAIN_SPECIFIC_RULES,
        curation_landmarks=MOUNTAIN_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
