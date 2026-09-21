"""Reusable Cinematic Color Grading and Film Print Emulation Filters for FFmpeg."""

FILM_LUT_PRESETS: dict[str, dict[str, str]] = {
    "kodak_2383": {
        "display_name": "Kodak 2383 Print Film Stock",
        "description": "Rich contrast, warm highlight rolloff, deep blacks, natural skin tones",
        "ffmpeg_filter": "eq=contrast=1.08:brightness=0.01:saturation=1.06,curves=master='0/0 0.25/0.22 0.75/0.78 1/1':red='0/0 0.5/0.52 1/1':blue='0/0 0.5/0.47 1/0.95'",
    },
    "nordic_noir": {
        "display_name": "Nordic Slate Cool Blue-Grey",
        "description": "Desaturated moody slate tones, cool highlights, crisp cinematic clarity",
        "ffmpeg_filter": "eq=contrast=1.12:brightness=0.0:saturation=0.92,curves=master='0/0 0.5/0.48 1/1':blue='0/0 0.5/0.54 1/1':red='0/0 0.5/0.46 1/0.96'",
    },
    "golden_festival": {
        "display_name": "Golden Festival Vibrant Warmth",
        "description": "High-energy saturated primaries, glowing golden-hour sun radiance, vibrant silks",
        "ffmpeg_filter": "eq=contrast=1.06:brightness=0.02:saturation=1.18,curves=master='0/0 0.5/0.52 1/1':red='0/0 0.5/0.55 1/1':green='0/0 0.5/0.52 1/1':blue='0/0 0.5/0.44 1/0.92'",
    },
    "technicolor_vintage": {
        "display_name": "Technicolor 3-Strip Classic",
        "description": "Deep bold primaries, vintage cinematic drama, balanced shadows",
        "ffmpeg_filter": "eq=contrast=1.10:brightness=0.01:saturation=1.22,curves=master='0/0 0.2/0.18 0.8/0.82 1/1'",
    },
    "pristine_neutral": {
        "display_name": "Broadcast 4K Natural Neutral",
        "description": "True-to-life 5600K daylight fidelity, unadulterated micro-textures",
        "ffmpeg_filter": "eq=contrast=1.02:brightness=0.0:saturation=1.02",
    },
}


def resolve_film_lut(culture: str = "", genre: str = "", weather: str = "", custom_lut: str | None = None) -> str:
    """Deterministically select optimal cinematic film color grade filter for FFmpeg."""
    if custom_lut and custom_lut.lower() in FILM_LUT_PRESETS:
        return FILM_LUT_PRESETS[custom_lut.lower()]["ffmpeg_filter"]

    c_low = (culture or "").lower()
    g_low = (genre or "").lower()
    w_low = (weather or "").lower()

    if any(k in c_low for k in ("nordic", "iceland", "sweden", "norway", "scandinavia")) or "snow" in w_low or "noir" in g_low:
        return FILM_LUT_PRESETS["nordic_noir"]["ffmpeg_filter"]
    if any(k in g_low for k in ("dance", "mass", "folk", "jathara", "teenmaar", "music")) or "festival" in g_low:
        return FILM_LUT_PRESETS["golden_festival"]["ffmpeg_filter"]
    if any(k in g_low for k in ("movie", "epic", "cinema", "drama", "action")):
        return FILM_LUT_PRESETS["kodak_2383"]["ffmpeg_filter"]

    return FILM_LUT_PRESETS["kodak_2383"]["ffmpeg_filter"]


__all__ = ["FILM_LUT_PRESETS", "resolve_film_lut"]
