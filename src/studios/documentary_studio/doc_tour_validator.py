"""Strict Zero-Fallback Tour Screenplay Contract Validator.

Validates that Gemini's directorial response satisfies all mandatory keys
for tour and itinerary archetypes (GPS coordinates, entry fees, itinerary summary).
Zero silent fallback is permitted: any missing or invalid data raises ValueError immediately.
"""

from __future__ import annotations

from typing import Any, Dict, List


def validate_tour_screenplay_contract(data: Dict[str, Any]) -> None:
    """Enforces strict, zero-fallback contract validation for Tour Archetype screenplays.

    Raises:
        ValueError: If Gemini failed to output mandatory tour elements
            (itinerary_summary, GPS coordinates, visit durations, ticket/entry costs).
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Tour Contract Violation: Screenplay payload is not a dictionary (got {type(data)})."
        )

    scenes = data.get("scenes")
    if not scenes or not isinstance(scenes, list) or len(scenes) < 2:
        raise ValueError(
            f"Tour Contract Violation: Tour must have at least 2 scenes "
            f"(got {len(scenes) if isinstance(scenes, list) else 0})."
        )

    # 1. Enforce root itinerary_summary presence and metrics
    summary = data.get("itinerary_summary")
    if not summary or not isinstance(summary, list) or len(summary) < 1:
        raise ValueError(
            "Tour Contract Violation: Root 'itinerary_summary' is missing or empty. "
            "Gemini must supply the master daily breakdown with total_attraction_time, "
            "total_travel_time, total_walk_time, total_drive_time, and total_travel_cost."
        )

    sum_card = summary[0]
    if not isinstance(sum_card, dict):
        raise ValueError(
            "Tour Contract Violation: 'itinerary_summary' elements must be dictionaries."
        )

    required_summary_keys = (
        "total_attraction_time",
        "total_travel_time",
        "total_travel_cost",
    )
    missing_summary = [k for k in required_summary_keys if not sum_card.get(k)]
    if missing_summary:
        raise ValueError(
            f"Tour Contract Violation: 'itinerary_summary' missing required metrics: {missing_summary}"
        )

    # 2. Enforce Scene-by-Scene Contract for Physical Landmarks and Map Stops
    for idx, sc in enumerate(scenes, 1):
        if not isinstance(sc, dict):
            raise ValueError(f"Tour Contract Violation in Scene {idx}: Scene must be a dictionary.")

        shot_type_str = str(sc.get("shot_type", "")).lower()
        is_card = bool(
            sc.get("is_map_transition")
            or sc.get("is_itinerary_overview")
            or sc.get("is_itinerary_summary")
            or sc.get("is_vacation_scope")
            or any(
                w in shot_type_str
                for w in (
                    "card",
                    "overview",
                    "map",
                    "transition",
                    "cartographic",
                    "vacation",
                    "summary",
                )
            )
        )

        # Basic mandates for ALL scenes
        if not sc.get("narration_text") and not sc.get("visual_prompt") and not sc.get("visual_description"):
            raise ValueError(
                f"Tour Contract Violation in Scene {idx}: Missing narration_text and visual_prompt."
            )

        # Coordinate checks (both origin_coords and destination_coords must be valid [lat, lon])
        origin_coords = sc.get("origin_coords")
        if not origin_coords or not isinstance(origin_coords, (list, tuple)) or len(origin_coords) < 2:
            raise ValueError(
                f"Tour Contract Violation in Scene {idx} ('{sc.get('origin_name', 'Unnamed')}'): "
                f"'origin_coords' is missing or invalid (expected [lat, lon] floats, got {origin_coords}). "
                "Gemini must supply exact GPS coordinates for all tour stops."
            )

        destination_coords = sc.get("destination_coords")
        if not destination_coords or not isinstance(destination_coords, (list, tuple)) or len(destination_coords) < 2:
            raise ValueError(
                f"Tour Contract Violation in Scene {idx} ('{sc.get('destination_name', 'Unnamed')}'): "
                f"'destination_coords' is missing or invalid (expected [lat, lon] floats, got {destination_coords}). "
                "Gemini must supply exact GPS coordinates for all tour stops."
            )

        for name, coords in (("origin_coords", origin_coords), ("destination_coords", destination_coords)):
            try:
                lat, lon = float(coords[0]), float(coords[1])
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                    raise ValueError(f"Latitude ({lat}) or Longitude ({lon}) out of bounds.")
            except Exception as e_c:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: '{name}' has invalid numeric coordinates {coords}: {e_c}"
                )

        # Landmark-specific mandates
        if not is_card:
            if not sc.get("attraction_name") and not sc.get("origin_name"):
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: Landmark scene missing 'attraction_name'."
                )
            if not sc.get("visit_duration") and not sc.get("duration_seconds"):
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: Landmark scene missing 'visit_duration'."
                )
            if sc.get("attraction_cost") is None or str(sc.get("attraction_cost")).strip() == "":
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx} ('{sc.get('attraction_name') or sc.get('origin_name')}'): "
                    "Missing 'attraction_cost' (e.g. '£29.00 Ticket', 'Free Entry', or entry fee)."
                )


__all__ = ["validate_tour_screenplay_contract"]
