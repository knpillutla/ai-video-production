"""Downloadable GPX & KML GPS Route File Export Service ($0.00 Spend).

Generates standard GPX 1.1 and KML 2.2 route files from documentary itineraries
for direct import into Garmin, Google Maps, Apple Maps, and Google Earth.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_templates import DocStoryboard

# Default geographic waypoints for top sovereign destinations
DEFAULT_DESTINATION_WAYPOINTS: Dict[str, List[Tuple[str, float, float, str]]] = {
    "italy": [
        ("Colosseum & Roman Forum", 41.8902, 12.4922, "Ancient Roman Amphitheatre & Forum"),
        ("Pantheon", 41.8986, 12.4769, "Roman temple of antiquity"),
        ("Trevi Fountain", 41.9009, 12.4833, "Baroque architectural marvel"),
        ("Vatican City & St. Peter's", 41.9029, 12.4534, "Sovereign sanctuary of the Papacy"),
        ("Florence Cathedral (Duomo)", 43.7731, 11.2560, "Renaissance dome and citadel"),
    ],
    "france": [
        ("Eiffel Tower & Champ de Mars", 48.8584, 2.2945, "Iconic wrought-iron lattice monument"),
        ("Louvre Palace & Pyramid", 48.8606, 2.3376, "Historic royal citadel and museum"),
        ("Notre-Dame Cathedral", 48.8530, 2.3499, "Medieval Gothic cathedral"),
        ("Montmartre & Sacré-Cœur", 48.8867, 2.3431, "Historic hilltop artistic quarter"),
        ("Palace of Versailles", 48.8049, 2.1204, "Grand monarchical estate & gardens"),
    ],
    "japan": [
        ("Senso-ji Temple & Asakusa", 35.7148, 139.7967, "Tokyo's oldest Buddhist temple"),
        ("Shibuya Crossing & Hachiko", 35.6595, 139.7005, "Vibrant urban heart of modern Tokyo"),
        ("Fushimi Inari-taisha", 34.9671, 135.7727, "Sacred mountain path of 10,000 torii gates"),
        ("Kinkaku-ji (Golden Pavilion)", 35.0394, 135.7292, "Zen Buddhist temple covered in gold leaf"),
        ("Arashiyama Bamboo Grove", 35.0169, 135.6713, "Serene natural bamboo forest"),
    ],
    "switzerland": [
        ("Lauterbrunnen Valley", 46.5935, 7.9090, "Valley of 72 waterfalls"),
        ("Jungfraujoch - Top of Europe", 46.5475, 7.9825, "High alpine glacial saddle (3,454m)"),
        ("Zermatt & The Matterhorn", 45.9765, 7.7491, "Iconic pyramidal alpine peak"),
        ("Lake Geneva & Chillon Castle", 46.4142, 6.9275, "Medieval island fortress on lake"),
        ("Lucerne Chapel Bridge", 47.0516, 8.3073, "Historic covered wooden footbridge"),
    ],
}


def _extract_waypoints(storyboard: DocStoryboard) -> List[Tuple[str, float, float, str]]:
    """Extract ordered waypoints (name, lat, lon, description) from scenes or fallbacks."""
    waypoints: List[Tuple[str, float, float, str]] = []

    for sc in storyboard.scenes:
        name = sc.fact_badge or f"Stop {sc.scene_index}"
        desc = sc.narration_text[:120] if sc.narration_text else sc.visual_prompt[:120]
        # Check explicit scene attributes if present
        coords = getattr(sc, "origin_coords", None) or getattr(sc, "coordinates", None)
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            try:
                lat, lon = float(coords[0]), float(coords[1])
                waypoints.append((name, lat, lon, desc))
            except (ValueError, TypeError):
                pass

    if waypoints:
        return waypoints

    # Match country or destination entity
    c_val = getattr(storyboard, "country", "") or ""
    dest_val = getattr(storyboard, "destination_entity", "") or ""
    query = f"{c_val} {dest_val} {storyboard.title}".lower()
    for key, pts in DEFAULT_DESTINATION_WAYPOINTS.items():
        if key in query:
            return pts

    # Generic global default (Rome cultural corridor)
    return DEFAULT_DESTINATION_WAYPOINTS["italy"]


def export_itinerary_gps_package(
    storyboard: DocStoryboard,
    output_dir: Path,
) -> Dict[str, Path]:
    """Generate and save route_itinerary.gpx and route_itinerary.kml files.

    Strictly idempotent: returns cached files if non-empty on disk (Rule 3).
    """
    gpx_file = output_dir / "route_itinerary.gpx"
    kml_file = output_dir / "route_itinerary.kml"

    if (
        gpx_file.is_file()
        and gpx_file.stat().st_size > 100
        and kml_file.is_file()
        and kml_file.stat().st_size > 100
    ):
        logger.info(f"reusing_existing_gps_route_package: {gpx_file.name}, {kml_file.name}")
        return {"gpx": gpx_file, "kml": kml_file}

    output_dir.mkdir(parents=True, exist_ok=True)
    waypoints = _extract_waypoints(storyboard)
    esc_title = escape(storyboard.title)
    esc_desc = escape(f"Curated Educational Tour Itinerary for {storyboard.title}")

    # Build GPX 1.1 XML
    gpx_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="AI Video Producer Studio" xmlns="http://www.topografix.com/GPX/1/1">',
        f'  <metadata><name>{esc_title}</name><desc>{esc_desc}</desc></metadata>',
    ]
    for name, lat, lon, desc in waypoints:
        gpx_lines.append(
            f'  <wpt lat="{lat:.6f}" lon="{lon:.6f}">'
            f'<name>{escape(name)}</name><desc>{escape(desc)}</desc></wpt>'
        )
    gpx_lines.append(f'  <trk><name>{esc_title} Route</name><trkseg>')
    for name, lat, lon, _ in waypoints:
        gpx_lines.append(f'    <trkpt lat="{lat:.6f}" lon="{lon:.6f}"><name>{escape(name)}</name></trkpt>')
    gpx_lines.extend(['  </trkseg></trk>', '</gpx>'])
    gpx_file.write_text("\n".join(gpx_lines), encoding="utf-8")

    # Build KML 2.2 XML
    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        f'  <Document><name>{esc_title}</name><description>{esc_desc}</description>',
        '    <Style id="routeLine"><LineStyle><color>ff37afd4</color><width>4</width></LineStyle></Style>',
    ]
    for name, lat, lon, desc in waypoints:
        kml_lines.append(
            f'    <Placemark><name>{escape(name)}</name><description>{escape(desc)}</description>'
            f'<Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point></Placemark>'
        )
    coord_str = " ".join(f"{lon:.6f},{lat:.6f},0" for _, lat, lon, _ in waypoints)
    kml_lines.append(
        f'    <Placemark><name>{esc_title} Itinerary Path</name>'
        f'<styleUrl>#routeLine</styleUrl><LineString><extrude>1</extrude><tessellate>1</tessellate>'
        f'<coordinates>{coord_str}</coordinates></LineString></Placemark>'
    )
    kml_lines.extend(['  </Document>', '</kml>'])
    kml_file.write_text("\n".join(kml_lines), encoding="utf-8")

    logger.info(f"itinerary_gps_package_exported: {gpx_file.name}, {kml_file.name} ({len(waypoints)} waypoints)")
    return {"gpx": gpx_file, "kml": kml_file}
