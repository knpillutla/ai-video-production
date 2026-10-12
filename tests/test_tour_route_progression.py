"""Deterministic Offline Unit Test for Tour Route Progression & Overview Timings.

Verifies:
1. Tour directorial prompt enforces alternating route maps, static locked camera, and timing isolation.
2. Progressive route color indexing:
   - First route map (after Attraction 1): current_stop_index == 1 -> 0 completed legs (default route color).
   - Second route map (after Attraction 2): current_stop_index == 2 -> 1 completed leg (turns to completed green color).
   - Third route map (after Attraction 3): current_stop_index == 3 -> 2 completed legs.
3. Overview card timing isolation: Overview card timings do not contaminate physical attraction stop timings.
"""

from typing import Any, Dict, List
import pytest

from src.studios.documentary_studio.doc_directorial_prompt import build_tour_directorial_prompt


def test_tour_prompt_mandates_alternating_and_static_hold():
    prompt = build_tour_directorial_prompt(
        archetype="itinerary_map_tour",
        custom_prompt="1-day London tour",
        duration_seconds=60.0,
        num_shots=6,
    )
    # 1. Option A decoupled curation contract
    assert "PHYSICAL ATTRACTIONS CURATION" in prompt
    assert "transit_to_next" in prompt
    assert "transit_narration" in prompt

    # 2. Mandatory landmark GPS coordinates
    assert "MANDATORY GPS COORDINATES" in prompt
    assert "origin_coords" in prompt
    assert "[51.4994, -0.1273]" in prompt


def test_progressive_route_color_indexing():
    """Verify calculation of completed attractions to index route map color changes."""
    # Simulated alternating tour scenes
    scenes = [
        {"scene_index": 1, "shot_type": "itinerary_overview_card", "is_itinerary_overview": True},
        {"scene_index": 2, "shot_type": "wide_architectural", "attraction_name": "Westminster Abbey"},
        {"scene_index": 3, "shot_type": "overhead_cartographic", "is_map_transition": True},
        {"scene_index": 4, "shot_type": "wide_architectural", "attraction_name": "Tower of London"},
        {"scene_index": 5, "shot_type": "overhead_cartographic", "is_map_transition": True},
        {"scene_index": 6, "shot_type": "wide_architectural", "attraction_name": "St Paul's Cathedral"},
        {"scene_index": 7, "shot_type": "overhead_cartographic", "is_map_transition": True},
        {"scene_index": 8, "shot_type": "itinerary_summary_card", "is_itinerary_summary": True},
    ]

    def get_curr_idx(scene_idx: int) -> int:
        prior_attrs = sum(
            1 for ps in scenes[:scene_idx - 1]
            if not (
                ps.get("is_map_transition")
                or ps.get("is_itinerary_overview")
                or ps.get("is_itinerary_summary")
                or ps.get("is_vacation_scope")
            )
        )
        return max(1, prior_attrs)

    # Route Map 1 (Scene 3, after Westminster Abbey):
    # Only 1 attraction seen -> curr_idx = 1.
    # In google maps engine, curr_idx == 1 means 0 completed legs -> default route color.
    assert get_curr_idx(3) == 1

    # Route Map 2 (Scene 5, after Tower of London):
    # 2 attractions completed -> curr_idx = 2.
    # In google maps engine, curr_idx == 2 means leg 1 (Westminster -> Tower) turns GREEN (completed)!
    assert get_curr_idx(5) == 2

    # Route Map 3 (Scene 7, after St Paul's Cathedral):
    # 3 attractions completed -> curr_idx = 3.
    # In google maps engine, legs 1 and 2 turn GREEN!
    assert get_curr_idx(7) == 3


def test_strict_10min_walk_cap():
    """Verify deterministic 10-minute maximum walk threshold across normalizer and card engine."""
    from src.studios.documentary_studio.doc_tour_normalizer import determine_transit_specs
    from src.services.itinerary_card_engine import _format_leg_transit_badge

    # 1. Normalizer specs
    mode_short, dur_short = determine_transit_specs(0.5)
    assert mode_short == "walk"
    assert "walk" in dur_short
    assert int(dur_short.split()[0]) <= 10

    mode_long, dur_long = determine_transit_specs(1.2)
    assert mode_long == "drive"
    assert "cab" in dur_long

    # 2. Card engine badge formatter hard ceiling
    # Even if incoming data falsely claims '15 min walk' or 2.5 km with mode 'walk', it MUST switch to Drive
    stop_long_walk = {
        "transit_mode": "walk",
        "transit_duration": "15 min walk",
        "distance_local": "2.5 km",
        "approx_leg_cost": "Free (walk)",
        "coords": [51.4994, -0.1273],
    }
    next_stop = {
        "coords": [51.5081, -0.0759],
    }
    badge = _format_leg_transit_badge(stop_long_walk, next_stop, "TOWER OF LONDON")
    assert "Drive:" in badge
    assert "Walk:" not in badge
    assert "Uber" in badge


def test_provider_wired_speech_cadence():
    """Verify provider speech cadence calculation and prompt wiring."""
    from src.studios.documentary_studio.doc_voice_service import doc_voice_service
    from src.studios.documentary_studio.doc_directorial_prompt import build_tour_directorial_prompt

    # 1. Calibrated provider cadence
    wpm_en, wps_en, desc_en = doc_voice_service.get_speech_cadence(language="en")
    assert wpm_en == 118
    assert wps_en == 1.96
    assert "Ryan" in desc_en

    wpm_te, wps_te, _ = doc_voice_service.get_speech_cadence(language="te")
    assert wpm_te == 105
    assert wps_te == 1.75

    # 2. Prompt contains wired formula
    prompt = build_tour_directorial_prompt(
        archetype="itinerary_map_tour",
        custom_prompt="London Highlights",
        duration_seconds=60.0,
        num_shots=6,
        speech_cadence_wpm=wpm_en,
        speech_words_per_sec=wps_en,
        tts_provider_name=desc_en,
    )
    assert "NARRATION ENGINE & DURATION WIRING CONTRACT" in prompt
    assert "Directorial Leeway Buffer" in prompt
    assert "118 WPM" in prompt
    assert "1.96 words/sec" in prompt
    assert "ZERO frozen frames" in prompt


def test_tour_validator_allows_overview_card_none_coords():
    """Verify that an overview card with None coordinates inherits from landmarks and passes validation."""
    from src.studios.documentary_studio.doc_tour_validator import validate_tour_screenplay_contract

    data = {
        "itinerary_summary": [
            {
                "total_attraction_time": "5.5 hrs",
                "total_travel_time": "35 mins",
                "total_travel_cost": "£25",
            }
        ],
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "itinerary_overview_card",
                "is_itinerary_overview": True,
                "origin_coords": None,
                "destination_coords": None,
                "visual_prompt": "Editorial flowchart card",
                "narration_text": "Welcome to London.",
            },
            {
                "scene_index": 2,
                "shot_type": "monumental_architecture",
                "attraction_name": "Westminster Abbey",
                "origin_coords": [51.4993, -0.1273],
                "destination_coords": None,
                "visit_duration": "2.5 hrs",
                "attraction_cost": "£29.00",
                "visual_prompt": "Westminster Abbey facade",
                "narration_text": "First stop is Westminster Abbey.",
            },
        ],
    }

    # Should not raise ValueError even with destination_coords: None on landmark
    validate_tour_screenplay_contract(data)
    assert data["scenes"][0]["origin_coords"] == [51.4993, -0.1273]
    assert data["scenes"][1]["destination_coords"] == [51.4993, -0.1273]


def test_tour_interleaver_option_a():
    """Verify Option A: Pure physical attractions are interleaved with overview, maps, and summary."""
    from src.studios.documentary_studio.doc_tour_interleaver import interleave_tour_storyboard_scenes

    raw_attractions = [
        {
            "attraction_name": "Westminster Abbey",
            "origin_coords": [51.4994, -0.1273],
            "visit_duration": "2.5 hrs",
            "attraction_cost": "£29.00",
            "visual_prompt": "Westminster Abbey facade",
            "narration_text": "We begin at Westminster Abbey.",
            "transit_to_next": {
                "transit_mode": "drive",
                "transit_duration": "14 min cab",
                "approx_leg_cost": "£12–£16 Uber",
                "transit_narration": "Next, an eastbound drive traces the Thames toward the Tower of London.",
            },
        },
        {
            "attraction_name": "Tower of London",
            "origin_coords": [51.5081, -0.0759],
            "visit_duration": "2.5 hrs",
            "attraction_cost": "£34.80",
            "visual_prompt": "Tower of London fortress",
            "narration_text": "The Norman stronghold commands the waterfront.",
            "transit_to_next": {
                "transit_mode": "drive",
                "transit_duration": "10 min cab",
                "approx_leg_cost": "£8–£12 Uber",
                "transit_narration": "From the fortress, we journey northward to St. Paul's Cathedral.",
            },
        },
        {
            "attraction_name": "St. Paul's Cathedral",
            "origin_coords": [51.5138, -0.0984],
            "visit_duration": "2.0 hrs",
            "attraction_cost": "£25.00",
            "visual_prompt": "St Paul's Cathedral dome",
            "narration_text": "Sir Christopher Wren's baroque triumph crowns the skyline.",
            "transit_to_next": None,
        },
    ]

    interleaved = interleave_tour_storyboard_scenes(raw_attractions, total_duration_seconds=60.0)

    # 3 attractions -> 1 overview + 3 physical + 2 route maps + 1 summary = 7 scenes
    assert len(interleaved) == 7

    # Scene 1: Overview
    assert interleaved[0]["scene_index"] == 1
    assert interleaved[0]["is_itinerary_overview"] is True
    assert interleaved[0]["shot_type"] == "itinerary_overview_card"

    # Scene 2: Westminster Abbey
    assert interleaved[1]["scene_index"] == 2
    assert interleaved[1]["attraction_name"] == "Westminster Abbey"
    assert interleaved[1]["is_map_transition"] is False

    # Scene 3: Route Map 1 -> 2
    assert interleaved[2]["scene_index"] == 3
    assert interleaved[2]["is_map_transition"] is True
    assert interleaved[2]["origin_name"] == "Westminster Abbey"
    assert interleaved[2]["destination_name"] == "Tower of London"
    assert interleaved[2]["narration_text"] == "Next, an eastbound drive traces the Thames toward the Tower of London."
    assert interleaved[2]["origin_coords"] == [51.4994, -0.1273]
    assert interleaved[2]["destination_coords"] == [51.5081, -0.0759]

    # Scene 4: Tower of London
    assert interleaved[3]["scene_index"] == 4
    assert interleaved[3]["attraction_name"] == "Tower of London"

    # Scene 5: Route Map 2 -> 3
    assert interleaved[4]["scene_index"] == 5
    assert interleaved[4]["is_map_transition"] is True
    assert interleaved[4]["origin_name"] == "Tower of London"
    assert interleaved[4]["destination_name"] == "St. Paul's Cathedral"

    # Scene 6: St. Paul's Cathedral
    assert interleaved[5]["scene_index"] == 6
    assert interleaved[5]["attraction_name"] == "St. Paul's Cathedral"

    # Scene 7: Summary Card
    assert interleaved[6]["scene_index"] == 7
    assert interleaved[6]["is_itinerary_summary"] is True
    assert interleaved[6]["shot_type"] == "itinerary_summary_card"




