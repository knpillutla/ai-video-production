"""Tests for World Theme Rotator: Dynamic world place and environment rotation for themes."""

import pytest
from src.services.world_theme_rotator import (
    WORLD_DESTINATIONS,
    resolve_world_theme_setting,
)


def test_walking_in_rain_cycles_through_diverse_world_destinations():
    """Verify that 'walking in rain' rotates through distinct places on Earth on repeated execution."""
    locations_encountered = set()
    categories_encountered = set()

    for i in range(len(WORLD_DESTINATIONS)):
        setting = resolve_world_theme_setting("walking in rain", user_id=f"test_user_{i}")
        locations_encountered.add(setting.location)
        categories_encountered.add(setting.category)
        assert len(setting.palette_rgb) >= 2
        assert len(setting.architecture) > 10
        assert len(setting.lighting) > 10
        assert len(setting.scene_1_beat) > 10

    # Must cover multiple geographical categories: cities, alpine villages, coastal oceans, mountains
    assert len(locations_encountered) >= 4
    assert len(categories_encountered) >= 3


def test_user_specific_sequential_rotation():
    """Verify that a single user gets a different world destination on consecutive runs."""
    uid = "user_consistent_runner"
    first = resolve_world_theme_setting("walking in rain", user_id=uid)
    second = resolve_world_theme_setting("walking in rain", user_id=uid)

    assert first.location != second.location


def test_explicit_location_override():
    """Verify that if user explicitly requests a location, it is honored over random rotation."""
    tokyo_setting = resolve_world_theme_setting("walking in rain in tokyo")
    assert "Tokyo" in tokyo_setting.location

    hallstatt_setting = resolve_world_theme_setting("walking in rain in hallstatt")
    assert "Hallstatt" in hallstatt_setting.location
