"""Universal Lighting & Photorealism Directorial Engine.

Enforces:
1. 4K/8K Hasselblad/Arri photorealism by default (zero CGI/cartoon/AI-plastic).
2. Universal Crisp Natural Daytime default (5400K-5600K, clear skies, natural sun).
3. User Intent Priority: Strictly honors user-requested time-of-day (sunrise, sunset,
   golden hour, evening, twilight, dusk, night, midnight, starlit).
"""
from __future__ import annotations
import re
from typing import Optional, Tuple

SUNRISE_KEYWORDS = ("sunrise", "dawn", "alpenglow", "morning light", "early morning")
SUNSET_KEYWORDS = ("sunset", "golden hour", "dusk", "sundown", "sun-down")
EVENING_KEYWORDS = ("evening", "twilight", "blue hour", "nightfall")
NIGHT_KEYWORDS = (
    "night", "midnight", "starlight", "starlit", "starry", "stars",
    "milky way", "moonlight", "moonlit", "dark night", "aurora", "campfire", "hearth"
)


def detect_lighting_directive(
    prompt: Optional[str] = None,
    archetype: Optional[str] = None,
    default_kelvin: int = 5500,
) -> Tuple[int, str, str]:
    """Detect appropriate lighting and color temperature from user prompt, honoring intent.

    Returns:
        (color_temp_kelvin, time_of_day_key, lighting_description)
    """
    text = (prompt or "").strip().lower()

    # 1. User Prompt takes absolute priority
    if text:
        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in SUNRISE_KEYWORDS):
            return (3800, "sunrise_dawn", "Soft golden morning sunrise and pastel alpenglow (3800K)")
        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in SUNSET_KEYWORDS):
            return (3000, "sunset_golden_hour", "Warm golden hour sunset, rich amber and rose illumination (3000K)")
        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in EVENING_KEYWORDS):
            return (3800, "evening_twilight", "Blue hour evening twilight with gentle warm illumination (3800K)")
        if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in NIGHT_KEYWORDS):
            return (2200, "night_starlight", "Deep indigo velvet midnight sky with celestial starlight (2200K)")

    # 2. If prompt did NOT specify, check if archetype explicitly specifies non-daytime
    arch = (archetype or "").strip().lower()
    if arch and not text:
        if any(kw in arch for kw in ("sunrise", "dawn")):
            return (3800, "sunrise_dawn", "Soft golden morning sunrise and pastel alpenglow (3800K)")
        if any(kw in arch for kw in ("sunset", "golden_hour")):
            return (3000, "sunset_golden_hour", "Warm golden hour sunset, rich amber and rose illumination (3000K)")
        if any(kw in arch for kw in ("evening", "twilight")):
            return (3800, "evening_twilight", "Blue hour evening twilight with gentle warm illumination (3800K)")
        if any(kw in arch for kw in ("night", "midnight", "starlight", "hearth", "campfire")):
            return (2200, "night_starlight", "Deep indigo velvet midnight sky with celestial starlight (2200K)")

    # 3. Base directive: Crisp Natural Daytime (5400K-5600K)
    return (default_kelvin, "daytime_natural", "Crisp balanced natural daytime sunlight (5400K-5600K), clear sky, true-to-life exposure")


def format_universal_lighting_guardrails(time_of_day_key: str, color_temp: int, desc: str) -> str:
    """Format the mandatory prompt directive block for Gemini screenplay generation."""
    return f"""======================================================================
UNIVERSAL PHOTOREALISM & LIGHTING DIRECTIVE (MANDATORY):
======================================================================
1. 4K/8K PHOTOREALISTIC CINEMATIC MASTERY (ZERO CGI / ZERO CARTOON):
   - Every scene MUST be authored as ultra-photorealistic photography shot on high-end cinema optics (Hasselblad H6D-100c / 35mm Arri cinema prime lenses, razor-sharp natural textures, balanced optical depth-of-field).
   - Strictly prohibit 3D render, cartoon, digital illustration, anime, CGI, video game graphics, or synthetic AI-plastic textures.

2. LIGHTING CALIBRATION ({time_of_day_key.upper()} - {color_temp}K):
   - Atmosphere: {desc}.
   - Default Standard: Crisp natural daytime (5400K-5600K) is the mandatory studio foundation.
   - Non-daytime lighting (sunrise, sunset, evening, night) is ONLY permitted when explicitly requested by user prompt.
   - Strictly prohibit artificial yellow flare blowouts, oversaturated amber washes, or unrealistic neon tinting."""
