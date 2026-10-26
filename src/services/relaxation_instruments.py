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
    """Stochastically select diverse, complementary soothing instruments suited to the visual scene."""
    ctx_lower = setting_context.lower()

    if any(k in ctx_lower for k in ("beach", "ocean", "surf", "coast", "pool", "terrace", "pergola", "cabana")):
        lead_candidates = [
            "classical Spanish nylon guitar", "warm Rhodes electric piano", "Celtic acoustic harp",
            "resonant handpan in major pentatonic (pantam / hang drum)", "Middle Eastern wooden ney",
        ]
        acc_candidates = ["warm acoustic cello", "gentle viola", "soft tuned brass wind chimes", "warm acoustic vibraphone", "upright acoustic bass drone"]
        ambient_texture = "warm analog velvet synth pads"
    elif any(k in ctx_lower for k in ("alps", "swiss", "mountain", "valley", "pastoral", "meadow", "dolomite")):
        lead_candidates = [
            "breathy alpine wooden flute", "wooden pan flute", "Native American cedar flute",
            "Celtic acoustic harp", "intimate felted upright piano",
        ]
        acc_candidates = ["warm acoustic cello", "gentle viola", "resonant handpan in major pentatonic (pantam / hang drum)", "crystal singing bowls", "acoustic zither"]
        ambient_texture = "432Hz Solfeggio velvet drone bed"
    elif any(k in ctx_lower for k in ("desert", "dune", "glamping", "bedouin", "pavilion", "sahara")):
        lead_candidates = [
            "Persian santur", "Middle Eastern wooden ney", "Indian bansuri bamboo flute",
            "classical Spanish nylon guitar", "Indian sarod",
        ]
        acc_candidates = ["warm acoustic cello", "esraj", "dilruba", "Tibetan singing bowls", "bronze temple singing bell"]
        ambient_texture = "warm analog velvet synth pads"
    elif any(k in ctx_lower for k in ("forest", "woodland", "stream", "moss", "river", "komorebi")):
        lead_candidates = [
            "wooden pan flute", "Native American cedar flute", "clay ocarina",
            "Celtic acoustic harp", "African kalimba (thumb piano)",
        ]
        acc_candidates = ["soft wooden marimba", "resonant handpan in major pentatonic (pantam / hang drum)", "warm acoustic cello", "gentle viola"]
        ambient_texture = "432Hz Solfeggio velvet drone bed"
    elif any(k in ctx_lower for k in ("hearth", "cabin", "fireplace", "blizzard", "winter", "snow")):
        lead_candidates = [
            "intimate felted upright piano", "warm acoustic cello", "classical Spanish nylon guitar",
            "warm Rhodes electric piano", "Celtic acoustic harp",
        ]
        acc_candidates = ["muted string quartet harmonics", "gentle viola", "upright acoustic bass drone", "warm acoustic vibraphone"]
        ambient_texture = "warm analog velvet synth pads"
    elif any(k in ctx_lower for k in ("zen", "lotus", "temple", "bamboo", "kyoto")):
        lead_candidates = [
            "Japanese shakuhachi bamboo flute", "Japanese koto", "Chinese guzheng",
            "Tibetan singing bowls", "Indian bansuri bamboo flute",
        ]
        acc_candidates = ["bronze temple singing bell", "crystal singing bowls", "warm acoustic cello", "gentle celesta"]
        ambient_texture = "432Hz Solfeggio velvet drone bed"
    else:
        lead_pools = [GENTLE_WINDS, PLUCKED_STRINGS, KEYS_AND_PADS, BELLS_AND_RESONATORS]
        chosen_lead_pool = random.choice(lead_pools)
        lead_candidates = chosen_lead_pool
        acc_candidates = [p for p in PLUCKED_STRINGS + BOWED_STRINGS + BELLS_AND_RESONATORS if p not in lead_candidates]
        ambient_texture = random.choice(KEYS_AND_PADS)

    lead = random.choice(lead_candidates)
    accompaniment = random.choice([a for a in acc_candidates if a != lead])

    eff_bpm = tempo_bpm or random.choice([48, 50, 52, 54, 56])
    tuning = random.choice(["432Hz Solfeggio Harmonic Resonance", "528Hz Love & Transformation Frequency", "432Hz Deep Grounding Bed"])

    clean_lead = lead.split("(")[0].replace("in major pentatonic", "").strip()
    clean_acc = accompaniment.split("(")[0].replace("in major pentatonic", "").strip()
    clean_tex = ambient_texture.split("(")[0].replace("in major pentatonic", "").strip()

    suno_tags = (
        f"432hz, instrumental relaxation, {clean_lead.lower()}, {clean_acc.lower()}, "
        f"{clean_tex.lower()}, peaceful soundscape, zero drums, zero vocals, -21 LUFS"
    )

    ctx_line = f"[Scene Context: {setting_context}]\n" if setting_context else ""
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
LLM DIRECTIVE FOR RELAXATION SCENE-TO-MUSIC HARMONY & FIXED TRIPOD:
======================================================================
1. SCENE-MATCHED RELAXING MUSIC DIRECTIVES (SUIT THE VISUAL IMAGE):
   - PURE RELAXATION SOUND: ZERO BACKGROUND SONG, ZERO VOCALS, ZERO DRUMS.
   - The LLM knows it is directing a relaxing video production.
   - STOCHASTIC INSTRUMENT DIVERSITY: Gemini must NEVER hardcode the same instruments every time.
     It must dynamically pick soothing instruments that SUIT AND COMPLEMENT THE EXACT VISUAL IMAGE:
     * Beach / Luxury Terrace / Pool / Pergola: Warm acoustic Spanish nylon guitar, Rhodes electric piano, gentle ocean swell ambient pads, rolling surf foley, 432Hz warmth, 48-54 BPM, zero drums, zero vocals.
     * Swiss Alps / Mountain Valleys / Meadows: Breathy alpine wooden flute, warm resonant cello drone, crystal stream chimes, mountain breeze, Celtic harp, 432Hz Solfeggio, resting 48-52 BPM.
     * Desert Sanctuaries / Dunes / Pavilion: Meditative Persian santur / acoustic oud whispers, ethereal wooden ney flute, warm desert wind drone, starlit serenity, bansuri, 48-50 BPM.
     * Forest / Streams / Woodlands: Wooden pan flute, Native American cedar flute, acoustic harp, soft marimba, singing bowls, babbling brook foley.
     * Cozy Cabin / Hearth / Fireplace: felted upright piano, cello harmonics, crackling hearth embers foley, intimate fireside warmth.
   - Populating "audio_master.suno_prompt" is MANDATORY. Do NOT leave it empty:
     [Instrumental Ambient Meditation]
     [Scene Context: <specific visual setting matching image prompt>]
     [Tempo: 48-54 BPM - Resting Heartbeat Pulse]
     [Tuning: 432Hz Solfeggio Velvet Harmony]
     [Lead Melody: Hypnotic, slow, tranquil phrasing on <Soothing Lead Instrument suited to scene>]
     [Accompaniment: Soft acoustic harmonies on <Second Instrument suited to scene>]
     [Atmosphere: <Ambient Texture suited to scene>, warm velvet pads, natural foley, long smooth reverb decays]
     [Acoustic Direction: Studio master recording, zero harsh percussion, zero brass, zero vocals, zero drums]
     [Emotion: Deep tranquil calm, anxiety reduction, effortless meditation and sleep induction]
     [Outro: Lingering resonant acoustic dissolve]

2. STRICT FIXED LOCKED TRIPOD MANDATE FOR RELAXATION MOTION MODELS:
   - For relaxation format productions, Gemini MUST direct all motion models that the shot is a
     STRICTLY FIXED LOCKED TRIPOD and NOT camera angles or movements.
   - Prohibit all pans, tilts, zooms, sweeps, aerial tracking, and angle shifts. The camera never moves.
   - In "motion_prompt" and all video models ("wan_2_1", "kling_v3_4k", "kling_v1_6_pro", "local_drone"):
     * POSITIVE PROMPT: "Cinemagraph living wallpaper. Strictly 100% locked stationary camera on a heavy fixed tripod with zero camera movement, zero camera angles, zero pan, zero tilt, zero zoom, zero camera drift. Entire frame, landscape topography, and architecture remain 100% frozen, solid, and motionless. Only subtle organic living motion in the scene: [gentle water ripples / soft waves lapping / breeze swaying distant foliage / embers glowing]."
     * NEGATIVE PROMPT: "camera movement, camera motion, camera angles, camera pan, panning, camera tilt, tilting, camera zoom, zooming, camera rotation, dolly, drone, tracking shot, flythrough, handheld camera, camera drift, jitter, shaky camera, moving perspective, perspective shift, morphing architecture, changing furniture".
"""
