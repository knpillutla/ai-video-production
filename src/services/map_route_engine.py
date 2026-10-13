"""Deterministic 4K Topographic Route Map Engine.

Renders broadcast-grade 4K travel maps exclusively via Google Maps Static API,
glowing royal blue route lines, numbered destination pins, and HUD transit distance badges.
Strict Zero-Fallback Policy: Uses Google Maps exclusively; errors out if API fails.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger
from src.services.google_maps_engine import render_4k_google_itinerary_map


def render_4k_route_map(
    origin_name: str,
    dest_name: str,
    origin_coords: Tuple[float, float],
    dest_coords: Tuple[float, float],
    distance_badge: str,
    transit_mode: str,
    output_path: Path,
    target_res: Tuple[int, int] = (3840, 2160),
    all_stops: Optional[List[Dict[str, Any]]] = None,
    tour_title: Optional[str] = None,
    current_stop_index: int = 1,
    force_rerun: bool = False,
) -> Path:
    """Renders a stunning 4K Google Maps route map with progressive green completed and blue upcoming paths."""
    stops = all_stops or [
        {"name": origin_name, "coords": origin_coords},
        {"name": dest_name, "coords": dest_coords},
    ]
    title = tour_title or f"{origin_name} to {dest_name}"

    if (current_stop_index is None or current_stop_index <= 0) and all_stops:
        d_lower = (dest_name or "").lower()
        for idx, s in enumerate(all_stops):
            s_name = (s.get("name") or s.get("attraction_name") or "").lower()
            s_coords = s.get("coords")
            if (d_lower and (d_lower in s_name or s_name in d_lower)) or (
                s_coords and abs(s_coords[0] - dest_coords[0]) < 0.001 and abs(s_coords[1] - dest_coords[1]) < 0.001
            ):
                current_stop_index = idx + 1
                break
    curr_idx = max(1, current_stop_index if current_stop_index is not None else 1)

    return render_4k_google_itinerary_map(
        tour_title=title,
        stops=stops,
        output_path=output_path,
        distance_badge=distance_badge,
        transit_mode=transit_mode,
        target_res=target_res,
        current_stop_index=curr_idx,
        force_rerun=force_rerun,
    )



def render_4k_itinerary_summary_card(
    tour_title: str,
    day_summaries: List[Dict[str, Any]],
    output_path: Path,
    target_res: Tuple[int, int] = (3840, 2160),
) -> Path:
    """Renders a prestigious 4K master itinerary recap card summarizing each day's schedule."""
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file() and out.stat().st_size > 1000:
        return out

    w, h = target_res
    # Deep midnight slate gradient background
    bg = np.zeros((h, w, 3), dtype=np.uint8)
    for y_idx in range(h):
        blend = y_idx / float(h)
        bg[y_idx, :] = [int(28 * (1 - blend) + 14 * blend), int(22 * (1 - blend) + 12 * blend), int(18 * (1 - blend) + 10 * blend)]

    pil_img = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 64)
        font_sub = ImageFont.truetype("arial.ttf", 34)
        font_card_title = ImageFont.truetype("arialbd.ttf", 40)
        font_body_bold = ImageFont.truetype("arialbd.ttf", 30)
        font_body = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font_header = font_card_title = font_body_bold = font_body = font_sub = ImageFont.load_default()

    # Master Header
    draw.text((180, 100), "MASTER TRAVEL ITINERARY SUMMARY", fill=(0, 210, 255), font=font_sub)
    draw.text((180, 150), f"{tour_title} • Complete Daily Planner (9:00 AM – 6:00 PM)", fill=(255, 255, 255), font=font_header)

    num_days = max(1, min(4, len(day_summaries)))
    gap = 60
    card_w = int((w - 360 - (num_days - 1) * gap) / num_days)
    card_h = 1600
    top_y = 280

    for d_idx, day_info in enumerate(day_summaries[:num_days]):
        x_left = 180 + d_idx * (card_w + gap)
        # Draw glass container background
        card_rect = [x_left, top_y, x_left + card_w, top_y + card_h]
        draw.rectangle(card_rect, fill=(24, 30, 40), outline=(50, 70, 95), width=3)
        # Header accent band
        draw.rectangle([x_left, top_y, x_left + card_w, top_y + 120], fill=(32, 44, 62))
        draw.rectangle([x_left, top_y + 114, x_left + card_w, top_y + 120], fill=(0, 210, 255))

        day_num = day_info.get("day", d_idx + 1)
        day_title = day_info.get("day_title", f"Day {day_num} Highlights")
        draw.text((x_left + 35, top_y + 25), f"DAY {day_num}", fill=(0, 210, 255), font=font_body_bold)
        draw.text((x_left + 35, top_y + 65), day_title[:28], fill=(255, 255, 255), font=font_card_title)

        cur_y = top_y + 160
        # Attractions List
        draw.text((x_left + 35, cur_y), "🏛️ ATTRACTIONS VISITED:", fill=(180, 205, 235), font=font_body_bold)
        cur_y += 45
        attractions = day_info.get("attractions", [])
        for att in attractions[:5]:
            draw.text((x_left + 50, cur_y), f"• {att}", fill=(240, 240, 245), font=font_body)
            cur_y += 40

        cur_y += 30
        draw.line([x_left + 35, cur_y, x_left + card_w - 35, cur_y], fill=(50, 70, 95), width=2)
        cur_y += 35

        # Key Metrics - Complete Breakdown
        metrics = [
            ("⏱️ Total Attraction Time:", day_info.get("total_attraction_time") or day_info.get("total_attraction_hours", "6.5 hrs")),
            ("🚕 Total Travel Time:", day_info.get("total_travel_time") or day_info.get("total_transit_hours", "1.0 hr")),
            ("🚶 Total Walk Time:", day_info.get("total_walk_time", "35 mins")),
            ("🚗 Total Drive Time:", day_info.get("total_drive_time", "25 mins")),
            ("📍 Transit Distance:", day_info.get("transit_distance", "4.5 km circuit")),
            ("💳 Total Travel Cost:", day_info.get("total_travel_cost") or day_info.get("approx_transit_cost", "£24–£34 (~$45 USD)")),
            ("🍽️ Midday Lunch Break:", day_info.get("meal_break", "1.0 hr Lunch Break")),
            ("🏨 Complete Schedule:", "09:00 AM – 06:00 PM (9.0 hrs)"),
        ]
        for label, val in metrics:
            draw.text((x_left + 35, cur_y), label, fill=(160, 180, 205), font=font_body)
            draw.text((x_left + 35, cur_y + 35), str(val), fill=(255, 255, 255), font=font_body_bold)
            cur_y += 75

    out_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(out), out_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    logger.info(f"itinerary_summary_card_rendered: {tour_title} at {out.name}")
    return out


def render_4k_leisure_vacation_card(
    tour_title: str,
    ideal_days: str = "4–5 Days",
    additional_attractions: Optional[List[str]] = None,
    safe_neighborhood_squares: Optional[List[str]] = None,
    output_path: Optional[Path] = None,
    force_rerun: bool = False,
) -> Path:
    """Renders a magazine-grade 4K infographic slide for ideal vacation duration and safest neighborhood cafes/squares."""
    out = (output_path or Path("vacation_scope_4k.jpg")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if not force_rerun and out.is_file() and out.stat().st_size > 50_000:
        return out
    w, h = 3840, 2160

    # Modern slate deep navy canvas
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas[:, :] = [18, 22, 28]

    # Subtle ambient gradient
    for y in range(h):
        blend = y / float(h)
        canvas[y, :] = [int(18 + 12 * blend), int(22 + 16 * blend), int(28 + 24 * blend)]

    pil_img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(pil_img)

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 68)
        font_sub = ImageFont.truetype("arial.ttf", 36)
        font_badge = ImageFont.truetype("arialbd.ttf", 52)
        font_card_title = ImageFont.truetype("arialbd.ttf", 44)
        font_body_bold = ImageFont.truetype("arialbd.ttf", 34)
        font_body = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font_header = font_card_title = font_body_bold = font_body = font_sub = font_badge = ImageFont.load_default()

    # Master Header
    draw.text((180, 100), "PLANNING YOUR EXTENDED TRIP", fill=(0, 210, 255), font=font_sub)
    draw.text((180, 155), f"{tour_title} • The Complete Leisure Vacation Guide", fill=(255, 255, 255), font=font_header)

    # Big Recommended Stay Badge Box
    draw.rectangle([180, 260, 3660, 420], fill=(26, 36, 52), outline=(0, 210, 255), width=3)
    draw.text((220, 285), "RECOMMENDED LEISURE PACE:", fill=(180, 210, 240), font=font_sub)
    draw.text((220, 335), f"✨ {ideal_days} for a relaxed, unhurried vacation", fill=(255, 215, 0), font=font_badge)

    col_w, top_y, bot_y = 1700, 470, 2020
    # Box 1: Landmark Extensions
    draw.rectangle([180, top_y, 180 + col_w, bot_y], fill=(24, 30, 40), outline=(50, 70, 95), width=3)
    draw.rectangle([180, top_y, 180 + col_w, top_y + 110], fill=(32, 44, 62))
    draw.rectangle([180, top_y + 104, 180 + col_w, top_y + 110], fill=(0, 210, 255))
    draw.text((220, top_y + 35), "🏛️ EXPANDED LANDMARKS & DAY TRIPS", fill=(255, 255, 255), font=font_card_title)

    default_attractions = [
        "British Museum & Bloomsbury Gardens", "Kensington Palace & Hyde Park Walk",
        "Tate Modern & Millennium Bridge Southbank", "Royal Observatory & Maritime Greenwich",
        "Day Trip: Historic Windsor Castle & Great Park", "Day Trip: University City of Oxford (1 hr train)",
    ]
    cur_y = top_y + 160
    for item in (additional_attractions or default_attractions)[:6]:
        draw.text((230, cur_y), f"• {item}", fill=(240, 245, 255), font=font_body_bold)
        cur_y += 75

    # Box 2: Safest Neighborhood Squares, Cafes & Family Havens
    col2_x = 180 + col_w + 80
    draw.rectangle([col2_x, top_y, col2_x + col_w, bot_y], fill=(24, 30, 40), outline=(50, 70, 95), width=3)
    draw.rectangle([col2_x, top_y, col2_x + col_w, top_y + 110], fill=(32, 44, 62))
    draw.rectangle([col2_x, top_y + 104, col2_x + col_w, top_y + 110], fill=(46, 213, 115))
    draw.text((col2_x + 40, top_y + 35), "☕ SAFEST SQUARES, CAFES & FAMILY HAVENS", fill=(255, 255, 255), font=font_card_title)

    default_safe_spots = [
        "Covent Garden Piazza (Pedestrianized, street music, kid-safe)",
        "St Katharine Docks Marina (Calm waterside cafes, zero traffic)",
        "Neal's Yard & Seven Dials (Vibrant boutique bakeries, cozy courtyards)",
        "Marylebone High Street (Charming tea salons, refined neighborhood)",
        "Richmond Riverside (Quiet family meadows, relaxed terrace cafes)",
        "Greenwich Market & Painted Hall (Artisan foods, pedestrian-only)",
    ]
    cur_y = top_y + 160
    for item in (safe_neighborhood_squares or default_safe_spots)[:6]:
        draw.text((col2_x + 50, cur_y), f"✓ {item}", fill=(230, 245, 235), font=font_body)
        cur_y += 75

    out_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(out), out_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    logger.info(f"leisure_vacation_card_rendered: {tour_title} at {out.name}")
    return out


def create_lower_third_hud_overlay(
    attraction_name: str,
    timing_text: str,
    day_badge: str = "DAY 1",
    target_res: Tuple[int, int] = (3840, 2160),
    cost_text: Optional[str] = None,
    transit_text: Optional[str] = None,
) -> np.ndarray:
    """Creates a broadcast-grade 4K RGBA lower-third glass HUD overlay with safe margins."""
    w, h = target_res
    overlay = np.zeros((h, w, 4), dtype=np.uint8)

    # Safe bottom-left positioning (x=120, y=h-420, w=1180, h=280)
    hud_h = 280 if (cost_text or transit_text) else 230
    hud_x, hud_y = 120, h - (hud_h + 120)
    hud_w = 1180

    # Draw dark frosted glass card (alpha = 220 / 255 = 86% opacity)
    card_rgba = np.zeros((hud_h, hud_w, 4), dtype=np.uint8)
    card_rgba[:, :] = [14, 18, 25, 220]
    # Gold accent border
    card_rgba[:, :10] = [255, 195, 0, 255]
    overlay[hud_y : hud_y + hud_h, hud_x : hud_x + hud_w] = card_rgba

    # PIL rendering for crisp typography
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 32)
        font_title = ImageFont.truetype("arialbd.ttf", 52)
        font_time = ImageFont.truetype("arial.ttf", 36)
        font_detail = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        font_sub = font_title = font_time = font_detail = ImageFont.load_default()

    draw.text((hud_x + 36, hud_y + 24), day_badge.upper(), fill=(0, 220, 255, 255), font=font_sub)
    draw.text((hud_x + 36, hud_y + 68), attraction_name[:38], fill=(255, 255, 255, 255), font=font_title)
    draw.text((hud_x + 36, hud_y + 138), timing_text, fill=(220, 235, 250, 255), font=font_time)

    # Optional 4th line for Admission Cost and Next Transit leg
    if cost_text or transit_text:
        parts = []
        if cost_text:
            parts.append(f"🎟️ {cost_text}")
        if transit_text:
            parts.append(f"🚶 {transit_text}")
        extra_line = "   •   ".join(parts)
        draw.text((hud_x + 36, hud_y + 198), extra_line, fill=(255, 215, 0, 255), font=font_detail)

    return np.array(pil_overlay)
