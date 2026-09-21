"""Unit tests for flexible duration parser."""

import pytest
from src.core.utils.duration_parser import parse_duration


def test_parse_duration_integers_and_floats():
    assert parse_duration(10) == 10
    assert parse_duration(20.0) == 20
    assert parse_duration("45") == 45
    assert parse_duration(None) == 10


def test_parse_duration_seconds():
    assert parse_duration("10s") == 10
    assert parse_duration("10 sec") == 10
    assert parse_duration("10secs") == 10
    assert parse_duration("15seconds") == 15


def test_parse_duration_minutes():
    assert parse_duration("30m") == 1800
    assert parse_duration("1m") == 60
    assert parse_duration("2 mins") == 120
    assert parse_duration("5minutes") == 300


def test_parse_duration_hours():
    assert parse_duration("1h") == 3600
    assert parse_duration("2 hours") == 7200


def test_parse_duration_combined():
    assert parse_duration("1m30s") == 90
    assert parse_duration("1h 15m") == 4500


def test_parse_duration_invalid():
    with pytest.raises(ValueError, match="Invalid duration format"):
        parse_duration("invalid_duration_text")
