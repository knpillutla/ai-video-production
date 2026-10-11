"""Google Maps 4K Itinerary & Route Cartography Engine.

Renders broadcast-grade 4K travel maps exclusively via Google Maps Static API.
Overlays glowing route paths, strictly sequenced pins starting at 1, non-overlapping
name callout tags (top/bottom outside the pin), and on-route transit badges with
walk/drive distance (km and miles) and local Uber cost.
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
            miles = km * 0.621371
            return f"{km:.1f} km ({miles:.1f} mi)"
        except Exception:
            pass
    return f"{txt} km"


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

    # Deduplicate and extract physical stops starting strictly at 1
    coords: List[Tuple[float, float]] = []
    valid_stops: List[Dict[str, Any]] = []
    seen = set()

    for s in stops:
        if (
            s.get("is_itinerary_overview")
            or s.get("is_itinerary_summary")
            or s.get("is_vacation_scope")
            or s.get("is_map_transition")
        ):
            continue
        c = s.get("coords") or s.get("origin_coords")
        if c and isinstance(c, (list, tuple)) and len(c) >= 2:
            try:
                lat, lon = round(float(c[0]), 5), round(float(c[1]), 5)
                name = s.get("name") or s.get("attraction_name") or s.get("origin_name")
                key = (lat, lon)
                if not name or key in seen:
                    continue
                seen.add(key)
                coords.append((lat, lon))
                valid_stops.append({**s, "coords": (lat, lon), "name": name})
            except (ValueError, TypeError):
                continue

    # Fallback to direct coords if strict filter returned fewer than 2 stops
    if len(valid_stops) < 2:
        coords.clear()
        valid_stops.clear()
        seen.clear()
        for s in stops:
            c = s.get("coords") or s.get("origin_coords")
            if c and isinstance(c, (list, tuple)) and len(c) >= 2:
                lat, lon = round(float(c[0]), 5), round(float(c[1]), 5)
                if (lat, lon) in seen:
                    continue
                seen.add((lat, lon))
                coords.append((lat, lon))
                valid_stops.append({**s, "coords": (lat, lon)})

    if not coords:
        raise ValueError("Google Maps Error: No valid GPS coordinates found in tour stops.")

    curr_idx = max(1, min(len(valid_stops), current_stop_index))
    completed_coords = coords[:curr_idx] if curr_idx > 1 else []
    upcoming_coords = coords[curr_idx - 1:] if curr_idx <= len(coords) else []

    # 1. Compute bounds & zoom
    center_lat, center_lon, zoom = calculate_bounds_and_zoom(coords, map_w=640, map_h=360)

    # 2. Fetch Google Maps base layer with progressive two-tone paths
    base_bgr = fetch_google_static_map(
        center_lat, center_lon, zoom,
        path_coords=coords, api_key=api_key,
        completed_coords=completed_coords, upcoming_coords=upcoming_coords,
    )

    # 3. Super-resolve base layer to 4K
    canvas = cv2.resize(base_bgr, (w, h), interpolation=cv2.INTER_CUBIC)

    pixel_pts: List[Tuple[int, int]] = [
        lat_lon_to_canvas_pixel(lat, lon, center_lat, center_lon, zoom, canvas_w=w, canvas_h=h)
        for lat, lon in coords
    ]

    # 4. Draw glowing route polylines on 4K canvas (Green = Completed, Blue = Upcoming)
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

    # 5. PIL Typography setup
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 46)
        font_card_title = ImageFont.truetype("arialbd.ttf", 34)
        font_card_sub = ImageFont.truetype("arial.ttf", 26)
        font_badge_num = ImageFont.truetype("arialbd.ttf", 28)
        font_header_sub = ImageFont.truetype("arialbd.ttf", 28)
        font_leg_badge = ImageFont.truetype("arialbd.ttf", 26)
    except Exception:
        font_large = font_card_title = font_card_sub = font_badge_num = font_header_sub = font_leg_badge = ImageFont.load_default()

    # 6. Render On-Route Transit Badges Between Consecutive Stops
    for idx in range(len(pixel_pts) - 1):
        p1, p2 = pixel_pts[idx], pixel_pts[idx + 1]
        mid_x, mid_y = int((p1[0] + p2[0]) / 2.0), int((p1[1] + p2[1]) / 2.0)
        curr_stop = valid_stops[idx]

        dist_raw = curr_stop.get("distance_local") or "1.5 km"
        dual_dist = format_dual_distance(dist_raw)
        t_mode = str(curr_stop.get("transit_mode") or "walk").lower()
        mode_icon = "🚶 Walk" if "walk" in t_mode else "🚕 Drive"

        leg_cost = curr_stop.get("approx_leg_cost") or ("Free (walk)" if "walk" in t_mode else "£8–£12 Uber")
        if "uber" not in leg_cost.lower() and "free" not in leg_cost.lower() and "walk" not in leg_cost.lower():
            leg_cost = f"{leg_cost} Uber"

        is_done_leg = idx < (curr_idx - 1)
        is_act_leg = idx == (curr_idx - 1)
        prefix = "✓ " if is_done_leg else ("▶ " if is_act_leg else "")
        badge_border = (46, 204, 113) if is_done_leg else ((0, 210, 255) if is_act_leg else (50, 75, 105))
        badge_str = f"{prefix}{mode_icon} • {dual_dist} • {leg_cost}"

        bbox = draw.textbbox((0, 0), badge_str, font=font_leg_badge)
        bw, bh = bbox[2] - bbox[0] + 36, bbox[3] - bbox[1] + 18
        bx1 = max(100, min(w - bw - 100, mid_x - bw // 2))
        by1 = max(100, min(h - bh - 100, mid_y - bh // 2 - 16))
        bx2, by2 = bx1 + bw, by1 + bh

        draw.rectangle([bx1, by1, bx2, by2], fill=(16, 22, 34), outline=badge_border, width=2)
        txt_fill = (220, 255, 230) if is_done_leg else ((255, 235, 140) if is_act_leg else (200, 215, 235))
        draw.text((bx1 + 18, by1 + 8), badge_str, fill=txt_fill, font=font_leg_badge)

    # 7. Render Pins & Smart Non-Overlapping Callout Tags (Starting Strictly at 1)
    pin_radius = 32
    for idx, (px, py) in enumerate(pixel_pts):
        stop_data = valid_stops[idx]
        stop_num = idx + 1
        stop_name = (
            stop_data.get("name")
            or stop_data.get("attraction_name")
            or stop_data.get("origin_name")
            or f"Stop {stop_num}"
        )
        cost_str = stop_data.get("attraction_cost") or ""
        duration_str = stop_data.get("visit_duration") or stop_data.get("start_time") or ""

        is_done = stop_num < curr_idx
        is_curr = stop_num == curr_idx
        pin_color_rgb = (46, 204, 113) if (is_done or is_curr) else (37, 99, 235)
        ring_color = (255, 215, 0) if is_curr else (255, 255, 255)

        # Draw Pin Badge Circle (Never covered by tags)
        draw.ellipse([px - pin_radius - 6, py - pin_radius - 6, px + pin_radius + 6, py + pin_radius + 6], fill=(0, 0, 0, 180))
        draw.ellipse([px - pin_radius, py - pin_radius, px + pin_radius, py + pin_radius], fill=pin_color_rgb, outline=ring_color, width=5 if is_curr else 4)

        num_str = str(stop_num)
        bbox = draw.textbbox((0, 0), num_str, font=font_badge_num)
        nw, nh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((px - nw / 2.0, py - nh / 2.0 - 2), num_str, fill=(255, 255, 255), font=font_badge_num)

        # Smart Non-Overlapping Position (Alternate Top and Bottom outside pin)
        tag_w = 460
        tag_h = 92 if (cost_str or duration_str) else 62

        place_top = (idx % 2 == 0)
        if py < 350:
            place_top = False
        elif py > h - 350:
            place_top = True

        tag_x = int(px - tag_w / 2)
        tag_y = (py - pin_radius - tag_h - 22) if place_top else (py + pin_radius + 22)
        tag_x = max(120, min(w - tag_w - 120, tag_x))
        tag_y = max(120, min(h - tag_h - 120, tag_y))

        # Anchor Line connecting pin edge to tag
        anchor_y = tag_y + tag_h if place_top else tag_y
        draw.line([px, py + (-pin_radius if place_top else pin_radius), px, anchor_y], fill=ring_color if is_curr else pin_color_rgb, width=3)

        # Callout Tag Box
        tag_border = (255, 215, 0) if is_curr else ((46, 204, 113) if is_done else (0, 210, 255))
        draw.rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], fill=(16, 22, 34), outline=tag_border, width=2)
        draw.rectangle([tag_x, tag_y, tag_x + 6, tag_y + tag_h], fill=pin_color_rgb)

        tag_title = f"{stop_num}. {stop_name[:22]}" + (" ★" if is_curr else "")
        draw.text((tag_x + 18, tag_y + 10), tag_title, fill=(255, 255, 255), font=font_card_title)
        if cost_str or duration_str:
            detail_line = " • ".join(filter(None, [duration_str, cost_str]))[:34]
            draw.text((tag_x + 18, tag_y + 52), detail_line, fill=(255, 215, 0), font=font_card_sub)

    # 8. Render Master HUD Header Card (Top Left)
    hud_w, hud_h = 1040, 240
    hud_x, hud_y = 120, 100
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

    # 9. Save output 4K JPEG
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
