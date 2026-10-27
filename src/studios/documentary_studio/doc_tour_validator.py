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

    # Pre-scan landmarks for first and last coordinates
    first_coords, last_coords = None, None
    for s in scenes:
        if isinstance(s, dict) and not (s.get("is_itinerary_overview") or s.get("is_itinerary_summary")):
            c_orig = s.get("origin_coords")
            c_dest = s.get("destination_coords")
            if isinstance(c_orig, (list, tuple)) and len(c_orig) >= 2 and first_coords is None:
                first_coords = c_orig
            if isinstance(c_dest, (list, tuple)) and len(c_dest) >= 2:
                last_coords = c_dest
            elif isinstance(c_orig, (list, tuple)) and len(c_orig) >= 2 and last_coords is None:
                last_coords = c_orig

    # 2. Enforce Scene-by-Scene Contract for Physical Landmarks and Map Stops
    for idx, sc in enumerate(scenes, 1):
        if not isinstance(sc, dict):
            raise ValueError(f"Tour Contract Violation in Scene {idx}: Scene must be a dictionary.")

        shot_type_str = str(sc.get("shot_type", "")).lower()
        is_info_slide = bool(
            sc.get("is_itinerary_overview")
            or sc.get("is_itinerary_summary")
            or sc.get("is_vacation_scope")
            or any(w in shot_type_str for w in ("overview", "summary", "vacation"))
        )
        is_card = is_info_slide or bool(
            sc.get("is_map_transition")
            or any(w in shot_type_str for w in ("card", "map", "transition", "cartographic"))
        )

        # Basic mandates for ALL scenes
        if not sc.get("narration_text") and not sc.get("visual_prompt") and not sc.get("visual_description"):
            raise ValueError(
                f"Tour Contract Violation in Scene {idx}: Missing narration_text and visual_prompt."
            )

        is_map_trans = bool(
            sc.get("is_map_transition")
            or any(w in shot_type_str for w in ("map", "transition", "cartographic"))
        )

        # Coordinate checks
        if is_info_slide:
            if not sc.get("origin_coords") and first_coords:
                sc["origin_coords"] = first_coords
            if not sc.get("destination_coords") and (last_coords or first_coords):
                sc["destination_coords"] = last_coords or first_coords
            origin_coords = sc.get("origin_coords")
            if not origin_coords or not isinstance(origin_coords, (list, tuple)) or len(origin_coords) < 2:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: 'origin_coords' is missing or invalid (expected [lat, lon] floats, got {origin_coords})."
                )
            destination_coords = sc.get("destination_coords")
            if not destination_coords or not isinstance(destination_coords, (list, tuple)) or len(destination_coords) < 2:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: 'destination_coords' is missing or invalid (expected [lat, lon] floats, got {destination_coords})."
                )
        elif is_map_trans:
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
                    "Gemini must supply exact GPS coordinates for all route maps."
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
        else:
            origin_coords = sc.get("origin_coords")
            # Deterministic coordinate healing if missing
            if not origin_coords or not isinstance(origin_coords, (list, tuple)) or len(origin_coords) < 2:
                from src.studios.documentary_studio.doc_tour_normalizer import resolve_coordinates
                cand_name = sc.get("attraction_name") or sc.get("origin_name") or sc.get("location_hub") or sc.get("title")
                if cand_name and str(cand_name).strip():
                    healed = resolve_coordinates(str(cand_name).strip())
                    if healed and len(healed) >= 2:
                        sc["origin_coords"] = healed
                        origin_coords = healed

            if not origin_coords or not isinstance(origin_coords, (list, tuple)) or len(origin_coords) < 2:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx} ('{sc.get('attraction_name') or sc.get('origin_name', 'Unnamed')}'): "
                    f"'origin_coords' is missing or invalid (expected [lat, lon] floats, got {origin_coords}). "
                    "Gemini must supply exact GPS coordinates for all tour stops."
                )
            try:
                lat, lon = float(origin_coords[0]), float(origin_coords[1])
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                    raise ValueError(f"Latitude ({lat}) or Longitude ({lon}) out of bounds.")
            except Exception as e_c:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx}: 'origin_coords' has invalid numeric coordinates {origin_coords}: {e_c}"
                )
            if not sc.get("destination_coords") or not isinstance(sc.get("destination_coords"), (list, tuple)):
                sc["destination_coords"] = origin_coords

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
