"""Alpine Nature Studio Directorial Prompt Engineering.

Specialized exclusively in panoramic mountain landscapes, Swiss Alps, Dolomites,
snow-capped peaks, wildflower meadows, and crystal-clear glacial streams.
Conforms strictly to the global RelaxScreenplay schema contract via Ambient World Studio.
"""

from __future__ import annotations
from typing import Optional
from src.studios.ambient_world.ambient_directorial_prompt import build_ambient_directorial_prompt

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
    eff_prompt = custom_prompt or "Majestic Swiss Alps panoramic peaks and wildflower meadows with crystal glacial stream"
    return build_ambient_directorial_prompt(
        genre="relax/nature",
        archetype="alpine_meadow",
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion or "locked_tripod",
        excluded_topics=excluded_topics,
        image_model=image_model,
        google_search_enabled=False,
        tier=tier,
    )
