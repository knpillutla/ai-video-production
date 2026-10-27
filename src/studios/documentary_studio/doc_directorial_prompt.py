"""Directorial Prompt Engineering for Documentary & Tour Studio Agents.

Defines dedicated system instructions for:
1. build_doc_directorial_prompt: Pure BBC/NatGeo wildlife & extreme environment documentaries.
2. build_tour_directorial_prompt: City/places tour archetypes (itinerary_map_tour, grand_tour, etc.).
"""

from __future__ import annotations

from typing import List, Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt
from src.studios.documentary_studio.doc_nations_archetypes import get_nations_archetype_directive

TOUR_ARCHETYPES = {
    "itinerary_map_tour",
    "travel_itinerary_tour",
    "grand_tour",
    "top_attractions_tour",
    "local_neighborhood_tour",
    "culinary_food_tour",
    "architecture_design_tour",
}


def is_tour_archetype(archetype: str) -> bool:
    """Check if an archetype belongs to the dedicated Tour Map Itinerary Director."""
    return (archetype or "").lower().strip() in TOUR_ARCHETYPES


def build_doc_directorial_prompt(
    genre: str,
    archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "slow_pan",
    speech_cadence_wpm: int = 120,
    speech_words_per_sec: float = 2.0,
    tts_provider_name: str = "Azure Speech Neural",
    channel_id: Optional[str] = "euro_discovery",
) -> str:
    """Build BBC/NatGeo blue-chip documentary instructions layered on base directorial prompt."""
    doc_rules = """
======================================================================
DOCUMENTARY DIRECTORIAL MANDATES (BBC / NATGEO BLUE-CHIP CALIBER):
======================================================================
1. CINEMATIC 24.0 FPS CADENCE & MONUMENTAL CINEMATOGRAPHY (Rules 14, 17, 18):
   - Set "recommended_fps": 24.
   - Sweeping slow aerial glides over pristine terrain, slow crane descents over granite peaks, deep optical depth-of-field.
   - Strictly prohibit high-speed zooms or jerky translations.

2. MANDATORY AUDIO-VISUAL GROUNDING & SHOW-AND-TELL COHESION:
   - In "scenes[].narration_text", every line MUST DIRECTLY DESCRIBE AND INTERPRET WHAT IS VISIBLE ON SCREEN in that scene's "visual_prompt" and "location_hub".
   - The viewer must hear authoritative commentary anchored strictly to the landscape, architecture, and geology seen in the camera frame.
   - ZERO PHANTOM SUBJECTS & SCALE CLASHES:
     * Never narrate off-screen geography (e.g., speaking of flowing rivers when the visual depicts desert rock-cut reservoirs, or speaking of oceans in a mountain pass).
     * Never describe handheld or microscopic objects (e.g., handheld seals, coins, pottery shards) during wide panoramic landscape drone vistas.
     * Scale Matching: Wide panoramic shots require narration on macro-architecture, landscape topography, and civil engineering systems. Close-ups focus on craftsmanship and textures.
   - TRIADIC SCENE HARMONY: "visual_prompt" establishes the visual subject -> "narration_text" explains what the eyes see -> "motion_prompt" guides the camera towards the focus of narration.
   - In "audio_master.spoken_narration_script", unify the per-scene narration texts into a poetic, scientifically accurate master narrative (~120 WPM) weaving geological and cultural lore.

3. SOUND DESIGN & ACOUSTIC SPATIAL FOLEY:
   - Grand orchestral elements (swelling strings, French horn fanfares, cello drone) layered with natural environmental foley.
   - Target -14.0 LUFS broadcast loudness with -18.0 dB ducking during voiceover narration.

4. FLUID KINETICS & SURVIVAL REALISM (Rules 18, 20):
   - For mountain/extreme climates: depictions of biting sub-zero blizzards, wind gusts carving powder drifts, weathered timber shelters.
   - For rivers/waterfalls: parallel flow camera alignment, smooth glassy currents, zero static foam blobs.

5. LOCAL DRONE CAMERA MOVEMENTS ("model_configs.local_drone"):
   - For documentary and travel shots, model_configs["local_drone"] MUST specify dynamic camera flight matching the scene:
     * Supported primitives: "dollyin", "dollyout", "pan-left", "pan-right", "tilt-up", "tilt-down", "orbit-left", "orbit-right", "stay".
     * Sequential timeline array: "movement": [{{"movement": "dollyin", "duration": 6.0}}, {{"movement": "pan-right", "duration": 4.0}}]
     * Parallel compound movements: "movement": [{{"stage": 1, "duration": 5.0, "movements": ["dollyin", "pan-right"]}}]
     * Framing: "start_pan": "center"|"left"|"right", "start_zoom": "normal"|"wide"|"in", "curve": "cosine"
   - Camera movements for AI diffusion models (kling, wan, h3_max) are part of their prompt text, not mechanical commands.

6. AI VIDEO DIFFUSION & MINIMAX H3 MAX TURBO DIRECTIVE:
   - For scenes requiring living micro-motion, Gemini can select:
     * "h3_max" (MiniMax H3 Max Turbo, ~$0.015/sec): Subtle atmospheric movement. Ideal for low-intensity animations like moving clouds, smoke plumes, drifting fog, gentle tree sway, or light water texture movement without changing the original image structure. Camera strictly locked or slow pan.
     * "wan_4k": Native 4K continuous laminar fluid dynamics (flowing rivers, coastal swells).
     * "kling_v3_4k": Native 4K violent impact (crashing surf, cascading waterfalls).
   - In "motion_prompt" for "h3_max", explicitly direct subtle micro-motion: "Subtle atmospheric movement, locked stationary camera. Architecture, cliffs, and land topography remain 100% structurally frozen and unmoving. Only subtle organic micro-motion of drifting clouds, gentle breeze on distant foliage, and soft water ripples."

7. COMPREHENSIVE EDUCATIONAL DOCUMENTARY DIRECTIVES (COUNTRY & CITY EXPLORATION):
   When exploring a nation or city ("countries", "cities", "nations", "country", "city"), this is a high-caliber, BBC/NatGeo-grade EDUCATIONAL DOCUMENTARY exploring everything about the destination:
   A. FOR COUNTRY EXPLORATION & 360° DOSSIER ("countries", "nations", "country", "nation", "country_dossier", "country_profile"):
      Gemini must dedicate the ENTIRE documentary to ONE SINGLE COUNTRY as an authoritative, BBC/NatGeo-grade 360° Country Profile & Almanac, systematically structuring scenes across these core factual sections:
      * 1. NATIONAL IDENTITY & SOVEREIGN ESSENCE: What this country is about, national spirit, world position, borders, and founding character.
      * 2. GEOGRAPHY, AREA & CLIMATE EXTREMES: Total land area in km², coastline length, mountains, primeval forests, major rivers/seas, four seasons, and precipitation extremes (max and min annual rainfalls/snowfalls).
      * 3. CAPITAL CITY & GREAT METROPOLISES: The capital city (government seat, iconic architecture) and major regional economic/cultural cities.
      * 4. PEOPLE, POPULATION & EDUCATION: Demographics, population count, daily lifestyle and living standards, high education levels, and world-renowned top universities.
      * 5. ECONOMY, PRODUCTION & EMPLOYMENT: What the country produces (manufacturing, agriculture, high-tech, exports), primary jobs, major industries, and economic engines.
      * 6. TRADE, POLITICS & GLOBAL ALLIANCES: International commerce, major trading partners, political structure and major parties, memberships in international bodies (UN, EU, NATO, etc.), international peacekeeping/humanitarian missions, and diplomatic allies.
      * 7. HISTORIC CITADELS & ARCHIVAL PATINA: Ancient citadels, castles, and titans who shaped history. Contrast modern majesty with archival patina: 5200K grading, weathered stone cloister sunbeams, and tactile macro craftsmanship.
      * 8. GRAND CONCLUSION & FUTURE OUTLOOK: Summary of national resilience, modern vision, and heartfelt closing reflection.
      * MANDATORY OVERLAY FIELDS: Output "chapter_title", "chapter_subtitle", "chapter_stats" (e.g. "Area: 551,695 km² • Coastline: 3,427 km"), and "fact_badge" (compact frosted pill badge, e.g. "⚡ 70% Nuclear Energy", "💶 $3.0T GDP (Rank #7)", "🏛️ 58 UNESCO Sites").
   B. FOR TOP COUNTDOWN EPISODES ("top_20_places", "top_10_cities", "top_places_to_visit", "top_20", "top_cities"):
      MANDATORY REVERSE COUNTDOWN (RETENTION RULE): All countdowns MUST count backwards from the highest number down to #1 (e.g. #20, #19, #18... down to #01; or #10 down to #01) to maximize YouTube retention and anticipation for the #1 climax!
      * In & Nearby Formula: Each scene showcases the attraction atmosphere + #1 landmark + nearby day trips / surrounding gems.
      * Outputs: "chapter_title": "RANK #03 • FLORENCE", "chapter_subtitle": "Renaissance Piazzas & Chianti Valleys", "chapter_stats": "Region: Tuscany • Best Day Trip: 45 min drive", "fact_badge": "🏛️ UNESCO World Heritage".
   D. FOR SINGLE CITY EXPLORATION ("cities", "city"):
      Gemini must dedicate the ENTIRE documentary to ONE SINGLE CITY, comprehensively weaving:
      * Famous Attractions In & Around: World-renowned monuments, iconic landmarks, palaces, cathedrals, and surrounding day trips.
      * History & Architecture: Founding legends, ancient roots, architectural evolution across centuries, and structural wonders.
      * Famous Persons: Renowned thinkers, artists, writers, architects, rulers, and pioneers born in or defining the city.
      * Famous Joints, Historic Squares & Gathering Places: World-famous piazzas, market squares, iconic cafes, bustling joints, and boulevards.
      * Great Things About the City & Living Spirit: What makes it globally revered—its soul, atmosphere, culture, and culinary joints.
      * Trade, Commerce & Major Businesses: Business districts, financial centers, innovation hubs, and historic commerce.
      * People, Population & Daily Life: How locals live, neighborhoods, population, daily rhythms, and social rituals.
      * Main Sources of Livelihood: Dominant professions, creative industries, tourism, trade, and artisanal crafts.
      * Transportation & Infrastructure: Urban transit (metro, trams, canals/waterways, bridges), central rail stations, and major airports.
      * Nature in the City: Urban riverbanks, canals, historic parks, and surrounding hills/viewpoints.
   C. MANDATORY SINGLE-DESTINATION SCOPE & TOP-LEVEL EXTRACTION:
      * Strictly 100% of scenes must be dedicated to that single city or country (NEVER jump across unrelated countries or mix cities).
      * Output top-level fields: "destination_entity" (clean city/country name, e.g. "Rome" or "Poland") and "destination_category" ("city" or "country").
      * EPISODE TITLE MANDATE: The "title" field MUST explicitly start with the destination name (e.g. "Rome: Eternal Piazzas, Living Spirit & Historic Luminaries" or "Poland: Living Heritage, Castles & Visionary Pioneers").
   D. MANDATORY SCENE 1 CURIOSITY COLD OPEN HOOK (10 TO 12 SECONDS KEN BURNS):
      Scene 1 of the documentary MUST strictly establish the destination hook following this 3-beat formula:
      * Duration: Exactly 10.0 to 12.0 seconds ("duration_seconds": 11.0, "motion_type": "ken_burns", "recommended_model": "local_drone").
      * Visual Prompt: The destination's single most iconic monument, citadel, or main square (e.g. Colosseum for Rome; Eiffel Tower for Paris).
      * Narration Text 3-Beat Formula:
        1. The Paradox Hook (First 3-4s): A startling paradox or mystery (e.g. "In the heart of Europe lies a sovereign enigma...").
        2. The Sovereign Reveal: "Welcome to [Destination Name]..."
        3. The Cinematic Roadmap: One sentence outlining what this 360° documentary explores (landscapes, history, commerce, living heritage).
   E. MANDATORY FINAL SCENE CONCLUSION DIRECTIVE (10 TO 12 SECONDS CINEMATIC OUTRO):
      The FINAL scene of the documentary MUST strictly provide an inspiring, poetic conclusion:
      * Duration: Exactly 10.0 to 12.0 seconds ("duration_seconds": 11.0).
      * Proper Cinematic Image: A breathtaking wide panoramic landscape or architectural skyline at golden twilight or sunset (e.g. dramatic aerial pull-back over the historic capital citadel, iconic hills, or shimmering horizon vista). STRICTLY a proper photographic image—NEVER an infographic slide, table, or recap card!
      * Motion Engine: Smooth cinematic drone pull-back or slow drift ("motion_type": "ken_burns", "recommended_model": "local_drone", "camera_movement": "dollyout").
      * Conclusion Narration: An authoritative, heartfelt closing reflection honoring the enduring spirit, timeless cultural legacy, resilience, and living soul of [Destination Name], warmly inviting the audience to explore its heritage.

8. STRICT BAN ON OUTRO INFOGRAPHIC SUMMARY CARDS & YOUTUBE END-SCREEN SAFE ZONE:
   - Conclude naturally on a panoramic twilight pull-back vista (never an infographic recap slide).
   - End-Screen Safe Zone: Keep top-left and top-center clear for YouTube end-card recommendations.

9. AUTONOMOUS HIGH-CTR A/B/C THUMBNAIL SUITE & PINNED ENGAGEMENT HOOK:
   - Synthesize 3 distinct high-CTR psychological thumbnail variants ("thumbnail_variants") for YouTube Test & Compare:
     * Variant A (Sovereign Curiosity Question): e.g. "WHAT IS [DESTINATION] BEST KNOWN FOR?"
     * Variant B (Hidden Anomaly / Secret): e.g. "EUROPE'S GREATEST SECRET"
     * Variant C (Scale Paradox / Survival): e.g. "HOW THEY SURVIVED THREE EMPIRES"
   - Root Output Fields: "thumbnail_headline" (Variant A), "thumbnail_hero_scene_index", "thumbnail_curiosity_rationale", "thumbnail_variants" (3 dicts: variant, headline, angle), and "pinned_comment" (provocative trivia/debate question to drive comment velocity).

10. MANDATORY 80/20 OPTICAL SCALE & RICH CINEMATIC AESTHETICS:
   To deliver BBC Earth & National Geographic visual grandeur:
   A. 80% Monumental Aerials & 3D Drone Orbits (Scenes 1, 2, 3, 5, 7, 8):
      * Lens & Perspective: "High-altitude 45-degree bird's-eye aerial drone perspective from 250m altitude, expansive panoramic vista, 18mm ultra-wide lens, deep optical field of view, generous sky headroom". Maintain 20%-30% environmental border buffer.
      * Rich Aesthetics: "Vibrant natural color palette, authentic architectural relief, Hasselblad H6D-100c medium-format clarity, zero plastic sheen, context-matched lighting (crisp balanced daylight, golden hour sidelight, or atmospheric night illumination with warm architectural glow)".
      * Motion: Slow forward drone push or smooth continuous 360-degree orbital banking flight around the landmark ("camera_movement": "slow_drone_forward"|"orbit-left"|"orbit-right").
   B. 20% Intimate 85mm Optical Bokeh (Scenes 4 & 6 - Education, People & Artisanal Craft):
      * Scene 4 (Education & Universities): "85mm portrait lens, f/1.8 creamy optical bokeh, luminous golden sunbeams streaming through gothic university library cloisters or historic cobblestones".
      * Scene 6 (Trade & Craftsmanship): "Tactile 85mm macro craftsmanship, f/1.8 depth-of-field, artisan hands shaping copper/glass or aged oak wine barrels in historic cellars".
      * Motion: Locked stationary cinemagraph hold ("camera_movement": "locked_stationary_cinemagraph").
"""
    arch_mandate = get_nations_archetype_directive(archetype)
    if arch_mandate:
        doc_rules += f"\n11. THEMATIC ARCHETYPE DIRECTIVE:\n{arch_mandate}\n"
    return build_base_directorial_prompt(
        genre="documentary",
        sub_genre=archetype,
        archetype=archetype,
        cluster="documentary",
        custom_prompt=custom_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        specific_rules=doc_rules,
        channel_id=channel_id or "euro_discovery",
        tier="balanced",
        speech_cadence_wpm=speech_cadence_wpm,
        speech_words_per_sec=speech_words_per_sec,
        tts_provider_name=tts_provider_name,
    )


def build_tour_directorial_prompt(
    archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "perspective_drone",
    speech_cadence_wpm: int = 120,
    speech_words_per_sec: float = 2.0,
    tts_provider_name: str = "Azure Speech Neural",
    channel_id: Optional[str] = "euro_discovery",
) -> str:
    """Build dedicated Tour Director instructions layered on base directorial prompt."""
    tour_rules = """
======================================================================
TOUR & ITINERARY DIRECTORIAL MANDATES (RICK STEVES & BBC TRAVEL CALIBER):
======================================================================
1. PHYSICAL ATTRACTIONS CURATION (DECOUPLED STUDIO ENGINE ARCHITECTURE):
   - In "scenes", output ONLY the sequential physical landmark stops on the itinerary (e.g. Stop 1, Stop 2, Stop 3, Stop 4).
   - Do NOT generate cartographic map slides or overview/summary cards in "scenes". The Studio Engine automatically injects the Master Overview Card, the Connecting Route Maps, and the Recap Table in post-production!
   - Every physical attraction scene gets its FULL cinematic duration without being truncated by map slides.

2. ATTRACTION DATA & REAL-WORLD ACCURACY (MANDATORY GPS COORDINATES):
   - On each physical attraction scene:
     * "attraction_name": Real name of the landmark (e.g. "Westminster Abbey").
     * "origin_coords": Real GPS coordinates [lat, lon] (e.g. [51.4994, -0.1273]). MANDATORY: NEVER null!
     * "destination_coords": Set to match "origin_coords" [lat, lon].
     * "origin_name": Same as attraction_name.
     * "start_time" and "end_time" (e.g. "09:00 AM", "11:30 AM").
     * "visit_duration": Realistic exploration time (e.g. "2.5 hrs").
     * "attraction_cost": Real admission fee (e.g. "£29.00 Ticket", "Free Entry").
     * "visual_prompt": 4K architectural cinematography (POI Orbit, Hero Dolly In, Rising Technocrane).
     * "narration_text": Authoritative, poetic commentary on the history and architecture.

3. TRANSIT TO NEXT STOP (OPTION A DECOUPLED ROUTE BRIDGE):
   - On each attraction (except the final stop), supply "transit_to_next":
     * "transit_mode": "walk" if distance <= 0.8 km (<= 10 mins, zero cost); "drive" if distance > 0.8 km (> 10 mins).
     * "transit_duration": e.g. "14 min cab" or "8 min walk".
     * "approx_leg_cost": e.g. "£12–£16 Uber" or "Free (walk)".
     * "transit_narration": A seamless, evocative 1-sentence transition line linking to the next stop (e.g. "Next, an eastbound drive traces the Thames toward the ancient Norman stronghold of the Tower of London.").
     * For the final attraction on the tour, set "transit_to_next": null.

4. MASTER ITINERARY SUMMARY (ROOT FIELD):
   - Supply the master daily summary array in "itinerary_summary" with "total_attraction_time", "total_travel_time", "total_walk_time", "total_drive_time", "transit_distance", "total_travel_cost", and "meal_break".

5. LOCAL DRONE CAMERA MOVEMENTS ("model_configs.local_drone"):
   - For all attraction scenes, camera motion is handled by our Tier-0 local perspective drone engine ($0.00 compute).
   - In "model_configs.local_drone", "movement" MUST specify supported engine actions:
     * Primitives: "dollyin", "dollyout", "pan-left", "pan-right", "tilt-up", "tilt-down", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "orbit-left", "orbit-right", "stay".
     * Multi-stage compound: [{{"stage": 1, "duration": 5.0, "movements": ["dollyin", "pan-right"]}}, ...]
     * Framing: "start_pan": "center"|"left"|"right", "start_zoom": "normal"|"wide"|"in", "curve": "cosine".
   - Camera movements for AI diffusion models (kling, wan, h3_max) are written into their prompt text, not mechanical flight names.
"""
    tour_root_schema = """  "itinerary_summary": [
    {
      "day": 1,
      "day_title": "Day 1 Highlights",
      "attractions": ["Landmark 1", "Landmark 2", "Landmark 3"],
      "total_attraction_time": "6.5 hrs",
      "total_travel_time": "1.0 hr",
      "total_walk_time": "25 mins",
      "total_drive_time": "35 mins",
      "transit_distance": "6.8 km circuit",
      "total_travel_cost": "£24–£34 (~$45 USD)",
      "meal_break": "1.0 hr Lunch Break at Local Market"
    }
  ],"""

    tour_scene_schema = """      "is_itinerary_overview": false,
      "is_map_transition": false,
      "origin_name": "Landmark 1",
      "destination_name": "Landmark 1",
      "origin_coords": [51.4994, -0.1273],
      "destination_coords": [51.4994, -0.1273],
      "distance_local": null,
      "transit_mode": null,
      "transit_duration": null,
      "approx_leg_cost": null,
      "attraction_name": "Landmark 1",
      "start_time": "09:00 AM",
      "end_time": "11:30 AM",
      "visit_duration": "2.5 hrs",
      "attraction_cost": "£29.00 Ticket",
      "transit_to_next": {
        "transit_mode": "drive",
        "transit_duration": "14 min cab",
        "approx_leg_cost": "£12–£16 Uber",
        "transit_narration": "Next, an eastbound drive traces the Thames toward the ancient Norman stronghold of the Tower of London."
      },"""

    return build_base_directorial_prompt(
        genre="documentary",
        sub_genre=archetype,
        archetype=archetype,
        cluster="documentary",
        custom_prompt=custom_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        specific_rules=tour_rules,
        channel_id=channel_id or "euro_discovery",
        tier="balanced",
        extra_root_schema=tour_root_schema,
        extra_scene_schema=tour_scene_schema,
        speech_cadence_wpm=speech_cadence_wpm,
        speech_words_per_sec=speech_words_per_sec,
        tts_provider_name=tts_provider_name,
    )



__all__ = [
    "TOUR_ARCHETYPES",
    "is_tour_archetype",
    "build_doc_directorial_prompt",
    "build_tour_directorial_prompt",
]
