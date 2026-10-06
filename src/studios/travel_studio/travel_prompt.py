"""Travel & Scenic Wonders Studio Directorial Prompt Engineering.

Specialized in 4K aerial drone flights, world cities, heritage citadels, and natural wonders.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

TRAVEL_LANDMARK_POOL = [
    "Hyderabad: Charminar, Golconda Fort Ramparts, Hussain Sagar Buddha, HITEC City Skyline, Durgam Cheruvu Cable Bridge",
    "Varanasi: Dashashwamedh Ghat, Manikarnika Ghat, River Ganga at Sunrise Dawn",
    "Tokyo: Shinjuku & Shibuya Neon Skylines, Rainbow Bridge, Tokyo Tower Twilight",
    "New York: Manhattan Skyline, Brooklyn Bridge, Central Park Aerial",
    "Amalfi Coast & Positano Cliffside Pastel Villages, Tyrrhenian Sea, Italy",
    "Grand Canyon Colossal Desert Chasms & Colorado River, Arizona, USA",
    "Lauterbrunnen & Swiss Alps Glacial Valleys, Switzerland",
    "Santorini Caldera & White Oia Cliffside Terraces, Greece",
    "Kyoto Ancient Pagodas, Yasaka Shrine & Arashiyama Bamboo Ridge, Japan",
    "Dubai Marina, Burj Khalifa & Palm Jumeirah Coastal Aerials, UAE",
]

TRAVEL_SPECIFIC_RULES = """
======================================================================
TRAVEL & SCENIC WONDERS DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. 4K CINEMATIC AERIAL DRONE FRAMING (DEFAULT PERSPECTIVE):
   - All shots default to 4K cinematic aerial drone cinematography (sweeping forward glides, slow circular orbits, dramatic reveals, or high-altitude skyline panoramas).
   - Gimbal Purity: Ensure horizons remain 100% level, transitions are buttery-smooth, zero erratic camera maneuvers.
   - Architectural & Urban Elegance: Unlike pure wilderness relaxation, Travel & Scenic explicitly showcases world cities, iconic glass skyscrapers, architectural bridges, historic citadels, temples, and evening traffic light trails.

2. STORY-DRIVEN HYBRID MOTION ARCHITECTURE (70% KEN BURNS / 30% AI VIDEO MOTION):
   - Allocate approximately 70% of scenes to majestic high-res 4K camera glides (smooth deterministic pan/zoom at $0.00 compute).
   - Allocate approximately 30% of key landmark scenes to live AI video motion (for moving water, traffic light trails, or mist plumes).
   - For all shots, ensure landmark monuments, buildings, and cliffs remain rigid, stable, and razor-sharp.

3. AUTONOMOUS DRONE MUSIC & SOUNDTRACK DIRECTION (MANDATORY DIRECTIVE):
   - User Music Override: If the user explicitly specifies a musical style or instrument in the prompt (e.g. "jazz", "lo-fi", "sitar"), strictly honor and enrich that preference.
   - Autonomous Soundtrack Directive (When user does not specify music): NEVER produce silence or bland generic drones. Gemini MUST autonomously synthesize a mesmerizing, melodious, joyful, expressive, hummable, elegant, and energetic BGM with instruments that make sense for sweeping 4K drone cinematography and smooth movements:
     * Metropolises & City Skylines (e.g., Hyderabad, Tokyo, NY): Melodious cosmopolitan jazz lounge, warm Rhodes piano, brushed swing drums, upright acoustic bass, expressive muted trumpet/sax melodies, joyful and hummable city cadence.
     * Heritage & Ancient Citadels (e.g., Golconda, Temples, Forts): Regal melodious acoustic fusion, hummable sitar & santoor melodies, resonant cello, elegant acoustic guitar, and subtle rhythmic tabla groove.
     * Coastal & Tourist Havens (e.g., Amalfi, Mediterranean): Breezy joyful acoustic Spanish guitar, warm melodic accordion, and sparkling seaside percussion.
     * Natural Wonders & Canyons: Soaring majestic orchestral score, uplifting French horns, resonant strings, and cinematic pulse.
   - All audio tags in 'audio_master.suno_musical_tags' must be broadcast-ready (48,000 Hz, -14.0 LUFS broadcast normalization).

4. FLUID DYNAMICS (RULE 20):
   - In shots with urban rivers, lakes, oceans, or waterfalls, specify smooth laminar water surfaces and specular light reflections.
"""


def build_travel_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "cities",
    camera_motion: str = "slow_drone_forward",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Travel studio directorial prompt conforming to RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if "city" in arch_lower or "skylin" in arch_lower or "metropol" in arch_lower:
        color_temp = 3800
        cluster = "Metropolises & Skylines"
        default_topic = "4K cinematic drone flight over illuminated Hyderabad skyline, Charminar, Hussain Sagar, and HITEC City with jazz score"
    elif "spirit" in arch_lower or "temple" in arch_lower or "ghat" in arch_lower:
        color_temp = 4000
        cluster = "Spiritual & Sacred Sanctuaries"
        default_topic = "Sunrise dawn drone glide over sacred ancient temple ghats along a revered river with meditative sitar music"
    elif "iconic" in arch_lower or "fort" in arch_lower or "monument" in arch_lower or "herit" in arch_lower:
        color_temp = 3000
        cluster = "Iconic Heritage Citadels"
        default_topic = "Golden sunset drone orbit circling ancient Golconda Fort granite ramparts and royal bastions"
    elif "tourist" in arch_lower or "coastal" in arch_lower or "beach" in arch_lower:
        color_temp = 3200
        cluster = "World Tourist Havens"
        default_topic = "Sun-drenched drone flight along colorful coastal cliffside villas and azure Mediterranean harbor"
    elif "wonder" in arch_lower or "canyon" in arch_lower:
        color_temp = 5400
        cluster = "Monumental Natural Wonders"
        default_topic = "Panoramic aerial drone flight sweeping across monumental canyon chasms and emerald rivers in crisp daylight"
    elif "remote" in arch_lower:
        color_temp = 4800
        cluster = "Remote Untouched Frontiers"
        default_topic = "High-altitude drone flight over remote windswept peaks of Patagonia and solitary glacial outposts"
    else:
        color_temp = 5500
        cluster = "Untamed Wilderness & Nature"
        default_topic = "Untamed mountain river gorge and emerald forest aerial glide under crisp natural daylight"

    raw_p = (custom_prompt or "").strip()
    if raw_p:
        words = raw_p.split()
        drone_terms = {"drone", "aerial", "flight", "cinematic", "glide", "orbit", "flyover", "skyline"}
        if len(words) <= 6 and not any(w.lower() in drone_terms for w in words):
            eff_topic = f"4K cinematic aerial drone showcase of {raw_p}: sweeping forward glides and orbital reveals across iconic architectural skylines, illuminated bridges, monuments, and evening urban glow"
        else:
            eff_topic = raw_p
    else:
        eff_topic = default_topic

    return build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=eff_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion or "slow_drone_forward",
        excluded_topics=excluded_topics,
        specific_rules=TRAVEL_SPECIFIC_RULES,
        curation_landmarks=TRAVEL_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
