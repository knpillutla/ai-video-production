"""Contextual 3D 360-Degree Camera Flight Orbit Engine for Concert Productions.

Dynamically synthesizes cinema-grade 10-second 360 orbital camera trajectories
matching the exact musical style, venue architecture, and audience demeanor.
"""

from __future__ import annotations

from typing import Any, Tuple


def build_contextual_orbit_prompt(
    style: str = "Carnatic Classical",
    setting: str = "beach",
    venue_type: str = "outdoor",
    background: str = "beach_ocean",
    weather: str = "clear",
    chars: str = "Radha",
    instrument: str = "mic",
    position: str = "standing",
    has_chorus: bool = False,
) -> Tuple[str, str]:
    """Generate authentic 3D 360-degree orbit prompt and negative prompt tailored to genre, venue, and audience atmosphere."""
    style_l = (style or "").lower()
    setting_l = f"{setting} {background}".lower()
    is_classical = any(k in style_l for k in ("carnatic", "hindustani", "classical", "fusion", "devotional", "spiritual", "acoustic", "melody", "ballad"))
    is_beach = any(k in setting_l for k in ("beach", "coastal", "ocean", "shore", "sea"))
    is_outdoor = "outdoor" in (venue_type or "").lower() or is_beach or any(k in setting_l for k in ("garden", "rooftop", "terrace", "desert", "courtyard"))

    if is_classical:
        aud_desc = "serene open-air listeners seated comfortably along the seaside promenade, listening in deep appreciation with gentle head nods under warm ambient lanterns, with ocean waves in the background" if (is_beach or is_outdoor) else "serene classical music connoisseurs seated attentively in the hall, listening in deep appreciation with graceful hand gestures, under warm acoustic hall chandeliers"
        aud_neg = "waving lights, lightsticks, glowing sticks, smartphone flashlights, wild jumping fans, screaming crowd, rave party, EDM lasers, stadium lightsticks"
    elif any(k in style_l for k in ("party", "rock", "edm", "banger")):
        aud_desc = "ecstatic cheering concert fans waving glowing lightsticks and swaying to the driving rhythm"
        aud_neg = "empty audience, bored crowd"
    else:
        aud_desc = "engaged concert audience seated and standing in warm appreciation, swaying to the melodic performance"
        aud_neg = "empty audience"

    if is_beach:
        flight_title = "Continuous 10-second 360-degree coastal aerial camera trajectory:"
        stage_desc = "open-air seaside stage deck overlooking glistening ocean waves"
        venue_neg = "indoor stadium, stadium bowl, steel stadium roof, sports arena, arena bleachers, concrete stadium"
    elif is_outdoor:
        flight_title = "Continuous 10-second 360-degree open-air aerial camera trajectory:"
        stage_desc = "open-air concert stage pavilion under the evening sky"
        venue_neg = "indoor stadium, steel stadium roof, sports arena"
    else:
        flight_title = "Continuous 10-second 360-degree auditorium camera trajectory:"
        stage_desc = "illuminated concert hall stage deck"
        venue_neg = "sports stadium, soccer stadium, stadium bowl"

    chorus_desc = ", and 2-3 backing chorus vocalists swaying gracefully in rhythm at their microphones" if has_chorus else ""
    eff_inst = (instrument or "mic").lower()
    has_custom = eff_inst not in ("mic", "none", "vocal", "vocals")
    inst_desc = (
        f"playing {eff_inst.title()} with microphone strictly below chin level at chest height, lips gently closed, calm natural breathing"
        if has_custom
        else "holding microphone lowered strictly below chin at chest level with open space between chin and microphone, lips gently closed, calm natural breathing, subtle torso micro-sway and hand mudras (closed mouth, neutral expression, zero mouth movement, completely visible mouth and chin)"
    )

    prompt = (
        f"{flight_title} "
        f"(0.0s-2.5s) Centerstage living hold: locked front eye-level framing capturing lead singer {chars} on the {stage_desc}, {inst_desc}, flanked by live acoustic accompanists (violinist bowing, mridangam percussionist){chorus_desc}; "
        f"(2.5s-7.5s) 360-degree environment orbit: sweeps around stage left showing the singer and accompanists in side profile at face and instrument level, sweeps behind the stage capturing {aud_desc}, and continues across stage right showing accompanists and chorus in profile; "
        f"(7.5s-10.0s) Seamless return and frame-lock: dollies smoothly forward back toward centerstage at singer face level, zooming in so the final frame at 10.0s matches the initial frame at 0.0s, creating an infinite zero-distortion loop. "
        f"Authentic stage lighting, photorealistic cinema-grade 8k broadcast."
    )
    neg_prompt = f"jump cut, camera shake, erratic camera, microphone covering mouth, microphone blocking lips, mic covering face, microphone in front of lips, open mouth, mouth flapping, singing mouth, talking mouth, moving lips, parted lips, teeth showing, distorted faces, {aud_neg}, {venue_neg}"
    if has_chorus:
        neg_prompt += ", solo singer, missing chorus"
    return prompt, neg_prompt


__all__ = ["build_contextual_orbit_prompt"]
