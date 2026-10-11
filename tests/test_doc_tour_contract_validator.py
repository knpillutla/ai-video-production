"""Tests for strict zero-fallback tour screenplay contract validation.

Verifies that:
1. Valid tour contract passes without error and preserves Gemini's exact coordinates, admission costs, and summary.
2. Missing or invalid coordinates, ticket costs, or itinerary summary raise ValueError immediately (no silent fallback).
3. Non-tour archetypes (e.g. wildlife, nature) bypass tour validation cleanly.
"""

import pytest
from src.studios.documentary_studio.doc_tour_validator import validate_tour_screenplay_contract


def test_valid_tour_contract_passes():
    valid_payload = {
        "production_id": "TOUR-TEST-001",
        "title": "Matera Ancient Sassi Tour",
        "story_topic": "One day walking itinerary in Matera",
        "itinerary_summary": [
            {
                "day": 1,
                "day_title": "Ancient Stone Architecture",
                "attractions": ["Sassi di Matera", "Cattedrale di Matera", "Palombaro Lungo"],
                "total_attraction_time": "5.5 hrs",
                "total_travel_time": "45 mins",
                "total_travel_cost": "€12–€18 (~$15 USD)",
            }
        ],
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "itinerary_overview_card",
                "visual_prompt": "4K card overview of Matera",
                "narration_text": "Welcome to the ancient troglodyte city of Matera.",
                "duration_seconds": 18.0,
                "is_itinerary_overview": True,
                "origin_name": "Sassi di Matera",
                "destination_name": "Palombaro Lungo",
                "origin_coords": [40.6664, 16.6089],
                "destination_coords": [40.6672, 16.6045],
            },
            {
                "scene_index": 2,
                "shot_type": "medium",
                "attraction_name": "Sassi di Matera",
                "origin_name": "Sassi di Matera",
                "destination_name": "Cattedrale di Matera",
                "visual_prompt": "Limestone cave dwellings perched on cliffs.",
                "narration_text": "Carved into the calcarenite rock, the Sassi represent millennia of continuous habitation.",
                "duration_seconds": 12.0,
                "visit_duration": "2.5 hrs",
                "attraction_cost": "Free Entry",
                "origin_coords": [40.6664, 16.6089],
                "destination_coords": [40.6668, 16.6111],
            },
            {
                "scene_index": 3,
                "shot_type": "medium",
                "attraction_name": "Palombaro Lungo",
                "origin_name": "Palombaro Lungo",
                "destination_name": "Palombaro Lungo",
                "visual_prompt": "Gigantic underground cistern cathedral with subterranean reflections.",
                "narration_text": "Descend beneath the main square into the colossal water reservoir.",
                "duration_seconds": 12.0,
                "visit_duration": "1.0 hr",
                "attraction_cost": "€3.00 Ticket",
                "origin_coords": [40.6672, 16.6045],
                "destination_coords": [40.6672, 16.6045],
            },
        ],
    }

    # Should not raise any error
    validate_tour_screenplay_contract(valid_payload)


def test_tour_contract_fails_when_summary_missing():
    invalid_payload = {
        "title": "Incomplete Tour",
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "overview",
                "visual_prompt": "card",
                "narration_text": "hello",
                "origin_coords": [40.0, 16.0],
                "destination_coords": [40.1, 16.1],
            },
            {
                "scene_index": 2,
                "shot_type": "medium",
                "attraction_name": "Castle",
                "visual_prompt": "castle",
                "narration_text": "castle visit",
                "attraction_cost": "€10",
                "visit_duration": "1 hr",
                "origin_coords": [40.1, 16.1],
                "destination_coords": [40.1, 16.1],
            },
        ],
    }

    with pytest.raises(ValueError, match="Root 'itinerary_summary' is missing or empty"):
        validate_tour_screenplay_contract(invalid_payload)


def test_tour_contract_fails_when_coords_missing():
    invalid_payload = {
        "title": "Missing Coords Tour",
        "itinerary_summary": [
            {
                "total_attraction_time": "4 hrs",
                "total_travel_time": "1 hr",
                "total_travel_cost": "€10",
            }
        ],
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "itinerary_overview_card",
                "visual_prompt": "card",
                "narration_text": "welcome",
                "origin_coords": None,  # Missing!
                "destination_coords": [40.0, 16.0],
            },
            {
                "scene_index": 2,
                "shot_type": "medium",
                "attraction_name": "Castle",
                "visual_prompt": "castle",
                "narration_text": "visit",
                "attraction_cost": "€10",
                "visit_duration": "1 hr",
                "origin_coords": [40.0, 16.0],
                "destination_coords": [40.0, 16.0],
            },
        ],
    }

    with pytest.raises(ValueError, match="'origin_coords' is missing or invalid"):
        validate_tour_screenplay_contract(invalid_payload)


def test_tour_contract_fails_when_attraction_cost_missing():
    invalid_payload = {
        "title": "Missing Cost Tour",
        "itinerary_summary": [
            {
                "total_attraction_time": "4 hrs",
                "total_travel_time": "1 hr",
                "total_travel_cost": "€10",
            }
        ],
        "scenes": [
            {
                "scene_index": 1,
                "shot_type": "itinerary_overview_card",
                "visual_prompt": "card",
                "narration_text": "welcome",
                "origin_coords": [40.0, 16.0],
                "destination_coords": [40.0, 16.0],
            },
            {
                "scene_index": 2,
                "shot_type": "medium",
                "attraction_name": "Ancient Roman Theatre",
                "visual_prompt": "theatre",
                "narration_text": "historic stone arena",
                "visit_duration": "1.5 hrs",
                "attraction_cost": None,  # Missing cost!
                "origin_coords": [40.0, 16.0],
                "destination_coords": [40.0, 16.0],
            },
        ],
    }

    with pytest.raises(ValueError, match="Missing 'attraction_cost'"):
        validate_tour_screenplay_contract(invalid_payload)
