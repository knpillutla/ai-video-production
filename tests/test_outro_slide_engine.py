"""Deterministic offline tests for 4K Outro Slide Engine & Documentary Duration Boundaries."""

from pathlib import Path
import numpy as np
import pytest
from PIL import Image

from src.services.outro_slide_engine import (
    is_documentary_or_tour,
    render_4k_outro_slide,
    _wrap_text,
)


def test_is_documentary_or_tour_detection():
    assert is_documentary_or_tour("documentary", "blue_chip_doc") is True
    assert is_documentary_or_tour("travel/scenic", "walking_tour") is True
    assert is_documentary_or_tour("relax/nature", "forest", "ancient_forest") is False
    assert is_documentary_or_tour("comedy/telugu") is False
    assert is_documentary_or_tour("travel", archetype="one_day_tour") is True
    assert is_documentary_or_tour("nature_doc", archetype="wildlife") is True


def test_wrap_text():
    text = "Wonders of Europe: A Continental Odyssey Across High Mountain Passes"
    lines = _wrap_text(text, max_chars=35)
    assert len(lines) >= 2
    assert all(len(line) <= 40 for line in lines)


def test_render_4k_outro_slide_documentary(tmp_path: Path):
    out_img = tmp_path / "outro_doc.jpg"
    res = render_4k_outro_slide(
        output_image_path=out_img,
        title="Wonders of Europe: A Continental Odyssey",
        channel_name="Euro Discovery",
        is_tour=False,
        target_res=(1920, 1080),  # test at 1080p for fast unit testing
    )
    assert res.is_file()
    assert res.stat().st_size > 5000
    with Image.open(res) as img:
        assert img.size == (1920, 1080)


def test_render_4k_outro_slide_tour_with_stops(tmp_path: Path):
    out_img = tmp_path / "outro_tour.jpg"
    stops = [
        {"name": "Eiffel Tower", "visit_duration": "2.0 hrs"},
        {"name": "Louvre Museum", "visit_duration": "3.0 hrs"},
        {"name": "Notre Dame", "visit_duration": "1.5 hrs"},
    ]
    res = render_4k_outro_slide(
        output_image_path=out_img,
        title="1-Day Ultimate Paris Odyssey",
        channel_name="Euro Discovery",
        is_tour=True,
        tour_stops=stops,
        target_res=(1920, 1080),
    )
    assert res.is_file()
    assert res.stat().st_size > 5000
    with Image.open(res) as img:
        assert img.size == (1920, 1080)


def test_living_environment_engine_water_flag():
    from src.scripts.local_perspective_drone import LivingEnvironmentEngine

    dummy_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
    # Paint lower region with cyan to mimic shaded rock
    dummy_img[400:, :] = [120, 80, 80]  # Hue in water range

    # Case 1: enable_water = False -> water_mask must be None
    engine_no_water = LivingEnvironmentEngine(dummy_img, 1920, 1080, enable_water=False)
    assert engine_no_water.water_mask is None
    assert engine_no_water.cycle_plates is None

    # Case 2: enable_water = True -> water detection activates without sinusoidal grating
    engine_water = LivingEnvironmentEngine(dummy_img, 1920, 1080, enable_water=True)
    assert engine_water.water_mask is not None
