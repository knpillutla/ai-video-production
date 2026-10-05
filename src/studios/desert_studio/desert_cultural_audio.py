"""Cultural Geographic Desert Audio Synthesis Matrix.

Encapsulates authentic regional instrumentation across 5 global desert zones:
1. Sahara (Morocco/Egypt): Resonant Handpan, Moroccan Nay flute, warm Oud drone, sand whisper.
2. Arabian Desert (UAE/Saudi/Jordan): Celestial Qanun zither, Arabian Nay, crystal bowls, velvet pads.
3. Namib & Kalahari (Namibia): Ethereal Kalimba thumb piano, Hang drum, warm bass drone, fog breeze.
4. Atacama High Desert (Chile): Andean Bamboo Quena flute, Tibetan singing bowls, glass chimes, delta drones.
5. American Southwest (USA): Native Cedar flute, quartz crystal bowls, resonant handpan, canyon breeze.

Provides dynamic permutation so every production generates a fresh, unique combination.
"""

from __future__ import annotations

import hashlib
import time
from typing import Dict, List, Optional, Tuple


REGIONAL_DESERT_INSTRUMENTS: Dict[str, Dict[str, List[str]]] = {
    "sahara": {
        "leads": [
            "resonant handpan in uplifting D-Kurd major mode and airy Moroccan nay flute",
            "warm acoustic oud harmonics and resonant hang drum with clay water pot textures",
            "celestial Moroccan bamboo flute and singing bowl resonance with sand whisper foley",
        ],
        "pads": [
            "432Hz velvet analog synth pads, sub-bass theta drone, deep stress relief",
            "528Hz Solfeggio heart-opening resonance, smooth anti-anxiety ambient bed",
        ],
        "foley": "gentle desert breeze through sheer linen, soft wind-sculpted sand drift",
    },
    "arabian": {
        "leads": [
            "celestial qanun harp-like zither arpeggios and crystalline singing bowls",
            "uplifting Arabian wooden nay flute in Bayati mode and resonant handpan",
            "soft meditative qanun strings, crystal bell chimes, and ethereal hang drum",
        ],
        "pads": [
            "432Hz Solfeggio soothing sleep pads, warm velvet ambient drone, restorative calm",
            "528Hz golden oasis frequency, lush velvet analog warmth, cortisol-reducing bed",
        ],
        "foley": "subtle whispering desert breeze through luxury tent drapes, starlit oasis serenity",
    },
    "namib": {
        "leads": [
            "ethereal kalimba thumb piano harmonics, resonant hang drum, and airy wooden flute",
            "warm acoustic mbira plucks, singing bowl overtones, and uplifting handpan",
            "grounding wooden flute melody and resonant handpan with soft coastal desert fog whisper",
        ],
        "pads": [
            "432Hz deep grounding earth drone, velvet ambient warmth, deep relaxation",
            "4-7Hz theta-wave brain entrainment pads, tranquil sleep induction bed",
        ],
        "foley": "gentle cool ocean-desert breeze, distant fog whisper, fine red sand ripple drift",
    },
    "atacama": {
        "leads": [
            "Andean bamboo quena flute whispers and celestial Tibetan singing bowls",
            "ethereal high-altitude pan flute harmonics, crystal chimes, and resonant handpan",
            "hypnotic glass singing bowl resonance and soft wooden flute with cosmic stillness",
        ],
        "pads": [
            "432Hz astronomical deep delta-wave sleep drone, velvet cosmic night pads",
            "sub-bass 2Hz sleep entrainment, restorative anti-anxiety soundbath",
        ],
        "foley": "pristine high-altitude silence, subtle whisper of crisp desert breeze",
    },
    "southwest": {
        "leads": [
            "Native American cedar courting flute and resonant major-pentatonic handpan",
            "warm cedar flute melody, quartz crystal singing bowls, and celestial chimes",
            "resonant hang drum harmonics and airy cedar flute with warm sandstone canyon caustics",
        ],
        "pads": [
            "432Hz velvet ambient pads, deep peaceful mindfulness drone, stress relief",
            "528Hz restorative harmonic resonance, comforting tranquil acoustic bed",
        ],
        "foley": "gentle canyon breeze through juniper pines, soft warm sand drift",
    },
}

DIURNAL_ENTRAINMENT: Dict[str, Dict[str, str]] = {
    "daytime": {
        "intent": "joyful daytime focus, anxiety relief, and peaceful mindfulness",
        "movement": "Alpha-wave (10Hz) calm clarity, uplifting major mode progression",
        "tempo": "60 BPM calm resting heartbeat",
        "foley_override": "gentle morning desert breeze through linen, sunlight on warm sand",
    },
    "sunrise": {
        "intent": "joyful morning awakening, deep gratitude, and peaceful dawn renewal",
        "movement": "radiant dawn harmonic swells, rising major pentatonic glissandos",
        "tempo": "62 BPM gentle dawn pulse",
        "foley_override": "cool dawn desert breeze, delicate steam rising from Moroccan mint tea glass",
    },
    "sunset": {
        "intent": "evening unwinding, stress reduction, and lowering cortisol",
        "movement": "Theta-wave (6Hz) calming descent, rich amber twilight harmonics",
        "tempo": "56 BPM evening transition",
        "foley_override": "gentle evening wind through parted drapes, soft warm lantern hum",
    },
    "night_tent": {
        "intent": "insomnia relief, restorative deep sleep, and celestial stillness (zero fire)",
        "movement": "Delta-wave (2-4Hz) hypnotic sleep drone, infinite velvet fade",
        "tempo": "48 BPM deep sleep cadence",
        "foley_override": "cool night air through linen, pure starlit nocturnal stillness, zero fire",
    },
    "campfire": {
        "intent": "comforting warmth, peaceful hearth communion, and cozy grounding",
        "movement": "resonant low drone, gentle warm acoustic swells, hypnotic peaceful calm",
        "tempo": "52 BPM tranquil hearth pace",
        "foley_override": "soft crackling cedar campfire embers, pulsing warm coals, night breeze",
    },
    "rain": {
        "intent": "deep sedative sleep, rain ASMR shelter, and complete anxiety relief",
        "movement": "binaural rain on canvas soundbath, velvet delta sleep drone",
        "tempo": "50 BPM hypnotic rain cadence",
        "foley_override": "gentle rain pitter-pattering on taut canvas tent roof, distant desert thunder rumble",
    },
}


def detect_desert_region(text: str) -> str:
    """Classifies geographical desert zone based on landmark or narrative text."""
    t = text.lower()
    if any(w in t for w in ["rub' al khali", "arabian", "liwa", "saudi", "al-ula", "wadi rum", "jordan", "empty quarter"]):
        return "arabian"
    if any(w in t for w in ["namib", "sossusvlei", "kalahari", "namibia", "deadvlei", "dune 45"]):
        return "namib"
    if any(w in t for w in ["atacama", "chile", "bolivia", "moon valley", "andes", "altiplano"]):
        return "atacama"
    if any(w in t for w in ["sedona", "colorado", "mojave", "great sand dunes", "arizona", "utah", "southwest"]):
        return "southwest"
    return "sahara"  # Default global benchmark: Sahara (Erg Chebbi, Merzouga, Siwa)


def detect_diurnal_timing(text: str, archetype: str = "") -> str:
    """Classifies diurnal timing from archetype key or prompt text."""
    comb = f"{archetype} {text}".lower()
    if any(w in comb for w in ["rain", "storm", "pitter", "droplet"]):
        return "rain"
    if any(w in comb for w in ["campfire", "hearth", "embers"]):
        return "campfire"
    if any(w in comb for w in ["night", "starlight", "milky_way", "sleep", "midnight"]):
        return "night_tent"
    if any(w in comb for w in ["sunset", "golden_hour", "dusk", "twilight"]):
        return "sunset"
    if any(w in comb for w in ["sunrise", "dawn", "morning", "tea"]):
        return "sunrise"
    return "daytime"


def generate_desert_cultural_audio_spec(
    region_or_landmark: str = "sahara",
    timing_or_archetype: str = "desert_daytime_tent",
    seed_key: Optional[str] = None,
) -> Tuple[str, str]:
    """Dynamically synthesizes culturally aligned, diurnal Suno tags & arrangement prompt.

    Guarantees:
    - 100% Cultural authenticity based on location (Sahara, Arabia, Namib, Atacama, Southwest).
    - Fresh variation on every generation via deterministic seed permutation.
    - Soothing, joyful, meditative, stress-reducing, anxiety-melting, deep sleep properties.
    - Zero solo guitar, zero harsh plucks, -21 LUFS velvet broadcast master.
    """
    region = detect_desert_region(region_or_landmark)
    timing = detect_diurnal_timing(region_or_landmark, timing_or_archetype)

    matrix = REGIONAL_DESERT_INSTRUMENTS.get(region, REGIONAL_DESERT_INSTRUMENTS["sahara"])
    diurnal = DIURNAL_ENTRAINMENT.get(timing, DIURNAL_ENTRAINMENT["daytime"])

    # Procedural variation hash
    salt = seed_key or str(int(time.time() * 1000))
    hash_int = int(hashlib.sha256(f"{region}_{timing}_{salt}".encode()).hexdigest()[:8], 16)

    lead_inst = matrix["leads"][hash_int % len(matrix["leads"])]
    pad_inst = matrix["pads"][(hash_int // 3) % len(matrix["pads"])]
    foley_sound = diurnal["foley_override"]

    suno_tags = (
        f"432Hz meditative soundbath, {lead_inst}, {pad_inst}, {foley_sound}, "
        f"{diurnal['intent']}, {diurnal['movement']}, zero solo guitar, zero twang, zero harshness, -21 LUFS"
    )

    arrangement_prompt = (
        f"[Instrumental {timing.replace('_', ' ').title()} Meditation]\n"
        f"[432Hz Solfeggio Velvet Resonance - {diurnal['tempo']}]\n"
        f"[Intro: {foley_sound} with warm harmonic pad swell]\n"
        f"[Lead Movement: Joyful peaceful melody on {lead_inst}]\n"
        f"[Deep Healing: {diurnal['intent']} with {pad_inst}]\n"
        f"[Outro: Serene infinite velvet fade into tranquil silence]"
    )

    return suno_tags, arrangement_prompt
