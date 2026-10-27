"""Broadcast-Grade 4K Cartographic Inset & Geographic Locator Overlay Service.

Renders high-definition dark-slate cartographic locator cards for educational documentaries,
featuring country borders, capital coordinate beacons, topographic grid crosshairs, and key almanac metrics.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_overlay_service import _load_font


COUNTRY_GEO_ALMANAC: Dict[str, Dict[str, Any]] = {
    "france": {
        "display_name": "FRANCE",
        "region": "WESTERN EUROPE",
        "capital": "Paris",
        "coords": "48.85° N, 2.35° E",
        "area": "643,801 km²",
        "coastline": "3,427 km",
        "seas": ["Atlantic Ocean", "Mediterranean Sea"],
        "borders": ["Spain", "Germany", "Italy", "Belgium", "Swiss"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.42, 0.28), (0.56, 0.26), (0.68, 0.38), (0.64, 0.62), (0.50, 0.74), (0.36, 0.66), (0.32, 0.44)],
        "capital_pos": (0.52, 0.38),
    },
    "spain": {
        "display_name": "SPAIN",
        "region": "IBERIAN PENINSULA",
        "capital": "Madrid",
        "coords": "40.41° N, 3.70° W",
        "area": "505,990 km²",
        "coastline": "4,964 km",
        "seas": ["Atlantic Ocean", "Mediterranean Sea", "Bay of Biscay"],
        "borders": ["Portugal", "France", "Andorra"],
        "map_center": (0.50, 0.52),
        "polygon_points": [(0.32, 0.34), (0.68, 0.30), (0.76, 0.52), (0.64, 0.74), (0.36, 0.76), (0.28, 0.54)],
        "capital_pos": (0.50, 0.50),
    },
    "italy": {
        "display_name": "ITALY",
        "region": "SOUTHERN EUROPE",
        "capital": "Rome",
        "coords": "41.90° N, 12.49° E",
        "area": "302,073 km²",
        "coastline": "7,600 km",
        "seas": ["Adriatic Sea", "Tyrrhenian Sea", "Ionian Sea"],
        "borders": ["France", "Switzerland", "Austria", "Slovenia"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.30, 0.24), (0.68, 0.22), (0.62, 0.44), (0.74, 0.68), (0.62, 0.76), (0.46, 0.54), (0.42, 0.36)],
        "capital_pos": (0.52, 0.50),
    },
    "germany": {
        "display_name": "GERMANY",
        "region": "CENTRAL EUROPE",
        "capital": "Berlin",
        "coords": "52.52° N, 13.40° E",
        "area": "357,592 km²",
        "coastline": "2,389 km",
        "seas": ["North Sea", "Baltic Sea"],
        "borders": ["France", "Poland", "Czechia", "Austria", "Swiss"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.42, 0.22), (0.64, 0.24), (0.70, 0.46), (0.62, 0.76), (0.38, 0.74), (0.32, 0.48)],
        "capital_pos": (0.62, 0.36),
    },
    "uk": {
        "display_name": "UNITED KINGDOM",
        "region": "BRITISH ISLES",
        "capital": "London",
        "coords": "51.50° N, 0.12° W",
        "area": "242,495 km²",
        "coastline": "12,429 km",
        "seas": ["North Sea", "Atlantic Ocean", "English Channel"],
        "borders": ["Ireland"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.48, 0.20), (0.58, 0.34), (0.52, 0.58), (0.62, 0.74), (0.42, 0.78), (0.38, 0.52)],
        "capital_pos": (0.58, 0.70),
    },
    "poland": {
        "display_name": "POLAND",
        "region": "CENTRAL EUROPE",
        "capital": "Warsaw",
        "coords": "52.23° N, 21.01° E",
        "area": "312,696 km²",
        "coastline": "440 km",
        "seas": ["Baltic Sea"],
        "borders": ["Germany", "Czechia", "Slovakia", "Ukraine", "Lithuania"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.34, 0.28), (0.64, 0.24), (0.74, 0.46), (0.68, 0.72), (0.36, 0.70), (0.28, 0.48)],
        "capital_pos": (0.58, 0.46),
    },
    "greece": {
        "display_name": "GREECE",
        "region": "MEDITERRANEAN & AEGEAN",
        "capital": "Athens",
        "coords": "37.98° N, 23.72° E",
        "area": "131,957 km²",
        "coastline": "13,676 km",
        "seas": ["Aegean Sea", "Ionian Sea", "Cretan Sea"],
        "borders": ["Albania", "North Macedonia", "Bulgaria", "Turkey"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.36, 0.26), (0.62, 0.28), (0.58, 0.54), (0.72, 0.72), (0.42, 0.78), (0.30, 0.50)],
        "capital_pos": (0.56, 0.60),
    },
    "norway": {
        "display_name": "NORWAY",
        "region": "SCANDINAVIA",
        "capital": "Oslo",
        "coords": "59.91° N, 10.75° E",
        "area": "385,207 km²",
        "coastline": "25,148 km",
        "seas": ["Norwegian Sea", "North Sea", "Barents Sea"],
        "borders": ["Sweden", "Finland", "Russia"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.72, 0.16), (0.66, 0.32), (0.52, 0.54), (0.42, 0.78), (0.34, 0.68), (0.48, 0.42)],
        "capital_pos": (0.46, 0.74),
    },
    "japan": {
        "display_name": "JAPAN",
        "region": "EAST ASIA",
        "capital": "Tokyo",
        "coords": "35.67° N, 139.65° E",
        "area": "377,975 km²",
        "coastline": "29,751 km",
        "seas": ["Pacific Ocean", "Sea of Japan", "East China Sea"],
        "borders": ["Maritime Borders: Korea, China, Russia"],
        "map_center": (0.50, 0.50),
        "polygon_points": [(0.72, 0.22), (0.64, 0.42), (0.46, 0.64), (0.32, 0.74), (0.38, 0.66), (0.54, 0.44)],
        "capital_pos": (0.56, 0.54),
    },
}


def _match_country_key(query: str) -> str:
    cleaned = (query or "").lower().strip()
    for k in COUNTRY_GEO_ALMANAC:
        if k in cleaned:
            return k
    if any(w in cleaned for w in ("scotland", "britain", "england", "london")):
        return "uk"
    return "france"


def create_cartographic_locator_overlay(
    country_query: str,
    target_res: Tuple[int, int] = (3840, 2160),
) -> np.ndarray:
    """Renders a prestigious 4K RGBA Cartographic Locator Inset Card in the upper right quadrant."""
    w, h = target_res
    s = h / 2160.0

    key = _match_country_key(country_query)
    data = COUNTRY_GEO_ALMANAC.get(key, COUNTRY_GEO_ALMANAC["france"])

    overlay = np.zeros((h, w, 4), dtype=np.uint8)

    card_w = int(720 * s)
    card_h = int(410 * s)
    # Upper-right quadrant placement: safe 6% margin from right, 7% from top
    card_x = w - card_w - int(w * 0.055)
    card_y = int(h * 0.075)

    card_rgba = np.zeros((card_h, card_w, 4), dtype=np.uint8)
    card_rgba[:, :] = [10, 14, 22, 220]  # 86% opacity obsidian slate

    top_h = max(3, int(4 * s))
    card_rgba[:top_h, :] = [255, 204, 51, 255]  # Golden top accent
    card_rgba[-1, :] = [255, 255, 255, 50]
    card_rgba[:, 0] = [255, 255, 255, 50]
    card_rgba[:, -1] = [255, 255, 255, 50]

    overlay[card_y : card_y + card_h, card_x : card_x + card_w] = card_rgba
    pil_overlay = Image.fromarray(overlay)
    draw = ImageDraw.Draw(pil_overlay)

    font_badge = _load_font(int(20 * s), bold=True)
    font_title = _load_font(int(36 * s), bold=True)
    font_sub = _load_font(int(22 * s), bold=False)
    font_stats = _load_font(int(19 * s), bold=False)
    font_compass = _load_font(int(18 * s), bold=True)

    cur_x = card_x + int(24 * s)
    cur_y = card_y + int(18 * s)

    # 1. Badge & Country Header
    draw.text((cur_x, cur_y), "🗺️ GEOGRAPHIC LOCATOR", fill=(255, 215, 0, 240), font=font_badge)
    cur_y += int(26 * s)
    draw.text((cur_x, cur_y), f"{data['display_name']} • {data['region']}", fill=(255, 255, 255, 255), font=font_title)
    cur_y += int(42 * s)

    # Hairline divider
    draw.line([(cur_x, cur_y), (card_x + card_w - int(24 * s), cur_y)], fill=(255, 215, 0, 70), width=1)
    cur_y += int(14 * s)

    # 2. Left Column: Topographic vector mini-map
    map_box_w = int(280 * s)
    map_box_h = int(240 * s)
    map_x1, map_y1 = cur_x, cur_y
    map_x2, map_y2 = map_x1 + map_box_w, map_y1 + map_box_h

    draw.rectangle([(map_x1, map_y1), (map_x2, map_y2)], fill=(16, 22, 34, 255), outline=(60, 80, 110, 160), width=1)

    # Subtle cartographic latitude/longitude grid crosshairs
    for gx in (0.33, 0.66):
        px = int(map_x1 + (map_box_w * gx))
        draw.line([(px, map_y1), (px, map_y2)], fill=(40, 55, 80, 100), width=1)
    for gy in (0.33, 0.66):
        py = int(map_y1 + (map_box_h * gy))
        draw.line([(map_x1, py), (map_x2, py)], fill=(40, 55, 80, 100), width=1)

    # Draw Country Vector Polygon with glowing golden outline and warm fill
    pts = [(int(map_x1 + (px * map_box_w)), int(map_y1 + (py * map_box_h))) for px, py in data["polygon_points"]]
    if len(pts) >= 3:
        draw.polygon(pts, fill=(255, 200, 50, 45), outline=(255, 215, 0, 240))

    # Capital City Beacon
    cap_px = int(map_x1 + (data["capital_pos"][0] * map_box_w))
    cap_py = int(map_y1 + (data["capital_pos"][1] * map_box_h))
    draw.ellipse([(cap_px - 8, cap_py - 8), (cap_px + 8, cap_py + 8)], fill=(255, 215, 0, 80))
    draw.ellipse([(cap_px - 4, cap_py - 4), (cap_px + 4, cap_py + 4)], fill=(255, 255, 255, 255))
    draw.text((cap_px + 8, cap_py - 10), f"★ {data['capital']}", fill=(255, 240, 180, 255), font=font_stats)

    # Compass Rose in Corner of Mini-Map
    comp_x, comp_y = map_x2 - int(24 * s), map_y1 + int(20 * s)
    draw.text((comp_x, comp_y), "N", fill=(255, 215, 0, 230), font=font_compass, anchor="mm")
    draw.line([(comp_x, comp_y + 10), (comp_x, comp_y + 20)], fill=(255, 215, 0, 200), width=2)

    # 3. Right Column: Geographic & Almanac Metrics
    stats_x = map_x2 + int(20 * s)
    stat_y = cur_y + int(6 * s)

    draw.text((stats_x, stat_y), f"📍 Capital: {data['capital']}", fill=(255, 255, 255, 240), font=font_sub)
    stat_y += int(30 * s)
    draw.text((stats_x, stat_y), f"🌐 Coords: {data['coords']}", fill=(210, 225, 245, 210), font=font_stats)
    stat_y += int(28 * s)
    draw.text((stats_x, stat_y), f"📐 Land Area: {data['area']}", fill=(255, 215, 0, 230), font=font_stats)
    stat_y += int(28 * s)
    draw.text((stats_x, stat_y), f"🌊 Coastline: {data['coastline']}", fill=(180, 220, 255, 210), font=font_stats)
    stat_y += int(28 * s)
    seas_preview = ", ".join(data["seas"][:2])
    draw.text((stats_x, stat_y), f"⚓ Waters: {seas_preview}", fill=(180, 210, 230, 190), font=font_stats)
    stat_y += int(28 * s)
    borders_preview = ", ".join(data["borders"][:3])
    draw.text((stats_x, stat_y), f"🛡️ Borders: {borders_preview}...", fill=(180, 200, 210, 180), font=font_stats)

    return np.array(pil_overlay)
