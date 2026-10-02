"""Rain Optics & Droplet Dynamics Engine.

Authoritative specification for studio-grade rain physics across:
- Type A: Glass Window Streaming & Rivulets (Cabin TrackSound / Indoor ASMR)
- Type B: Kinetic Puddle Impact & Walking Tour (POV Wet Street Reflections)
- Type C: Canopy & River Surface Ripples (Lush Temperate Nature)

Conforms strictly to 4K Master, Wan 2.1 / Kling v3, and FLUX 1.1 Pro Ultra directives.
"""

from __future__ import annotations
from typing import Any, Dict


# ======================================================================
# TYPE A: GLASS WINDOW STREAMING & RIVULETS (Cabin TrackSound Archetype)
# ======================================================================
RAIN_GLASS_VISUAL_DIRECTIVE = (
    "Ultra-photorealistic 8K UHD macro and environmental perspective through a large panoramic floor-to-ceiling glass window pane. "
    "Clear, high-surface-tension spherical water droplets clinging to the glass, with meandering gravity-driven rivulets trickling and streaming downward. "
    "Subtle misty condensation along window corners with pinpoint specular light glints reflecting warm 2700K interior amber lamplight. "
    "Foreground features an unmade plush king bed with thick textured linen duvet and dark cedar timber framing. "
    "Background outside shows a dark emerald misty pine forest softly diffused in optical bokeh (f/2.0) under continuous steady rainfall."
)

RAIN_GLASS_MOTION_DIRECTIVE = (
    "Living wallpaper cinemagraph fluid mechanics. Rigid interior bedroom structure, bed, furniture, lamp, and window frame remain 100% stationary, frozen, and unmoving. "
    "Animate ONLY the natural fluid mechanics: continuous gravity rivulets and water droplets sliding, trickling, and meandering smoothly downward along the glass window surface, "
    "with subtle soft drifting rain mist in the distant pine canopy outside. Stable uniform 2700K interior lighting, seamless loop cadence."
)


# ======================================================================
# TYPE B: KINETIC PUDDLE IMPACT & WALKING TOUR (Rain Walking Archetype)
# ======================================================================
RAIN_WALKING_VISUAL_DIRECTIVE = (
    "First-person POV cinematic 4K UHD walking tour perspective during gentle continuous rain. "
    "Wet dark cobblestone and asphalt pavements displaying glistening mirror reflections of warm ambient street lanterns and shop lights. "
    "Crystal-clear water puddles showing sharp, expanding concentric circular Rayleigh ripple waves from falling raindrops. "
    "Atmospheric vertical rain streaks, delicate misty air, clean umbrella canopy framing overhead, strictly zero human tourists, pristine tranquil mood."
)

RAIN_WALKING_MOTION_DIRECTIVE = (
    "Ultra-slow tranquil walking tour cadence (~1.5 km/h) with subtle steadycam floating sway. "
    "Continuous vertical raindrops descending naturally, striking wet pavement and generating smooth expanding circular ripples across puddles. "
    "Glistening specular reflections shifting gently with slow camera translation. Regular gravitational droplet detachment from umbrella edge."
)


# ======================================================================
# FLUID NEGATIVE PROMPT GUARDS (Rule 20)
# ======================================================================
RAIN_FLUID_NEGATIVE_TOKENS = (
    "gelatinous water, melting foam, static frozen water, boiling water artifacts, rubbery water, "
    "unnatural foam blobs, static vertical streaks, falling wire artifacts, unnatural fast motion, "
    "flickering, morphing architecture, structural drift, camera shudder, sudden color shifts"
)


def get_rain_droplet_specs(archetype_or_subgenre: str) -> Dict[str, Any]:
    """Retrieve fine-tuned droplet optics and motion directives for a given archetype."""
    key = (archetype_or_subgenre or "").lower()

    if "walking" in key or "street" in key or "tour" in key or "puddle" in key:
        return {
            "type": "walking_puddles",
            "visual_prompt": RAIN_WALKING_VISUAL_DIRECTIVE,
            "motion_prompt": RAIN_WALKING_MOTION_DIRECTIVE,
            "negative_prompt": RAIN_FLUID_NEGATIVE_TOKENS,
            "color_temp_kelvin": 3800,
            "camera_cadence": "walking_steadycam_slow",
            "audio_tags": "432Hz binaural rain ASMR, umbrella rain pitter-patter, wet pavement puddle splash footsteps, quiet night ambiance, -14 LUFS, zero vocals",
        }

    # Default to Type A Glass Bedroom / Cabin (Cabin TrackSound)
    return {
        "type": "glass_window_rivulets",
        "visual_prompt": RAIN_GLASS_VISUAL_DIRECTIVE,
        "motion_prompt": RAIN_GLASS_MOTION_DIRECTIVE,
        "negative_prompt": RAIN_FLUID_NEGATIVE_TOKENS,
        "color_temp_kelvin": 2700,
        "camera_cadence": "locked_tripod_cinemagraph",
        "audio_tags": "432Hz binaural rain ASMR, steady raindrops streaming on glass window, soft roof rainfall pitter-patter, deep sleep soundscape, -14 LUFS, zero vocals, zero drums",
    }
