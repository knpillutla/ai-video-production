"""Google Maps 4K Itinerary & Route Cartography Engine.

Renders broadcast-grade 4K travel maps exclusively via Google Maps Static API.
Overlays glowing route paths, sequenced pins starting at 1, collision-free
cardinal attraction callout cards (outside route and pins), and perpendicular
on-route transit badges.
Strict Zero-Fallback Policy: Any API key failure or HTTP error raises RuntimeError.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger
from src.services.google_maps_client import (
    calculate_bounds_and_zoom,
    fetch_google_static_map,
    get_google_maps_api_key,
    lat_lon_to_canvas_pixel,
)
from src.services.map_callout_layout import (
    filter_valid_tour_stops,
    format_dual_distance,
    solve_callout_positions,
    solve_transit_badge_position,
)


def render_4k_google_itinerary_map(
    tour_title: str,
    stops: List[Dict[str, Any]],
    output_path: Path,
    active_leg: Optional[Tuple[int, int]] = None,
    distance_badge: Optional[str] = None,
    transit_mode: Optional[str] = "walk",
    target_res: Tuple[int, int] = (3840, 2160),
    current_stop_index: int = 1,
    force_rerun: bool = False,
) -> Path:
    """Renders 4K broadcast map with progressive green completed and blue upcoming routes."""
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 50_000:
        return out

    if not stops:
        raise ValueError("Google Maps Error: Cannot render itinerary map with zero stops.")

    api_key = get_google_maps_api_key()
    w, h = target_res

    coords, valid_stops = filter_valid_tour_stops(stops)
    if not coords:
        raise ValueError("Google Maps Error: No valid GPS coordinates found in tour stops.")

    curr_idx = max(1, min(len(valid_stops), current_stop_index))
    completed_coords = coords[:curr_idx] if curr_idx > 1 else []
    upcoming_coords = coords[curr_idx - 1:] if curr_idx <= len(coords) else []

    center_lat, center_lon, zoom = calculate_bounds_and_zoom(coords, map_w=640, map_h=360)
    base_bgr = fetch_google_static_map(
        center_lat, center_lon, zoom,
        path_coords=coords, api_key=api_key,
        completed_coords=completed_coords, upcoming_coords=upcoming_coords,
    )
    canvas = cv2.resize(base_bgr, (w, h), interpolation=cv2.INTER_CUBIC)

    pixel_pts: List[Tuple[int, int]] = [
        lat_lon_to_canvas_pixel(lat, lon, center_lat, center_lon, zoom, canvas_w=w, canvas_h=h)
        for lat, lon in coords
    ]

    # Draw glowing route polylines on 4K canvas (Green = Completed, Blue = Upcoming)
    if curr_idx > 1 and len(pixel_pts[:curr_idx]) >= 2:
        cv_comp = np.array(pixel_pts[:curr_idx], dtype=np.int32)
        cv2.polylines(canvas, [cv_comp], isClosed=False, color=(50, 180, 80), thickness=24, lineType=cv2.LINE_AA)
        cv2.polylines(canvas, [cv_comp], isClosed=False, color=(113, 204, 46), thickness=14, lineType=cv2.LINE_AA)
        cv2.polylines(canvas, [cv_comp], isClosed=False, color=(235, 255, 220), thickness=5, lineType=cv2.LINE_AA)

    if len(pixel_pts[curr_idx - 1:]) >= 2:
        cv_upc = np.array(pixel_pts[curr_idx - 1:], dtype=np.int32)
        cv2.polylines(canvas, [cv_upc], isClosed=False, color=(255, 200, 0), thickness=24, lineType=cv2.LINE_AA)
        cv2.polylines(canvas, [cv_upc], isClosed=False, color=(240, 120, 20), thickness=14, lineType=cv2.LINE_AA)
        cv2.polylines(canvas, [cv_upc], isClosed=False, color=(255, 245, 220), thickness=5, lineType=cv2.LINE_AA)

    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 44)
        font_card_title = ImageFont.truetype("arialbd.ttf", 22)
        font_card_sub = ImageFont.truetype("arial.ttf", 16)
        font_badge_num = ImageFont.truetype("arialbd.ttf", 24)
        font_header_sub = ImageFont.truetype("arialbd.ttf", 24)
        font_leg_badge = ImageFont.truetype("arialbd.ttf", 20)
    except Exception:
        font_large = font_card_title = font_card_sub = font_badge_num = font_header_sub = font_leg_badge = ImageFont.load_default()

    hud_x, hud_y, hud_w, hud_h = 100, 80, 1040, 240
    hud_box = (hud_x, hud_y, hud_x + hud_w, hud_y + hud_h)

    # Prepare labels and measure card dimensions
    card_sizes: List[Tuple[int, int]] = []
    card_data: List[Tuple[str, str]] = []
    pin_radius = 28
    for idx, (px, py) in enumerate(pixel_pts):
        stop_num = idx + 1
        sdata = valid_stops[idx]
        sname = sdata.get("name") or sdata.get("attraction_name") or f"Stop {stop_num}"
        cost_str = sdata.get("attraction_cost") or ""
        dur_str = sdata.get("visit_duration") or sdata.get("start_time") or ""

        tag_title = f"{stop_num}. {sname[:30]}"
        detail_line = " • ".join(filter(None, [dur_str, cost_str]))[:34]

        tb = draw.textbbox((0, 0), tag_title, font=font_card_title)
        tw = tb[2] - tb[0]
        if detail_line:
            sb = draw.textbbox((0, 0), detail_line, font=font_card_sub)
            tw = max(tw, sb[2] - sb[0])
        cw = max(220, min(420, tw + 36))
        ch = 60 if detail_line else 42
        card_sizes.append((cw, ch))
        card_data.append((tag_title, detail_line))

    route_segments = [(pixel_pts[i], pixel_pts[i + 1]) for i in range(len(pixel_pts) - 1)]

    # Compute optimal collision-free placements outside the route and outside all pins
    placements = solve_callout_positions(
        pixel_pts, pin_radius, card_sizes, route_segments, hud_box, canvas_w=w, canvas_h=h
    )
    placed_boxes = [p[0] for p in placements]

    # Render on-route transit badge for active leg, offset perpendicularly so route remains 100% visible
    act_leg_idx = (curr_idx - 2) if curr_idx > 1 else 0
    if 0 <= act_leg_idx < len(pixel_pts) - 1:
        p1, p2 = pixel_pts[act_leg_idx], pixel_pts[act_leg_idx + 1]
        c_stop = valid_stops[act_leg_idx]
        d_raw = c_stop.get("distance_local") or "1.5 km"
        dual_d = format_dual_distance(d_raw)
        t_m = str(c_stop.get("transit_mode") or "walk").lower()
        t_d = str(c_stop.get("transit_duration") or "").lower()

        dm = re.search(r"([\d\.]+)", str(d_raw))
        d_km = float(dm.group(1)) if dm else 1.0
        dur_m = re.search(r"(\d+)\s*min", t_d)
        w_mins = int(dur_m.group(1)) if (dur_m and "walk" in t_d) else int(d_km * 12.5)

        if "walk" in t_m and (d_km > 0.8 or w_mins > 10):
            t_m = "drive"

        m_icon = "🚶 Walk" if "walk" in t_m else "🚕 Drive"
        l_cost = c_stop.get("approx_leg_cost") or ("Free (walk)" if "walk" in t_m else "£8–£12 Uber")
        if "walk" not in t_m and ("free" in l_cost.lower() or not any(ch.isdigit() for ch in l_cost)):
            l_cost = "£8–£12 Uber"
        elif "uber" not in l_cost.lower() and "free" not in l_cost.lower() and "walk" not in l_cost.lower():
            l_cost = f"{l_cost} Uber"

        badge_str = f"▶ {m_icon} • {dual_d} • {l_cost}"
        b_box = draw.textbbox((0, 0), badge_str, font=font_leg_badge)
        bw, bh = b_box[2] - b_box[0] + 30, b_box[3] - b_box[1] + 16

        transit_badge_box = solve_transit_badge_position(
            p1, p2, bw, bh, route_segments, pin_radius, pixel_pts, placed_boxes, hud_box, canvas_w=w, canvas_h=h
        )
        if transit_badge_box:
            bx1, by1, bx2, by2 = transit_badge_box
            draw.rectangle([bx1, by1, bx2, by2], fill=(16, 22, 34), outline=(0, 210, 255), width=2)
            draw.text((bx1 + 15, by1 + 6), badge_str, fill=(255, 235, 140), font=font_leg_badge)

    # Render Anchor Lines and Attraction Callout Boxes
    for idx, (px, py) in enumerate(pixel_pts):
        stop_num = idx + 1
        is_done = stop_num < curr_idx
        is_curr = stop_num == curr_idx
        pin_rgb = (46, 204, 113) if (is_done or is_curr) else (37, 99, 235)
        ring_col = (255, 215, 0) if is_curr else (255, 255, 255)

        (bx1, by1, bx2, by2), (sx, sy), (ex, ey) = placements[idx]
        tag_title, detail_line = card_data[idx]

        draw.line([(sx, sy), (ex, ey)], fill=ring_col if is_curr else pin_rgb, width=3)

        tag_border = (255, 215, 0) if is_curr else ((46, 204, 113) if is_done else (0, 210, 255))
        draw.rectangle([bx1, by1, bx2, by2], fill=(16, 22, 34), outline=tag_border, width=2)
        draw.rectangle([bx1, by1, bx1 + 6, by2], fill=pin_rgb)

        draw.text((bx1 + 14, by1 + 8), tag_title, fill=(255, 255, 255), font=font_card_title)
        if detail_line:
            draw.text((bx1 + 14, by1 + 33), detail_line, fill=(255, 215, 0), font=font_card_sub)

    # Render Pins (Circles with Numbers strictly starting at 1)
    for idx, (px, py) in enumerate(pixel_pts):
        stop_num = idx + 1
        is_done = stop_num < curr_idx
        is_curr = stop_num == curr_idx
        pin_rgb = (46, 204, 113) if (is_done or is_curr) else (37, 99, 235)
        ring_col = (255, 215, 0) if is_curr else (255, 255, 255)

        draw.ellipse([px - pin_radius - 5, py - pin_radius - 5, px + pin_radius + 5, py + pin_radius + 5], fill=(0, 0, 0, 180))
        draw.ellipse([px - pin_radius, py - pin_radius, px + pin_radius, py + pin_radius], fill=pin_rgb, outline=ring_col, width=4 if is_curr else 3)

        num_str = str(stop_num)
        bbox = draw.textbbox((0, 0), num_str, font=font_badge_num)
        nw, nh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((px - nw / 2.0, py - nh / 2.0 - 2), num_str, fill=(255, 255, 255), font=font_badge_num)

    # Render Master HUD Header Card (Top Left)
    draw.rectangle([hud_x, hud_y, hud_x + hud_w, hud_y + hud_h], fill=(18, 24, 36), outline=(50, 75, 105), width=3)
    draw.rectangle([hud_x, hud_y, hud_x + 8, hud_y + hud_h], fill=(0, 210, 255))

    draw.text((hud_x + 36, hud_y + 25), "GOOGLE MAPS 4K ITINERARY ROUTE", fill=(0, 210, 255), font=font_header_sub)
    draw.text((hud_x + 36, hud_y + 70), tour_title[:38], fill=(255, 255, 255), font=font_large)

    pct_done = int((curr_idx - 1) / max(1, len(valid_stops) - 1) * 100) if len(valid_stops) > 1 else 0
    stats_text = f"Stop {curr_idx} of {len(valid_stops)} ({pct_done}% Completed)"
    if distance_badge:
        stats_text += f"   •   Distance: {format_dual_distance(distance_badge)}"
    if transit_mode:
        stats_text += f"   •   Transit: {transit_mode.title()}"
    draw.text((hud_x + 36, hud_y + 155), stats_text, fill=(210, 225, 245), font=font_card_title)

    final_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(out), final_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    logger.info(f"google_maps_4k_rendered: '{tour_title}' ({len(valid_stops)} stops) -> {out.name}")
    return out


__all__ = [
    "format_dual_distance",
    "get_google_maps_api_key",
    "calculate_bounds_and_zoom",
    "lat_lon_to_canvas_pixel",
    "fetch_google_static_map",
    "render_4k_google_itinerary_map",
]
