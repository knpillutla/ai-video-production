"""Deterministic offline unit tests for local Ken Burns pan, zoom, and tilt movements."""

import pytest
from src.scripts.local_pan_zoom import (
    CameraMovement,
    assign_scene_camera_movement,
    build_zoompan_expression,
)


def test_camera_movement_enum_values():
    assert CameraMovement.PAN_LEFT == "pan_left"
    assert CameraMovement.PAN_RIGHT == "pan_right"
    assert CameraMovement.TILT_UP == "tilt_up"
    assert CameraMovement.TILT_DOWN == "tilt_down"
    assert CameraMovement.SLOW_ZOOM_IN == "slow_zoom_in"
    assert CameraMovement.SLOW_ZOOM_OUT == "slow_zoom_out"


def test_assign_scene_camera_movement_cadence():
    # Scene 0 / hook defaults to slow_zoom_in
    assert assign_scene_camera_movement(0, "establishing") == CameraMovement.SLOW_ZOOM_IN
    # Spire / vertical defaults to tilt_up
    assert assign_scene_camera_movement(1, "cathedral_spire") == CameraMovement.TILT_UP
    # Wide facade alternates pan
    assert assign_scene_camera_movement(2, "wide_square") == CameraMovement.PAN_RIGHT
    assert assign_scene_camera_movement(3, "wide_facade") == CameraMovement.PAN_LEFT


def test_build_zoompan_expression():
    expr = build_zoompan_expression(CameraMovement.PAN_RIGHT, duration_seconds=5.0, fps=30, target_res=(1920, 1080))
    assert "zoompan" in expr
    assert "1920x1080" in expr
    assert "fps=30" in expr
