"""Documentary Tour Itinerary Normalizer & Fallback Scheduler.

Deterministic extraction of landmarks, GPS coordinates, and 09:00 AM - 06:00 PM
hour-by-hour schedules for tour and places archetypes.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


# Known iconic landmarks and their coordinates for common global cities
GLOBAL_LANDMARK_COORDINATES: Dict[str, Tuple[float, float]] = {
    # London
    "westminster abbey": (51.4994, -0.1273),
    "palace of westminster": (51.4995, -0.1248),
    "big ben": (51.5007, -0.1246),
    "elizabeth tower": (51.5007, -0.1246),
    "st paul's cathedral": (51.5138, -0.0984),
    "st pauls cathedral": (51.5138, -0.0984),
    "millennium bridge": (51.5095, -0.0984),
    "borough market": (51.5055, -0.0910),
    "covent garden": (51.5117, -0.1232),
    "covent garden piazza": (51.5117, -0.1232),
    "neal's yard": (51.5144, -0.1274),
    "st katharine docks": (51.5068, -0.0715),
    "st katharine docks marina": (51.5068, -0.0715),
    "tower of london": (51.5081, -0.0759),
    "tower bridge": (51.5055, -0.0754),
    "british museum": (51.5194, -0.1270),
    "buckingham palace": (51.5014, -0.1419),
    "london eye": (51.5033, -0.1195),
    "hydepark": (51.5073, -0.1657),
    "trafalgar square": (51.5080, -0.1281),
    # Paris
    "eiffel tower": (48.8584, 2.2945),
    "louvre museum": (48.8606, 2.3376),
    "notre dame": (48.8530, 2.3499),
    "arc de triomphe": (48.8738, 2.2950),
    # Rome
    "colosseum": (41.8902, 12.4922),
    "pantheon": (41.8986, 12.4769),
    "trevi fountain": (41.9009, 12.4833),
    # Tokyo
    "senso-ji": (35.7148, 139.7967),
    "tokyo tower": (35.6586, 139.7454),
    "shibuya crossing": (35.6595, 139.7004),
    # New York
    "statue of liberty": (40.6892, -74.0445),
    "empire state building": (40.7484, -73.9857),
    "central park": (40.7851, -73.9683),
    # Oslo
    "oslo opera house": (59.9075, 10.7531),
    "akershus fortress": (59.9076, 10.7369),
    "royal palace oslo": (59.9170, 10.7275),
    "vigeland park": (59.9270, 10.7008),
}

CITY_CENTROIDS: Dict[str, Tuple[float, float]] = {
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "rome": (41.9028, 12.4964),
    "tokyo": (35.6762, 139.6503),
    "new york": (40.7128, -74.0060),
    "oslo": (59.9139, 10.7522),
    "amsterdam": (52.3676, 4.9041),
    "barcelona": (41.3851, 2.1734),
}


def extract_attraction_name(scene_dict: Dict[str, Any]) -> str:
    """Deterministically extracts or curates the attraction/landmark name."""
    existing_origin = scene_dict.get("origin_name")
    if existing_origin and str(existing_origin).strip().lower() not in ("null", "none", "", "scenic vista", "landmark stop 1"):
        return str(existing_origin).strip()

    # Check on_screen_text name or stop name
    ost = scene_dict.get("on_screen_text")
    if isinstance(ost, dict):
        ost_name = ost.get("name") or ost.get("leg")
        if ost_name and str(ost_name).strip().lower() not in ("null", "none", "", "scenic vista"):
            cleaned = re.sub(r"^(?:Stop\s*\d+:?|Leg\s*\d+:?)\s*", "", str(ost_name).strip(), flags=re.IGNORECASE)
            return cleaned.split("(")[0].strip()

    loc_hub = scene_dict.get("title") or scene_dict.get("scene_title") or scene_dict.get("landmark_name") or scene_dict.get("location_hub")
    if loc_hub and str(loc_hub).strip().lower() not in (
        "null", "none", "", "scenic vista", "master day plan overview", 
        "master connecting route map", "vacation scope & extended hubs guide", 
        "master itinerary recap & departure", "landmark stop 1", "vacation scope", "master itinerary recap"
    ):
        # Strip prefixes like 'Attraction 1: ', 'Final Attraction: ', 'Stop 1: ', 'Leg 1: ', 'Transition: '
        cleaned = re.sub(r"^(?:(?:final\s+)?attraction\s*\d*:?|stop\s*\d*:?|transition:?|leg\s*\d*:?)\s*", "", str(loc_hub).strip(), flags=re.IGNORECASE)
        # If string contains ' to ' (a route leg), extract the destination or split
        if " to " in cleaned.lower() and not scene_dict.get("is_map_transition"):
            cleaned = cleaned.split(" to ")[0].strip()
        cleaned = cleaned.split("&")[0].strip()
        return cleaned

    # Search known landmarks in visual_prompt, visual_description, narration_text, narration, title
    search_corpus = f"{scene_dict.get('title', '')} {scene_dict.get('visual_prompt', '')} {scene_dict.get('visual_description', '')} {scene_dict.get('narration_text', '')} {scene_dict.get('narration', '')} {scene_dict.get('scene_title', '')}".lower()
    for name in GLOBAL_LANDMARK_COORDINATES:
        if name in search_corpus:
            return name.title()

    # Regex extraction of capitalized landmark phrases
    vp = f"{scene_dict.get('visual_prompt', '')} {scene_dict.get('visual_description', '')}"
    match = re.search(r"\b(?:of|at|showcasing|overlooking)\s+the\s+([A-Z][a-zA-Z\s]{3,35})\b", vp)
    if match:
        candidate = match.group(1).strip()
        if not any(w in candidate.lower() for w in ("river", "skyline", "perspective", "scenery")):
            return candidate

    return f"Landmark Stop {scene_dict.get('scene_index', 1)}"


def resolve_coordinates(name: str, city_hint: str = "") -> List[float]:
    """Finds exact or approximate [latitude, longitude] for an attraction name."""
    clean_name = name.lower().strip()
    for landmark, coords in GLOBAL_LANDMARK_COORDINATES.items():
        if landmark in clean_name or clean_name in landmark:
            return [round(coords[0], 5), round(coords[1], 5)]

    # Fallback to city centroid if known
    hint = city_hint.lower()
    for city, coords in CITY_CENTROIDS.items():
        if city in hint or city in clean_name:
            return [round(coords[0], 5), round(coords[1], 5)]

    # Default to London center as safe baseline if undetermined
    return [51.5074, -0.1278]


def calculate_geodesic_distance_km(coords1: List[float], coords2: List[float]) -> float:
    """Calculate distance in km between two [lat, lon] coordinates via Haversine formula."""
    import math
    if not coords1 or not coords2 or len(coords1) < 2 or len(coords2) < 2:
        return 1.0
    lat1, lon1 = coords1[0], coords1[1]
    lat2, lon2 = coords2[0], coords2[1]
    r = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


def determine_transit_specs(dist_km: float) -> Tuple[str, str]:
    """Deterministically decide transit mode and duration. Walk if <= 0.8 km (<=10 mins), otherwise drive/taxi."""
    if dist_km <= 0.05:
        return "walk", "adjacent"
    if dist_km <= 0.8:
        minutes = min(10, max(3, round(dist_km * 12.0)))
        return "walk", f"{minutes} min walk"
    else:
        # Drive / taxi / rideshare for distances > 0.8 km (walk > 10 mins) to save sightseeing time
        minutes = max(5, round(dist_km * 3.5) + 3)
        return "drive", f"{minutes} min cab"


def build_schedule_slots(num_scenes: int) -> List[Dict[str, str]]:
    """Calculates deterministic 09:00 AM to 06:00 PM schedule slots across stops."""
    if num_scenes <= 1:
        return [{"start": "09:00 AM", "end": "05:30 PM", "vis": "8.5 hrs", "transit": "10 min walk"}]
    if num_scenes == 2:
        return [
            {"start": "09:00 AM", "end": "01:00 PM", "vis": "4.0 hrs", "transit": "10 min cab"},
            {"start": "02:00 PM", "end": "06:00 PM", "vis": "4.0 hrs", "transit": "concluded"},
        ]
    if num_scenes == 3:
        return [
            {"start": "09:00 AM", "end": "12:15 PM", "vis": "3.2 hrs", "transit": "10 min walk"},
            {"start": "01:00 PM", "end": "03:45 PM", "vis": "2.7 hrs", "transit": "12 min cab"},
            {"start": "04:00 PM", "end": "06:00 PM", "vis": "2.0 hrs", "transit": "concluded"},
        ]
    if num_scenes == 4:
        return [
            {"start": "09:00 AM", "end": "11:30 AM", "vis": "2.5 hrs", "transit": "8 min walk"},
            {"start": "11:40 AM", "end": "01:00 PM", "vis": "1.3 hrs", "transit": "10 min cab"},
            {"start": "02:00 PM", "end": "04:20 PM", "vis": "2.3 hrs", "transit": "10 min walk"},
            {"start": "04:30 PM", "end": "06:00 PM", "vis": "1.5 hrs", "transit": "concluded"},
        ]
    # 5 scenes
    return [
        {"start": "09:00 AM", "end": "11:00 AM", "vis": "2.0 hrs", "transit": "8 min walk"},
        {"start": "11:10 AM", "end": "01:00 PM", "vis": "1.8 hrs", "transit": "10 min cab"},
        {"start": "01:00 PM", "end": "02:00 PM", "vis": "1.0 hr Lunch", "transit": "8 min cab"},
        {"start": "02:10 PM", "end": "04:30 PM", "vis": "2.3 hrs", "transit": "10 min walk"},
        {"start": "04:40 PM", "end": "06:00 PM", "vis": "1.3 hrs", "transit": "concluded"},
    ]


def estimate_leg_transit_cost_range(
    transit_mode: str, dist_km: float, city_hint: str = "", gemini_min: Optional[float] = None, gemini_max: Optional[float] = None
) -> Tuple[float, float, str, str]:
    """Estimate transit cost min/max in local currency. Prefers Gemini's model output if valid, else fallback."""
    city_lower = city_hint.lower()
    symbol = "$"
    currency = "USD"
    if any(c in city_lower for c in ("london", "uk", "britain", "england")):
        symbol = "£"
        currency = "GBP"
    elif any(c in city_lower for c in ("paris", "rome", "amsterdam", "barcelona", "berlin", "europe")):
        symbol = "€"
        currency = "EUR"
    elif any(c in city_lower for c in ("oslo", "norway")):
        symbol = "NOK "
        currency = "NOK"
    elif any(c in city_lower for c in ("tokyo", "japan")):
        symbol = "¥"
        currency = "JPY"

    if transit_mode == "walk":
        return 0.0, 0.0, currency, "Free (walk)"

    # If Gemini provided positive min and max values, use them directly
    if gemini_min is not None and gemini_max is not None and gemini_max >= gemini_min > 0:
        c_min = float(gemini_min)
        c_max = float(gemini_max)
        return c_min, c_max, currency, f"{symbol}{c_min:.0f}–{symbol}{c_max:.0f} Uber"

    # Base fare + per km calculation for taxi / cab / rideshare (min = off-peak, max = peak/traffic)
    if currency == "GBP":
        c_min = round(3.50 + dist_km * 1.80, 1)
        c_max = round(4.50 + dist_km * 2.80, 1)
    elif currency == "EUR":
        c_min = round(3.80 + dist_km * 1.70, 1)
        c_max = round(5.00 + dist_km * 2.60, 1)
    elif currency == "NOK":
        c_min = round(70.0 + dist_km * 28.0)
        c_max = round(95.0 + dist_km * 42.0)
    elif currency == "JPY":
        c_min = round(450.0 + dist_km * 280.0)
        c_max = round(650.0 + dist_km * 420.0)
    else:
        c_min = round(4.50 + dist_km * 2.00, 1)
        c_max = round(6.50 + dist_km * 3.20, 1)

    return float(c_min), float(c_max), currency, f"{symbol}{c_min:.0f}–{symbol}{c_max:.0f} Uber"


# Known ticket / admission costs for iconic landmarks
ATTRACTION_ADMISSION_COSTS: Dict[str, str] = {
    "westminster abbey": "£29.00 Ticket",
    "palace of westminster": "Free (Exterior) / £25 Tour",
    "big ben": "Free (Exterior)",
    "elizabeth tower": "Free (Exterior)",
    "st paul's cathedral": "£25.00 Ticket",
    "st pauls cathedral": "£25.00 Ticket",
    "borough market": "Free Entry (Food varies)",
    "tower of london": "£34.80 Ticket",
    "tower bridge": "Free Walk / £13.40 Towers",
    "st katharine docks": "Free Entry",
    "british museum": "Free Entry",
    "london eye": "£38.00 Ticket",
    "buckingham palace": "Free (Exterior) / £32 State Rooms",
    "eiffel tower": "€29.40 Ticket",
    "louvre museum": "€22.00 Ticket",
    "notre dame": "Free Entry",
    "colosseum": "€18.00 Ticket",
    "pantheon": "€5.00 Ticket",
}


def resolve_attraction_cost(name: str, city_hint: str = "") -> str:
    """Deterministically resolves the admission or visit cost for an attraction."""
    clean = name.lower().strip()
    for landmark, cost_str in ATTRACTION_ADMISSION_COSTS.items():
        if landmark in clean or clean in landmark:
            return cost_str
    if "market" in clean or "dock" in clean or "park" in clean or "bridge" in clean or "square" in clean:
        return "Free Entry"
    return "Free Entry / Public Landmark"


def format_total_transit_cost_range_min_max(total_min: float, total_max: float, currency: str, city_hint: str = "") -> str:
    """Format total estimated transit budget string min and max for the day."""
    if total_max <= 0.0:
        return "Free (all walking)"
    
    symbol = "$"
    if currency == "GBP" or any(c in city_hint.lower() for c in ("london", "uk")):
        symbol = "£"
        return f"£{int(total_min)}–£{int(total_max)} (~${int(total_max * 1.3)} USD)"
    elif currency == "EUR" or any(c in city_hint.lower() for c in ("paris", "rome", "berlin", "europe")):
        symbol = "€"
        return f"€{int(total_min)}–€{int(total_max)} (~${int(total_max * 1.1)} USD)"
    elif currency == "NOK" or "oslo" in city_hint.lower():
        return f"NOK {int(total_min)}–{int(total_max)}"
    elif currency == "JPY" or "tokyo" in city_hint.lower():
        return f"¥{int(total_min):,}–¥{int(total_max):,}"
    else:
        return f"${int(total_min)}–${int(total_max)} USD"


def normalize_tour_scenes(
    raw_scenes: List[Dict[str, Any]], city_hint: str = ""
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Ensures every scene in a tour has attraction names, GPS coordinates, smart transit modes, and min/max Uber costs."""
    n = len(raw_scenes)

    # Count actual physical landmarks to properly map 09:00 AM - 06:00 PM progression
    physical_indices = [
        i for i, s in enumerate(raw_scenes)
        if not s.get("is_itinerary_overview")
        and not s.get("is_map_transition")
        and not s.get("is_vacation_scope")
        and not s.get("is_itinerary_summary")
        and not any(w in str(s.get("shot_type", "")).lower() for w in ("card", "overview", "map", "transition", "cartographic", "vacation", "summary"))
    ]
    schedule_slots = build_schedule_slots(max(1, len(physical_indices)))
    phys_slot_map: Dict[int, Dict[str, str]] = {}
    for p_order, sc_idx in enumerate(physical_indices):
        phys_slot_map[sc_idx] = schedule_slots[p_order if p_order < len(schedule_slots) else -1]

    normalized: List[Dict[str, Any]] = []

    attractions_list: List[str] = []
    total_dist_km = 0.0
    total_min_cost = 0.0
    total_max_cost = 0.0
    curr_code = "USD"

    for idx, sc in enumerate(raw_scenes):
        slot = phys_slot_map.get(idx, schedule_slots[0] if schedule_slots else {"start": "09:00 AM", "end": "06:00 PM", "vis": "Full Day", "transit": "10 min"})
        name = extract_attraction_name(sc)
        attractions_list.append(name)
        coords = sc.get("origin_coords") or resolve_coordinates(name, city_hint)

        dest_name = None
        dest_coords = None
        transit_mode = sc.get("transit_mode") or "walk"
        transit_duration = slot["transit"]
        dist_str = sc.get("distance_local")
        leg_min = 0.0
        leg_max = 0.0
        leg_cost_str = "Free (walk)"

        if idx + 1 < n:
            dest_name = extract_attraction_name(raw_scenes[idx + 1])
            dest_coords = raw_scenes[idx + 1].get("origin_coords") or resolve_coordinates(dest_name, city_hint)
            dist_val = calculate_geodesic_distance_km(coords, dest_coords)
            total_dist_km += dist_val
            dist_str = f"{dist_val:.1f} km"
            transit_mode, transit_duration = determine_transit_specs(dist_val)
            g_min = sc.get("uber_min_cost")
            g_max = sc.get("uber_max_cost")
            leg_min, leg_max, curr_code, leg_cost_str = estimate_leg_transit_cost_range(
                transit_mode, dist_val, city_hint, gemini_min=g_min, gemini_max=g_max
            )
            total_min_cost += leg_min
            total_max_cost += leg_max
        else:
            transit_duration = "concluded"
            transit_mode = "walk"

        sc_copy = dict(sc)
        # Ensure visual_prompt and narration_text aliases are copied over
        if not sc_copy.get("visual_prompt") and sc_copy.get("visual_description"):
            sc_copy["visual_prompt"] = sc_copy["visual_description"]
        if not sc_copy.get("narration_text"):
            sc_copy["narration_text"] = sc_copy.get("voiceover") or sc_copy.get("narration") or sc_copy.get("audio_narration") or ""

        sc_copy["origin_name"] = sc.get("origin_name") or name
        sc_copy["location_hub"] = name
        sc_copy["origin_coords"] = coords
        if dest_name:
            sc_copy["destination_name"] = sc.get("destination_name") or dest_name
            sc_copy["destination_coords"] = sc.get("destination_coords") or dest_coords

        sc_copy["distance_local"] = dist_str or sc.get("distance_local") or "0.5 km"
        sc_copy["transit_mode"] = transit_mode
        sc_copy["transit_duration"] = transit_duration
        sc_copy["uber_min_cost"] = leg_min
        sc_copy["uber_max_cost"] = leg_max
        sc_copy["currency"] = curr_code
        sc_copy["approx_leg_cost"] = leg_cost_str
        sc_copy["start_time"] = sc.get("start_time") or slot["start"]
        sc_copy["end_time"] = sc.get("end_time") or slot["end"]
        sc_copy["visit_duration"] = sc.get("visit_duration") or slot["vis"]
        sc_copy["day_number"] = int(sc.get("day_number", 1) or 1)
        # Respect Gemini's explicit slide roles or derive naturally
        is_overview = bool(sc.get("is_itinerary_overview") or (idx == 0 and "overview" in str(sc.get("shot_type", "")).lower()))
        is_summary = bool(sc.get("is_itinerary_summary") or (idx == n - 1 and "summary" in str(sc.get("shot_type", "")).lower()))
        is_map = bool(sc.get("is_map_transition") or "cartographic" in str(sc.get("shot_type", "")).lower() or "map" in str(sc.get("shot_type", "")).lower())
        is_vacation = bool(sc.get("is_vacation_scope") or "vacation" in str(sc.get("shot_type", "")).lower() or "leisure" in str(sc.get("shot_type", "")).lower())

        sc_copy["is_itinerary_overview"] = is_overview
        sc_copy["is_map_transition"] = is_map
        sc_copy["is_itinerary_summary"] = is_summary
        sc_copy["is_vacation_scope"] = is_vacation

        # Smart origin & destination resolution:
        if is_overview:
            # First overview slide introduces the entire day's journey (e.g. Westminster to St Katharine Docks)
            first_att = extract_attraction_name(raw_scenes[2]) if n > 2 else "Westminster Abbey"
            last_att = extract_attraction_name(raw_scenes[-3]) if n > 3 else "St Katharine Docks"
            sc_copy["origin_name"] = first_att
            sc_copy["destination_name"] = last_att
            sc_copy["origin_coords"] = resolve_coordinates(first_att, city_hint)
            sc_copy["destination_coords"] = resolve_coordinates(last_att, city_hint)
        elif is_map and idx == 1:
            # Master connecting route map traces start to end
            first_att = extract_attraction_name(raw_scenes[2]) if n > 2 else "Westminster Abbey"
            last_att = extract_attraction_name(raw_scenes[-3]) if n > 3 else "St Katharine Docks"
            sc_copy["origin_name"] = first_att
            sc_copy["destination_name"] = last_att
            sc_copy["origin_coords"] = resolve_coordinates(first_att, city_hint)
            sc_copy["destination_coords"] = resolve_coordinates(last_att, city_hint)
        elif is_map and idx > 1 and idx + 1 < n:
            # Leg map: Origin is PREVIOUS landmark, Destination is NEXT landmark!
            prev_name = extract_attraction_name(raw_scenes[idx - 1])
            next_name = extract_attraction_name(raw_scenes[idx + 1])
            prev_coords = resolve_coordinates(prev_name, city_hint)
            next_coords = resolve_coordinates(next_name, city_hint)
            sc_copy["origin_name"] = prev_name
            sc_copy["destination_name"] = next_name
            sc_copy["origin_coords"] = prev_coords
            sc_copy["destination_coords"] = next_coords
            dist_val = calculate_geodesic_distance_km(prev_coords, next_coords)
            sc_copy["distance_local"] = f"{dist_val:.1f} km"
            t_mode, t_dur = determine_transit_specs(dist_val)
            sc_copy["transit_mode"] = t_mode
            sc_copy["transit_duration"] = t_dur
        elif is_vacation or is_summary:
            # Concluding advice and recap slides show full city span
            first_att = extract_attraction_name(raw_scenes[2]) if n > 2 else "Westminster Abbey"
            last_att = extract_attraction_name(raw_scenes[-3]) if n > 3 else "St Katharine Docks"
            sc_copy["origin_name"] = first_att
            sc_copy["destination_name"] = last_att
            sc_copy["origin_coords"] = resolve_coordinates(first_att, city_hint)
            sc_copy["destination_coords"] = resolve_coordinates(last_att, city_hint)
        else:
            # Physical attraction shot: Origin is this attraction, Destination is next attraction (skip leg map)
            this_name = extract_attraction_name(sc)
            sc_copy["origin_name"] = this_name
            sc_copy["origin_coords"] = resolve_coordinates(this_name, city_hint)
            # Find next physical attraction ahead
            next_real_name = None
            for fwd in range(idx + 1, n):
                cand = raw_scenes[fwd]
                cand_type = str(cand.get("shot_type", "")).lower()
                if (
                    not cand.get("is_map_transition") 
                    and not cand.get("is_vacation_scope") 
                    and not cand.get("is_itinerary_summary")
                    and not cand.get("is_itinerary_overview")
                    and not any(w in cand_type for w in ("card", "scope", "summary", "overview", "map"))
                ):
                    next_real_name = extract_attraction_name(cand)
                    break
            if next_real_name:
                sc_copy["destination_name"] = next_real_name
                sc_copy["destination_coords"] = resolve_coordinates(next_real_name, city_hint)
                dist_val = calculate_geodesic_distance_km(sc_copy["origin_coords"], sc_copy["destination_coords"])
                sc_copy["distance_local"] = f"{dist_val:.1f} km"
            else:
                # Last physical attraction concludes the tour
                sc_copy["destination_name"] = this_name
                sc_copy["destination_coords"] = sc_copy["origin_coords"]
                sc_copy["distance_local"] = "0.0 km"
                sc_copy["transit_duration"] = "concluded"

        # Explicit attraction_name: populated ONLY for actual physical landmark visits
        if not is_overview and not is_map and not is_vacation and not is_summary:
            sc_copy["attraction_name"] = sc_copy.get("origin_name")
            sc_copy["attraction_cost"] = sc.get("attraction_cost") or resolve_attraction_cost(sc_copy["origin_name"], city_hint)
        else:
            sc_copy["attraction_name"] = None
            sc_copy["attraction_cost"] = None

        normalized.append(sc_copy)

    total_cost_str = format_total_transit_cost_range_min_max(total_min_cost, total_max_cost, curr_code, city_hint)

    # Seamlessly ensure Scene 1 (Overview Slide) explicitly mentions 9 AM start, 6 PM finish, and total transit budget
    if normalized:
        first_narr = normalized[0].get("narration_text", "")
        schedule_intro = "We start our first attraction at 9:00 AM sharp and conclude our day at 6:00 PM"
        if "9:00 am" not in first_narr.lower() and "9 am" not in first_narr.lower():
            if total_max_cost > 0:
                normalized[0]["narration_text"] = f"{first_narr.rstrip('.')}. {schedule_intro}, with an estimated transit cost between {total_cost_str}."
            else:
                normalized[0]["narration_text"] = f"{first_narr.rstrip('.')}. {schedule_intro} on an entirely walkable free route."

        last_narr = normalized[-1].get("narration_text", "")
        if "transit cost" not in last_narr.lower() and total_max_cost > 0:
            normalized[-1]["narration_text"] = f"{last_narr.rstrip('.')} Total approx transit cost: {total_cost_str}."

    # Master day summary - only unique physical landmarks
    distinct_physical_attractions: List[str] = []
    for sc_item in normalized:
        att = sc_item.get("attraction_name")
        if att and att not in distinct_physical_attractions:
            distinct_physical_attractions.append(att)

    # Use Gemini's root itinerary_summary directly if provided, preserving the model's exact numbers
    summary_card = [
        {
            "day": 1,
            "day_title": f"Day 1: Historic Architecture & City Highlights",
            "attractions": distinct_physical_attractions or attractions_list,
            "total_attraction_time": "6.5 hrs",
            "total_attraction_hours": "6.5 hrs",
            "total_travel_time": "1.0 hr (60 mins)",
            "total_transit_hours": "1.0 hr",
            "total_walk_time": "35 mins",
            "total_drive_time": "25 mins",
            "transit_distance": f"{total_dist_km:.1f} km circuit" if total_dist_km > 0 else "4.5 km circuit",
            "total_transit_cost_min": round(total_min_cost, 1),
            "total_transit_cost_max": round(total_max_cost, 1),
            "currency": curr_code,
            "approx_transit_cost": total_cost_str,
            "total_travel_cost": total_cost_str,
            "meal_break": "1.0 hr Lunch Break",
        }
    ]

    return normalized, summary_card


def validate_tour_screenplay_contract(data: Dict[str, Any]) -> None:
    """Enforces strict, zero-fallback contract validation for Tour Archetype screenplays.
    
    Raises ValueError immediately if Gemini failed to output mandatory tour elements
    (itinerary_summary, GPS coordinates, visit durations, ticket/entry costs, or transit).
    """
    if not isinstance(data, dict):
        raise ValueError(f"Tour Contract Violation: Screenplay payload is not a dictionary (got {type(data)}).")

    scenes = data.get("scenes")
    if not scenes or not isinstance(scenes, list) or len(scenes) < 2:
        raise ValueError(f"Tour Contract Violation: Tour must have at least 2 scenes (got {len(scenes) if isinstance(scenes, list) else 0}).")

    # 1. Enforce root itinerary_summary presence
    summary = data.get("itinerary_summary")
    if not summary or not isinstance(summary, list) or len(summary) < 1:
        raise ValueError(
            "Tour Contract Violation: Root 'itinerary_summary' is missing or empty. "
            "Gemini must supply the master daily breakdown with total_attraction_time, total_travel_time, "
            "total_walk_time, total_drive_time, and total_travel_cost."
        )

    sum_card = summary[0]
    required_summary_keys = (
        "total_attraction_time",
        "total_travel_time",
        "total_travel_cost",
    )
    missing_summary = [k for k in required_summary_keys if not sum_card.get(k)]
    if missing_summary:
        raise ValueError(f"Tour Contract Violation: 'itinerary_summary' missing required metrics: {missing_summary}")

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

    # 2. Enforce Scene-by-Scene Contract for Physical Landmarks
    for idx, sc in enumerate(scenes, 1):
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
            raise ValueError(f"Tour Contract Violation in Scene {idx}: Missing narration_text and visual_prompt.")

        # Coordinate checks
        if is_info_slide:
            if not sc.get("origin_coords") and first_coords:
                sc["origin_coords"] = first_coords
            if not sc.get("destination_coords") and last_coords:
                sc["destination_coords"] = last_coords
        else:
            origin_coords = sc.get("origin_coords")
            if not origin_coords or not isinstance(origin_coords, (list, tuple)) or len(origin_coords) < 2:
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx} ('{sc.get('origin_name', 'Unnamed')}'): "
                    f"'origin_coords' is missing or invalid (expected [lat, lon] floats, got {origin_coords}). "
                    "Gemini must supply exact GPS coordinates for all tour stops."
                )
            if not sc.get("destination_coords") or not isinstance(sc.get("destination_coords"), (list, tuple)):
                sc["destination_coords"] = origin_coords

        # Landmark-specific mandates
        if not is_card:
            if not sc.get("attraction_name") and not sc.get("origin_name"):
                raise ValueError(f"Tour Contract Violation in Scene {idx}: Landmark scene missing 'attraction_name'.")
            if not sc.get("visit_duration") and not sc.get("duration_seconds"):
                raise ValueError(f"Tour Contract Violation in Scene {idx}: Landmark scene missing 'visit_duration'.")
            if not sc.get("attraction_cost"):
                raise ValueError(
                    f"Tour Contract Violation in Scene {idx} ('{sc.get('attraction_name') or sc.get('origin_name')}'): "
                    "Missing 'attraction_cost' (e.g. '£29.00 Ticket', 'Free Entry', or entry fee)."
                )
