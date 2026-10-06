"""Deterministic offline unit tests for CPU perspective drone & camera homography motion engine."""

import numpy as np
import pytest
from src.scripts.local_perspective_drone import compute_perspective_corners


def test_compute_perspective_corners_forward():
    corners_start = compute_perspective_corners(3840, 2160, 0.0, "slow_drone_forward")
    corners_end = compute_perspective_corners(3840, 2160, 1.0, "slow_drone_forward")

    assert isinstance(corners_start, np.ndarray)
    assert corners_start.shape == (4, 2)
    assert isinstance(corners_end, np.ndarray)
    assert corners_end.shape == (4, 2)

    # At progress=0, corners match the outer canvas edges
    assert np.allclose(corners_start[0], [0, 0], atol=1e-2)
    assert np.allclose(corners_start[3], [3840, 2160], atol=1e-2)

    # At progress=1, top-left is moved inward (zoom + tilt)
    assert corners_end[0][0] > 0
    assert corners_end[0][1] > 0
    # Top-right is moved inward from right edge
    assert corners_end[1][0] < 3840


def test_compute_perspective_corners_sweep_directions():
    corners_left = compute_perspective_corners(1920, 1080, 1.0, "drone_sweep_left")
    corners_right = compute_perspective_corners(1920, 1080, 1.0, "drone_sweep_right")

    # Lateral tracking coordinates must be non-zero and distinct
    assert not np.array_equal(corners_left, corners_right)
    # Left sweep shifts x negatively or inward
    assert corners_left[0][0] < corners_right[0][0]


def test_compute_perspective_corners_crane_ascend():
    corners_crane = compute_perspective_corners(1920, 1080, 1.0, "crane_ascend")
    assert corners_crane.shape == (4, 2)
    # Vertical perspective tilt should alter y coordinates
    assert corners_crane[0][1] < corners_crane[2][1]
