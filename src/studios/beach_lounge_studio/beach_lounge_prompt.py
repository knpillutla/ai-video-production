"""Beach Lounge Studio Directorial Prompt Engineering.

Specialized in 4K luxury beach lounges, ocean cabanas, sunset pergolas, and shoreline living wallpapers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

BEACH_LOUNGE_LANDMARK_POOL = [
    "Anse Source d'Argent Beach Cabana, La Digue, Seychelles",
    "Bora Bora Overwater Teak Terrace & Mt Otemanu, French Polynesia",
    "Grace Bay Luxury Beachfront Pergola, Turks and Caicos",
    "Amalfi Coast Cliffside Lemon Pergola, Positano, Italy",
    "Tulum Private Beachfront Daybed & Turquoise Surf, Mexico",
    "Whitehaven Beach Whispering Palm Lounge, Whitsunday Islands, Australia",
]

BEACH_LOUNGE_SPECIFIC_RULES = """
======================================================================
BEACH LOUNGE & OCEAN TERRACE DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. PERSPECTIVE & ARCHITECTURAL FRAMING:
   - For Infinity Pool & Villa Terraces (e.g. 'pool_terrace', 'beach_infinity_pool_terrace', or prompts mentioning 'pool', 'swimming', 'terrace', 'villa'):
     * Frame 16:9 panoramic compositions on a locked tripod from an elevated modern luxury villa terrace overlooking an illuminated infinity swimming pool edge merging seamlessly into the panoramic ocean horizon.
     * Architectural elements: Smooth travertine/limestone decking, sleek low-profile designer chaise loungers, recessed warm architectural LED floor uplights, soft turquoise underwater pool glow, silhouette of coastal palms, and rolling ocean waves under twilight/sunset sky.
     * Strictly PROHIBIT adding rustic driftwood pergolas, thatching, or beach cabanas when an infinity pool terrace is requested.
   - For Beachfront Cabanas & Pergolas (e.g. 'beach_cabana', 'beach_luxury_cabana_day', 'beach_twilight_pergola'):
     * Frame 16:9 inside-out compositions from a luxury beachfront cabana or timber pergola looking out to turquoise surf.
     * Elements: Billowing sheer white linen drapes, teak daybed with canvas cushions, weathered low table, gentle sea breeze.
   - Purity Guard: Strictly mandate zero crowds, zero tourists, zero plastic beach chairs, zero modern watercraft.
2. NATURAL BALANCED LIGHTING:
   - Default to crisp 5500K natural daylight, warm 2800K sunset alpenglow, or soft 2400K blue-hour twilight.
3. CINEMAGRAPH KINETICS (Wan 2.1 & Kling v1.6 Pro):
   - Terrace, loungers, pool structure, or cabana frame remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY subtle glassy water surface ripples across the pool, gentle palm sway, and rhythmic ocean swells in the background.
   - Domain: "water_fluid".
4. DYNAMIC SCENE-MATCHED AUDIO & MUSIC SCORING:
   - Modern Luxury Villa & Infinity Pool Terraces ('pool_terrace', 'beach_infinity_pool_terrace'):
     * Set 'suno_musical_tags' to sophisticated modern chillout lounge:
       "chic modern chillout lounge, deep velvet synth pads, sophisticated acoustic nylon guitar harmonics, warm downtempo bassline, gentle pool water caustics, subtle distant surf foley, 432Hz warmth, -21 LUFS"
     * 'tempo_bpm': 82 to 92 BPM.
   - Party / Upbeat / Celebration Atmosphere (when prompt mentions party, vibrant, celebration, summer beats, beach club):
     * Set 'suno_musical_tags' to energetic tropical lounge / melodic beach house:
       "energetic tropical beach club, melodic house groove, rhythmic percussion, joyful acoustic guitar plucks, uplifting summer vibes, vibrant ocean ambiance, -18 LUFS"
     * 'tempo_bpm': 116 to 124 BPM.
   - Peaceful Sunset & Twilight Relaxation:
     * Set 'suno_musical_tags' to warm sunset ambient peace:
       "sunset chillout lounge, warm Spanish nylon guitar, golden hour ambient synth pads, rolling ocean swell foley, peaceful 432Hz, -21 LUFS"
     * 'tempo_bpm': 70 to 80 BPM.
   - Deep Sleep & Night Sanctuaries (Starlit Hammock / Night Pavilion):
     * Set 'suno_musical_tags' to ultra-calming deep delta sleep:
       "deep delta sleep drone, 432Hz velvet ambient sleep pads, slow rhythmic midnight ocean surf, distant sea shell chimes, calming stress relief, zero drums, -21 LUFS"
     * 'tempo_bpm': 55 to 65 BPM.
"""


def build_beach_lounge_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "beach_luxury_cabana_day",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Beach Lounge studio directorial prompt conforming to global RelaxScreenplay schema."""
    arch_lower = archetype.lower()
    prompt_lower = (custom_prompt or "").lower()

    if any(w in prompt_lower for w in ["party", "energetic", "upbeat", "celebration", "beach club", "cocktail"]):
        color_temp = 2800
        cluster = "Vibrant Beach Lounge Party"
        default_topic = "Luxury oceanfront terrace beach lounge celebration with vibrant sunset lighting, infinity pool, and chic energetic ambiance"
    elif any(w in arch_lower or w in prompt_lower for w in ["pool", "infinity", "swimming"]):
        color_temp = 2400
        cluster = "Luxury Infinity Pool Terrace"
        default_topic = "Modern luxury villa terrace with an illuminated infinity swimming pool seamlessly overlooking panoramic ocean swells and golden twilight horizon"
    elif any(w in arch_lower for w in ["sunset", "terrace"]) or "sunset" in prompt_lower:
        color_temp = 2800
        cluster = "Sunset Beach Terrace"
        default_topic = "Private clifftop terrace overlooking golden hour ocean sunset, glowing amber horizon, and gentle rolling waves"
    elif any(w in arch_lower for w in ["twilight", "dusk", "pergola"]) or "twilight" in prompt_lower:
        color_temp = 2200
        cluster = "Twilight Beach Pergola"
        default_topic = "Open-air luxury beach pergola at deep violet twilight, warm amber lanterns, and soothing ocean tide lullaby"
    elif any(w in arch_lower for w in ["night", "starlight", "hammock"]) or "starlit" in prompt_lower:
        color_temp = 2000
        cluster = "Starlit Beachfront Hammock"
        default_topic = "Starlit beachfront hammock between palms, glowing starlight reflecting on gentle dark turquoise waves, zero fire"
    else:
        color_temp = 5500
        cluster = "Luxury Beach Cabana Daytime"
        default_topic = "Shaded luxury beachfront cabana with billowing sheer linen drapes looking out at pristine turquoise ocean surf in bright 5500K daylight"

    return build_base_directorial_prompt(
        genre="relax/beach_lounge",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=BEACH_LOUNGE_SPECIFIC_RULES,
        curation_landmarks=BEACH_LOUNGE_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
