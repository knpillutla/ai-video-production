"""Deterministic unit tests for Drone Living Dynamics ($0.00 cost, 100% offline)."""
import cv2
import numpy as np
import pytest
from src.scripts.drone_living_dynamics import (
    SpecularWaterShimmerEngine,
    AtmosphericCloudDriftEngine,
    DroneLivingWorld,
)
from src.scripts.local_perspective_drone import LivingEnvironmentEngine


def _create_synthetic_landscape(w: int = 640, h: int = 360) -> np.ndarray:
    """Create synthetic test frame: top 30% white sky, middle 30% noisy rocky mountain, bottom 40% blue water."""
    img = np.zeros((h, w, 3), dtype=np.uint8)

    y_sky = int(h * 0.30)
    y_mount = int(h * 0.65)
    # 1. Sky: soft gradient with subtle cloud texture
    sky_grad = np.linspace(235, 190, y_sky, dtype=np.uint8)[:, None, None]
    sky_tex = np.random.randint(-12, 12, (y_sky, w, 3), dtype=np.int16)
    img[:y_sky, :] = np.clip(sky_grad + sky_tex, 0, 255).astype(np.uint8)
    img[y_sky:y_mount, :] = np.random.randint(40, 140, (y_mount - y_sky, w, 3), dtype=np.uint8)
    img[y_mount:, :] = [160, 110, 40]
    return img


def test_specular_water_shimmer_detection_and_safety():
    """Verify water body is detected, wave & caustic glints generated, and land is untouched."""
    img = _create_synthetic_landscape(640, 360)
    engine = SpecularWaterShimmerEngine(img, 640, 360, num_frames=12)

    assert engine.has_water is True
    assert len(engine.plates) == 12

    # Check temporal variation in water
    diff_water = cv2.absdiff(engine.plates[0], engine.plates[6])
    # Water region (bottom 35%) should have dynamic wave & shimmer changes
    assert diff_water[int(360 * 0.70) :, :].mean() > 0.5

    # Critical anti-bleed safety: rocky mountain zone (y: 120-220) must be 100% untouched
    mountain_diff = diff_water[int(360 * 0.35) : int(360 * 0.55), :]
    assert mountain_diff.max() == 0, "Water waves/shimmer must never bleed onto rocky mountain terrain"


def test_atmospheric_cloud_drift():
    """Verify sky is detected, clouds billow/drift, and ground is untouched."""
    img = _create_synthetic_landscape(640, 360)
    engine = AtmosphericCloudDriftEngine(img, 640, 360, num_frames=12)

    assert engine.has_clouds is True
    assert len(engine.plates) == 12

    diff_sky = cv2.absdiff(engine.plates[0], engine.plates[6])
    # Sky region (top 20%) should have drift
    assert diff_sky[: int(360 * 0.20), :].mean() > 0.2

    # Ground/water region (bottom 40%) must be 100% untouched by cloud drift
    ground_diff = diff_sky[int(360 * 0.60) :, :]
    assert ground_diff.max() == 0, "Cloud drift must never bleed onto ground/water"


def test_drone_living_world_orchestrator():
    """Verify unified DroneLivingWorld produces composite cyclic plates with O(1) lookup."""
    img = _create_synthetic_landscape(640, 360)
    living_world = DroneLivingWorld(img, 640, 360, enable_water=True, enable_clouds=True, enable_objects=False, num_frames=12)

    assert len(living_world.cycle_plates) == 12
    plate_0 = living_world.get_source_plate(0, img)
    plate_100 = living_world.get_source_plate(100, img)

    assert plate_0.shape == (360, 640, 3)
    assert plate_100.shape == (360, 640, 3)
    # Frame 100 modulo 12 is frame 4
    plate_4 = living_world.get_source_plate(4, img)
    assert np.array_equal(plate_100, plate_4)


def test_living_environment_engine_backward_compatibility():
    """Verify LivingEnvironmentEngine integration in local_perspective_drone retains backward compatibility."""
    img = _create_synthetic_landscape(640, 360)
    env = LivingEnvironmentEngine(img, 640, 360, enable_water=True, enable_clouds=True)

    assert env.cycle_plates is not None
    assert len(env.cycle_plates) == 36

    p0 = env.get_source_plate(0)
    p72 = env.get_source_plate(72)
    assert p0.shape == (360, 640, 3)
    assert np.array_equal(p0, p72)
