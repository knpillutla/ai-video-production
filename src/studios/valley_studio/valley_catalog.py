"""Valley Studio Archetype Catalog & Diurnal Visual Specifications."""
from __future__ import annotations
from typing import Any, Dict

VALLEY_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "valley_wildflower_meadow": {
        "title": "Lush Alpine Valley & Wildflower Meadow",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5400,
        "lighting_desc": "Vibrant, crisp 5400K natural daylight illuminating lush green meadows and colourful wildflower carpets",
        "visual_prompt": (
            "Masterpiece 4K photograph looking across an expansive emerald green alpine valley blanketed with dense blooming "
            "purple lupine, yellow buttercups, and white edelweiss wildflowers in brilliant 5400K daylight. A crystal-clear shallow "
            "stream ripples gently over smooth pebbles in the foreground, with distant forested slopes rising toward misty blue peaks. "
            "35mm Arri cinematography, locked tripod framing, 16:9 aspect ratio, pure pristine nature, zero tourists."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The distant forested hills and "
            "rolling green valley slopes remain 100% frozen, rigid, and temporally stable. Only gentle pastoral breezes softly sway "
            "the foreground wildflower petals, and micro ripples glide over the stream. Zero camera movement, zero panning, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[pastoral peace], gentle acoustic Celtic harp, airy wooden flute harmonics, morning valley birdsong, babbling pebble stream, 432Hz velvet pads, -21 LUFS",
    },
    "valley_morning_mist": {
        "title": "Golden Dawn Mist Rolling Over Pastoral Valley",
        "diurnal_timing": "dawn",
        "color_temp_kelvin": 4200,
        "lighting_desc": "Ethereal golden dawn sunlight piercing soft low-hanging morning mist over green rolling hills",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from a soft grassy knoll over a tranquil pastoral river valley during dawn. "
            "Soft horizontal sunbeams illuminate golden layers of gentle morning mist floating just above the emerald pastures. "
            "A rustic wooden split-rail fence meanders through the foreground with morning dew glinting on lush clover. "
            "16:9 framing, locked tripod, Hasselblad medium format clarity, pure untouched countryside, zero clutter."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod framing. The rolling pastures, wooden fence, and distant "
            "ridges remain 100% rigid and temporally stable. Only thin ethereal layers of morning mist slowly glide through the valley floor. "
            "Zero camera movement, zero panning, zero jitter."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[dawn meditation], classical nylon guitar harmonics, warm cello drone, gentle valley wind whisper, singing crystal bowls, 432Hz, -21 LUFS",
    },
    "valley_glacial_stream": {
        "title": "Crystal Glacial Valley Stream & Granite Boulders",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Crisp, balanced natural daylight with specular water caustics dancing on clean granite stones",
        "visual_prompt": (
            "Masterpiece 4K photograph capturing a pristine turquoise glacial stream winding through a tranquil sub-alpine valley. "
            "Smooth rounded granite boulders and mossy banks frame the crystal-clear water where swimming trout are visible in the "
            "deep pools. Distant snow-capped peaks frame the horizon under a spotless azure sky. Symmetrical 16:9 framing, locked tripod, 35mm film grain."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The large mossy boulders, pine trees, and "
            "distant peaks remain 100% frozen, rigid, and temporally stable. Continuous smooth laminar stream currents ripple gently over the rocks. "
            "Zero camera translation, zero morphing."
        ),
        "domain": "water_fluid",
        "audio_tags": "[stress relief], continuous gentle bubbling brook water foley, resonant handpan in major pentatonic, airy bansuri flute, 432Hz, -21 LUFS",
    },
    "valley_sunset_pastoral": {
        "title": "Sunset Golden Hour Over Rolling Lavender Valley",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 3000,
        "lighting_desc": "Warm molten amber and lavender sunset hues painting undulating slopes with long soothing shadows",
        "visual_prompt": (
            "Masterpiece 4K photograph looking across undulating rows of blooming purple lavender and pastoral fields glowing under "
            "the warm golden sunset light. Distant cypress trees and a rustic stone terrace overlook the horizon as the sun casts long "
            "violet shadows across the valley. Cinematic 16:9 panoramic perspective on locked tripod, pure serene beauty."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod perspective. The rolling lavender rows, "
            "stone terrace, and cypress trees remain 100% rigid and temporally stable. A faint evening breeze delicately caresses the topmost blossoms. "
            "Zero panning, zero camera movement."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep relaxation], soothing acoustic harp, warm velvet ambient pads, distant evening cicadas, calming sunset serenity, 432Hz, -21 LUFS",
    },
}


def get_valley_archetype(key: str) -> Dict[str, Any]:
    """Retrieve valley archetype by key with graceful fallback."""
    return VALLEY_ARCHETYPES.get(key, VALLEY_ARCHETYPES["valley_wildflower_meadow"])


def get_all_valley_archetypes() -> list[Dict[str, Any]]:
    """Return all valley archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in VALLEY_ARCHETYPES.items()]
