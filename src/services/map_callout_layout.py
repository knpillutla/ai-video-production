"""Smart Non-Overlapping Callout & Transit Badge Placement Solver for 4K Maps.

Calculates collision-free cardinal placements (right, left, bottom, top, diagonals)
for attraction callout cards and perpendicular on-route transit badges to guarantee
that pins, destination labels, and route paths never overlap each other.
"""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple

Box = Tuple[int, int, int, int]  # (x1, y1, x2, y2)
Point = Tuple[int, int]


def format_dual_distance(dist_str_or_val: Any) -> str:
    """Formats distance with both kilometers and miles, e.g. '2.8 km (1.7 mi)'."""
    if not dist_str_or_val:
        return "1.5 km (0.9 mi)"
    txt = str(dist_str_or_val).strip()
    if "mi" in txt.lower():
        return txt
    m = re.search(r"([\d\.]+)\s*(?:km)?", txt, re.IGNORECASE)
    if m:
        try:
            km = float(m.group(1))
            return f"{km:.1f} km ({km * 0.621371:.1f} mi)"
        except Exception:
            pass
    return f"{txt} km"


def filter_valid_tour_stops(stops: List[Dict[str, Any]]) -> Tuple[List[Tuple[float, float]], List[Dict[str, Any]]]:
    """Extracts deduplicated physical stops with GPS coordinates starting strictly at 1."""
    coords: List[Tuple[float, float]] = []
    valid: List[Dict[str, Any]] = []
    seen = set()

    for s in stops:
        if s.get("is_itinerary_overview") or s.get("is_itinerary_summary") or s.get("is_vacation_scope") or s.get("is_map_transition"):
            continue
        c = s.get("coords") or s.get("origin_coords")
        if c and isinstance(c, (list, tuple)) and len(c) >= 2:
            try:
                lat, lon = round(float(c[0]), 5), round(float(c[1]), 5)
                name = s.get("name") or s.get("attraction_name") or s.get("origin_name")
                if not name or (lat, lon) in seen:
                    continue
                seen.add((lat, lon))
                coords.append((lat, lon))
                valid.append({**s, "coords": (lat, lon), "name": name})
            except (ValueError, TypeError):
                continue

    if len(valid) < 2:
        coords.clear()
        valid.clear()
        seen.clear()
        for s in stops:
            c = s.get("coords") or s.get("origin_coords")
            if c and isinstance(c, (list, tuple)) and len(c) >= 2:
                lat, lon = round(float(c[0]), 5), round(float(c[1]), 5)
                if (lat, lon) in seen:
                    continue
                seen.add((lat, lon))
                coords.append((lat, lon))
                valid.append({**s, "coords": (lat, lon)})

    return coords, valid


def ccw(A: Point, B: Point, C: Point) -> bool:
    """Tests if points A, B, C are in counter-clockwise order."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def segments_intersect(A: Point, B: Point, C: Point, D: Point) -> bool:
    """Determines whether 2D line segment AB intersects CD."""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def segment_intersects_box(p1: Point, p2: Point, box: Box, buffer: int = 18) -> bool:
    """Checks if line segment p1-p2 intersects box with safety buffer."""
    bx1, by1, bx2, by2 = box[0] - buffer, box[1] - buffer, box[2] + buffer, box[3] + buffer
    if (bx1 <= p1[0] <= bx2 and by1 <= p1[1] <= by2) or (bx1 <= p2[0] <= bx2 and by1 <= p2[1] <= by2):
        return True
    corners = [(bx1, by1), (bx2, by1), (bx2, by2), (bx1, by2)]
    for i in range(4):
        if segments_intersect(p1, p2, corners[i], corners[(i + 1) % 4]):
            return True
    return False


def box_intersects_circle(box: Box, center: Point, radius: int) -> bool:
    """Checks if box intersects circle at center with radius."""
    cx, cy = center
    bx1, by1, bx2, by2 = box
    clx = max(bx1, min(cx, bx2))
    cly = max(by1, min(cy, by2))
    return (cx - clx) ** 2 + (cy - cly) ** 2 < (radius ** 2)


def boxes_intersect(b1: Box, b2: Box, margin: int = 12) -> bool:
    """Checks if two axis-aligned bounding boxes overlap within margin."""
    return not (
        b1[2] + margin < b2[0]
        or b1[0] - margin > b2[2]
        or b1[3] + margin < b2[1]
        or b1[1] - margin > b2[3]
    )


def solve_callout_positions(
    pixel_pts: List[Point],
    pin_radius: int,
    card_sizes: List[Tuple[int, int]],
    route_segments: List[Tuple[Point, Point]],
    hud_box: Box,
    canvas_w: int = 3840,
    canvas_h: int = 2160,
) -> List[Tuple[Box, Point, Point]]:
    """Calculates non-overlapping cardinal placements for all stop callouts.

    Returns list of (box, anchor_start, anchor_end) tuples.
    """
    placed_boxes: List[Box] = []
    results: List[Tuple[Box, Point, Point]] = []

    directions = [
        "right", "left", "bottom", "top",
        "bottom_right", "top_right", "bottom_left", "top_left",
    ]
    gaps = [28, 55, 90, 135, 185, 245, 320]

    for idx, (px, py) in enumerate(pixel_pts):
        tw, th = card_sizes[idx]
        best_candidate: Optional[Tuple[Box, Point, Point, float]] = None

        for gap in gaps:
            for d in directions:
                if d == "right":
                    bx1 = px + pin_radius + gap
                    by1 = py - th // 2
                elif d == "left":
                    bx1 = px - pin_radius - gap - tw
                    by1 = py - th // 2
                elif d == "bottom":
                    bx1 = px - tw // 2
                    by1 = py + pin_radius + gap
                elif d == "top":
                    bx1 = px - tw // 2
                    by1 = py - pin_radius - gap - th
                elif d == "bottom_right":
                    bx1 = px + pin_radius + gap
                    by1 = py + pin_radius + gap
                elif d == "top_right":
                    bx1 = px + pin_radius + gap
                    by1 = py - pin_radius - gap - th
                elif d == "bottom_left":
                    bx1 = px - pin_radius - gap - tw
                    by1 = py + pin_radius + gap
                elif d == "top_left":
                    bx1 = px - pin_radius - gap - tw
                    by1 = py - pin_radius - gap - th
                else:
                    continue

                bx2, by2 = bx1 + tw, by1 + th
                cand_box: Box = (bx1, by1, bx2, by2)

                if bx1 < 80 or bx2 > canvas_w - 80 or by1 < 80 or by2 > canvas_h - 80:
                    continue
                if boxes_intersect(cand_box, hud_box, margin=20):
                    continue
                if any(box_intersects_circle(cand_box, pt, pin_radius + 16) for pt in pixel_pts):
                    continue
                if any(segment_intersects_box(pa, pb, cand_box, buffer=22) for pa, pb in route_segments):
                    continue
                if any(boxes_intersect(cand_box, pb, margin=14) for pb in placed_boxes):
                    continue

                cost = float(gap)
                if best_candidate is None or cost < best_candidate[3]:
                    clx = max(bx1, min(px, bx2))
                    cly = max(by1, min(py, by2))
                    dx, dy = clx - px, cly - py
                    dist = math.hypot(dx, dy)
                    sx = int(round(px + (dx / dist) * pin_radius)) if dist > 0 else px
                    sy = int(round(py + (dy / dist) * pin_radius)) if dist > 0 else py
                    best_candidate = (cand_box, (sx, sy), (clx, cly), cost)

            if best_candidate is not None:
                break

        if best_candidate is None:
            fb_bx1 = max(80, min(canvas_w - tw - 80, px + pin_radius + 20))
            fb_by1 = max(80, min(canvas_h - th - 80, py - th // 2))
            cand_box = (fb_bx1, fb_by1, fb_bx1 + tw, fb_by1 + th)
            best_candidate = (cand_box, (px + pin_radius, py), (fb_bx1, py), 999.0)

        placed_boxes.append(best_candidate[0])
        results.append((best_candidate[0], best_candidate[1], best_candidate[2]))

    return results


def solve_transit_badge_position(
    p1: Point,
    p2: Point,
    badge_w: int,
    badge_h: int,
    route_segments: List[Tuple[Point, Point]],
    pin_radius: int,
    pixel_pts: List[Point],
    placed_boxes: List[Box],
    hud_box: Box,
    canvas_w: int = 3840,
    canvas_h: int = 2160,
) -> Optional[Box]:
    """Calculates perpendicular offset for transit badge to avoid covering the route."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    seg_len = math.hypot(dx, dy)
    if seg_len < 40:
        return None

    mx = (p1[0] + p2[0]) / 2.0
    my = (p1[1] + p2[1]) / 2.0
    nx = -dy / seg_len
    ny = dx / seg_len

    for offset_dist in [55, -55, 95, -95]:
        cx = int(round(mx + nx * offset_dist))
        cy = int(round(my + ny * offset_dist))
        bx1 = cx - badge_w // 2
        by1 = cy - badge_h // 2
        bx2, by2 = bx1 + badge_w, by1 + badge_h
        cand: Box = (bx1, by1, bx2, by2)

        if bx1 < 80 or bx2 > canvas_w - 80 or by1 < 80 or by2 > canvas_h - 80:
            continue
        if boxes_intersect(cand, hud_box, margin=15):
            continue
        if any(box_intersects_circle(cand, pt, pin_radius + 14) for pt in pixel_pts):
            continue
        if any(segment_intersects_box(pa, pb, cand, buffer=16) for pa, pb in route_segments):
            continue
        if any(boxes_intersect(cand, pb, margin=10) for pb in placed_boxes):
            continue
        return cand

    return None
