"""Directorial Prompt Engineering for Documentary Studio Agent.

Enforces 24.0 fps film cadence, authoritative voiceover narration, rich geographical/ecological lore,
and YPP monetization compliance (Rules 11, 14, 17, 18).
"""

from __future__ import annotations


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
   - In all "visual_prompt" strings, create majestic static landscape and architectural compositions with ZERO moving objects (strictly NO moving trains, vehicles, cars, boats, airplanes, pedestrians, or animals).
   - Moving objects produce smear/warp artifacts when camera perspective moves. Focus purely on timeless terrain, static architecture, empty tracks/roads, and grand vistas.

5. GENERIC CITY/PLACES TOURS & AUTONOMOUS ATTRACTION CURATION:
   - Zero User Burden for Attractions: When the user enters only a city name and duration (e.g. "Oslo Tour, 2 Days" or "London Tour, 3 Days"), Gemini MUST autonomously research and curate the top famous attractions from its global travel knowledge base. Do NOT require the user to name attractions.
   - Strict 9:00 AM to 6:00 PM Daylight Window: For all tours, schedule visits strictly between 9:00 AM and 6:00 PM local time. Frame all landmark images in crisp natural daylight (5400K-5600K) or warm late-afternoon golden hour (3500K-4500K). Strictly PROHIBIT dark night scenes, dim moonlight, or pitch-black darkness. The last attraction must conclude by 6:00 PM.
   - Realistic Time Budgeting: Sequence attractions logically by geographic proximity and realistic visiting time (e.g. 2-3 major sights per day, grouping nearby landmarks like waterfronts or historic districts together).
   - For "itinerary_map_tour": Divide the sequence into an ordered travel plan (e.g. Day 1: Morning, Day 1: Afternoon, Day 2: Morning). Alternate between clean, minimalist 8K illustrated topographic route map transition scenes (showing the transit route between stops) and grand architectural landmark vistas.
   - For "grand_tour" / "top_attractions_tour": Autonomously select and sequence the city's most defining monuments and iconic viewpoints in order of cultural prominence.
   - For "local_neighborhood_tour": Autonomously identify the city's most authentic bohemian quarters, local squares, cobblestone street corners, and artisan cafes.
   - For "culinary_food_tour": Autonomously highlight the city's authentic historic food halls, local delicacies, and traditional markets.
   - For "heritage_history_tour" / "architecture_design_tour": Autonomously curate the city's pivotal historic citadels and architectural masterworks across centuries.

6. FLUID KINETICS & SURVIVAL REALISM (Rules 18, 20):
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
      "location_hub": "Specific Wilderness Vista",
      "shot_type": "wide_aerial",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5500,
      "visual_prompt": "Ultra-photorealistic 8K UHD shot on RED V-Raptor 8K VV with master prime 35mm lens. Sweeping cinematic vista...",
      "motion_prompt": "Slow aerial glide forward looking downstream/shoreward. Smooth laminar fluid movement...",
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
