"""Deterministic offline unit tests for Tier-0 CPU Micro-Kinetics Engine ($0.00 spend)."""

import numpy as np
import pytest
from src.scripts.local_micro_kinetics import (
    apply_celestial_shimmer,
    apply_tree_canopy_sway,
    apply_water_surface_ripples,
    prepare_micro_kinetics,
    render_micro_kinetics_frame,
)


@pytest.fixture
def sample_canvas() -> np.ndarray:
    """Create a synthetic 4K canvas (3840x2160x3) with identifiable zones."""
    canvas = np.full((2160, 3840, 3), 128, dtype=np.uint8)
    # Add a mock sprite (red car/figure) at y: [1400, 1460], x: [1500, 1580]
    canvas[1400:1460, 1500:1580] = [0, 0, 255]
    # Add mock trees (green) with horizontal texture gradient
    canvas[400:900, 2800:3600] = [0, 200, 0]
    canvas[400:900, 2800:3600, 1] = (np.arange(800) % 256).astype(np.uint8)
    # Add mock water (blue) with horizontal texture gradient
    canvas[1600:2000, 400:2000] = [255, 100, 0]
    canvas[1600:2000, 400:2000, 0] = (np.arange(1600) % 256).astype(np.uint8)
    return canvas


def test_prepare_micro_kinetics_inpainting(sample_canvas: np.ndarray):
    spec = {
        "sprites": [
            {
                "label": "test_car",
                "bbox": [1400 / 2160, 1460 / 2160, 1500 / 3840, 1580 / 3840],
                "delta_pct": [0.05, 0.0],
                "bobbing": False,
            }
        ]
    }
    clean_base, prepared_sprites = prepare_micro_kinetics(sample_canvas, spec)

    assert clean_base.shape == sample_canvas.shape
    assert len(prepared_sprites) == 1
    assert prepared_sprites[0]["sw"] == 80
    assert prepared_sprites[0]["sh"] == 60
    assert prepared_sprites[0]["delta_x"] == pytest.approx(0.05 * 3840, abs=1.0)

    # Inpainted region should no longer be pure red [0, 0, 255]
    inpaint_crop = clean_base[1410:1450, 1510:1570]
    assert not np.all(inpaint_crop == [0, 0, 255])


def test_render_micro_kinetics_sprite_drift(sample_canvas: np.ndarray):
    spec = {
        "sprites": [
            {
                "label": "test_pedestrian",
                "bbox": [1400 / 2160, 1460 / 2160, 1500 / 3840, 1580 / 3840],
                "delta_pct": [0.05, 0.0],
                "bobbing": True,
            }
        ]
    }
    clean_base, prepared_sprites = prepare_micro_kinetics(sample_canvas, spec)

    # Frame 0: sprite is at original position
    frame_0 = render_micro_kinetics_frame(clean_base, prepared_sprites, spec, 0, 120)
    # Frame 60: sprite has drifted forward
    frame_60 = render_micro_kinetics_frame(clean_base, prepared_sprites, spec, 60, 120)

    assert frame_0.shape == sample_canvas.shape
    assert frame_60.shape == sample_canvas.shape
    # Drifted frame must be distinct from initial frame
    assert not np.array_equal(frame_0, frame_60)


def test_apply_tree_canopy_sway_and_water_ripples(sample_canvas: np.ndarray):
    frame = sample_canvas.copy()
    tree_zones = [[400 / 2160, 900 / 2160, 2800 / 3840, 3600 / 3840]]
    water_zones = [[1600 / 2160, 2000 / 2160, 400 / 3840, 2000 / 3840]]

    apply_tree_canopy_sway(frame, tree_zones, frame_idx=15)
    apply_water_surface_ripples(frame, water_zones, frame_idx=15)

    # Tree and water regions should be modified while outside remains unchanged
    assert not np.array_equal(frame[400:900, 2800:3600], sample_canvas[400:900, 2800:3600])
    assert not np.array_equal(frame[1600:2000, 400:2000], sample_canvas[1600:2000, 400:2000])
    # Unrelated region remains identical
    assert np.array_equal(frame[0:100, 0:100], sample_canvas[0:100, 0:100])


def test_apply_celestial_shimmer(sample_canvas: np.ndarray):
    frame = sample_canvas.copy()
    cel = {"type": "sun", "center": [0.2, 0.8]}
    apply_celestial_shimmer(frame, cel, frame_idx=10)

    assert frame.shape == sample_canvas.shape
    # Corona area around [0.2*2160, 0.8*3840] should have altered brightness
    cy, cx = int(0.2 * 2160), int(0.8 * 3840)
    assert not np.array_equal(frame[cy - 20:cy + 20, cx - 20:cx + 20], sample_canvas[cy - 20:cy + 20, cx - 20:cx + 20])
