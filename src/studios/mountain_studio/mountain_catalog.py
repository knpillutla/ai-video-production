"""Mountain Studio Archetype Catalog & Diurnal Visual Specifications."""
from __future__ import annotations
from typing import Any, Dict

MOUNTAIN_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "mountain_summit_dawn": {
        "title": "Jagged Alpine Summit & Golden Dawn Radiance",
        "diurnal_timing": "dawn",
        "color_temp_kelvin": 3800,
        "lighting_desc": "Soft pastel peach and gold dawn radiance kissing jagged snow-dusted granite peaks",
        "visual_prompt": (
            "Masterpiece 4K photograph looking out from a high-altitude alpine ridge onto towering jagged snow-dusted "
            "granite mountain peaks during dawn. First golden sunbeams illuminate jagged summit ridges, casting soft "
            "pink and amber gradients across pristine snowfields. Far below, a sea of soft morning clouds blankets the "
            "valley. 35mm Arri cinematography, locked tripod framing, 16:9 aspect ratio, pure pristine nature, zero tourists."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The jagged granite peaks "
            "and snowy summit ridge remain 100% rigid, frozen, and temporally stable. Only delicate wisps of morning summit "
            "mist slowly drift across distant mountain passes. Zero camera movement, zero panning, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep relaxation], airy wooden mountain flute, Tibetan singing bowls, crisp high-altitude wind whisper, warm 432Hz ambient pads, -21 LUFS",
    },
    "mountain_daytime_vista": {
        "title": "Dolomite Granite Peaks & Turquoise Glacial Lake Vista",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Crisp, balanced natural daylight under pure cerulean blue sky, zero yellow haze",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from a weathered cedar alpine viewpoint onto monumental jagged Dolomite granite "
            "towers rising dramatically into a brilliant cerulean blue sky in crisp 5500K daylight. At the base of the sheer "
            "cliffs lies a mirror-still turquoise glacial lake reflecting snow patches and rocky pinnacles. Symmetrical 16:9 framing, "
            "locked tripod, Hasselblad medium format clarity, zero modern clutter."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod framing. The massive Dolomite peaks, cedar viewpoint, "
            "and rocky ridges remain 100% frozen and temporally stable. Microscopic gentle ripples glide across the glacial lake surface. "
            "Zero camera movement, zero panning, zero jitter."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[peaceful meditation], gentle resonant handpan in major pentatonic, soft mountain breeze, crystalline chimes, 432Hz velvet drone, -21 LUFS",
    },
    "mountain_sunset_alpenglow": {
        "title": "Monumental Mountain Alpenglow & Terracotta Summit",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 2800,
        "lighting_desc": "Fiery terracotta and burnt crimson alpenglow painting western mountain faces with deep purple valley shadows",
        "visual_prompt": (
            "Masterpiece 4K photograph looking onto majestic alpine peaks glowing with intense fiery crimson and terracotta alpenglow "
            "during sunset. The sheer western rock faces radiate warm molten gold while long deep indigo shadows stretch across the "
            "lower glacial valleys. Cinematic 16:9 panoramic perspective, shot on a locked tripod, 35mm film grain, pure untouched wilderness."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod perspective. The glowing alpenglow mountain "
            "faces and foreground stone crags remain 100% rigid and temporally stable. Only subtle high-altitude twilight clouds gently "
            "drift along the distant horizon. Zero camera translation, zero warping."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[restorative sleep], deep cello harmonics, resonant singing bowls, warm alpenglow velvet synth pads, distant wind whisper, 432Hz, -21 LUFS",
    },
    "mountain_starlit_ridge": {
        "title": "Midnight Alpine Ridge & Milky Way Galaxy",
        "diurnal_timing": "starlight",
        "color_temp_kelvin": 2000,
        "lighting_desc": "Deep velvet indigo night with glittering diamond Milky Way galaxy arching over mountain silhouettes",
        "visual_prompt": (
            "Masterpiece 4K long-exposure photograph from an alpine mountain pass looking at the monumental silhouettes of snow-capped "
            "mountain summits under a crystal-clear velvet indigo night sky. The glowing Milky Way galaxy arches majestically overhead, "
            "reflecting faint starlight on snow patches below. Strictly zero fire, zero artificial lights, 16:9 cinematic framing on locked tripod."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The rugged alpine peaks, foreground boulders, "
            "and snow remain 100% rigid, frozen, and temporally stable. The starlit night sky features gentle, imperceptible stellar twinkling. "
            "Zero panning, zero camera movement, zero distortion."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep delta sleep], warm 432Hz velvet ambient drones, celestial glass bells, distant midnight alpine breeze, soothing stress relief, -21 LUFS",
    },
}


def get_mountain_archetype(key: str) -> Dict[str, Any]:
    """Retrieve mountain archetype by key with graceful fallback."""
    return MOUNTAIN_ARCHETYPES.get(key, MOUNTAIN_ARCHETYPES["mountain_daytime_vista"])


def get_all_mountain_archetypes() -> list[Dict[str, Any]]:
    """Return all mountain archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in MOUNTAIN_ARCHETYPES.items()]
