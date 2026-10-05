"""Blizzard Studio Archetype Catalog & Diurnal Visual Specifications."""
from __future__ import annotations
from typing import Any, Dict

BLIZZARD_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "blizzard_cozy_cabin_window": {
        "title": "Warm Timber Cabin Looking Out at Ferocious Alpine Blizzard",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 2700,
        "lighting_desc": "Warm 2700K cedar cabin interior contrasting against sub-zero silver-blue howling blizzard outside",
        "visual_prompt": (
            "Masterpiece 4K photograph looking through a large panoramic double-glazed window of a cozy cedar alpine cabin. "
            "Delicate frost crystals frame the edges of the warm glass pane. Outside, a ferocious whiteout blizzard howls through "
            "towering snow-laden evergreen pines with dense swirling snowflakes. Inside on the wide wooden windowsill, a steaming "
            "brass mug of spiced cider and an open book rest near a soft wool throw blanket. 35mm Arri cinematography, locked tripod, "
            "16:9 aspect ratio, pure winter warmth, zero tourists, zero clutter."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The cozy wooden windowsill, mug, "
            "and interior cabin architecture remain 100% frozen, rigid, and temporally stable. Outside the window, dense snowflakes "
            "whirl in realistic horizontal wind gusts through the misty pines, with faint steam rising from the hot mug. "
            "Zero camera movement, zero panning, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep winter sleep], realistic howling sub-zero blizzard wind ASMR, muffled interior shelter foley, soft crackling cedar fire embers, warm 432Hz ambient drone, -21 LUFS",
    },
    "blizzard_frosted_pine_forest": {
        "title": "Sub-Zero Snowstorm & Snow-Laden Pine Canopy",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 4500,
        "lighting_desc": "Crisp silver-slate winter blizzard light filtering through dense snow-covered spruce and fir trees",
        "visual_prompt": (
            "Masterpiece 4K photograph from an open-air stone shelter looking out into an ancient frosted boreal pine forest during "
            "a heavy winter snowstorm. Majestic evergreen boughs sag heavily under inches of pristine powdered snow. Swirling powder snow "
            "drifts across the forest floor in rhythmic gusts under a dramatic overcast winter sky. Symmetrical 16:9 framing, locked tripod, 35mm film grain."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod framing. The stone shelter and heavy pine trunks "
            "remain 100% frozen, rigid, and temporally stable. Continuous steady snowfall drifts diagonally through the forest canopy, "
            "with occasional powdery snow dust dislodging from branches. Zero camera movement, zero jitter."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[snowstorm ASMR], continuous heavy falling snow white noise, rhythmic winter wind gusts through pine needles, distant muffled thunder of falling snow clumps, 432Hz, -21 LUFS",
    },
    "blizzard_alpine_hearth_shelter": {
        "title": "Rustic Stone Hearth Fireplace & Howling Mountain Storm",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 2200,
        "lighting_desc": "Rich glowing 2200K firelight from a rugged stone hearth illuminating a mountain storm shelter at dusk",
        "visual_prompt": (
            "Masterpiece 4K photograph inside a rugged mountain refuge stone fireplace nook. A roaring hardwood fire crackles within "
            "an ancient river stone hearth, casting amber dancing shadows over rough-hewn pine logs and hand-woven blankets. To the side, "
            "a small frosty window pane reveals a dark howling twilight blizzard raging outside. 16:9 cinematic framing, locked tripod."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The stone fireplace mantle, timber walls, "
            "and floor remain 100% rigid and temporally stable. Gentle flickering amber flames and pulsing coals burn in the hearth, "
            "contrasting with the muffled blizzard visible through the frost glass. Zero camera translation."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[fireside winter retreat], deep crackling oak log fire, exterior blizzard wind howling ducked by -20dB, soothing cello drone, restorative 432Hz warmth, -21 LUFS",
    },
    "blizzard_twilight_snowfall": {
        "title": "Quiet Twilight Blue-Hour Deep Snowfall",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 3500,
        "lighting_desc": "Peaceful cobalt blue-hour twilight with large gentle snowflakes descending silently upon deep powder snow",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from a sheltered cedar porch over a tranquil alpine clearing at deep twilight. "
            "Large, fluffy, feather-like snowflakes fall vertically through the calm blue-hour atmosphere onto untouched, pristine "
            "powder snowbanks. An unlit antique copper lantern hangs from a timber beam. Strictly zero tourists, 16:9 framing, locked tripod."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The cedar porch beam, lantern, and deep snow drifts "
            "remain 100% frozen, rigid, and temporally stable. Large fluffy snowflakes float gently and steadily downward through the calm twilight air. "
            "Zero panning, zero camera movement."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[silent snow meditation], softest velvet brown noise snowfall, gentle acoustic harp, peaceful midnight cello, calming winter serenity, 432Hz, -21 LUFS",
    },
}


def get_blizzard_archetype(key: str) -> Dict[str, Any]:
    """Retrieve blizzard archetype by key with graceful fallback."""
    return BLIZZARD_ARCHETYPES.get(key, BLIZZARD_ARCHETYPES["blizzard_cozy_cabin_window"])


def get_all_blizzard_archetypes() -> list[Dict[str, Any]]:
    """Return all blizzard archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in BLIZZARD_ARCHETYPES.items()]
