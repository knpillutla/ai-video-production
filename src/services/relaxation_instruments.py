"""Dynamic Soothing Instrument Diversity & Suno Relaxation Prompting Engine.

Provides stochastic instrument curation and rich directorial instructions
for Gemini and Suno v3.5 to produce soothing, non-repetitive relaxation soundscapes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


PLUCKED_STRINGS: List[str] = [
    "Celtic acoustic harp",
    "Japanese koto",
    "Chinese guzheng",
    "classical Spanish nylon guitar",
    "Persian santur",
    "Indian sarod",
    "African kalimba (thumb piano)",
    "resonant mbira",
    "acoustic zither",
    "renaissance lute",
]

BOWED_STRINGS: List[str] = [
    "warm acoustic cello",
    "gentle viola",
    "Chinese erhu",
    "Indian dilruba",
    "esraj",
    "upright acoustic bass drone",
    "muted string quartet harmonics",
]

GENTLE_WINDS: List[str] = [
    "Japanese shakuhachi bamboo flute",
    "Indian bansuri bamboo flute",
    "Native American cedar flute",
    "wooden pan flute",
    "clay ocarina",
    "Middle Eastern wooden ney",
    "warm muted clarinet",
    "breathy alpine wooden flute",
]

BELLS_AND_RESONATORS: List[str] = [
    "Tibetan singing bowls",
    "crystal singing bowls",
    "resonant handpan in major pentatonic (pantam / hang drum)",
    "soft tuned brass wind chimes",
    "gentle celesta",
    "warm acoustic vibraphone",
    "soft wooden marimba",
    "bronze temple singing bell",
]

KEYS_AND_PADS: List[str] = [
    "intimate felted upright piano",
    "warm Rhodes electric piano",
    "warm analog velvet synth pads",
    "432Hz Solfeggio velvet drone bed",
    "528Hz harmonic resonance",
    "gentle ethereal choral hum",
    "6Hz theta-wave binaural soundbed",
]


@dataclass(frozen=True)
class SoothingInstrumentPalette:
    """Stochastically curated instrument trio for a relaxation production."""
    lead_instrument: str
    accompaniment: str
    ambient_texture: str
    tempo_bpm: int
    tuning: str
    suno_tags: str
    suno_prompt: str


def get_random_soothing_instrument_set(
    setting_context: str = "",
    tempo_bpm: Optional[int] = None,
) -> SoothingInstrumentPalette:
    """Stochastically select diverse, complementary soothing instruments for pure relaxation."""
    lead_pools = [GENTLE_WINDS, PLUCKED_STRINGS, KEYS_AND_PADS, BELLS_AND_RESONATORS]
    chosen_lead_pool = random.choice(lead_pools)
    lead = random.choice(chosen_lead_pool)

    remaining_pools = [p for p in lead_pools if p is not chosen_lead_pool] + [BOWED_STRINGS]
    chosen_acc_pool = random.choice(remaining_pools)
    accompaniment = random.choice(chosen_acc_pool)

    ambient_texture = random.choice(KEYS_AND_PADS if chosen_lead_pool != KEYS_AND_PADS else BELLS_AND_RESONATORS)

    eff_bpm = tempo_bpm or random.choice([48, 50, 52, 54, 56])
    tuning = random.choice(["432Hz Solfeggio Harmonic Resonance", "528Hz Love & Transformation Frequency", "432Hz Deep Grounding Bed"])

    clean_lead = lead.split("(")[0].replace("in major pentatonic", "").strip()
    clean_acc = accompaniment.split("(")[0].replace("in major pentatonic", "").strip()
    clean_tex = ambient_texture.split("(")[0].replace("in major pentatonic", "").strip()

    suno_tags = (
        f"432hz, instrumental relaxation, {clean_lead.lower()}, {clean_acc.lower()}, "
        f"{clean_tex.lower()}, peaceful soundscape, zero drums, zero vocals, -21 LUFS"
    )

    ctx_line = f"[Setting: {setting_context}]\n" if setting_context else ""
    suno_prompt = (
        f"[Instrumental Ambient Meditation]\n"
        f"{ctx_line}"
        f"[Tempo: {eff_bpm} BPM - Resting Heartbeat Pulse]\n"
        f"[Tuning: {tuning}]\n"
        f"[Lead Melody: Hypnotic, slow, tranquil phrasing on {lead}]\n"
        f"[Accompaniment: Gentle, spacious acoustic accompaniment on {accompaniment}]\n"
        f"[Atmosphere: {ambient_texture}, warm velvet ambient pads, long smooth reverb decays]\n"
        f"[Acoustic Direction: Studio master recording, zero harsh percussion, zero brass, zero vocals, zero hiss]\n"
        f"[Emotion: Deep tranquil peace, anxiety reduction, restorative sleep induction]\n"
        f"[Outro: Lingering resonant acoustic dissolve]"
    )

    return SoothingInstrumentPalette(
        lead_instrument=lead,
        accompaniment=accompaniment,
        ambient_texture=ambient_texture,
        tempo_bpm=eff_bpm,
        tuning=tuning,
        suno_tags=suno_tags,
        suno_prompt=suno_prompt,
    )


def get_llm_soothing_music_guidance() -> str:
    """Return authoritative directorial instructions for Gemini to give directions to Suno."""
    return """
======================================================================
LLM DIRECTIVE FOR SOOTHING RELAXATION MUSIC & SUNO V3.5 DIRECTION:
======================================================================
1. PURE RELAXATION SOUND (ZERO BACKGROUND SONG / ZERO VOCALS):
   - Relaxation format productions have NO background vocal song or pop track.
   - It is 100% PURE SOOTHING RELAXATION SOUND: a meditative acoustic soundscape and natural foley.
   - Set "vocal_gender": "none", "singing_lyrics_spec": "".

2. STOCHASTIC INSTRUMENT DIVERSITY (STRICT BAN ON HARDCODED REPETITION):
   - DO NOT hardcode or repeat the same instruments across productions.
   - For every execution, Gemini MUST pick up soothing instruments randomly from diverse organic palettes:
     * Plucked Strings: Celtic harp, koto, guzheng, nylon guitar, santur, sarod, kalimba, mbira, zither, lute.
     * Bowed Strings: warm cello harmonics, gentle viola, erhu, dilruba, esraj, upright acoustic bass drone.
     * Gentle Winds: shakuhachi, bansuri bamboo flute, Native American cedar flute, pan flute, ocarina, wooden ney.
     * Resonators & Bells: Tibetan singing bowls, crystal singing bowls, tuned handpan (pantam / hang drum), wind chimes, celesta, vibraphone, marimba.
     * Keys & Beds: felted upright piano, Rhodes electric piano, warm analog velvet pads, 432Hz/528Hz Solfeggio drone.

3. EXPLICIT SOOTHING DIRECTIONS TO SUNO IN "suno_prompt" & "suno_musical_tags":
   - In "audio_master.suno_prompt", format structured directorial blocks:
     [Instrumental Ambient Meditation]
     [Tempo: 48-54 BPM - Resting Heartbeat Pulse]
     [Tuning: 432Hz Solfeggio Harmonic Bed]
     [Lead Melody: Hypnotic, gentle, spacious melody on <Randomly Chosen Soothing Lead Instrument>]
     [Accompaniment: Plucked or bowed acoustic harmonies on <Randomly Chosen Second Instrument>]
     [Atmosphere: <Randomly Chosen Resonator/Pad>, warm velvet pads, long smooth reverb, studio master, zero hiss]
     [Negative Constraints: Zero vocals, zero drums, zero percussion, zero synth screech, zero brass]
     [Emotion: Deep tranquil calm, anxiety dissolving, peaceful sleep]
     [Outro: Soft lingering resonance dissolve]
   - In "audio_master.suno_musical_tags", output clean tags:
     "432hz, pure instrumental relaxation, <lead instrument>, <accompaniment>, <texture>, peaceful soundscape, zero drums, zero vocals, studio master, -21 LUFS".
"""
