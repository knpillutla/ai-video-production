"""Targeted unit tests for 4K Hierarchical Itinerary Timeline Card Engine."""

from pathlib import Path
import cv2
import pytest

from src.services.itinerary_card_engine import render_4k_itinerary_hierarchy_card


def test_render_4k_itinerary_hierarchy_card(tmp_path):
    stops = [
        {
            "attraction_name": "Westminster Abbey",
            "start_time": "09:00 AM",
            "end_time": "11:30 AM",
            "visit_duration": "2.5 hrs",
            "attraction_cost": "£29.00 Ticket",
            "distance_local": "0.6 km",
            "transit_duration": "8 min walk",
            "approx_leg_cost": "£6–£9 Uber",
        },
        {
            "attraction_name": "Borough Market",
            "start_time": "11:45 AM",
            "end_time": "01:15 PM",
            "visit_duration": "1.5 hrs",
            "attraction_cost": "Free Entry",
            "distance_local": "1.4 km",
            "transit_duration": "18 min walk",
            "approx_leg_cost": "£8–£12 Uber",
        },
        {
            "attraction_name": "Tower of London",
            "start_time": "01:35 PM",
            "end_time": "04:05 PM",
            "visit_duration": "2.5 hrs",
            "attraction_cost": "£34.00 Ticket",
            "distance_local": "0.8 km",
            "transit_duration": "10 min walk",
            "approx_leg_cost": "£7–£10 Uber",
        },
        {
            "attraction_name": "St Katharine Docks",
            "start_time": "04:15 PM",
            "end_time": "06:00 PM",
            "visit_duration": "1.75 hrs",
            "attraction_cost": "Free Entry",
            "distance_local": "concluded",
            "transit_duration": "concluded",
            "approx_leg_cost": "concluded",
        },
    ]

    summary = {
        "transit_distance": "5.2 km Circuit",
        "total_attraction_time": "6.5 hrs Exploring",
        "total_travel_time": "1.0 hr Transit",
        "total_travel_cost": "£24–£34 (~$45 USD)",
    }

    out_file = tmp_path / "test_hierarchy_card_4k.jpg"
    res = render_4k_itinerary_hierarchy_card(
        tour_title="London Historic Highlights",
        stops=stops,
        output_path=out_file,
        summary=summary,
    )

    assert res.is_file()
    assert res.stat().st_size > 1000
    img = cv2.imread(str(res))
    assert img.shape == (2160, 3840, 3)
