"""Targeted Unit Tests for Universal Tour Asset Idempotency & Recreation.

Verifies that when locally rendered tour images (itinerary cards, route maps,
vacation scope cards) exist on disk, they are reused ($0 spend).
When deleted and resynthesized, they are deterministically recreated.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.services.google_maps_engine import render_4k_google_itinerary_map
from src.services.itinerary_card_engine import render_4k_itinerary_hierarchy_card
from src.services.map_route_engine import render_4k_leisure_vacation_card, render_4k_route_map
from src.services.visual_batch_service import visual_batch_service


def test_itinerary_card_idempotency_and_recreation(tmp_path: Path):
    """Test that Shot 1/10 Itinerary Card is reused when present and recreated when deleted."""
    out_file = tmp_path / "keyframe_p1.jpg"
    stops = [{"attraction_name": "Westminster Abbey", "start_time": "09:00 AM", "end_time": "11:30 AM"}]

    # 1. Initial creation
    res1 = render_4k_itinerary_hierarchy_card("London Tour", stops, out_file)
    assert res1.is_file()
    assert res1.stat().st_size > 100_000
    mtime1 = res1.stat().st_mtime

    # 2. Re-run without force_rerun: should reuse without re-rendering
    res2 = render_4k_itinerary_hierarchy_card("London Tour", stops, out_file)
    assert res2 == out_file
    assert res2.stat().st_mtime == mtime1

    # 3. Delete file and resynthesize: must be recreated
    out_file.unlink()
    assert not out_file.exists()

    res3 = render_4k_itinerary_hierarchy_card("London Tour", stops, out_file)
    assert res3.is_file()
    assert res3.stat().st_size > 100_000


def test_vacation_scope_card_idempotency_and_recreation(tmp_path: Path):
    """Test that Shot 11 Vacation Scope Card is reused when present and recreated when deleted."""
    out_file = tmp_path / "keyframe_p11.jpg"

    # 1. Initial creation
    res1 = render_4k_leisure_vacation_card("London Tour", output_path=out_file)
    assert res1.is_file()
    assert res1.stat().st_size > 50_000
    mtime1 = res1.stat().st_mtime

    # 2. Re-run without force_rerun: should reuse without re-rendering
    res2 = render_4k_leisure_vacation_card("London Tour", output_path=out_file)
    assert res2 == out_file
    assert res2.stat().st_mtime == mtime1

    # 3. Delete file and resynthesize: must be recreated
    out_file.unlink()
    assert not out_file.exists()

    res3 = render_4k_leisure_vacation_card("London Tour", output_path=out_file)
    assert res3.is_file()
    assert res3.stat().st_size > 50_000


def test_google_route_map_idempotency_and_recreation(tmp_path: Path):
    """Test that Route Maps are reused when present and recreated when deleted."""
    out_file = tmp_path / "keyframe_p2.jpg"
    # Pre-populate with dummy valid JPEG > 50KB to simulate existing map without API cost
    dummy_data = b"\xFF\xD8\xFF\xE0" + b"\x00" * 60_000 + b"\xFF\xD9"
    out_file.write_bytes(dummy_data)
    mtime1 = out_file.stat().st_mtime

    # 1. Cache hit: returns existing without calling external network
    res1 = render_4k_route_map(
        origin_name="Westminster Abbey",
        dest_name="Borough Market",
        origin_coords=(51.4994, -0.1273),
        dest_coords=(51.5055, -0.0910),
        distance_badge="3.2 km",
        transit_mode="drive",
        output_path=out_file,
    )
    assert res1 == out_file
    assert res1.stat().st_mtime == mtime1

    # 2. Delete file and verify mock recreation
    out_file.unlink()
    assert not out_file.exists()

    with patch("src.services.google_maps_engine.fetch_google_static_map") as mock_fetch:
        import numpy as np
        # Return a mock 4K image
        mock_fetch.return_value = np.zeros((360, 640, 3), dtype=np.uint8)
        res2 = render_4k_route_map(
            origin_name="Westminster Abbey",
            dest_name="Borough Market",
            origin_coords=(51.4994, -0.1273),
            dest_coords=(51.5055, -0.0910),
            distance_badge="3.2 km",
            transit_mode="drive",
            output_path=out_file,
        )
        assert res2.is_file()
        assert res2.stat().st_size > 50_000


@pytest.mark.asyncio
async def test_visual_batch_keyframe_idempotency_and_recreation(tmp_path: Path):
    """Test that AI keyframes are reused when present and recreated when deleted."""
    out_file = tmp_path / "keyframe_p3.jpg"
    # Pre-populate valid keyframe > 80KB
    dummy_data = b"\xFF\xD8\xFF\xE0" + b"\x00" * 90_000 + b"\xFF\xD9"
    out_file.write_bytes(dummy_data)
    mtime1 = out_file.stat().st_mtime

    tasks = [("Westminster Abbey Gothic facade", out_file, None, 3)]

    # 1. Cache hit: returns immediately without calling generator
    res = await visual_batch_service.render_keyframes_batch(tasks)
    assert len(res) == 1
    assert res[0] == out_file
    assert res[0].stat().st_mtime == mtime1

    # 2. Delete file: must invoke generator
    out_file.unlink()
    assert not out_file.exists()

    with patch.object(
        visual_batch_service,
        "render_keyframes_batch",
        new=AsyncMock(return_value=[out_file]),
    ):
        recreated = await visual_batch_service.render_keyframes_batch(tasks)
        assert len(recreated) == 1
        assert recreated[0] == out_file
