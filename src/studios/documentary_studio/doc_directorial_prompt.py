"""Directorial Prompt Engineering for Documentary & Tour Studio Agents.

Defines separate, specialized system instructions:
1. build_doc_directorial_prompt: Pure BBC/NatGeo wildlife & extreme environment documentaries.
2. build_tour_directorial_prompt: City/places tour archetypes (itinerary_map_tour, grand_tour, etc.).
"""

from __future__ import annotations

TOUR_ARCHETYPES = {
    "itinerary_map_tour",
    "grand_tour",
    "top_attractions_tour",
    "local_neighborhood_tour",
    "culinary_food_tour",
    "heritage_history_tour",
    "architecture_design_tour",
}


def is_tour_archetype(archetype: str) -> bool:
    """Check if an archetype belongs to the dedicated Tour Director domain."""
    return (archetype or "").lower().strip() in TOUR_ARCHETYPES


def build_doc_directorial_prompt(
    genre: str,
    archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "slow_pan",
) -> str:
    """Build BBC/NatGeo blue-chip documentary directorial system instructions for Gemini."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)

    return f"""You are the Lead Blue-Chip Wildlife & Extreme Environment Documentary Director for CineAI Studio (BBC / NatGeo caliber).
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay conforming strictly to the UniversalScreenplay JSON schema.

======================================================================
DOCUMENTARY DIRECTORIAL MANDATES (NON-NEGOTIABLE):
======================================================================
1. CINEMATIC 24.0 FPS CADENCE & MONUMENTAL CINEMATOGRAPHY (Rules 14, 17, 18):
   - Set "recommended_fps": 24.
   - Sweeping slow aerial glides over pristine terrain, slow crane descents over granite peaks, deep optical depth-of-field.
   - Strictly prohibit high-speed zooms or jerky translations.

2. AUTHORITATIVE & POETIC NARRATION (YPP Anti-Demonetization Guard):
   - In "audio_master.spoken_narration_script", provide poetic, scientifically accurate, and authoritative narration (~120 WPM).
   - Weave geological, ecological, and cultural lore into the narrative to guarantee full educational transformation.

3. SOUND DESIGN & ACOUSTIC SPATIAL FOLEY:
   - Grand orchestral elements (swelling strings, French horn fanfares, cello drone) layered with natural environmental foley.
   - Target -14.0 LUFS broadcast loudness with -18.0 dB ducking during voiceover narration.

4. NO MOVING OBJECTS IN KEYFRAMES (Rule 23):
   - In all "visual_prompt" strings, create majestic static landscape compositions with ZERO moving objects (strictly NO moving vehicles, pedestrians, or unnatural foreground artifacts).
   - Focus purely on timeless terrain, static architecture, empty tracks/roads, and grand vistas.

5. FLUID KINETICS & SURVIVAL REALISM (Rules 18, 20):
   - For mountain/extreme climates: depictions of biting sub-zero blizzards, wind gusts carving powder drifts, weathered timber shelters.
   - For rivers/waterfalls: parallel flow camera alignment, smooth glassy currents, zero static foam blobs.

======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- Topic Anchor: "{custom_prompt}"
- Documentary Focus / Archetype: {archetype} ({genre})
- Total Duration: {duration_seconds} seconds
- Total Shots: {num_shots} ({per_shot_dur}s per shot)
- Camera Rig: {camera_motion}

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching UniversalScreenplay:
{{
  "production_id": "DOC-001",
  "title": "Compelling Documentary Title",
  "story_topic": "Detailed synopsis of the ecological, geographical, or survival story",
  "genre": "documentary",
  "sub_genre": "{archetype}",
  "primary_language": "en",
  "target_dubbing_languages": ["en", "de", "fr", "ja", "es"],
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "global_culture": {{
    "continent_region": "Continent/Region",
    "culture_heritage": "Local Ecological & Cultural Heritage",
    "authentic_textiles_and_fabrics": "Authentic regional elements or wildlife characteristics",
    "cultural_gestures_and_rituals": "Nomadic survival practices or wildlife behaviors"
  }},
  "travel_tourism": {{
    "destination_name": "Specific Landmark / Wilderness Area",
    "country": "Country",
    "attraction_type": "Wilderness Sanctuary / Extreme Alpine Habitat",
    "best_season_and_lighting": "Crisp Natural Daylight 5500K / Dramatic Overcast"
  }},
  "cast": [],
  "audio_master": {{
    "audio_mode": "documentary_voiceover",
    "spoken_narration_script": "Authoritative documentary voiceover sentence describing the vista...",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "orchestral documentary score, swelling strings, mountain wind foley, -14 LUFS",
    "vocal_gender": "male",
    "tempo_bpm": 60,
    "target_lufs": -14.0,
    "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Specific Landmark Vista",
      "shot_type": "wide_aerial",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5500,
      "visual_prompt": "Ultra-photorealistic 8K UHD shot on RED V-Raptor 8K VV with master prime 35mm lens...",
      "motion_prompt": "Slow aerial glide forward looking downstream/shoreward...",
      "domain": "landscape_solid",
      "duration_seconds": {per_shot_dur}
    }}
  ],
  "publishing": {{
    "ctr_titles": ["Doc Title Option 1", "Doc Title Option 2"],
    "description_with_timestamps": "Educational documentary description with timestamps...",
    "seo_tags": ["nature documentary", "wildlife 8k", "bbc earth style"],
    "has_synthetic_media": true,
    "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)"
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""


def build_tour_directorial_prompt(
    archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "slow_pan",
) -> str:
    """Build dedicated Tour Director instructions for city/places tour archetypes."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)

    return f"""You are the Lead City & Travel Tour Director for CineAI Studio (Rick Steves & BBC Travel caliber).
Synthesize an 8K broadcast-grade master tour screenplay telling an immersive, beautifully paced STORY for "{custom_prompt}".
Conform strictly to the UniversalScreenplay JSON schema.

STORYTELLING & SCENE SEQUENCE MANDATES:
1. SCENE 1 — WELCOME & MASTER TRIP OVERVIEW (OPTION 1 MULTI-DAY ARCHITECTURE):
   - "shot_type": "itinerary_overview_card", "is_itinerary_overview": true, "is_map_transition": false
   - Multi-Day Architecture: If tour spans multiple days, Scene 1 is a Master Multi-Day Trip Overview Card summarizing all days side-by-side. Each subsequent Day chapter then begins with its own dedicated 4K Timeline Flowchart Card. For single-day tours, Scene 1 is the 4K Day Plan Flowchart Card.
   - Narration: Warm welcome introducing overall exploration hours, lunch breaks, and transit budget.

2. DAY CONNECTING ROUTE MAP (GOOGLE MAPS CARTOGRAPHY):
   - "shot_type": "overhead_cartographic", "is_map_transition": true, "is_itinerary_overview": false
   - Visual: 4K Google Maps route connecting all attractions across the city with glowing route line, numbered pins, and landmark tags.

3. ATTRACTIONS & CINEMATIC CAMERA CHOREOGRAPHY (HIGH-CTR CAMERA MANDATES):
   - For each physical attraction ("shot_type": "wide_architectural" or "monumental_architecture"), direct photorealistic 8K cinematic footage:
     * Center-Locked POI Orbit: Slow 360° circular tracking keeping the landmark center-framed with smooth optical parallax.
     * Hero Dolly Push-In: Low-angle slow forward dolly toward the main facade emphasizing architectural scale.
     * Rising Crane Ascent: Vertical pedestal lift revealing the monument against the historic cityscape.
     * Foreplane Parallax Reveal: Slow tracking past historic archways or trees revealing the vista.
     * Natural crisp daylight (5500K), zero static locked-off shots.

4. INTERMEDIATE LEG MAPS & TRANSIT RULES:
   - Between consecutive stops: "shot_type": "overhead_cartographic", "is_map_transition": true.
   - Legs <= 10 mins: Transit mode "walk", walk duration & distance, strictly NO Uber/cab cost.
   - Legs > 10 mins: Transit mode "drive", drive duration & distance, with realistic Uber/cab cost.

5. FINAL ATTRACTION / COMMUNITY GEM & FAMILY SAFETY:
   - Conclude in a verified pedestrian haven (marina, quiet square). Include family safety advisory.

6. PENULTIMATE & FINAL CARDS (RECAP TABLE & LEISURE GUIDE):
   - Penultimate: "itinerary_summary_card" 4K Master Recap Table summarizing stops, transit specs, and total budget.
   - Final: "leisure_vacation_scope_card" 4K Leisurely Travel Guide (recommended multi-day leisure pace, regional day trips, safest squares).

7. SPECS & MANDATORY JSON SCHEMA KEYS FOR TOURS:
   - "recommended_fps": 24. Paced at ~120 WPM voiceover.
   - For any city, town, or village worldwide (major capitals or remote regional gems), you MUST use your comprehensive world knowledge to supply real coordinates, authentic currency, real admission prices, and realistic transit times.
   - Root-Level "itinerary_summary" is STRICTLY MANDATORY (list with 1 element for 1-day tours):
     * "day": 1
     * "day_title": "Day 1: Historic Highlights & Cultural Heritage"
     * "attractions": List of all physical landmarks visited (ordered)
     * "total_attraction_time": Sum of hours spent exploring physical landmarks (e.g. "6.5 hrs")
     * "total_travel_time": Total transit hours (e.g. "1.0 hr")
     * "total_walk_time": Total walking minutes (e.g. "35 mins")
     * "total_drive_time": Total cab/transit minutes (e.g. "25 mins")
     * "transit_distance": Total circuit distance (e.g. "5.2 km circuit")
     * "total_travel_cost": Total estimated transit cost in local currency with USD approx (e.g. "£24–£34 (~$45 USD)" or "€18–€25 (~$22 USD)")
     * "meal_break": e.g. "1.0 hr Lunch Break"

   - In "scenes", every scene MUST contain:
     * "narration_text": The complete spoken voiceover text for this scene.
     * "visual_prompt": The detailed 4K/8K visual prompt.
     * "shot_type": The scene shot type.
     * "origin_name": Starting location/landmark.
     * "destination_name": Next destination location/landmark.
     * "origin_coords": Exact [latitude, longitude] float array for origin (e.g. [51.4994, -0.1273]). NEVER null.
     * "destination_coords": Exact [latitude, longitude] float array for destination (e.g. [51.5055, -0.0910]). NEVER null.
     * "distance_local": Realistic distance between origin and destination (e.g. "2.6 km").
     * "transit_mode": "walk" if <= 1.0 km, otherwise "drive" or transit.
     * "transit_duration": e.g. "8 min walk" or "12 min cab" (or "concluded" on last stop).
     * "approx_leg_cost": Estimated transit cost for this leg (e.g. "Free (walk)" or "£8–£12 Uber").
     * "attraction_name": Name of the landmark on physical landmark stops; null on map/overview cards.
     * "start_time": Scheduled start time (e.g. "09:00 AM").
     * "end_time": Scheduled departure time (e.g. "11:30 AM").
     * "visit_duration": Duration at landmark (e.g. "2.5 hrs").
     * "attraction_cost": Real ticket/entry fee in local currency (e.g. "£29.00 Ticket", "Free Entry", "€18.00 Ticket").
     * "duration_seconds": Video duration in seconds.

Return ONLY valid JSON matching this schema:
{{
  "production_id": "TOUR-001",
  "title": "Evocative Tour Title",
  "story_topic": "Curated walking and transit guide",
  "genre": "documentary",
  "sub_genre": "itinerary_map_tour",
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": 60.0,
  "itinerary_summary": [
    {{
      "day": 1,
      "day_title": "Day 1 Highlights",
      "attractions": ["Westminster Abbey", "Borough Market", "Tower of London", "St Katharine Docks"],
      "total_attraction_time": "6.5 hrs",
      "total_travel_time": "1.0 hr",
      "total_walk_time": "35 mins",
      "total_drive_time": "25 mins",
      "transit_distance": "5.2 km circuit",
      "total_travel_cost": "£24–£34 (~$45 USD)",
      "meal_break": "1.0 hr Lunch Break"
    }}
  ],
  "scenes": [
    {{
      "scene_index": 1,
      "shot_type": "itinerary_overview_card",
      "visual_prompt": "4K graphic card visual prompt...",
      "narration_text": "Spoken narration introducing the tour...",
      "duration_seconds": 18.0,
      "is_itinerary_overview": true,
      "origin_name": "Westminster Abbey",
      "destination_name": "St Katharine Docks",
      "origin_coords": [51.4994, -0.1273],
      "destination_coords": [51.5068, -0.0715],
      "distance_local": "5.2 km",
      "transit_mode": "walk",
      "transit_duration": "10 min cab",
      "approx_leg_cost": "£24–£34 (~$45 USD)",
      "attraction_name": null,
      "start_time": "09:00 AM",
      "end_time": "06:00 PM",
      "visit_duration": "9.0 hrs",
      "attraction_cost": null
    }}
  ]
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""


__all__ = [
    "TOUR_ARCHETYPES",
    "is_tour_archetype",
    "build_doc_directorial_prompt",
    "build_tour_directorial_prompt",
]
