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
    "itinerary_map_tour", "travel_itinerary_tour", "tour_itinerary", "grand_tour",
    "top_attractions_tour", "top_places_to_visit", "top_10_cities", "top_20_places",
    "local_neighborhood_tour", "culinary_food_tour", "architecture_design_tour",
    "tourism_guide", "road_trip_tour", "spiritual_journeys",
}


def is_tour_archetype(archetype: str) -> bool:
    """Check if an archetype belongs to the dedicated Tour Map Itinerary Director."""
    clean = (archetype or "").lower().strip()
    return clean in TOUR_ARCHETYPES or any(k in clean for k in ("itinerary", "tour", "places_to_visit", "attractions", "tourism_guide"))


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
    execution_mode: str = "prod",
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

2. MANDATORY SHOW-AND-TELL STORY SYNCHRONY (THE IMAGE MUST FOLLOW THE STORY):
   - DOCUMENTARY FIRST PRINCIPLE: The visual image MUST directly depict and illustrate what is being narrated on screen at that exact moment. ZERO OUT-OF-BOUND IMAGERY PERMITTED!
   - 1:1 TOPIC-TO-VISUAL GROUNDING MATRIX:
     * Education & Schools -> Universities, colleges, schools, historic libraries, lecture halls, campus quadrangles, student research labs. (STRICTLY BAN generic mountains, rivers, or random streets).
     * Trade, Shipping & Logistics -> Deepwater container berths, cargo shipping yards, massive gantry cranes, container ships, wholesale trade markets, freight logistics warehouses. (STRICTLY BAN beaches or empty hills).
     * Airports, Aviation & Transit -> International airport runways, commercial passenger airliners taxiing or taking off, modern glass terminal concourses, air traffic control towers, apron cargo freighters, high-speed rail hubs. (STRICTLY BAN empty roads or generic sky).
     * Clean Energy & Utilities -> Modern wind turbine farms, solar arrays, geothermal steam stations, or hydroelectric dams. (STRICTLY BAN barren mountains or rocks).
     * Industry & Manufacturing -> Automotive mega-factories, robotic assembly arms, molten metal foundries, or aerospace hangars.
     * Farming & Agriculture -> Golden wheat/crop fields, vineyards, combine harvesters, center-pivot irrigation, or pastoral dairy paddocks.
     * Civics, Governance & Politics -> National parliament buildings, executive state houses, supreme courts, or monumental civic government plazas.
     * Population, Family & Daily Life -> Historic living town squares, community markets, or lively pedestrian avenues.
     * Geography, Wilderness & Geology -> (ONLY when narrating geography, geology, or national parks) Majestic mountain massifs, glacial fjords, or pristine ancient rainforests.
   - STRICT BAN ON OUT-OF-BOUNDS VISUALS: If narrating education, PROHIBIT mountains or factories. If narrating trade or airports, PROHIBIT beaches or forests. If narrating clean power, PROHIBIT bare rocks without infrastructure. The visual subject MUST be the physical manifestation of what is spoken!
   - OVERLAY & BADGE GROUNDING: On-screen badges ("chapter_stats", "fact_badge") must quantify what the eyes see.
   - ZERO PHANTOM SUBJECTS: In "scenes[].narration_text", every line must directly describe what is visible on screen. Triadic harmony: visual establishes subject -> narration explains it -> camera moves toward it.
   - In "audio_master.spoken_narration_script", unify per-scene narration into a poetic, scientifically accurate master narrative (~120 WPM).

3. SOUND DESIGN & CULTURALLY AUTHENTIC BGM (SUNO DIRECTORIAL SPEC):
   - In "audio_master", Gemini MUST author explicit musical instructions for Suno tailored to the destination's authentic heritage:
     * "suno_prompt": Descriptive acoustic & orchestral score direction (e.g. for Pacific Islands: traditional South Pacific acoustic guitar, gentle lali slit drums, soothing tropical trade-wind foley; for Rome: classical chamber strings, gentle Renaissance lute, understated orchestral swells).
     * "suno_musical_tags": Specific musical tags (e.g. "cinematic documentary score, traditional acoustic instruments, 48kHz, subtle, zero vocals, broadcast master").
     * "ducking_db": -18.0 dB (ducking BGM under spoken voiceover).
   - Target -14.0 LUFS broadcast loudness with -18.0 dB ducking during voiceover narration.

4. FLUID KINETICS & SURVIVAL REALISM (Rules 18, 20):
   - For mountain/extreme climates: depictions of biting sub-zero blizzards, wind gusts carving powder drifts, weathered timber shelters.
   - For rivers/waterfalls: parallel flow camera alignment, smooth glassy currents, zero static foam blobs.

5. DYNAMIC LOCAL KEN BURNS DRONE MOVEMENTS (80% OF SCENES - NEVER STATIC):
   - 80% of scenes use local Ken Burns / perspective drone ($0.00 compute).
   - NEVER A STATIC SCREEN: The camera MUST actively move ("dollyin", "dollyout", "pan-left", "pan-right", "tilt-up", "drift-up-right") across 4K images illustrating that scene's story topic (power grids, farmlands, universities, factories, or peaks).
   - Supported primitives: "dollyin", "dollyout", "pan-left", "pan-right", "tilt-up", "tilt-down", "orbit-left", "orbit-right".
   - Multi-stage: [{{"movement": "dollyin", "duration": 6.0}}, {{"movement": "pan-right", "duration": 4.0}}].

6. HIERARCHICAL CHAPTER & MULTI-SHOT CADENCE (BBC / NATGEO 4-6s VISUAL RHYTHM):
   - In broadcast documentary production, the Voiceover Track is the master clock. A 12-16s narration chapter cuts between 2 to 3 complementary perspectives inside "shots", ALL STRICTLY WITHIN THE CHAPTER'S TOPIC:
     * Shot 1 (Establishing Wide Vista): Sweeping 4K high-altitude aerial drone vista or wide panorama of the chapter's specific subject (e.g. grand university campus, container port, or international airport).
     * Shot 2 (Living Kinetic Perspective): Living AI diffusion clip (5.0s native duration, "motion_type": "ai_diffusion", "recommended_model": "h3_max" | "kling_v3_4k") capturing intrinsic physical movement of that same subject (e.g. students walking in quad, gantry cranes loading container ship, or jetliner taxiing on tarmac). NEVER use generic rushing river rapids or unrelated town squares!
     * Shot 3 (Intimate Detail / Macro Architecture): 85mm optical bokeh close-up, low-angle monumental perspective, or architectural relief of that same subject (e.g. university clocktower crest, cargo ship mooring lines, or air traffic control tower).
   - ZERO ARTIFICIAL EXTENSIONS: AI diffusion clips run for their native 5.0s length; complementary Ken Burns cutaways carry the remaining narration duration without temporal snap-backs.
   - Inside each chapter in "chapters" (or "scenes"), populate: "chapter_title", "chapter_subtitle", "fact_badge", "chapter_stats", "narration_text", and "shots": [shot1, shot2, shot3].

7. COMPREHENSIVE EDUCATIONAL DOCUMENTARY DIRECTIVES (COUNTRY & CITY EXPLORATION):
   When exploring a nation or city ("countries", "cities", "nations", "country", "city"), this is a high-caliber, BBC/NatGeo-grade EDUCATIONAL DOCUMENTARY exploring everything about the destination:
   A. FOR COUNTRY EXPLORATION & 360° DOSSIER ("countries", "nations", "country", "nation", "country_dossier", "country_profile"):
      Gemini must dedicate the ENTIRE documentary to ONE SINGLE COUNTRY as an authoritative, BBC/NatGeo-grade 360° Country Profile & Almanac, systematically structuring scenes across the Master Sovereign Syllabus below.
      * MANDATORY OVERLAY FIELDS: Output "chapter_title", "chapter_subtitle", "chapter_stats" (e.g. "Area: 551,695 km² • Coastline: 3,427 km"), and "fact_badge" (compact frosted pill badge, e.g. "⚡ 70% Clean Energy", "🏛️ Capital City").
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
      * Proper Photographic Image Matching Outro Subject: Breathtaking wide panoramic vista at twilight/sunset strictly matching the closing topic (e.g. vast wind turbine arrays at sunset for clean energy & sovereign resilience; illuminated capital skyline for modern governance; or majestic peaks for alpine geography). NEVER mismatch badges/stats with an unrelated visual!
      * Motion Engine: Smooth drone pull-back ("motion_type": "ken_burns", "recommended_model": "local_drone", "camera_movement": "dollyout").
      * Conclusion Narration: Authoritative, heartfelt closing reflection honoring the enduring spirit, resilience, and living soul of [Destination Name].

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
      * Rich Aesthetics: "Hyper-realistic 4K UHD, vibrant saturated natural colors (luminous turquoise, emerald green, golden amber, sun-baked terracotta, deep cobalt), razor-sharp architectural relief, Hasselblad H6D-100c medium-format clarity, warm golden sidelight, crystalline atmospheric depth, zero grey haze".
      * Motion: Slow forward drone push or smooth continuous 360-degree orbital banking flight around the landmark ("camera_movement": "slow_drone_forward"|"orbit-left"|"orbit-right").
   B. 20% Intimate 85mm Optical Bokeh (Scenes 4 & 6 - Education, People & Artisanal Craft):
      * Scene 4 (Education & Universities): "85mm portrait lens, f/1.8 creamy optical bokeh, luminous golden sunbeams streaming through gothic university library cloisters or historic cobblestones".
      * Scene 6 (Trade & Craftsmanship): "Tactile 85mm macro craftsmanship, f/1.8 depth-of-field, artisan hands shaping copper/glass or aged oak wine barrels in historic cellars".
      * Motion: Locked stationary cinemagraph hold ("camera_movement": "locked_stationary_cinemagraph"). In PROD mode, if humans/artisans/students appear, Gemini MUST assign "recommended_model": "kling_v3_4k" (or "kling_pro") with "motion_type": "ai_diffusion". Kling is required for authentic human anatomy and motion.
"""
    arch_mandate = get_nations_archetype_directive(
        archetype, duration_seconds=duration_seconds, custom_prompt=custom_prompt
    )
    if arch_mandate:
        doc_rules += f"\n11. THEMATIC ARCHETYPE DIRECTIVE:\n{arch_mandate}\n"
    is_auto = (duration_seconds is None or duration_seconds <= 0 or duration_seconds == -1)
    dur_guidance = (
        "   - DURATION MODE: AUTO (-1) / COMPLETE STORY. Gemini MUST author the COMPLETE, UNABRIDGED story covering ALL syllabus chapters (never skip, omit, or merge chapters).\n"
        if is_auto
        else f"   - DURATION MODE: TARGET DURATION ~{duration_seconds}s. Gemini MUST budget the narration words across ALL syllabus chapters so that the sum of narration durations equals approximately ~{duration_seconds}s. ALL chapters must still be covered!\n"
    )
    doc_rules += (
        "\n12. PASS 1 STORY FORMULATION & NARRATION-BASED DURATION MANDATE:\n"
        "   - FULL STORY FOR ALL CHAPTERS: The raw Gemini story script MUST ALWAYS author the FULL story covering ALL chapters in the syllabus.\n"
        f"{dur_guidance}"
        "   - NARRATION TIME DERIVATION: Author authoritative, measured 'narration_text' (~120 WPM, 2.0 words/sec).\n"
        "   - For each chapter, compute and output:\n"
        "     * 'origin_coords': [latitude, longitude] (floats),\n"
        "     * 'chapter_title', 'chapter_subtitle', 'fact_badge', 'chapter_stats', 'location_hub',\n"
        "     * 'estimated_narration_seconds': round(word_count / 2.0, 1),\n"
        "     * 'visual_padding_seconds': 3.0,\n"
        "     * 'duration_seconds': estimated_narration_seconds + visual_padding_seconds.\n"
        "   - ROOT DURATION EXTRACTION: Set root 'total_duration_seconds' = sum of all chapter 'duration_seconds', and root 'estimated_narration_duration_seconds' = sum of all chapter 'estimated_narration_seconds', so the rough production video duration is explicitly defined in the raw screenplay.\n"
    )
    doc_scene_schema = """      "chapter_title": "1. SOVEREIGN ESSENCE & FOUNDATIONS", "chapter_subtitle": "Founding Character & Sovereign Origins", "chapter_stats": "Area: [AREA] km² • Population: [POP]M", "fact_badge": "🏛️ CAPITAL: [CAPITAL_CITY]", "location_hub": "Capital City & Landmark Citadel", "origin_coords": [-18.1416, 178.4419],
      "estimated_narration_seconds": 12.0, "visual_padding_seconds": 3.0, "duration_seconds": 15.0,
      "narration_text": "Deep, poetic, authoritative voiceover narrative crafted for measured spoken delivery (~120 WPM)." """
    doc_root_schema = """  "estimated_narration_duration_seconds": 120.0, "total_words_count": 240,"""
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
        extra_root_schema=doc_root_schema,
        extra_scene_schema=doc_scene_schema,
        speech_cadence_wpm=speech_cadence_wpm,
        speech_words_per_sec=speech_words_per_sec,
        tts_provider_name=tts_provider_name,
        execution_mode=execution_mode,
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
    execution_mode: str = "prod",
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
    tour_root_schema = """  "itinerary_summary": [{"day": 1, "day_title": "Day 1 Highlights", "attractions": ["Landmark 1", "Landmark 2"], "total_attraction_time": "6.5 hrs", "total_travel_time": "1.0 hr", "total_walk_time": "25 mins", "total_drive_time": "35 mins", "transit_distance": "6.8 km", "total_travel_cost": "£24–£34", "meal_break": "1.0 hr Lunch Break"}],"""
    tour_scene_schema = """      "is_itinerary_overview": false, "is_map_transition": false, "origin_name": "Landmark 1", "destination_name": "Landmark 1", "origin_coords": [51.4994, -0.1273], "destination_coords": [51.4994, -0.1273], "distance_local": null, "transit_mode": null, "transit_duration": null, "approx_leg_cost": null, "attraction_name": "Landmark 1", "start_time": "09:00 AM", "end_time": "11:30 AM", "visit_duration": "2.5 hrs", "attraction_cost": "£29.00 Ticket", "transit_to_next": {"transit_mode": "drive", "transit_duration": "14 min cab", "approx_leg_cost": "£12–£16 Uber", "transit_narration": "Next, an eastbound drive traces the Thames toward the ancient Norman stronghold."},"""

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
        execution_mode=execution_mode,
    )



__all__ = [
    "TOUR_ARCHETYPES",
    "is_tour_archetype",
    "build_doc_directorial_prompt",
    "build_tour_directorial_prompt",
]
