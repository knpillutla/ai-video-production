"""Google Maps Static API Network Client & Web Mercator Math.

Provides API key resolution, Mercator projection calculations, and strict
zero-fallback HTTP queries to Google Maps Static API.
"""

from __future__ import annotations

import math
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple

import cv2
import numpy as np


def get_google_maps_api_key() -> str:
    """Retrieves Google Maps API key or raises RuntimeError immediately (Zero Fallback)."""
    from src.core.config import settings

    key = (
        os.getenv("GOOGLE_MAPS_API_KEY")
        or getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        or getattr(settings, "google_maps_api_key", "")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or getattr(getattr(settings, "llm", None), "google_api_key", None)
        or getattr(getattr(settings, "llm", None), "gemini_api_key", None)
        or ""
    ).strip()

    if not key:
        raise RuntimeError(
            "Google Maps Error: No API key found. Strict zero-fallback mandate requires "
            "GOOGLE_MAPS_API_KEY, GOOGLE_API_KEY, or GEMINI_API_KEY to be set in environment."
        )
    return key


def calculate_bounds_and_zoom(
    coords: List[Tuple[float, float]],
    map_w: int = 640,
    map_h: int = 360,
) -> Tuple[float, float, int]:
    """Calculates center coordinates and optimal integer zoom level to fit all coordinates."""
    if not coords:
        raise ValueError("Cannot calculate map bounds for empty coordinate list.")

    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0

    lat_span = max(0.002, max_lat - min_lat)
    lon_span = max(0.002, max_lon - min_lon)

    margin_factor = 1.45
    lon_zoom = math.log2(360.0 * (map_w / 256.0) / (lon_span * margin_factor))
    lat_rad_span = math.radians(lat_span * margin_factor)
    lat_zoom = math.log2(math.pi * (map_h / 256.0) / lat_rad_span)

    zoom = int(math.floor(min(lon_zoom, lat_zoom)))
    return center_lat, center_lon, max(2, min(17, zoom))


def lat_lon_to_canvas_pixel(
    lat: float,
    lon: float,
    center_lat: float,
    center_lon: float,
    zoom: int,
    canvas_w: int = 3840,
    canvas_h: int = 2160,
    base_w: int = 1280,
    base_h: int = 720,
) -> Tuple[int, int]:
    """Projects geographic coordinates onto 4K canvas pixels using exact Web Mercator formula."""
    scale = 2
    total_size = 256 * (1 << zoom) * scale

    x = (lon + 180.0) / 360.0 * total_size
    center_x = (center_lon + 180.0) / 360.0 * total_size

    lat_rad = math.radians(max(-85.0511, min(85.0511, lat)))
    y = (1.0 - math.log(math.tan(math.pi / 4.0 + lat_rad / 2.0)) / math.pi) / 2.0 * total_size

    c_lat_rad = math.radians(max(-85.0511, min(85.0511, center_lat)))
    center_y = (1.0 - math.log(math.tan(math.pi / 4.0 + c_lat_rad / 2.0)) / math.pi) / 2.0 * total_size

    px = int(round(base_w / 2.0 + (x - center_x)))
    py = int(round(base_h / 2.0 + (y - center_y)))

    return int(round(px * (canvas_w / float(base_w)))), int(round(py * (canvas_h / float(base_h))))


def fetch_google_static_map(
    center_lat: float,
    center_lon: float,
    zoom: int,
    path_coords: List[Tuple[float, float]],
    api_key: str,
    maptype: str = "roadmap",
    completed_coords: Optional[List[Tuple[float, float]]] = None,
    upcoming_coords: Optional[List[Tuple[float, float]]] = None,
) -> np.ndarray:
    """Fetches high-DPI raster from Google Maps Static API. Strict: raises on any error."""
    base_url = "https://maps.googleapis.com/maps/api/staticmap"

    params: List[Tuple[str, str]] = [
        ("center", f"{center_lat:.6f},{center_lon:.6f}"),
        ("zoom", str(zoom)),
        ("size", "640x360"),
        ("scale", "2"),
        ("maptype", maptype),
        ("format", "png"),
        ("key", api_key),
    ]

    has_split = False
    if completed_coords and len(completed_coords) >= 2:
        params.append(("path", "color:0x2ECC71ff|weight:6|" + "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in completed_coords)))
        has_split = True
    if upcoming_coords and len(upcoming_coords) >= 2:
        params.append(("path", "color:0x2563EBff|weight:6|" + "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in upcoming_coords)))
        has_split = True
    if not has_split and len(path_coords) >= 2:
        params.append(("path", "color:0x2563EBff|weight:5|" + "|".join(f"{lat:.6f},{lon:.6f}" for lat, lon in path_coords)))

    req = urllib.request.Request(
        f"{base_url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "CineAIStudio/1.0 (GoogleMaps-4K-Engine)"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Google Maps Static API returned non-200 status: {resp.status}")
            data = resp.read()
            if not data.startswith(b"\x89PNG") and not data.startswith(b"\xff\xd8"):
                raise RuntimeError(f"Google Maps Static API Error: Invalid image:\n{data.decode('utf-8', errors='ignore')[:400]}")
            img = cv2.imdecode(np.asarray(bytearray(data), dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                raise RuntimeError("Google Maps Static API returned undecodable image bytes.")
            return img
    except urllib.error.HTTPError as e_http:
        err_body = e_http.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Google Maps Static API HTTP Error ({e_http.code}): {e_http.reason}\nBody: {err_body[:400]}") from e_http
    except Exception as ex:
        raise RuntimeError(f"Google Maps Static API Request Failed: {ex}") from ex
