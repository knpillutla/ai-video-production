"""Documentary Tour Storyboard Scene Interleaver.

Decouples Gemini's physical landmark curation from intermediate cartographic
transit maps and infographic overview/summary cards.
Automatically injects:
  1. Scene 1: Itinerary Overview Card (Header schedule & stops)
  2. Scene 2: Physical Attraction 1
  3. Scene 3: Overhead Cartographic Route Map 1 -> 2 (using transit_to_next)
  4. Scene 4: Physical Attraction 2
  ...
  Final Scene: Itinerary Summary Card (Full recap table)
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional
from src.studios.documentary_studio.doc_tour_normalizer import (
    calculate_geodesic_distance_km,
    determine_transit_specs,
    resolve_coordinates,
)


def _is_card_or_map(sc: Dict[str, Any]) -> bool:
    """Checks if a scene is already an informational card or map transition."""
    shot_type_str = str(sc.get("shot_type", "")).lower()
    return bool(
        sc.get("is_itinerary_overview")
        or sc.get("is_itinerary_summary")
        or sc.get("is_vacation_scope")
        or sc.get("is_map_transition")
        or any(w in shot_type_str for w in ("overview", "summary", "vacation", "map", "cartographic"))
    )


def interleave_tour_storyboard_scenes(
    raw_scenes: List[Dict[str, Any]],
    itinerary_summary: Optional[List[Dict[str, Any]]] = None,
    total_duration_seconds: float = 60.0,
) -> List[Dict[str, Any]]:
    """Interleaves physical attractions with overview cards, route maps, and summary cards.
    
    If raw_scenes already contains map transitions, returns raw_scenes as-is with normalized indices.
    Otherwise, injects:
      - Overview Card (Scene 1)
      - Physical Attraction 1
      - Connecting Route Map 1 -> 2 (with transit narration)
      - ...
      - Summary Card (Final Scene)
    """
    if not raw_scenes or not isinstance(raw_scenes, list):
        return raw_scenes

    # If scenes already contain map transitions, preserve existing structure
    has_map_transitions = any(sc.get("is_map_transition") for sc in raw_scenes if isinstance(sc, dict))
    if has_map_transitions and len(raw_scenes) >= 3:
        for idx, sc in enumerate(raw_scenes, 1):
            sc["scene_index"] = idx
        return raw_scenes

    # Extract physical attractions only
    physical_attractions: List[Dict[str, Any]] = [
        copy.deepcopy(sc) for sc in raw_scenes
        if isinstance(sc, dict) and not _is_card_or_map(sc)
    ]

    if not physical_attractions:
        return raw_scenes

    # Duration budgeting: 8s per card, 9s per map, remaining time divided across attractions
    num_attrs = len(physical_attractions)
    num_maps = max(0, num_attrs - 1)
    card_dur = 8.0
    map_dur = 9.0
    fixed_overhead = (2 * card_dur) + (num_maps * map_dur)  # Overview + Summary + Maps

    remaining_attr_time = max(9.0 * num_attrs, total_duration_seconds - fixed_overhead)
    per_attr_dur = round(max(9.0, remaining_attr_time / num_attrs), 1)

    interleaved: List[Dict[str, Any]] = []

    # 1. Inject Scene 1: Master Overview Card
    first_coords = physical_attractions[0].get("origin_coords")
    last_coords = physical_attractions[-1].get("origin_coords") or first_coords
    attr_names = [sc.get("attraction_name") or sc.get("origin_name", f"Stop {i+1}") for i, sc in enumerate(physical_attractions)]
    
    overview_scene: Dict[str, Any] = {
        "scene_index": 1,
        "location_hub": "Master Day Plan Overview",
        "shot_type": "itinerary_overview_card",
        "camera_rig": "locked_tripod_telephoto",
        "camera_movement": "stay",
        "motion_type": "ken_burns",
        "camera_waypoints": [{"motion": "stay", "duration_seconds": card_dur}],
        "color_temp_kelvin": 5500,
        "visual_prompt": (
            f"A pristine, high-resolution infographic presentation board of the 1-Day Heritage Tour, "
            f"displayed on elegant dark slate with refined brass typography. Route markers highlighting "
            f"{', '.join(attr_names[:4])} under balanced 5500K daylight."
        ),
        "narration_text": (
            f"Welcome to our definitive one-day journey, connecting {', '.join(attr_names[:3])} "
            f"with seamless transit efficiency."
        ),
        "duration_seconds": card_dur,
        "is_itinerary_overview": True,
        "is_map_transition": False,
        "origin_coords": first_coords,
        "destination_coords": last_coords,
        "attraction_name": None,
        "origin_name": None,
        "destination_name": None,
        "start_time": "08:30 AM",
        "end_time": "05:30 PM",
        "visit_duration": f"{len(physical_attractions) * 2.0:.1f} hrs total",
        "attraction_cost": None,
        "motion_rationale": "Static locked tripod preserves typographical clarity on overview card ($0.00 compute).",
    }
    interleaved.append(overview_scene)

    # 2. Interleave Physical Attractions and Connecting Route Maps
    for idx, attr_sc in enumerate(physical_attractions):
        attr_sc["duration_seconds"] = per_attr_dur
        attr_sc["is_map_transition"] = False
        attr_sc["is_itinerary_overview"] = False
        attr_sc["is_itinerary_summary"] = False
        attr_sc["scene_index"] = len(interleaved) + 1
        interleaved.append(attr_sc)

        # Inject Connecting Route Map if there is a subsequent stop
        if idx < num_attrs - 1:
            next_attr = physical_attractions[idx + 1]
            from_name = attr_sc.get("attraction_name") or attr_sc.get("origin_name", f"Stop {idx+1}")
            to_name = next_attr.get("attraction_name") or next_attr.get("origin_name", f"Stop {idx+2}")
            from_coords = attr_sc.get("origin_coords")
            to_coords = next_attr.get("origin_coords")

            # Extract transit details from transit_to_next or compute deterministically
            transit_info = attr_sc.get("transit_to_next") or {}
            mode = transit_info.get("transit_mode") or transit_info.get("mode")
            dur = transit_info.get("transit_duration") or transit_info.get("duration")
            cost = transit_info.get("approx_leg_cost") or transit_info.get("approx_cost") or transit_info.get("cost")
            transit_narr = transit_info.get("transit_narration") or transit_info.get("narration")

            if not mode or not dur:
                dist_km = calculate_geodesic_distance_km(from_coords or [0, 0], to_coords or [0, 0])
                derived_mode, derived_dur = determine_transit_specs(dist_km)
                mode = mode or derived_mode
                dur = dur or derived_dur
                cost = cost or ("Free (walk)" if mode == "walk" else "£8–£14 Uber")

            if not transit_narr:
                transit_narr = f"Next, an efficient {dur} journey leads us to {to_name}."

            map_scene: Dict[str, Any] = {
                "scene_index": len(interleaved) + 1,
                "location_hub": f"Transit: {from_name} to {to_name}",
                "shot_type": "overhead_cartographic",
                "camera_rig": "locked_tripod_telephoto",
                "camera_movement": "stay",
                "motion_type": "ken_burns",
                "camera_waypoints": [{"motion": "stay", "duration_seconds": map_dur}],
                "color_temp_kelvin": 5500,
                "visual_prompt": (
                    f"An exquisite cartographic route map tracing transit from {from_name} to {to_name}. "
                    f"Rich parchment and graphite styling, crisp golden transit vector line tracing the "
                    f"route with pin-drop precision."
                ),
                "narration_text": transit_narr,
                "duration_seconds": map_dur,
                "is_map_transition": True,
                "is_itinerary_overview": False,
                "is_itinerary_summary": False,
                "origin_name": from_name,
                "destination_name": to_name,
                "origin_coords": from_coords,
                "destination_coords": to_coords,
                "transit_mode": mode,
                "transit_duration": dur,
                "approx_leg_cost": cost,
                "attraction_name": None,
                "motion_rationale": "Locked tripod on cartographic transition guarantees sharp legibility of GPS vector lines ($0.00 compute).",
            }
            interleaved.append(map_scene)

    # 3. Inject Final Scene: Master Summary Card
    summary_scene: Dict[str, Any] = {
        "scene_index": len(interleaved) + 1,
        "location_hub": "Master Itinerary Recap",
        "shot_type": "itinerary_summary_card",
        "camera_rig": "locked_tripod_telephoto",
        "camera_movement": "stay",
        "motion_type": "ken_burns",
        "camera_waypoints": [{"motion": "stay", "duration_seconds": card_dur}],
        "color_temp_kelvin": 5500,
        "visual_prompt": (
            "An elegant, high-contrast infographic summary board presenting the complete schedule table, "
            "visitation durations, transit times, and budget breakdown in crisp typography."
        ),
        "narration_text": "Plan your day with ease using this complete master itinerary summary for an unforgettable journey.",
        "duration_seconds": card_dur,
        "is_itinerary_summary": True,
        "is_map_transition": False,
        "origin_coords": first_coords,
        "destination_coords": last_coords,
        "attraction_name": None,
        "origin_name": None,
        "destination_name": None,
        "motion_rationale": "Locked stationary cinemagraph preserves typographical clarity on itinerary summary table ($0.00 compute).",
    }
    interleaved.append(summary_scene)

    # Final pass: Normalize scene indices
    for idx, sc in enumerate(interleaved, 1):
        sc["scene_index"] = idx

    return interleaved


__all__ = ["interleave_tour_storyboard_scenes"]
