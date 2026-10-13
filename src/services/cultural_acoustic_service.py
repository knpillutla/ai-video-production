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
) -> CulturalAcousticProfile:
    """Resolve culturally authentic instruments and hummable melody specifications for any relax scene."""
    combo = f"{archetype} {sub_genre} {title} {tags}".lower()

    if any(k in combo for k in ["party", "beach club", "cocktail", "upbeat", "energetic", "summer beats"]):
        key = "party_lounge"
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
    elif any(k in combo for k in ["rain", "storm", "droplet", "river asmr", "umbrella"]):
        key = "rain"
    elif any(k in combo for k in ["hearth", "fireplace", "cabin", "blizzard", "winter", "snow", "cozy", "shelter"]):
        key = "hearth"
    elif any(k in combo for k in ["forest", "woodland", "trees", "komorebi", "river glade", "redwood"]):
        key = "forest"
    elif any(k in combo for k in ["ocean", "beach", "coastal", "lagoon", "maldives", "amalfi", "cabana", "sea", "wave", "island"]):
        key = "ocean"
    else:
        key = "ocean" if "water" in combo else "swiss_alps"

    raw = CULTURAL_PROFILES.get(key, CULTURAL_PROFILES["swiss_alps"])
    h = int(hashlib.md5(combo.encode()).hexdigest(), 16)
    motifs = MOTIF_VARIATIONS.get(key, [])
    selected_motif = motifs[h % len(motifs)] if motifs else ""

    suno_prompt = raw["suno_prompt"]
    if selected_motif and "[Lead Melody: " in suno_prompt:
        suno_prompt = suno_prompt.replace(
            "[Lead Melody: ",
            f"[Lead Motif: {selected_motif}]\n[Lead Melody: "
        )

    suno_tags = raw["suno_tags"]

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
        lead_instrument=raw["lead_instrument"],
        secondary_textures=raw["secondary_textures"],
        scale_and_tuning=raw["scale_and_tuning"],
        rhythm_and_tempo=raw["rhythm_and_tempo"],
        emotional_purpose=raw["emotional_purpose"],
        suno_tags=suno_tags,
        suno_prompt=suno_prompt,
    )


__all__ = ["CulturalAcousticProfile", "resolve_cultural_acoustic_profile"]
