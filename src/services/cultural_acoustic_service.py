"""Cultural Acoustic Engine & Hummable Ambient Soundscape Matrix.

Maps landscape archetypes, cultures, and environments to authentic traditional instruments,
hummable melodic motifs, Solfeggio frequencies (432Hz/528Hz), and resting heartbeat rhythms (52-60 BPM).
Guarantees stress relief, anxiety reduction, and sleep-inducing tranquility with zero generic guitar defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CulturalAcousticProfile:
    """Acoustic specification tailored to a specific cultural and environmental landscape."""
    culture_key: str
    lead_instrument: str
    secondary_textures: str
    scale_and_tuning: str
    rhythm_and_tempo: str
    emotional_purpose: str
    suno_tags: str
    suno_prompt: str


CULTURAL_PROFILES: dict[str, dict[str, str]] = {
    "desert": {
        "culture_key": "desert",
        "lead_instrument": "Airy Wooden Ney Flute in D-Minor",
        "secondary_textures": "Resonant acoustic Qanun, warm Oud harmonics, soft framed Daf heartbeat pulse, desert wind whisper",
        "scale_and_tuning": "432Hz Solfeggio tuning, Maqam Bayati / Hijaz modal resonance",
        "rhythm_and_tempo": "54 BPM gentle hypnotic pulse (resting heart rate entrainment)",
        "emotional_purpose": "Mystical serenity, vast tranquility, deep stress relief, mind-calming meditation",
        "suno_tags": "432hz, airy wooden ney flute, qanun, warm oud harmonics, soft daf pulse, velvet pads, desert ambient, hummable melody, deep stress relief, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Ambient Meditation]\n"
            "[Tempo: 54 BPM - Hypnotic Heartbeat Pulse]\n"
            "[Tuning: 432Hz Solfeggio Velvet Resonance]\n"
            "[Lead Melody: Mesmerizing Hummable Airy Wooden Ney Flute]\n"
            "[Accompaniment: Plucked Acoustic Qanun & Soft Oud Harmonics]\n"
            "[Rhythm: Gentle Framed Daf Drum Soft Heartbeat Tap]\n"
            "[Atmosphere: Warm Velvet Ambient Desert Wind Pads & Singing Bowls]\n"
            "[Emotion: Enchanting, Joyful, Anxiety-Reducing, Restful Sleep Drone]\n"
            "[Outro: Infinite Peaceful Desert Night Fade]"
        ),
    },
    "swiss_alps": {
        "culture_key": "swiss_alps",
        "lead_instrument": "Warm Alpine Wooden Flute in Major Pentatonic",
        "secondary_textures": "Acoustic Zither, gentle Cello harmonics, crystalline glass bells, distant alpine breeze",
        "scale_and_tuning": "528Hz Transformation & 432Hz Harmonic Solfeggio",
        "rhythm_and_tempo": "56 BPM slow pastoral breathing rhythm",
        "emotional_purpose": "Soaring wonder, joyous pastoral peace, uplifting lightness, anxiety relief",
        "suno_tags": "528hz, alpine wooden flute, acoustic zither, cello harmonics, crystalline bells, velvet pads, pastoral ambient, joyful hummable melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Pastoral Meditation]\n"
            "[Tempo: 56 BPM - Slow Breathing Cadence]\n"
            "[Tuning: 528Hz Love Frequency & 432Hz Velvet Bed]\n"
            "[Lead Melody: Joyous Hummable Alpine Wooden Flute Solos]\n"
            "[Accompaniment: Plucked Acoustic Zither & Resonant Cello Drone]\n"
            "[Texture: Pure Crystalline Glass Bells & Distant Wind Chimes]\n"
            "[Atmosphere: Soaring Velvet Ambient String Pads & Mountain Echo]\n"
            "[Emotion: Enlightened, Uplifting, Anti-Depression, Restful Serenity]\n"
            "[Outro: Soft Glacial Horizon Lullaby Fade]"
        ),
    },
    "zen": {
        "culture_key": "zen",
        "lead_instrument": "Japanese Bamboo Shakuhachi Flute",
        "secondary_textures": "Plucked Koto, resonant temple bronze bell, crystal singing bowl, serene water drops",
        "scale_and_tuning": "432Hz In-sen & Yo pentatonic meditative tuning",
        "rhythm_and_tempo": "50 BPM ultra-slow meditative breathing",
        "emotional_purpose": "Profound inner stillness, transcendent clarity, deep anxiety melting, zen sleep",
        "suno_tags": "432hz, japanese bamboo shakuhachi flute, koto, bronze temple bell, singing bowls, water drops, zen ambient, hummable serene melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Zen Soundbath]\n"
            "[Tempo: 50 BPM - Meditative Stillness]\n"
            "[Tuning: 432Hz Sacred Lotus Resonance]\n"
            "[Lead Melody: Hummable Bamboo Shakuhachi Flute Melodic Motif]\n"
            "[Accompaniment: Plucked Koto Harmonics & Soft Bronze Temple Bell]\n"
            "[Texture: Singing Bowls & Gentle Water Droplet Ripples]\n"
            "[Atmosphere: Transcendent Velvet Ambient Pads & White Sage Mist]\n"
            "[Emotion: Enlightened, Peaceful, Deep Stress Melt, Restorative Sleep]\n"
            "[Outro: Infinite Dissolving Stillness]"
        ),
    },
    "himalayas": {
        "culture_key": "himalayas",
        "lead_instrument": "Deep Resonant Bansuri Flute in E-Minor / Major",
        "secondary_textures": "Tibetan singing bowls, low overtone cello drone, brass monastery bell, resonant handpan",
        "scale_and_tuning": "432Hz Solfeggio Grounding Frequency",
        "rhythm_and_tempo": "52 BPM meditative heart pulse",
        "emotional_purpose": "Spiritual elevation, grounding calm, releasing worry and tension, profound sleep",
        "suno_tags": "432hz, bansuri flute, tibetan singing bowls, overtone cello drone, handpan, himalayan ambient, hummable spiritual melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Himalayan Sanctuary]\n"
            "[Tempo: 52 BPM - Heartbeat Entrainment]\n"
            "[Tuning: 432Hz Deep Solfeggio Resonance]\n"
            "[Lead Melody: Mesmerizing Hummable Bansuri Flute Solo]\n"
            "[Accompaniment: Resonant Tibetan Singing Bowls & Overtone Cello Drone]\n"
            "[Percussion: Soft Handpan Pentatonic Note Taps]\n"
            "[Atmosphere: Sacred Mountain Mist Velvet Pads]\n"
            "[Emotion: Enlightened, Serene, Anxiety-Relief, Deep Sleep Entrainment]\n"
            "[Outro: Endless Mountain Echo Fade]"
        ),
    },
    "ocean": {
        "culture_key": "ocean",
        "lead_instrument": "Melodic Resonant Handpan in D-Minor / Major Pentatonic",
        "secondary_textures": "Acoustic Kalimba, warm Marimba / Vibraphone, velvet Rhodes electric piano, ocean surf foley",
        "scale_and_tuning": "432Hz Harmonic Water Resonance",
        "rhythm_and_tempo": "58 BPM swaying oceanic lullaby rhythm",
        "emotional_purpose": "Sun-kissed joy, depression release, anxiety melting, calming shoreline sleep",
        "suno_tags": "432hz, melodic handpan, acoustic kalimba, marimba, velvet rhodes pads, ocean surf, coastal ambient, hummable joyful melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Coastal Sanctuary]\n"
            "[Tempo: 58 BPM - Oceanic Sway Cadence]\n"
            "[Tuning: 432Hz Harmonic Water Solfeggio]\n"
            "[Lead Melody: Joyous Hummable Melodic Handpan Motif]\n"
            "[Accompaniment: Plucked Acoustic Kalimba & Soft Wooden Marimba]\n"
            "[Texture: Velvet Rhodes Electric Piano & Rolling Ocean Wave Foley]\n"
            "[Atmosphere: Warm Tropical Sunbeam Velvet Pads]\n"
            "[Emotion: Joyful, Lovely, Anxiety-Melting, Healing Sleep Soundscape]\n"
            "[Outro: Gentle Shoreline Tide Fade]"
        ),
    },
    "forest": {
        "culture_key": "forest",
        "lead_instrument": "Native American Cedar Flute",
        "secondary_textures": "Celtic Harp, singing crystal chimes, bubbling brook foley, morning canopy birdsong",
        "scale_and_tuning": "432Hz Earth Grounding Frequency",
        "rhythm_and_tempo": "54 BPM tranquil river flow cadence",
        "emotional_purpose": "Restorative vitality, mental clarity, dissolving mental fatigue and stress",
        "suno_tags": "432hz, native american cedar flute, celtic harp, crystal chimes, stream foley, forest ambient, hummable serene melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Ancient Forest Glade]\n"
            "[Tempo: 54 BPM - Flowing Stream Pulse]\n"
            "[Tuning: 432Hz Natural Earth Resonance]\n"
            "[Lead Melody: Serene Hummable Cedar Flute Melody]\n"
            "[Accompaniment: Flowing Celtic Harp Arpeggios & Cello Harmonics]\n"
            "[Texture: Crystal Chimes, Babbling Brook & Morning Canopy Foley]\n"
            "[Atmosphere: Komorebi Sunbeam Velvet Pads]\n"
            "[Emotion: Lovely, Stress-Relieving, Grounding, Healing Nature Sleep]\n"
            "[Outro: Whispering Canopy Leaves Fade]"
        ),
    },
    "hearth": {
        "culture_key": "hearth",
        "lead_instrument": "Intimate Soft Felted Upright Piano",
        "secondary_textures": "Warm Solo Cello, crackling fireplace embers foley, soft celesta glass bells, warm sub-bass",
        "scale_and_tuning": "432Hz Warm Hearth Resonance",
        "rhythm_and_tempo": "52 BPM soothing lullaby tempo",
        "emotional_purpose": "Profound security, emotional comfort, soothing depression, deeply restorative sleep",
        "suno_tags": "432hz, soft felted piano, warm solo cello, celesta bells, fireplace crackle, cozy ambient, hummable lullaby melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Cozy Hearth Sanctuary]\n"
            "[Tempo: 52 BPM - Gentle Lullaby Pulse]\n"
            "[Tuning: 432Hz Warm Harmonic Glow]\n"
            "[Lead Melody: Intimate Hummable Felted Piano Lullaby Melody]\n"
            "[Accompaniment: Deep Warm Solo Cello & Soft Celesta Bells]\n"
            "[Texture: Authentic Cozy Crackling Fireplace Embers]\n"
            "[Atmosphere: Velvet Ambient Wool Blanket Warm Drone]\n"
            "[Emotion: Loving, Deeply Comforting, Anxiety-Free, Unbreakable Sleep]\n"
            "[Outro: Glowing Hearth Embers Fade]"
        ),
    },
    "rain": {
        "culture_key": "rain",
        "lead_instrument": "Warm Singing Crystal Handpan",
        "secondary_textures": "Steady binaural raindrops on glass, soft bamboo chimes, warm cello harmonics",
        "scale_and_tuning": "432Hz Delta Sleep Frequency",
        "rhythm_and_tempo": "54 BPM relaxing rainfall pulse",
        "emotional_purpose": "Hypnotic ASMR sleep, anxiety dispersion, cozy reading focus, deep rest",
        "suno_tags": "432hz, singing crystal handpan, bamboo chimes, cello harmonics, binaural rain, rain ambient, hummable calm melody, -21 LUFS",
        "suno_prompt": (
            "[Instrumental Rain Sanctuary]\n"
            "[Tempo: 54 BPM - Steady Rain Pitter-Patter]\n"
            "[Tuning: 432Hz ASMR Delta Bed]\n"
            "[Lead Melody: Hypnotic Hummable Crystal Handpan Motif]\n"
            "[Accompaniment: Soft Bamboo Chimes & Cello Harmonics]\n"
            "[Texture: Steady Windowpane Rain ASMR & Gentle River Foley]\n"
            "[Atmosphere: Cozy Velvet Ambient Grey-Sky Pads]\n"
            "[Emotion: Deeply Calming, Stress-Melt, Restful Sleep Entrainment]\n"
            "[Outro: Gentle Rain Falling to Silence]"
        ),
    },
}


def resolve_cultural_acoustic_profile(
    archetype: str = "",
    sub_genre: str = "",
    title: str = "",
    tags: str = "",
) -> CulturalAcousticProfile:
    """Resolve culturally authentic instruments and hummable melody specifications for any relax scene."""
    combo = f"{archetype} {sub_genre} {title} {tags}".lower()

    if any(k in combo for k in ["desert", "rub' al khali", "dune", "oasis", "sahara", "glamping", "pavilion", "bedouin"]):
        key = "desert"
    elif any(k in combo for k in ["swiss", "alps", "dolomites", "mountain", "lauterbrunnen", "matterhorn", "pastoral", "valley"]):
        key = "swiss_alps"
    elif any(k in combo for k in ["zen", "lotus", "shakuhachi", "kyoto", "temple", "bamboo", "japanese"]):
        key = "zen"
    elif any(k in combo for k in ["himalaya", "tibet", "ladakh", "monastery", "bansuri"]):
        key = "himalayas"
    elif any(k in combo for k in ["ocean", "beach", "coastal", "lagoon", "maldives", "amalfi", "cabana", "sea", "wave", "island"]):
        key = "ocean"
    elif any(k in combo for k in ["rain", "storm", "droplet", "river asmr", "umbrella"]):
        key = "rain"
    elif any(k in combo for k in ["hearth", "fireplace", "cabin", "blizzard", "winter", "snow", "cozy", "shelter"]):
        key = "hearth"
    elif any(k in combo for k in ["forest", "woodland", "trees", "komorebi", "river glade", "redwood"]):
        key = "forest"
    else:
        # Default for universal nature and relaxation: harmonious handpan & flute
        key = "ocean" if "water" in combo else "swiss_alps"

    raw = CULTURAL_PROFILES[key]
    return CulturalAcousticProfile(
        culture_key=raw["culture_key"],
        lead_instrument=raw["lead_instrument"],
        secondary_textures=raw["secondary_textures"],
        scale_and_tuning=raw["scale_and_tuning"],
        rhythm_and_tempo=raw["rhythm_and_tempo"],
        emotional_purpose=raw["emotional_purpose"],
        suno_tags=raw["suno_tags"],
        suno_prompt=raw["suno_prompt"],
    )
