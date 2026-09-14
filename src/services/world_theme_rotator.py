"""Thematic World Location Rotator: Expands themes across cities, villages, mountains, and oceans."""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any

WORLD_DESTINATIONS = [
    {
        "location": "Kyoto, Japan",
        "category": "Historic City & Alleys",
        "setting_title": "Gion Lantern-lit Stone Alleys",
        "architecture": "Edo-period wooden machiya townhouses, weeping willows, and red paper lanterns",
        "lighting": "Twilight rain with warm glowing lanterns reflecting on wet stone pavements",
        "palette_rgb": [(185, 28, 28), (20, 25, 40), (245, 158, 11)],
        "scene_1": "Raindrops rippling across ancient stone-paved alleys between traditional wooden machiya chalets",
        "scene_2": "Golden lantern light reflecting across wet flagstones as gentle rain falls on canal waters",
    },
    {
        "location": "Hallstatt, Austria",
        "category": "Alpine Lake Village",
        "setting_title": "Misty Alpine Lake & Steeper Slopes",
        "architecture": "16th-century Alpine wooden chalets, historic lake church with pointed steeple, flower boxes",
        "lighting": "Misty overcast mountain daylight with ethereal fog rolling across mirror-glass lake",
        "palette_rgb": [(30, 58, 138), (16, 185, 129), (241, 245, 249)],
        "scene_1": "Footsteps along quiet lakeside wooden boardwalk with raindrops creating circular ripples",
        "scene_2": "Wide panoramic vista of misty limestone cliffs plunging into crystal lake waters",
    },
    {
        "location": "Tokyo, Japan",
        "category": "World Megacity",
        "setting_title": "Shibuya Neon Crosswalks & Glass Walkways",
        "architecture": "Futuristic glass skyscrapers, glowing cybernetic billboards, multi-level pedestrian skyways",
        "lighting": "High-contrast neon pink, electric cyan, and amber reflections on rain-slicked asphalt",
        "palette_rgb": [(236, 72, 153), (6, 182, 212), (15, 23, 42)],
        "scene_1": "Crowds with transparent umbrellas gliding past towering neon screens under steady rain",
        "scene_2": "Low-angle reflection tracking shot across rain puddles mirroring vibrant city lights",
    },
    {
        "location": "Amalfi Coast, Italy",
        "category": "Coastal Ocean & Cliffs",
        "setting_title": "Positano Cliffside Paths Overlooking Azure Sea",
        "architecture": "Pastel terracotta villas cascading down vertical cliffs with curved stone stairways",
        "lighting": "Mediterranean stormy coastal daylight with dramatic sea spray and glistening lemon groves",
        "palette_rgb": [(3, 105, 161), (249, 115, 22), (248, 250, 252)],
        "scene_1": "Walking down narrow cobblestone steps flanked by wet bougainvillea overlooking turbulent sea",
        "scene_2": "Dramatic coastal overlook as waves crash against sea-sculpted limestone rocks in the mist",
    },
    {
        "location": "Western Ghats (Munnar), India",
        "category": "Misty Mountain Highlands",
        "setting_title": "Emerald Monsoon Tea Terraces & Waterfalls",
        "architecture": "British-era colonial stone bungalows and stepped emerald tea garden contours",
        "lighting": "Deep monsoon cloudbreak with lush saturated emerald tones and glistening tea leaves",
        "palette_rgb": [(6, 78, 59), (16, 185, 129), (202, 138, 4)],
        "scene_1": "Walking along winding red-earth pathway through endless stepped tea hills veiled in rain mist",
        "scene_2": "A sudden cascade of mountain waterfall roaring past granite boulders beside the path",
    },
    {
        "location": "London, United Kingdom",
        "category": "Historic Metropolis",
        "setting_title": "Westminster Embankment & Thames River Walk",
        "architecture": "Victorian Gothic stone arches, black wrought-iron gas lamps, and iconic red phone booths",
        "lighting": "Moody slate grey rain ambiance with warm amber streetlights reflecting in puddles",
        "palette_rgb": [(30, 41, 59), (185, 28, 28), (251, 191, 36)],
        "scene_1": "Rain pattering on Victorian stone balustrades along the misty river Thames embankment",
        "scene_2": "Glistening wet cobblestones leading toward historic clock towers silhouetted in evening drizzle",
    },
    {
        "location": "Ha Long Bay, Vietnam",
        "category": "Emerald Oceans & Water",
        "setting_title": "Limestone Karst Sea Caves & Rainforest Waters",
        "architecture": "Traditional wooden junk boats and stilt fishing huts nestled against sheer karst cliffs",
        "lighting": "Ethereal sea mist and tropical drizzle creating emerald reflections on calm ocean bays",
        "palette_rgb": [(13, 148, 136), (15, 118, 110), (224, 242, 254)],
        "scene_1": "Gliding on a quiet wooden sampan through misty limestone arches into a secluded sea cove",
        "scene_2": "Raindrops dancing on calm turquoise bay water surrounded by towering jungle-topped pillars",
    },
    {
        "location": "Bruges, Belgium",
        "category": "Canal Town & Medieval Village",
        "setting_title": "Medieval Brick Bridges & Weeping Canals",
        "architecture": "Gothic stepped-gable brick houses and arched stone bridges spanning quiet canals",
        "lighting": "Soft afternoon rain with amber reflections on wet historic brickwork and canal ripples",
        "palette_rgb": [(120, 53, 15), (71, 85, 105), (254, 240, 138)],
        "scene_1": "Solitary walk across an arched medieval stone bridge with rain whispering on canal water",
        "scene_2": "Reflections of ancient brick towers trembling in canal puddles as swans glide past",
    },
]

_GLOBAL_ROTATION_COUNTER: int = 0
_USER_ROTATION_COUNTER: dict[str, int] = {}


@dataclass
class WorldSetting:
    """Resolved geographic location setting for creative theme execution."""
    location: str
    category: str
    setting_title: str
    architecture: str
    lighting: str
    palette_rgb: list[tuple[int, int, int]]
    scene_1_beat: str
    scene_2_beat: str
    resolved_theme_title: str


def resolve_world_theme_setting(theme_or_prompt: str, user_id: str | None = None) -> WorldSetting:
    """Intelligently map theme concepts (e.g. 'walking in rain') to rotating world destinations."""
    global _GLOBAL_ROTATION_COUNTER
    t_lower = (theme_or_prompt or "").lower()

    # 1. Check if user explicitly named a specific world location
    for dest in WORLD_DESTINATIONS:
        loc_parts = dest["location"].lower().replace(",", "").split()
        if any(part in t_lower for part in loc_parts if len(part) > 3):
            return WorldSetting(
                location=dest["location"],
                category=dest["category"],
                setting_title=dest["setting_title"],
                architecture=dest["architecture"],
                lighting=dest["lighting"],
                palette_rgb=dest["palette_rgb"],
                scene_1_beat=dest["scene_1"],
                scene_2_beat=dest["scene_2"],
                resolved_theme_title=f"{theme_or_prompt.strip()} • {dest['location']}",
            )

    # 2. Dynamic rotation for open-ended themes across cities, villages, mountains, and oceans
    if user_id:
        idx = _USER_ROTATION_COUNTER.get(user_id, _GLOBAL_ROTATION_COUNTER) % len(WORLD_DESTINATIONS)
        _USER_ROTATION_COUNTER[user_id] = (idx + 1) % len(WORLD_DESTINATIONS)
        _GLOBAL_ROTATION_COUNTER = (idx + 1) % len(WORLD_DESTINATIONS)
    else:
        idx = _GLOBAL_ROTATION_COUNTER % len(WORLD_DESTINATIONS)
        _GLOBAL_ROTATION_COUNTER = (idx + 1) % len(WORLD_DESTINATIONS)

    dest = WORLD_DESTINATIONS[idx]

    clean_theme = theme_or_prompt.strip()
    title_display = f"{clean_theme} • {dest['location']}" if clean_theme else f"Walking in the Rain: {dest['location']}"

    return WorldSetting(
        location=dest["location"],
        category=dest["category"],
        setting_title=dest["setting_title"],
        architecture=dest["architecture"],
        lighting=dest["lighting"],
        palette_rgb=dest["palette_rgb"],
        scene_1_beat=dest["scene_1"],
        scene_2_beat=dest["scene_2"],
        resolved_theme_title=title_display,
    )


__all__ = ["WorldSetting", "WORLD_DESTINATIONS", "resolve_world_theme_setting"]
