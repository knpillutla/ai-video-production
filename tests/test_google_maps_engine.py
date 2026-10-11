"""Targeted unit tests for Google Maps 4K itinerary & route engine.

Verifies:
1. Zero-fallback API key enforcement (raises RuntimeError if no key).
2. Exact Web Mercator bounds and 4K pixel projection.
3. Successful 4K render with pins and callouts using mocked Google Static Maps response.
4. Fail-fast error propagation on HTTP 403 / API failures without silent fallback.
"""

import io
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import pytest

from src.services.google_maps_engine import (
    get_google_maps_api_key,
    calculate_bounds_and_zoom,
    lat_lon_to_canvas_pixel,
    render_4k_google_itinerary_map,
)


def test_api_key_missing_raises_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("src.core.config.settings") as mock_settings:
        mock_settings.GOOGLE_MAPS_API_KEY = ""
        mock_settings.google_maps_api_key = ""
        mock_settings.media.google_maps_api_key = ""
        mock_settings.llm.google_api_key = ""
        mock_settings.llm.gemini_api_key = ""
        with pytest.raises(RuntimeError, match="No API key found"):
            get_google_maps_api_key()


def test_calculate_bounds_and_zoom():
    coords = [(51.4994, -0.1273), (51.5055, -0.0910), (51.5081, -0.0759)]
    center_lat, center_lon, zoom = calculate_bounds_and_zoom(coords)
    assert 51.49 <= center_lat <= 51.52
    assert -0.14 <= center_lon <= -0.06
    assert 10 <= zoom <= 16


def test_lat_lon_to_canvas_pixel():
    center_lat, center_lon, zoom = 51.5037, -0.1016, 13
    px, py = lat_lon_to_canvas_pixel(51.5037, -0.1016, center_lat, center_lon, zoom)
    # Center point should land approximately in the center of 3840x2160 canvas
    assert 1800 <= px <= 2040
    assert 1000 <= py <= 1160


def test_render_4k_google_itinerary_map_success(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-12345")

    # Generate a dummy 1280x720 base image simulating Google Static Maps scale=2 response
    dummy_img = np.full((720, 1280, 3), 200, dtype=np.uint8)
    _, buf = cv2.imencode(".png", dummy_img)
    mock_bytes = buf.tobytes()

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = mock_bytes
    mock_resp.__enter__.return_value = mock_resp

    stops = [
        {"name": "Westminster Abbey", "coords": (51.4994, -0.1273), "attraction_cost": "£29.00", "visit_duration": "2.5 hrs"},
        {"name": "Borough Market", "coords": (51.5055, -0.0910), "attraction_cost": "Free", "visit_duration": "1.5 hrs"},
        {"name": "Tower of London", "coords": (51.5081, -0.0759), "attraction_cost": "£34.00", "visit_duration": "2.0 hrs"},
    ]

    out_file = tmp_path / "test_google_map_4k.jpg"

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = render_4k_google_itinerary_map(
            tour_title="London Historic Circuit",
            stops=stops,
            output_path=out_file,
            distance_badge="5.2 km",
            transit_mode="walk",
        )

    assert res.is_file()
    assert res.stat().st_size > 1000
    img = cv2.imread(str(res))
    assert img.shape == (2160, 3840, 3)


def test_render_4k_google_itinerary_map_fail_fast_on_api_error(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-12345")

    # Simulate HTTP 403 Forbidden from Google Static Maps
    mock_err = urllib.error.HTTPError(
        url="https://maps.googleapis.com",
        code=403,
        msg="Forbidden",
        hdrs={},
        fp=io.BytesIO(b'{"error_message": "The provided API key is invalid or lacks Maps permissions."}'),
    )

    stops = [
        {"name": "Stop A", "coords": (51.5, -0.1)},
        {"name": "Stop B", "coords": (51.51, -0.08)},
    ]
    out_file = tmp_path / "test_error_map.jpg"

    with patch("urllib.request.urlopen", side_effect=mock_err):
        with pytest.raises(RuntimeError, match="Google Maps Static API HTTP Error \\(403\\)"):
            render_4k_google_itinerary_map(
                tour_title="Error Test Tour",
                stops=stops,
                output_path=out_file,
            )


def test_format_dual_distance():
    from src.services.google_maps_engine import format_dual_distance

    assert format_dual_distance("2.8 km") == "2.8 km (1.7 mi)"
    assert format_dual_distance("4.5 km") == "4.5 km (2.8 mi)"
    assert format_dual_distance("1.0 mi") == "1.0 mi"
    assert format_dual_distance(None) == "1.5 km (0.9 mi)"


def test_render_4k_google_itinerary_map_progressive_colors(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-12345")

    dummy_img = np.full((720, 1280, 3), 200, dtype=np.uint8)
    _, buf = cv2.imencode(".png", dummy_img)
    mock_bytes = buf.tobytes()

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = mock_bytes
    mock_resp.__enter__.return_value = mock_resp

    stops = [
        {"name": "Stop 1", "coords": (51.49, -0.12)},
        {"name": "Stop 2", "coords": (51.50, -0.09)},
        {"name": "Stop 3", "coords": (51.51, -0.07)},
    ]
    out_file = tmp_path / "test_progressive_map.jpg"

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        res = render_4k_google_itinerary_map(
            tour_title="Progressive Tour",
            stops=stops,
            output_path=out_file,
            current_stop_index=2,
        )

    assert res.is_file()
    assert res.stat().st_size > 1000
    # Verify request had both completed (green) and upcoming (blue) paths
    req_call = mock_urlopen.call_args[0][0]
    req_url = req_call.full_url
    assert "0x2ECC71ff" in req_url  # Emerald Green for completed leg (Stop 1 to Stop 2)
    assert "0x2563EBff" in req_url  # Royal Blue for upcoming leg (Stop 2 to Stop 3)


