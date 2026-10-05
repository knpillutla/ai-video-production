"""Cultural Geographic Ocean Audio Synthesis Matrix.

Encapsulates authentic regional instrumentation across 5 global ocean/coastal zones:
1. Polynesian / Pacific (Hawaii, Tahiti, Bora Bora): Slack key guitar, ukulele overtones, sea shell chimes.
2. Mediterranean / Aegean (Santorini, Amalfi, Cyclades): Greek bouzouki harmonics, Spanish nylon guitar.
3. Caribbean / Tropical Atolls (Maldives, Bahamas): Handpan in major pentatonic, wooden tongue drum, marimba.
4. Pacific Northwest & Atlantic (Big Sur, Oregon, Ireland): Resonant cello drone, fingerpicked guitar, misty fog.
5. Indian Ocean Sanctuary (Seychelles, Mauritius): Crystal bowls, ethereal bamboo flute, soft harp arpeggios.

Provides dynamic permutation so every production generates a fresh, unique combination.
"""

from __future__ import annotations

import hashlib
import time
from typing import Dict, List, Optional, Tuple


REGIONAL_OCEAN_INSTRUMENTS: Dict[str, Dict[str, List[str]]] = {
    "polynesian": {
        "leads": [
            "Hawaiian slack-key acoustic guitar in warm open-tuning harmonics and gentle ukulele swells",
            "celestial sea shell wind chimes, resonant handpan, and soft acoustic ukulele overtones",
            "airy bamboo nose flute melody, resonant tongue drum, and uplifting slack-key guitar notes",
        ],
        "pads": [
            "432Hz velvet analog ocean pads, sub-bass theta drone, deep stress relief",
            "528Hz Solfeggio heart-opening resonance, smooth anti-anxiety ambient bed",
        ],
        "foley": "gentle rhythmic Pacific ocean surf, subtle warm coastal trade wind breeze",
    },
    "mediterranean": {
        "leads": [
            "soft melodic Mediterranean bouzouki harmonics and Spanish nylon-string classical guitar",
            "crystalline singing bowls, warm acoustic nylon guitar arpeggios, and soft bell chimes",
            "ethereal Greek santouri zither plucks, resonant handpan, and gentle coastal breeze",
        ],
        "pads": [
            "432Hz Solfeggio soothing sleep pads, warm velvet ambient drone, restorative calm",
            "528Hz golden Aegean frequency, lush velvet analog warmth, cortisol-reducing bed",
        ],
        "foley": "gentle turquoise sea waves lapping on warm cobblestones, subtle sea salt breeze",
    },
    "caribbean": {
        "leads": [
            "resonant handpan in uplifting major pentatonic mode and soft wooden tongue drum",
            "warm acoustic marimba harmonics, gentle steel pan resonance, and crystal chimes",
            "ethereal bamboo flute and singing bowl overtones with rhythmic turquoise water lapping",
        ],
        "pads": [
            "432Hz deep grounding tropical drone, velvet ambient warmth, deep relaxation",
            "4-7Hz theta-wave brain entrainment pads, tranquil stress relief bed",
        ],
        "foley": "crystal clear calm lagoon water lapping softly against teak stilts, distant reef surf",
    },
    "atlantic": {
        "leads": [
            "low resonant acoustic cello drone and warm fingerpicked folk guitar overtones",
            "ethereal Celtic low whistle whispers, crystal singing bowls, and acoustic guitar",
            "hypnotic bowed glass resonance and soft fingerstyle acoustic melody with coastal stillness",
        ],
        "pads": [
            "432Hz deep delta-wave sleep drone, velvet misty coastal night pads",
            "sub-bass 2Hz sleep entrainment, restorative anti-anxiety soundbath",
        ],
        "foley": "deep rolling Pacific surf against sea stacks, distant coastal foghorn whisper, ocean mist",
    },
    "indian_ocean": {
        "leads": [
            "crystalline Tibetan singing bowls and ethereal bamboo bansuri flute whispers",
            "soft ambient concert harp arpeggios, crystal bell chimes, and resonant handpan",
            "warm acoustic swarmandal harmonics and airy flute with pristine tropical water stillness",
        ],
        "pads": [
            "432Hz velvet ambient pads, deep peaceful mindfulness drone, stress relief",
            "528Hz restorative harmonic resonance, comforting tranquil acoustic bed",
        ],
        "foley": "gentle warm tropical ocean ripples, soft palm frond rustle, pristine reef tranquility",
    },
}

DIURNAL_ENTRAINMENT: Dict[str, Dict[str, str]] = {
    "daytime": {
        "intent": "joyful daytime focus, anxiety relief, and peaceful tropical mindfulness",
        "movement": "Alpha-wave (10Hz) calm clarity, uplifting major mode progression",
        "tempo": "60 BPM calm resting heartbeat",
        "foley_override": "gentle rhythmic turquoise ocean waves, warm sea breeze through linen",
    },
    "sunrise": {
        "intent": "joyful morning awakening, deep gratitude, and peaceful dawn renewal",
        "movement": "radiant dawn harmonic swells, rising major pentatonic glissandos",
        "tempo": "62 BPM gentle dawn pulse",
        "foley_override": "cool dawn sea breeze, glassy ocean swells, first sunbeams on water",
    },
    "sunset": {
        "intent": "evening unwinding, stress reduction, and lowering cortisol",
        "movement": "Theta-wave (6Hz) calming descent, rich amber twilight harmonics",
        "tempo": "56 BPM evening transition",
        "foley_override": "gentle evening surf surges, soft offshore wind, golden hour caustics",
    },
    "night_bioluminescent": {
        "intent": "insomnia relief, restorative deep sleep, and celestial ocean stillness (zero fire)",
        "movement": "Delta-wave (2-4Hz) hypnotic sleep drone, infinite velvet fade",
        "tempo": "48 BPM deep sleep cadence",
        "foley_override": "gentle nocturnal tide lapping, cool night breeze, electric-blue glowing surf, zero fire",
    },
    "campfire": {
        "intent": "comforting warmth, peaceful beach hearth communion, and cozy grounding",
        "movement": "resonant low drone, gentle warm acoustic swells, hypnotic peaceful calm",
        "tempo": "52 BPM tranquil hearth pace",
        "foley_override": "soft crackling driftwood campfire embers, pulsing coals, rhythmic night surf",
    },
    "rain": {
        "intent": "deep sedative sleep, tropical rain ASMR shelter, and complete anxiety relief",
        "movement": "binaural rain on ocean water soundbath, velvet delta sleep drone",
        "tempo": "50 BPM hypnotic rain cadence",
        "foley_override": "gentle warm rain falling on turquoise sea surface, soft drops dripping from palm leaves",
    },
}


def detect_ocean_region(text: str) -> str:
    """Classifies geographical ocean zone based on landmark or narrative text."""
    t = text.lower()
    if any(w in t for w in ["hawaii", "maui", "kauai", "oahu", "tahiti", "bora bora", "polynesia", "fiji"]):
        return "polynesian"
    if any(w in t for w in ["santorini", "greece", "amalfi", "italy", "cyclades", "mediterranean", "mallorca"]):
        return "mediterranean"
    if any(w in t for w in ["maldives", "seychelles", "mauritius", "zanzibar", "bali"]):
        return "indian_ocean"
    if any(w in t for w in ["big sur", "oregon", "cannon beach", "vancouver island", "pacific northwest", "ireland", "atlantic"]):
        return "atlantic"
    if any(w in t for w in ["bahamas", "caribbean", "turks", "barbados", "cayman", "jamaica"]):
        return "caribbean"
    return "polynesian"  # Default global benchmark


def detect_diurnal_timing(text: str, archetype: str = "") -> str:
    """Classifies diurnal timing from archetype key or prompt text."""
    comb = f"{archetype} {text}".lower()
    if any(w in comb for w in ["rain", "storm", "shower", "droplet"]):
        return "rain"
    if any(w in comb for w in ["campfire", "hearth", "embers", "bonfire"]):
        return "campfire"
    if any(w in comb for w in ["night", "bioluminescent", "starlight", "milky_way", "sleep", "midnight"]):
        return "night_bioluminescent"
    if any(w in comb for w in ["sunset", "golden_hour", "dusk", "twilight"]):
        return "sunset"
    if any(w in comb for w in ["sunrise", "dawn", "morning", "coffee"]):
        return "sunrise"
    return "daytime"


def generate_ocean_cultural_audio_spec(
    region_or_landmark: str = "polynesian",
    timing_or_archetype: str = "ocean_daytime_shore",
    seed_key: Optional[str] = None,
) -> Tuple[str, str]:
    """Dynamically synthesizes culturally aligned, diurnal Suno tags & arrangement prompt."""
    reg_key = detect_ocean_region(region_or_landmark)
    time_key = detect_diurnal_timing(region_or_landmark, archetype=timing_or_archetype)

    region_data = REGIONAL_OCEAN_INSTRUMENTS[reg_key]
    timing_data = DIURNAL_ENTRAINMENT[time_key]

    raw_seed = seed_key or f"{reg_key}-{time_key}-{time.time()}"
    seed_int = int(hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()[:8], 16)

    leads = region_data["leads"]
    pads = region_data["pads"]

    selected_lead = leads[seed_int % len(leads)]
    selected_pad = pads[(seed_int // len(leads)) % len(pads)]
    foley = timing_data.get("foley_override") or region_data["foley"]

    tags = (
        f"432Hz meditative soundbath, {selected_lead}, {selected_pad}, "
        f"{foley}, {timing_data['tempo']}, broadcast master, zero hiss, -21 LUFS"
    )

    arrangement_prompt = (
        f"Genre: 432Hz Ambient Ocean Soundscape & Anti-Anxiety Soundbath\n"
        f"Intent: {timing_data['intent']}\n"
        f"Movement: {timing_data['movement']}\n"
        f"Instrumentation: {selected_lead}, supported by {selected_pad}\n"
        f"Environmental Foley: {foley}\n"
        f"Pacing: {timing_data['tempo']}, smooth seamless living wallpaper loop\n"
        f"Vocal: Strictly instrumental, zero singing, zero vocal chanting\n"
    )

    return tags, arrangement_prompt
