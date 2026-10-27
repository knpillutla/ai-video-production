"""Cultural Acoustic Engine & Hummable Ambient Soundscape Resolver.

Maps landscape archetypes, cultures, environments, and weather variants to authentic
traditional instruments, hummable melodic motifs, Solfeggio frequencies (432Hz/528Hz),
and resting heartbeat rhythms (52-60 BPM) or chic modern lounge cadences (85 BPM).
Guarantees stress relief, anxiety reduction, and sleep-inducing tranquility with zero generic guitar defaults.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from src.services.cultural_acoustic_profiles import (
    CulturalAcousticProfile,
    CULTURAL_PROFILES,
    MOTIF_VARIATIONS,
    WEATHER_ACOUSTIC_MODIFIERS,
)


def resolve_cultural_acoustic_profile(
    archetype: str = "",
    sub_genre: str = "",
    title: str = "",
    tags: str = "",
    weather: Optional[str] = "normal",
    randomize: bool = False,
    visual_prompt: Optional[str] = None,
) -> CulturalAcousticProfile:
    """Resolve culturally authentic instruments and hummable melody specifications for any relax scene."""
    combo = f"{archetype} {sub_genre} {title} {tags} {visual_prompt or ''}".lower()

    from src.services.national_acoustic_profiles import resolve_national_acoustic_profile
    national_profile = resolve_national_acoustic_profile(combo)
    if national_profile:
        return national_profile

    eff_w = (weather or "").lower().strip()
    is_rain = eff_w in ("rain", "storm", "downpour") or any(k in combo for k in ["rain", "storm", "downpour", "droplet", "monsoon", "river asmr", "umbrella", "relax/rain"])

    if any(k in combo for k in ["party", "beach club", "cocktail", "upbeat", "energetic", "summer beats"]):
        key = "party_lounge"
    elif is_rain:
        key = "rain"
    elif any(k in combo for k in ["hearth", "fireplace", "blizzard", "winter snow", "cozy cabin"]):
        key = "hearth"
    elif any(k in combo for k in ["pool_terrace", "beach_lounge", "chillout", "lounge", "infinity pool", "villa terrace"]):
        key = "beach_lounge"
    elif any(k in combo for k in ["waterfall", "cataract", "cascade"]):
        key = "waterfall"
    elif any(k in combo for k in ["desert", "rub' al khali", "dune", "oasis", "sahara", "glamping", "pavilion", "bedouin"]):
        key = "desert"
    elif any(k in combo for k in ["swiss", "alps", "dolomites", "mountain", "lauterbrunnen", "matterhorn", "pastoral", "valley"]):
        key = "swiss_alps"
    elif any(k in combo for k in ["zen", "lotus", "shakuhachi", "kyoto", "temple", "bamboo", "japanese"]):
        key = "zen"
    elif any(k in combo for k in ["himalaya", "tibet", "ladakh", "monastery", "bansuri"]):
        key = "himalayas"
    elif any(k in combo for k in ["forest", "woodland", "trees", "komorebi", "river glade", "redwood"]):
        key = "forest"
    elif any(k in combo for k in ["ocean", "beach", "coastal", "lagoon", "maldives", "amalfi", "cabana", "sea", "wave", "island"]):
        key = "ocean"
    else:
        key = "ocean" if "water" in combo else "swiss_alps"

    raw = CULTURAL_PROFILES.get(key, CULTURAL_PROFILES["swiss_alps"])

    if randomize and key != "party_lounge":
        from src.services.relaxation_instruments import get_random_soothing_instrument_set
        palette = get_random_soothing_instrument_set(setting_context=combo)
        lead_instrument = palette.lead_instrument
        secondary_textures = f"{palette.accompaniment}, {palette.ambient_texture}"
        suno_prompt = palette.suno_prompt
        suno_tags = palette.suno_tags
    else:
        lead_instrument = raw["lead_instrument"]
        secondary_textures = raw["secondary_textures"]
        suno_prompt = raw["suno_prompt"]
        suno_tags = raw["suno_tags"]

    h = int(hashlib.md5(combo.encode()).hexdigest(), 16)
    motifs = MOTIF_VARIATIONS.get(key, [])
    selected_motif = motifs[h % len(motifs)] if motifs else ""

    if selected_motif and "[Lead Melody: " in suno_prompt:
        suno_prompt = suno_prompt.replace(
            "[Lead Melody: ",
            f"[Lead Motif: {selected_motif}]\n[Lead Melody: "
        )

    # Weather acoustic layering
    w_key = (weather or "normal").lower().strip()
    if w_key in WEATHER_ACOUSTIC_MODIFIERS and w_key != "normal":
        w_mod = WEATHER_ACOUSTIC_MODIFIERS[w_key]
        suno_tags = f"{suno_tags}, {w_mod['tag_addon']}"
        if "[Outro: " in suno_prompt:
            suno_prompt = suno_prompt.replace(
                "[Outro: ",
                f"{w_mod['prompt_layer']}\n[Outro: "
            )
        else:
            suno_prompt = f"{suno_prompt}\n{w_mod['prompt_layer']}"

    return CulturalAcousticProfile(
        culture_key=raw["culture_key"],
        lead_instrument=lead_instrument,
        secondary_textures=secondary_textures,
        scale_and_tuning=raw["scale_and_tuning"],
        rhythm_and_tempo=raw["rhythm_and_tempo"],
        emotional_purpose=raw["emotional_purpose"],
        suno_tags=suno_tags,
        suno_prompt=suno_prompt,
    )


__all__ = ["CulturalAcousticProfile", "resolve_cultural_acoustic_profile"]
