"""Travel & Scenic Wonders Studio Directorial Prompt Engineering.

Specialized in 4K aerial drone flights, world cities, heritage citadels, and natural wonders.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt
from src.studios.lighting_director import detect_lighting_directive

TRAVEL_SPECIFIC_RULES = """
======================================================================
TRAVEL & SCENIC STUDIO DIRECTORIAL & AUTONOMOUS CURATION RULES:
======================================================================
1. AUTONOMOUS CITY & DESTINATION SELECTION (IF NOT PROVIDED BY USER):
   - If the user prompt does not specify a city or region, Gemini MUST autonomously choose an iconic, visually breathtaking world city, cultural capital, or scenic wonder matching the archetype (e.g. European historic capitals, Asian metropolises, Mediterranean coastal havens, ancient heritage citadels) without repeating recently produced topics.

2. COMPREHENSIVE LANDMARK, ARCHITECTURE & CULTURAL CURATION:
   - When a city or destination is provided (e.g. "Hyderabad", "Kyoto", "Rome", "Seattle"), Gemini MUST autonomously query its geographic knowledge to identify the top iconic landmarks, architectural marvels, and cultural highlights.
   - Never expect the user to know or list attractions. Distribute distinct, authentic attractions across the exact requested shot count from diverse categories:
     * Monumental Heritage: Ancient citadels, royal palaces, historic fort ramparts, monumental temples, cathedrals.
     * Modern Architectural Skylines: Iconic towers, suspension bridges, geometric glass structures, financial districts.
     * Famous Roads, Boulevards & Waterfronts: Celebrated scenic avenues, historic bridges, coastal drives, river embankments.
     * Historic Quarters & Boutique Districts: Heritage bazaars, famous boutique streets, artisan lanes, cobblestone plazas.
   - Scene Diversity Contract: Every scene MUST showcase a distinct attraction or viewpoint; never repeat the same monument or angle across scenes.

3. 4K CINEMATIC AERIAL DRONE FRAMING & SCENIC PACING:
   - Cadence & Variety (10s-14s per Landmark): Direct distinct iconic attractions across scenes with ~12s per vista, matching the mesmerizing rhythm of 4K scenic relaxation films.
   - All shots feature deep 4K aerial drone cinematography with multi-waypoint camera choreography ('camera_waypoints').
   - Compound Rigs: Employ forward drone sweeps, orbital wraps, elevation reveals, and coastal glides with continuous perspective flight.
   - Architectural Elegance: Keep focus on breathtaking architectural geometry, bridges, and city planning without crowd clutter.

4. 100% TIER-0 LOCAL 4K PERSPECTIVE ENGINE ($0.00 COMPUTE):
   - Set "motion_type": "ken_burns" for all architectural & skyline scenes to preserve 100% geometric stability without AI diffusion warping.
   - Combine with "kinetic_micro_zones" for distant car drift, boat bobbing, water ripples, and canopy sway at zero cloud API cost.

5. AUTONOMOUS SOUNDTRACK DIRECTIVE (MANDATORY):
   - Metropolises & City Skylines: Melodious cosmopolitan jazz lounge, warm Rhodes piano, brushed swing drums, upright acoustic bass, expressive muted trumpet/sax melodies.
   - Heritage & Ancient Citadels: Regal melodious acoustic fusion, hummable sitar & santoor, resonant cello, elegant acoustic guitar, rhythmic tabla groove.
   - Coastal Havens: Breezy joyful acoustic Spanish guitar, warm melodic accordion, sparkling seaside percussion.
   - Natural Wonders: Soaring majestic orchestral score, uplifting French horns, resonant strings.
   - Audio tags in 'audio_master.suno_musical_tags' must be broadcast-ready (48,000 Hz, -14.0 LUFS broadcast normalization).

6. FLUID DYNAMICS (RULE 20):
   - For urban rivers, lakes, oceans, or waterfalls, specify smooth laminar water surfaces and specular light reflections.

7. WIDE-SCALE KINETIC MICRO-ZONES ('kinetic_micro_zones'):
   - For wide aerial shots, specify normalized bounding boxes [ymin, ymax, xmin, xmax] (0.0-1.0) to animate distant elements:
     * 'sprites': Distant cars on boulevards, boats on waterways, or pedestrian clusters in courtyards (drifting via 'delta_pct').
     * 'tree_sway_zones': Distant park/hillside tree canopies with wind sway.
     * 'water_zones': Distant river/lake surfaces with subtle harmonic ripples.
     * 'celestial_zone': Subtle solar/lunar corona shimmer.
"""


def build_travel_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "cities",
    camera_motion: str = "slow_drone_forward",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
    tier: str = "balanced",
) -> str:
    """Build dedicated Travel studio directorial prompt conforming to RelaxScreenplay schema."""
    arch_lower = archetype.lower()
    eff_kelvin, tod_key, tod_desc = detect_lighting_directive(custom_prompt, archetype, 5500)

    if "city" in arch_lower or "skylin" in arch_lower or "metropol" in arch_lower:
        cluster = "Metropolises & Skylines"
        default_topic = f"Autonomously select an iconic world metropolis and showcase its premier skyline, architectural monuments, and famous boulevards under {tod_desc} with cosmopolitan jazz score"
    elif "spirit" in arch_lower or "temple" in arch_lower or "ghat" in arch_lower:
        cluster = "Spiritual & Sacred Sanctuaries"
        default_topic = f"Autonomously select a sacred world sanctuary or ancient temple complex along a revered river under {tod_desc} with meditative acoustic music"
    elif "iconic" in arch_lower or "fort" in arch_lower or "monument" in arch_lower or "herit" in arch_lower:
        cluster = "Iconic Heritage Citadels"
        default_topic = f"Autonomously select a monumental ancient fortress, royal citadel, and royal palace ramparts under {tod_desc} with regal fusion score"
    elif "tourist" in arch_lower or "coastal" in arch_lower or "beach" in arch_lower:
        cluster = "World Tourist Havens"
        default_topic = f"Autonomously select a premier coastal harbor, cliffside pastel village, and azure sea promenade under {tod_desc} with acoustic guitar"
    elif "wonder" in arch_lower or "canyon" in arch_lower:
        cluster = "Monumental Natural Wonders"
        default_topic = f"Autonomously select a monumental natural chasm, river gorge, and dramatic geological wonder under {tod_desc}"
    elif "remote" in arch_lower:
        cluster = "Remote Untouched Frontiers"
        default_topic = f"Autonomously select an awe-inspiring remote mountain ridge and solitary glacial frontier under {tod_desc}"
    else:
        cluster = "Untamed Wilderness & Nature"
        default_topic = f"Autonomously select a breathtaking untamed river canyon and emerald forest landscape under {tod_desc}"

    raw_p = (custom_prompt or "").strip()
    if raw_p:
        words = raw_p.split()
        drone_terms = {"drone", "aerial", "flight", "cinematic", "glide", "orbit", "flyover", "skyline"}
        if len(words) <= 6 and not any(w.lower() in drone_terms for w in words):
            eff_topic = f"4K cinematic aerial drone showcase of {raw_p}: sweeping forward glides and orbital reveals across iconic landmarks, architectural marvels, famous boulevards, and scenic vistas under {tod_desc}"
        else:
            eff_topic = raw_p
    else:
        eff_topic = default_topic

    eff_shots = max(2, round(duration_seconds / 12.5))
    per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
    travel_rules_dynamic = TRAVEL_SPECIFIC_RULES + f"""
8. DURATION-DRIVEN SCENE CADENCE CONTRACT (MANDATORY, num_shots: -1):
   - Total Video Duration: {duration_seconds} seconds.
   - For all travel & skyline productions, shot count is strictly determined by duration (num_shots: -1), NEVER by a fixed 1-shot default.
   - You MUST author an array of exactly {eff_shots} scenes (~{per_shot_dur}s each) in 'scenes'.
   - Each of the {eff_shots} scenes MUST showcase a completely different landmark, monument, or viewpoint (e.g. Landmark 1 to Landmark {eff_shots}).
   - Under NO circumstances return 1 shot. Output all {eff_shots} distinct scenes.
"""
    return build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=eff_topic,
        duration_seconds=duration_seconds,
        num_shots=eff_shots,
        camera_motion=camera_motion or "slow_drone_forward",
        excluded_topics=excluded_topics,
        specific_rules=travel_rules_dynamic,
        curation_landmarks=None,
        color_temp_kelvin=eff_kelvin,
        channel_id=channel_id or "earth_serenade",
        tier=tier,
    )
