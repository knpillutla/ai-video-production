"""Directorial Prompt Engineering for Documentary & Tour Studio Agents.

Defines dedicated system instructions for:
1. build_doc_directorial_prompt: Pure BBC/NatGeo wildlife & extreme environment documentaries.
2. build_tour_directorial_prompt: City/places tour archetypes (itinerary_map_tour, grand_tour, etc.).
"""

from __future__ import annotations

from typing import List, Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

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
    speech_cadence_wpm: int = 120,
    speech_words_per_sec: float = 2.0,
    tts_provider_name: str = "Azure Speech Neural",
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

2. AUTHORITATIVE & POETIC NARRATION (YPP Anti-Demonetization Guard):
   - In "audio_master.spoken_narration_script", provide poetic, scientifically accurate, and authoritative narration (~120 WPM).
   - Weave geological, ecological, and cultural lore into the narrative to guarantee full educational transformation.

3. SOUND DESIGN & ACOUSTIC SPATIAL FOLEY:
   - Grand orchestral elements (swelling strings, French horn fanfares, cello drone) layered with natural environmental foley.
   - Target -14.0 LUFS broadcast loudness with -18.0 dB ducking during voiceover narration.

4. FLUID KINETICS & SURVIVAL REALISM (Rules 18, 20):
   - For mountain/extreme climates: depictions of biting sub-zero blizzards, wind gusts carving powder drifts, weathered timber shelters.
   - For rivers/waterfalls: parallel flow camera alignment, smooth glassy currents, zero static foam blobs.
"""
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
        channel_id="earth_serenade",
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
        channel_id="earth_serenade",
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
